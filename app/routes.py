import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from .db import get_db
from .models import User

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
