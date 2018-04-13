from flask import render_template, flash, redirect
from app import app
from app.forms import LoginForm


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/signup')
def signup():
    form = LoginForm()
    return render_template('signup.html', title='Sign In', form=form)


@app.route('/trade')
def trade():
    return render_template('trade.html')
