"""
Student Feedback System
A simple Flask + SQLite project for college.

Run with:  python app.py
"""

import os
import sqlite3
from functools import wraps

from flask import (Flask, render_template, request, redirect,
                   url_for, session, flash, g)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret key is needed to keep the admin session safe.
# Change this text before using the project anywhere other than your own PC.
app.secret_key = "change-this-secret-key-before-real-use"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# The database file is created next to app.py
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

# Sample admin login for local testing.
# The password is stored as a hash, never as plain text.
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

BRANCHES = ["CSE", "IT", "ECE", "EEE", "Mechanical", "Civil", "BCA", "MCA", "Other"]
SEMESTERS = [1, 2, 3, 4, 5, 6, 7, 8]


# ---------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------
def get_db():
    """Open one database connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us use row["column_name"]
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the database file and the feedback table if they do not exist."""
    connection = sqlite3.connect(DATABASE)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            branch TEXT NOT NULL,
            semester INTEGER NOT NULL,
            teacher_name TEXT NOT NULL,
            subject_name TEXT NOT NULL,
            teaching_quality INTEGER NOT NULL,
            communication INTEGER NOT NULL,
            doubt_clearing INTEGER NOT NULL,
            overall INTEGER NOT NULL,
            comments TEXT,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    connection.commit()
    connection.close()


# ---------------------------------------------------------------
# Login protection for admin pages
# ---------------------------------------------------------------
def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Please log in as admin first.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped_view


# ---------------------------------------------------------------
# Student pages
# ---------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "GET":
        return render_template("feedback.html", form={},
                               branches=BRANCHES, semesters=SEMESTERS)

    # ----- Read the form values -----
    student_name = request.form.get("student_name", "").strip()
    roll_number = request.form.get("roll_number", "").strip()
    branch = request.form.get("branch", "").strip()
    semester = request.form.get("semester", "").strip()
    teacher_name = request.form.get("teacher_name", "").strip()
    subject_name = request.form.get("subject_name", "").strip()
    comments = request.form.get("comments", "").strip()

    ratings = {}
    for field in ["teaching_quality", "communication", "doubt_clearing", "overall"]:
        ratings[field] = request.form.get(field, "").strip()

    # ----- Basic validation -----
    errors = []

    if not student_name:
        errors.append("Student name is required.")
    elif len(student_name) > 100:
        errors.append("Student name is too long (maximum 100 characters).")

    if not roll_number:
        errors.append("Roll number is required.")
    elif len(roll_number) > 30:
        errors.append("Roll number is too long (maximum 30 characters).")

    if branch not in BRANCHES:
        errors.append("Please choose a valid course / branch.")

    if not semester.isdigit() or int(semester) not in SEMESTERS:
        errors.append("Please choose a valid semester.")

    if not teacher_name:
        errors.append("Teacher name is required.")
    elif len(teacher_name) > 100:
        errors.append("Teacher name is too long (maximum 100 characters).")

    if not subject_name:
        errors.append("Subject name is required.")
    elif len(subject_name) > 100:
        errors.append("Subject name is too long (maximum 100 characters).")

    for field, value in ratings.items():
        if not value.isdigit() or not (1 <= int(value) <= 5):
            label = field.replace("_", " ").title()
            errors.append("Please give a rating from 1 to 5 for " + label + ".")

    if len(comments) > 500:
        errors.append("Comments are too long (maximum 500 characters).")

    # If something is wrong, show the form again with the typed values
    if errors:
        for message in errors:
            flash(message, "error")
        return render_template("feedback.html", form=request.form,
                               branches=BRANCHES, semesters=SEMESTERS)

    # ----- Save to the database (parameterized query) -----
    db = get_db()
    db.execute(
        """
        INSERT INTO feedback
            (student_name, roll_number, branch, semester, teacher_name,
             subject_name, teaching_quality, communication, doubt_clearing,
             overall, comments)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (student_name, roll_number, branch, int(semester), teacher_name,
         subject_name, int(ratings["teaching_quality"]),
         int(ratings["communication"]), int(ratings["doubt_clearing"]),
         int(ratings["overall"]), comments),
    )
    db.commit()

    return redirect(url_for("success"))


@app.route("/success")
def success():
    return render_template("success.html")


# ---------------------------------------------------------------
# Admin pages
# ---------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session.clear()
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))

        flash("Wrong username or password. Please try again.", "error")

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()

    rows = db.execute(
        """
        SELECT *,
               (teaching_quality + communication + doubt_clearing + overall) / 4.0
               AS average
        FROM feedback
        ORDER BY id DESC
        """
    ).fetchall()

    stats = db.execute(
        """
        SELECT COUNT(*) AS total,
               AVG(teaching_quality) AS teaching,
               AVG(communication) AS communication,
               AVG(doubt_clearing) AS doubt,
               AVG(overall) AS overall,
               AVG((teaching_quality + communication + doubt_clearing + overall) / 4.0)
               AS average
        FROM feedback
        """
    ).fetchone()

    return render_template("admin_dashboard.html", rows=rows, stats=stats)


@app.route("/admin/delete/<int:feedback_id>", methods=["POST"])
@admin_required
def delete_feedback(feedback_id):
    db = get_db()
    db.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
    db.commit()
    flash("Feedback deleted.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout", methods=["POST", "GET"])
def admin_logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("admin_login"))


# ---------------------------------------------------------------
# Start the app
# ---------------------------------------------------------------
init_db()  # creates database.db automatically

if __name__ == "__main__":
    app.run(debug=True)
