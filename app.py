from flask import Flask, render_template, request, redirect, session
from datetime import date, timedelta
import sqlite3
import csv
import io
from flask import Response

app = Flask(__name__)
app.secret_key = "libratrack-secret-key"

DATABASE = "library.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/books")
def books():
    conn = get_db()

    books = conn.execute("""
        SELECT books.*,
        CASE
            WHEN EXISTS (
                SELECT 1 FROM transactions
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


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect("/admin")

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect("/login")


@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    conn = get_db()

    total_books = conn.execute(
        "SELECT COUNT(*) FROM books"
    ).fetchone()[0]

    issued_books = conn.execute("""
        SELECT COUNT(*) FROM transactions
        WHERE status = 'Issued'
    """).fetchone()[0]

    returned_books = conn.execute("""
        SELECT COUNT(*) FROM transactions
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
        JOIN books ON books.id = transactions.book_id
        JOIN members ON members.id = transactions.member_id
        ORDER BY transactions.id DESC
    """).fetchall()

    books = conn.execute(
        "SELECT * FROM books ORDER BY title"
    ).fetchall()

    members = conn.execute(
        "SELECT * FROM members ORDER BY name"
    ).fetchall()

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
        members=members
    )

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
            INSERT INTO books (title, author, isbn, category)
            VALUES (?, ?, ?, ?)
        """ , (title, author, isbn, category))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/admin")


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
            INSERT INTO members (name, email, phone)
            VALUES (?, ?, ?)
        """, (name, email, phone))

        conn.commit()

    except sqlite3.IntegrityError:
        pass

    conn.close()

    return redirect("/admin")

@app.route("/issue_book", methods=["POST"])
def issue_book():

    if not session.get("admin_logged_in"):
        return redirect("/login")

    isbn = request.form["isbn"]
    member_id = request.form["member_id"]
    due_date = request.form["due_date"]

    conn = get_db()

    book = conn.execute(
        "SELECT id FROM books WHERE isbn = ?",
        (isbn,)
    ).fetchone()

    if not book:
        conn.close()
        return redirect("/admin")

    existing = conn.execute("""
        SELECT id FROM transactions
        WHERE book_id = ? AND status = 'Issued'
    """, (book["id"],)).fetchone()

    if not existing:

        conn.execute("""
            INSERT INTO transactions
            (book_id, member_id, issue_date, due_date, status)
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

@app.route("/return_book/<int:transaction_id>", methods=["POST"])
def return_book(transaction_id):

    if not session.get("admin_logged_in"):
        return redirect("/login")

    conn = get_db()

    conn.execute("""
        UPDATE transactions
        SET return_date = ?, status = 'Returned'
        WHERE id = ? AND status = 'Issued'
    """, (date.today().isoformat(), transaction_id))

    conn.commit()
    conn.close()

    return redirect("/admin")

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
        JOIN books ON books.id = transactions.book_id
        JOIN members ON members.id = transactions.member_id
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

init_db()


if __name__ == "__main__":
    app.run(debug=True)