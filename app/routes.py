from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm
from app.models import User, Balance
from app import app, db


@app.errorhandler(404)
def page_not_found(e):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data, username=form.username.data)
        user.set_password(form.password.data)
        balance = Balance(balance_btc=0, balance_usd=500000, client=user)
        db.session.add(user)
        db.session.add(balance)
        db.session.commit()
        flash('You have successfully registered - please log in')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    balances = Balance.query.get(user.id)
    return render_template('index.html', user=user, balances=balances)


@app.route('/trade')
@login_required
def trade():
    return render_template('trade.html')
