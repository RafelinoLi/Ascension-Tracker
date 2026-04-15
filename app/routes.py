from flask import Blueprint, render_template, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def login():
    return render_template('login.html')

@main.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@main.route('/add_workout')
def add_workout():
    return render_template('add_workout.html')

@main.route('/progress')
def progress():
    return render_template('progress.html')
