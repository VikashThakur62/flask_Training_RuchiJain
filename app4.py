"""
Library Management System - Flask

Folder structure:
  app4.py
  templates/  (home, signup, login, dashboard, issue_book, success, view_books .html)

Run:
  pip install flask
  python app4.py
Then open http://127.0.0.1:5001
"""

import os
import sqlite3
from functools import wraps

from flask import (Flask, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")


# ---------------------------- Database helpers ----------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS book_issues (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id      TEXT NOT NULL,
            book_name    TEXT NOT NULL,
            book_number  TEXT NOT NULL,
            student_name TEXT NOT NULL,
            issue_date   TEXT NOT NULL,
            due_date     TEXT NOT NULL,
            issued_by    INTEGER,
            FOREIGN KEY (issued_by) REFERENCES users (id)
        );
        """
    )
    db.commit()
    db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# --------------------------------- Routes ---------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not name or not username or not password:
            flash("All fields are required.", "error")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO users (name, username, password) VALUES (?, ?, ?)",
                    (name, username, generate_password_hash(password)),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash("That username is already taken.", "error")
            else:
                flash("Account created. Please log in.", "success")
                return redirect(url_for("login"))
    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/issue_book", methods=["GET", "POST"])
@login_required
def issue_book():
    if request.method == "POST":
        f = request.form
        data = [f.get(k, "").strip() for k in
                ("book_id", "book_name", "book_number",
                 "student_name", "issue_date", "due_date")]

        if not all(data):
            flash("Please fill in every field.", "error")
        elif data[5] < data[4]:
            flash("Due date cannot be before the issue date.", "error")
        else:
            db = get_db()
            cur = db.execute(
                """INSERT INTO book_issues
                   (book_id, book_name, book_number, student_name,
                    issue_date, due_date, issued_by)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (*data, session["user_id"]),
            )
            db.commit()
            return redirect(url_for("success", issue_id=cur.lastrowid))
    return render_template("issue_book.html")


@app.route("/success/<int:issue_id>")
@login_required
def success(issue_id):
    issue = get_db().execute(
        "SELECT * FROM book_issues WHERE id = ?", (issue_id,)
    ).fetchone()
    if issue is None:
        flash("Issue record not found.", "error")
        return redirect(url_for("dashboard"))
    return render_template("success.html", issue=issue)


@app.route("/view_books")
@login_required
def view_books():
    books = get_db().execute(
        "SELECT * FROM book_issues ORDER BY id"
    ).fetchall()
    return render_template("view_books.html", books=books)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


# --------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)