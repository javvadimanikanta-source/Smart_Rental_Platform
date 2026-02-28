from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ------------------- DATABASE INIT -------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    # Rentals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            price INTEGER NOT NULL,
            owner TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized successfully")

init_db()

# ------------------- ROUTES -------------------

# HOME PAGE
@app.route("/")
def home():
    rentals = []
    if "user" in session:
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM rentals")
        rentals = cursor.fetchall()
        conn.close()
    return render_template("home.html", rentals=rentals)

# ABOUT
@app.route("/about")
def about():
    return render_template("about.html")

# CONTACT
@app.route("/contact")
def contact():
    return render_template("contact.html")

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            flash("Registration successful! Login now.")
            return redirect("/login")
        except:
            flash("Email already exists!")
            return redirect("/register")
    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[0], password):
            session["user"] = email
            return redirect("/dashboard")
        else:
            flash("Invalid Email or Password! Try again.")
            return redirect("/login")
    return render_template("login.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.")
    return redirect("/login")

# DASHBOARD
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rentals WHERE owner=?", (session["user"],))
    rentals = cursor.fetchall()
    conn.close()

    return render_template("dashboard.html", rentals=rentals, user=session["user"])

# ADD RENTAL
@app.route("/add_rental", methods=["GET", "POST"])
def add_rental():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        owner = session["user"]

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO rentals (title, description, price, owner) VALUES (?, ?, ?, ?)",
            (title, description, price, owner)
        )
        conn.commit()
        conn.close()
        flash("Property added successfully!")
        return redirect("/dashboard")

    return render_template("add_rental.html")

# ------------------- RUN APP -------------------
if __name__ == "__main__":
    app.run(debug=True)