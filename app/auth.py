from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .user import User


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('main.index'))

    else:
        if request.method == 'GET':
            return render_template('login.html')

        elif request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

            user = User.find(email)
            
            if not user or not check_password_hash(user.password, password):
                flash('Please check your login credentials!')
                return redirect(url_for('auth.login'))

            login_user(user, remember=remember)

            return redirect(url_for('main.profile'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are logged in!')
        return redirect(url_for('main.index'))

    else:
        if request.method == 'GET':
            return render_template('register.html')

        elif request.method == 'POST':
            email = request.form.get('email')
            name = request.form.get('name')
            password = request.form.get('password')

            user = User.find(email)

            if user:
                flash('Email address already registered!')
                return redirect(url_for('auth.register'))

            data = (
                None, 
                name,
                generate_password_hash(password, method='sha256'),
                email
            )

            User(*data).create()

            return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
