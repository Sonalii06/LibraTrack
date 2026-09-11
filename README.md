# 📚 LibraTrack — Library Management System

**LibraTrack** is a full-stack Library Management System designed to simplify book, member, and transaction management through a clean and responsive web interface.

The system supports **book issue/return management, QR-based scanning, member management, real-time dashboard statistics, transaction tracking, and downloadable reports**.

---

## 🌐 Live Demo

**Live URL: https://libra-track-8kfj3qmo6-sonali-b5af.vercel.app/**

---

## ✨ Features

### 📊 Admin Dashboard

* Real-time library statistics
* Total books
* Available books
* Currently issued books
* Returned books
* Total members
* Recent transaction tracking

### 📚 Book Management

* Add new books
* Store book title, author, ISBN, and category
* View all books
* Track book availability
* Generate QR codes for books
* Prevent duplicate ISBN entries

### 👥 Member Management

* Add new members
* Edit member information
* Delete members
* Store name, email, and phone number
* Prevent deletion of members with existing transaction records

### 📖 Book Issue

Books can be issued using two methods:

**Manual Issue**

* Enter/select the book ISBN
* Select a member
* Select the due date
* Issue the book

**QR Issue**

* Scan the book's QR code
* Select the member
* Select the due date
* Confirm the issue

### 🔄 Book Return

Books can be returned using:

* Manual transaction-based return
* QR code scanning

The QR return process automatically identifies the active transaction associated with the scanned book.

### 📱 QR Code Support

* QR codes can be generated for books
* QR scanner is available for issuing books
* QR scanner is available for returning books
* Uses browser-based camera scanning

### 📑 Transaction Management

* Track issued and returned books
* View transaction history
* Filter transactions by status
* Record issue date, due date, and return date
* Return books directly from transaction records

### 📥 Reports

* Download library transaction data as a CSV report

### 🎨 Responsive UI

* Responsive layout for different screen sizes
* Pink-themed LibraTrack interface
* Rounded cards and buttons
* Clean dashboard layout
* Mobile-friendly sections

---

## 🔐 Admin Login

Administrative features are protected using a simple **session-based admin login**.

### Admin Credentials

| Field    | Value             |
| -------- | ----------------- |
| Username | `admin`           |
| Password | `LibraTrack@2026` |

> **Note:** These are demo credentials for the student project. For a production application, credentials should be stored securely using password hashing and environment variables.

### How to Access the Admin Dashboard

1. Open the LibraTrack application.
2. Go to the **Login** page.
3. Enter the admin credentials.
4. Click **Login**.
5. You will be redirected to the Admin Dashboard.

The admin dashboard is available at:

```text
/admin
```

Users who are not logged in are redirected to the login page when attempting to access protected admin functionality.

### Admin Features to Test

* Add books
* Generate book QR codes
* Add members
* Edit members
* Delete members
* Manually issue books
* Issue books using QR scanning
* Manually return books
* Return books using QR scanning
* View real-time statistics
* Filter transactions
* Download CSV reports
* Logout

---

## 🛠️ Tech Stack

| Technology   | Purpose                                       |
| ------------ | --------------------------------------------- |
| HTML5        | Page structure                                |
| CSS3         | Styling and responsive UI                     |
| JavaScript   | Client-side interactions and QR functionality |
| Python       | Backend programming                           |
| Flask        | Web framework                                 |
| SQLite       | Database                                      |
| Jinja2       | Dynamic HTML rendering                        |
| Git & GitHub | Version control                               |
| Gunicorn     | Production WSGI server                        |
| Vercel       | Deployment                                    |

### External Libraries

**QRCode.js**

* Used to generate QR codes for books.

**html5-qrcode**

* Used for browser-based QR code scanning through the device camera.

---

## 🏗️ Project Architecture

```text
User
  │
  ▼
HTML / CSS / JavaScript
  │
  ▼
Flask Backend
  │
  ├── Authentication
  ├── Book Management
  ├── Member Management
  ├── Issue / Return
  ├── QR Processing
  └── Reports
  │
  ▼
SQLite Database
```

---

## 📁 Project Structure

```text
library-management-system/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── admin.html
│   └── books.html
│
├── app.py
├── library.db
├── requirements.txt
├── README.md
└── vercel.json
```

> File names may change slightly as the project is updated.

---

## 🗄️ Database Design

LibraTrack uses **SQLite** as its database.

The main tables are:

### Books

Stores information about library books.

```text
books
├── id
├── title
├── author
├── isbn
└── category
```

### Members

Stores registered library members.

```text
members
├── id
├── name
├── email
└── phone
```

### Transactions

Stores book issue and return information.

```text
transactions
├── id
├── book_id
├── member_id
├── issue_date
├── due_date
├── return_date
└── status
```

The `book_id` and `member_id` fields connect transactions with their respective books and members.

---

## 🔄 Book Issue Flow

### Manual Issue

```text
Select Book
     ↓
Select Member
     ↓
Select Due Date
     ↓
Issue Book
     ↓
Transaction Created
     ↓
Book Status → Issued
```

### QR Issue

```text
Scan Book QR
     ↓
Identify ISBN
     ↓
Select Member
     ↓
Select Due Date
     ↓
Confirm Issue
     ↓
Book Status → Issued
```

---

## 🔄 Book Return Flow

### Manual Return

```text
Select Active Transaction
        ↓
Click Return
        ↓
Return Date Recorded
        ↓
Transaction Status → Returned
        ↓
Book Status → Available
```

### QR Return

```text
Scan Book QR
     ↓
Find Active Transaction
     ↓
Automatically Process Return
     ↓
Transaction Status → Returned
     ↓
Book Status → Available
```

---

## 📊 Dashboard Statistics

The dashboard statistics are calculated directly from the SQLite database rather than being hardcoded.

For example:

```text
Total Books
Available Books
Issued Books
Returned Books
Total Members
```

This means the dashboard automatically updates when books are added, issued, or returned.

---

## ⚙️ Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Sonalii06/library-management-system.git
```

Move into the project directory:

```bash
cd library-management-system
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The main dependencies include:

```text
Flask
gunicorn
```

### 4. Run the Application

```bash
python app.py
```

The application will normally run at:

```text
http://127.0.0.1:5000/
```

### 5. Open the Application

For the public home page:

```text
http://127.0.0.1:5000/
```

For login:

```text
http://127.0.0.1:5000/login
```

After logging in, access:

```text
http://127.0.0.1:5000/admin
```

---

## 🧪 Testing

The following functionality can be tested after logging in as admin:

### Books

* Add a book
* Check book details
* Generate its QR code
* Verify availability status

### Members

* Add a member
* Edit member details
* Delete a member without transaction history
* Verify deletion protection for members with transaction records

### Issue

* Issue a book manually
* Issue a book using QR scanning
* Verify that the dashboard statistics update

### Return

* Return a book manually
* Return a book using QR scanning
* Verify that the book becomes available again

### Transactions

* View transactions
* Filter issued/returned transactions
* Download the CSV report

### Authentication

* Try accessing `/admin` without logging in
* Verify redirection to `/login`
* Log in using the admin credentials
* Test logout

---

## 📸 Screenshots

### 🏠 Home Page
<img width="947" height="476" alt="image" src="https://github.com/user-attachments/assets/3ba4a88e-0b56-4c28-a680-84ab8bbc32e3" />

### 🔐 Admin Login

### 📊 Admin Dashboard

### 📚 Books

### 👥 Members

### 📱 QR Book Issue

### 📑 Transactions

> You can replace or add screenshots as the project UI evolves.

---

## 🚀 Deployment

LibraTrack can be deployed using **Vercel** with Flask and Gunicorn.

### 1. Push the Project to GitHub

```bash
git add .
git commit -m "Update LibraTrack"
git push
```

### 2. Import the Repository into Vercel

1. Open Vercel.
2. Sign in using your GitHub account.
3. Select **Add New Project**.
4. Import:

```text
Sonalii06/library-management-system
```

5. Configure the project according to the Flask/Vercel deployment setup.
6. Deploy the application.

### 3. Verify Deployment

After deployment, test:

```text
/
```

```text
/login
```

```text
/admin
```

Make sure the admin login, database operations, QR scanning, issue/return functionality, and reports work correctly on the deployed version.

---

## 🔒 Security Note

This project is designed as a **student-level academic/project implementation**.

The current admin authentication uses demo credentials and a simple Flask session.

For a production application, the following improvements would be recommended:

* Password hashing
* Environment variables for secrets
* Secure session configuration
* Proper user/account management
* CSRF protection
* Production-grade database hosting
* Role-based access control

---

## 🌱 Future Improvements

Possible future improvements include:

* Multiple admin/user roles
* Student login
* Email reminders for due dates
* Automatic overdue notifications
* Advanced analytics
* Search and sorting improvements
* Cloud database integration
* Password hashing and secure authentication
* Fine calculation for overdue books
* Better mobile optimization
* Deployment with a production database

---

## 💡 What I Learned

While developing LibraTrack, I worked with:

* Flask backend development
* HTML/CSS/JavaScript frontend development
* Jinja2 templates
* SQLite database management
* CRUD operations
* Database relationships
* Session-based authentication
* QR code generation
* QR code scanning
* Form handling in Flask
* Git and GitHub
* CSV report generation
* Responsive web design
* Web application deployment

The project also helped me understand how a frontend, backend, and database communicate together in a full-stack application.

---

## 👩‍💻 Author

**Sonali Panigrahi**

B.Tech CSE — Data Science
SRM Institute of Science and Technology

GitHub: [Sonalii06](https://github.com/Sonalii06)

---

## ⭐ Project

If you find this project useful, consider giving the repository a ⭐ on GitHub.

**LibraTrack — Making Library Management Simple, Fast & Organized.**
