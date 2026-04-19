import sqlite3
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .db import get_db
from .models import User


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

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')

@main.route('/login', methods=['GET', 'POST'])
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
    conn = get_db()
    user = conn.execute(
    "SELECT xp, level FROM users WHERE id = ?",
    (current_user.id,)
    ).fetchone()

    return render_template('dashboard.html', user=user)

@main.route('/add_workout', methods=['GET', 'POST'])
@login_required
def add_workout():
    EXERCISE_MULTIPLIER = {
        "Bench Press": 1.2,
        "Incline press": 1.2,
        "Chest Fly": 1.6,
        "Squat": 1,
        "Leg Press": 1,
        "Leg Extension": 1,
        "Hamstring Curl": 1,
        "Bicep Curl": 1.5,
        "Tricep Pushdown": 1.5,
        "Skull Crushers": 1.5,
        "Dips": 1.4,
        "Shoulder Press": 1.6,
        "Lateral Raise": 1.7,
        "Rear Delt Fly": 1.7,
        "Deadlift": 0.8,
        "Lat Pulldown": 1.0,
        "Rows": 1.0,
    }

    def xp_to_next_level(level):
        return 100 * (level ** 1.5)

    if request.method == 'POST':
        category = request.form['category']
        exercise = request.form['exercise']
        sets = int(request.form['sets'])
        reps = int(request.form['reps'])
        weight = float(request.form['weight'])

        multiplier = EXERCISE_MULTIPLIER.get(exercise, 1.0)
        xp_gained = int(sets * reps * weight * multiplier * 0.1)

        conn = get_db()

        conn.execute("""
            INSERT INTO workouts (user_id, category, exercise, sets, reps, weight)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (current_user.id, category, exercise, sets, reps, weight))

        user = conn.execute(
            "SELECT xp, level FROM users WHERE id = ?",
            (current_user.id,)
        ).fetchone()

        new_xp = user['xp'] + xp_gained
        level = user['level']

        while new_xp >= xp_to_next_level(level):
            new_xp -= xp_to_next_level(level)
            level += 1

        conn.execute("""
            UPDATE users
            SET xp = ?, level = ?
            WHERE id = ?
        """, (new_xp, level, current_user.id))

        conn.commit()
        conn.close()

        flash(f"+{xp_gained} XP gained!")
        return redirect(url_for('main.add_workout'))

    return render_template('add_workout.html')

@main.route('/history')
@login_required
def history():
    conn = get_db()
    workouts = conn.execute("""
        SELECT * FROM workouts
        WHERE user_id = ?
        ORDER BY date DESC
    """, (current_user.id,)).fetchall()
    conn.close()

    return render_template('history.html', workouts=workouts)

@main.route('/progress')
@login_required
def progress():
    return render_template('progress.html')
