from flask import Flask, render_template, request, redirect, session, Response
from datetime import date
import sqlite3
import csv
import io
import os
import shutil

app = Flask(__name__)

app.secret_key = "libratrack-secret-key"


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Vercel's deployed filesystem is read-only.
# /tmp is writable during serverless execution.
if os.environ.get("VERCEL"):
    DATABASE = "/tmp/library.db"
    SOURCE_DATABASE = os.path.join(BASE_DIR, "library.db")

    if not os.path.exists(DATABASE):
        if os.path.exists(SOURCE_DATABASE):
            shutil.copy2(SOURCE_DATABASE, DATABASE)
else:
    DATABASE = os.path.join(BASE_DIR, "library.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            member_id INTEGER NOT NULL,
            issue_date TEXT NOT NULL,
            due_date TEXT NOT NULL,
            return_date TEXT,
            status TEXT NOT NULL DEFAULT 'Issued',
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (member_id) REFERENCES members(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return render_template("index.html")


# =========================================================
# BOOKS
# =========================================================

@app.route("/books")
def books():
    conn = get_db()

    books = conn.execute("""
        SELECT books.*,
        CASE
            WHEN EXISTS (
                SELECT 1
                FROM transactions
                WHERE transactions.book_id = books.id
                AND transactions.status = 'Issued'
            )
            THEN 'Issued'
            ELSE 'Available'
        END AS status
        FROM books
        ORDER BY books.title
    """).fetchall()

    conn.close()

    return render_template("books.html", books=books)


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "LibraTrack@2026":

            session["admin_logged_in"] = True

            return redirect("/admin")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.pop("admin_logged_in", None)

    return redirect("/login")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    conn = get_db()

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    issued_books = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status = 'Issued'
    """).fetchone()[0]

    returned_books = conn.execute("""
        SELECT COUNT(*)
        FROM transactions
        WHERE status = 'Returned'
    """).fetchone()[0]

    total_members = conn.execute(
        "SELECT COUNT(*) FROM members"
    ).fetchone()[0]

    available_books = total_books - issued_books

    transactions = conn.execute("""
        SELECT
            transactions.id,
            books.title AS book_title,
            members.name AS member_name,
            transactions.issue_date,
            transactions.due_date,
            transactions.return_date,
            transactions.status
        FROM transactions
        JOIN books
            ON books.id = transactions.book_id
        JOIN members
            ON members.id = transactions.member_id
        ORDER BY transactions.id DESC
    """).fetchall()

    books = conn.execute("""
        SELECT *
        FROM books
        ORDER BY title
    """).fetchall()

    members = conn.execute("""
        SELECT *
        FROM members
        ORDER BY name
    """).fetchall()

    available_book_list = conn.execute("""
        SELECT *
        FROM books
        WHERE NOT EXISTS (
            SELECT 1
            FROM transactions
            WHERE transactions.book_id = books.id
            AND transactions.status = 'Issued'
        )
        ORDER BY title
    """).fetchall()

    issued_transactions = conn.execute("""
        SELECT
            transactions.id,
            books.title AS book_title,
            members.name AS member_name,
            transactions.issue_date,
            transactions.due_date
        FROM transactions
        JOIN books
            ON books.id = transactions.book_id
        JOIN members
            ON members.id = transactions.member_id
        WHERE transactions.status = 'Issued'
        ORDER BY books.title
    """).fetchall()

    conn.close()

    return render_template(
        "admin.html",
        total_books=total_books,
        available_books=available_books,
        issued_books=issued_books,
        returned_books=returned_books,
        total_members=total_members,
        transactions=transactions,
        books=books,
        members=members,
        available_book_list=available_book_list,
        issued_transactions=issued_transactions
    )


# =========================================================
# ADD BOOK
# =========================================================

@app.route("/add_book", methods=["POST"])
def add_book():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    title = request.form["title"]
    author = request.form["author"]
    isbn = request.form["isbn"]
    category = request.form["category"]

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO books
            (title, author, isbn, category)
            VALUES (?, ?, ?, ?)
        """, (
            title,
            author,
            isbn,
            category
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/admin")


# =========================================================
# EDIT BOOK
# =========================================================

@app.route("/edit_book/<int:book_id>", methods=["POST"])
def edit_book(book_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    title = request.form["title"]
    author = request.form["author"]
    isbn = request.form["isbn"]
    category = request.form["category"]

    conn = get_db()

    try:

        conn.execute("""
            UPDATE books
            SET title = ?,
                author = ?,
                isbn = ?,
                category = ?
            WHERE id = ?
        """, (
            title,
            author,
            isbn,
            category,
            book_id
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/admin")


# =========================================================
# ADD MEMBER
# =========================================================

@app.route("/add_member", methods=["POST"])
def add_member():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]

    conn = get_db()

    try:

        conn.execute("""
            INSERT INTO members
            (name, email, phone)
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            phone
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/admin")


# =========================================================
# EDIT MEMBER
# =========================================================

@app.route("/edit_member/<int:member_id>", methods=["POST"])
def edit_member(member_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    name = request.form["name"]
    email = request.form["email"]
    phone = request.form["phone"]

    conn = get_db()

    try:

        conn.execute("""
            UPDATE members
            SET name = ?,
                email = ?,
                phone = ?
            WHERE id = ?
        """, (
            name,
            email,
            phone,
            member_id
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/admin")


# =========================================================
# DELETE MEMBER
# =========================================================

@app.route("/delete_member/<int:member_id>", methods=["POST"])
def delete_member(member_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    conn = get_db()

    transaction = conn.execute("""
        SELECT id
        FROM transactions
        WHERE member_id = ?
        LIMIT 1
    """, (member_id,)).fetchone()

    if transaction:

        conn.close()

        return redirect("/admin?delete_blocked=1")

    conn.execute("""
        DELETE FROM members
        WHERE id = ?
    """, (member_id,))

    conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# ISSUE BOOK
# =========================================================

@app.route("/issue_book", methods=["POST"])
def issue_book():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    isbn = request.form["isbn"]
    member_id = request.form["member_id"]
    due_date = request.form["due_date"]

    conn = get_db()

    book = conn.execute("""
        SELECT id
        FROM books
        WHERE isbn = ?
    """, (isbn,)).fetchone()

    if not book:

        conn.close()

        return redirect("/admin")

    existing = conn.execute("""
        SELECT id
        FROM transactions
        WHERE book_id = ?
        AND status = 'Issued'
    """, (book["id"],)).fetchone()

    if not existing:

        conn.execute("""
            INSERT INTO transactions
            (
                book_id,
                member_id,
                issue_date,
                due_date,
                status
            )
            VALUES (?, ?, ?, ?, 'Issued')
        """, (
            book["id"],
            member_id,
            date.today().isoformat(),
            due_date
        ))

        conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# RETURN BOOK - MANUAL
# =========================================================

@app.route("/return_book", methods=["POST"])
def return_book_manual():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    transaction_id = request.form["transaction_id"]

    conn = get_db()

    conn.execute("""
        UPDATE transactions
        SET return_date = ?,
            status = 'Returned'
        WHERE id = ?
        AND status = 'Issued'
    """, (
        date.today().isoformat(),
        transaction_id
    ))

    conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# RETURN BOOK - TRANSACTION ID
# =========================================================

@app.route("/return_book/<int:transaction_id>", methods=["POST"])
def return_book(transaction_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    conn = get_db()

    conn.execute("""
        UPDATE transactions
        SET return_date = ?,
            status = 'Returned'
        WHERE id = ?
        AND status = 'Issued'
    """, (
        date.today().isoformat(),
        transaction_id
    ))

    conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# RETURN BOOK - QR / ISBN
# =========================================================

@app.route("/return_book_qr", methods=["POST"])
def return_book_qr():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    isbn = request.form["isbn"]

    conn = get_db()

    book = conn.execute("""
        SELECT id
        FROM books
        WHERE isbn = ?
    """, (isbn,)).fetchone()

    if not book:

        conn.close()

        return redirect("/admin")

    transaction = conn.execute("""
        SELECT id
        FROM transactions
        WHERE book_id = ?
        AND status = 'Issued'
        ORDER BY id DESC
        LIMIT 1
    """, (book["id"],)).fetchone()

    if transaction:

        conn.execute("""
            UPDATE transactions
            SET return_date = ?,
                status = 'Returned'
            WHERE id = ?
        """, (
            date.today().isoformat(),
            transaction["id"]
        ))

        conn.commit()

    conn.close()

    return redirect("/admin")


# =========================================================
# DOWNLOAD CSV REPORT
# =========================================================

@app.route("/download_report")
def download_report():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    conn = get_db()

    transactions = conn.execute("""
        SELECT
            books.title AS book,
            members.name AS member,
            transactions.issue_date,
            transactions.due_date,
            transactions.return_date,
            transactions.status
        FROM transactions
        JOIN books
            ON books.id = transactions.book_id
        JOIN members
            ON members.id = transactions.member_id
        ORDER BY transactions.id DESC
    """).fetchall()

    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Book",
        "Member",
        "Issue Date",
        "Due Date",
        "Return Date",
        "Status"
    ])

    for transaction in transactions:

        writer.writerow([
            transaction["book"],
            transaction["member"],
            transaction["issue_date"],
            transaction["due_date"],
            transaction["return_date"] or "",
            transaction["status"]
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=library_report.csv"
        }
    )


# =========================================================
# START DATABASE
# =========================================================

init_db()


# =========================================================
# RUN LOCALLY
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)