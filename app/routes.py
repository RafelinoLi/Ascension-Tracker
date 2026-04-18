import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .db import get_db
from .models import User
from flask_login import current_user
import sqlite3

main = Blueprint('main', __name__)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, hashed)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Username already exists")
            return redirect(url_for('main.register'))
        finally:
            conn.close()

        flash("Account created!")
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        user_data = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user_data:
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                password_hash=user_data['password_hash']
            )

            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
                login_user(user)
                return redirect(url_for('main.dashboard'))

        flash("Invalid username or password")

    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@main.route('/add_workout', methods=['GET', 'POST'])
@login_required
def add_workout():
    if request.method == 'POST':
        category = request.form['category']
        exercise = request.form['exercise']
        sets = request.form['sets']
        reps = request.form['reps']

        conn = get_db()
        conn.execute("""
            INSERT INTO workouts (user_id, category, exercise, sets, reps)
            VALUES (?, ?, ?, ?, ?)
        """, (current_user.id, category, exercise, sets, reps))
        conn.commit()
        conn.close()

        flash("Workout added!")
        return redirect(url_for('main.dashboard'))

    return render_template('add_workout.html')

@main.route('/progress')
@login_required
def progress():
    return render_template('progress.html')
