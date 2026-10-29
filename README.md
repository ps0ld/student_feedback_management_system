# Student Feedback System

A simple college project built with **HTML, CSS, basic JavaScript, Python (Flask) and SQLite**.
Students submit feedback about teachers. The admin logs in to see all feedback and the average ratings.

## Features

- Home page with **Student Login** and **Admin Login** buttons
- Student feedback form with 1-5 ratings and form validation
- Success message after submitting
- Admin login, dashboard, delete feedback, and logout
- Average rating (overall, per question, and per feedback)
- SQLite database created automatically (`database.db`)
- Blue and white responsive design (mobile and desktop)
- A small GSAP fade-in on page load (optional, loaded from a CDN)

## Folder Structure

```
student_feedback_system/
├── app.py
├── database.db            (created automatically when you run app.py)
├── requirements.txt
├── README.md
├── templates/
│   ├── index.html
│   ├── feedback.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   └── success.html
└── static/
    └── style.css
```

## Sample Admin Login (for local testing)

| Username | Password   |
|----------|------------|
| admin    | admin123   |

## How to Run on Windows with VS Code

1. **Install Python** from https://www.python.org/downloads/ . During installation, tick **"Add Python to PATH"**.
2. **Install VS Code** from https://code.visualstudio.com/ and install the **Python** extension.
3. Open VS Code, then choose **File > Open Folder** and select the `student_feedback_system` folder.
4. Open the terminal: **Terminal > New Terminal**.
5. Create a virtual environment:
   ```
   python -m venv venv
   ```
6. Activate it:
   ```
   venv\Scripts\activate
   ```
   If PowerShell blocks this, run
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
   and try again. (Or use Command Prompt instead.)
7. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
8. Start the server:
   ```
   python app.py
   ```
9. Open your browser and go to **http://127.0.0.1:5000**

Press `Ctrl + C` in the terminal to stop the server.

## How to Demonstrate to Your Teacher

1. Open the home page and show the two buttons.
2. Click **Student Login**, then press **Submit Feedback** with an empty form to show validation.
3. Fill in the form properly and submit. Show the success page.
4. Go back to the home page and click **Admin Login**.
5. Try a wrong password to show the error, then log in with `admin` / `admin123`.
6. Show the dashboard: total feedback, average ratings, and the full table.
7. Click **Delete** on one row to show that data can be removed.
8. Click **Logout**, then try opening `http://127.0.0.1:5000/admin/dashboard`. You will be sent back to the login page, which proves the dashboard is protected.
9. Open the site on a phone-sized browser window to show it is responsive.

## How It Works (short explanation)

- `app.py` has all Flask routes (`/`, `/feedback`, `/success`, `/admin/login`, `/admin/dashboard`, `/admin/logout`).
- `init_db()` creates `database.db` and the `feedback` table automatically.
- Every SQL query uses `?` placeholders (parameterized queries) to prevent SQL injection.
- The admin password is stored as a hash using Werkzeug, and the login is kept in a Flask session.
- The `admin_required` decorator blocks the dashboard for anyone who is not logged in.
- Jinja2 automatically escapes text in templates, so comments cannot inject HTML.

## Notes

- Before using this anywhere other than your own computer, change `app.secret_key` and the admin password in `app.py`, and turn off `debug=True`.
- To remove all saved feedback, stop the server and delete `database.db`. It will be created again on the next run.
- The GSAP animation needs internet. Without it, the site works exactly the same, just without the fade-in.
