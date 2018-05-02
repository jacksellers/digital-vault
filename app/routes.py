from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, \
                  jsonify, session
from app.forms import LoginForm, RegistrationForm, TradeForm
from app.models import User, Balance, Trade, Transfer
from app.tables import Table
from werkzeug.urls import url_parse
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
        db.session.add(user)
        db.session.commit()
        transfer = Transfer(tx_type="Deposit", amount=500000, currency="USD",
                            user_id=user.id)
        balances = Balance(balance_btc=0, balance_usd=500000, user_id=user.id)
        db.session.add_all([transfer, balances])
        db.session.commit()
        message = 'You have successfully registered - please log in'
        return redirect(url_for('login'))
    else:
        message = ''
    return render_template('register.html', title='Register', form=form,
                           message=message)


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    table = Table(user, 6)
    return render_template('index.html', user=user, balances=balances,
                           table=table)


@app.route('/trade', methods=['GET', 'POST'])
@login_required
def trade():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    form = TradeForm()
    if form.validate_on_submit():
        tx_type = form.option.data
        amount = form.btc_amount.data
        price = session['price']
        total = price * amount
        session.pop('price', None)
        if (tx_type == 'Buy' and balances.balance_usd >= total) or \
           (tx_type == 'Sell' and balances.balance_btc >= amount):
            if tx_type == 'Buy':
                new_balance_btc = balances.balance_btc + amount
                new_balance_usd = balances.balance_usd - total
            else:
                new_balance_btc = balances.balance_btc - amount
                new_balance_usd = balances.balance_usd + total
            db.session.delete(balances)
            db.session.commit()
            trade = Trade(tx_type=tx_type, amount=amount, price=price,
                          total=total, user_id=user.id)
            new_balances = Balance(balance_btc=new_balance_btc, 
                                   balance_usd=new_balance_usd, 
                                   user_id=user.id)
            db.session.add_all([trade, new_balances])
            db.session.commit()
            balances = Balance.query.filter_by(user_id=user.id).first()
            message = 'Your trade was successful'  # ADD ALL TRADE DETAILS !
        else:
            message = 'Your trade was unsuccessful - insufficient funds'
    else:
        message = ''
    return render_template('trade.html', user=user, balances=balances,
                           form=form, message=message)


@app.route('/get_price')
@login_required
def add_numbers():
    price = request.args.get('price', 0, type=float)
    session['price'] = price
    return jsonify(result=price)


@app.route('/history')
def history():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    table = Table(user)
    return render_template('history.html', user=user, balances=balances,
                           table=table)
