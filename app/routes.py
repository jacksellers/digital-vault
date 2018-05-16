from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, \
                  jsonify, session
from app.forms import LoginForm, RegistrationForm, TradeForm, ExplorerForm
from app.models import User, Balance, Trade, Transfer
from app.tables import clean, grid, big_grid, export
from werkzeug.urls import url_parse
import flask_excel as excel
from app import app, db


@app.errorhandler(404)
def page_not_found(e):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    print('SESSION: ', session)
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
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    print('SESSION: ', session)
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
        flash('You have successfully registered - please log in')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/')
@app.route('/index')
@login_required
def index():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    table = grid(user, 5)
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
            flash('Your {} trade was executed - {} BTC @ ${}'.format(
                  tx_type.lower(), clean(amount), clean(price)))
        else:
            flash('Your {} trade failed - insufficient funds'.format(
                  tx_type.lower()))
        return redirect(url_for('trade'))
    return render_template('trade.html', user=user, balances=balances,
                           form=form)


@app.route('/funding', methods=['GET', 'POST'])
@login_required
def funding():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    return render_template('funding.html', user=user, balances=balances)


@app.route('/get_price')
@login_required
def add_numbers():
    price = request.args.get('price', 0, type=float)
    session['price'] = price
    return jsonify(result=price)


@app.route('/history')
@login_required
def history():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    table = big_grid(user)
    return render_template('history.html', user=user, balances=balances,
                           table=table)


@app.route('/history/xlsx', methods=['GET'])
@login_required
def history_xlsx():
    user = current_user
    table = export(user)
    return excel.make_response_from_array(table, 'xlsx', file_name='history')


@app.route('/explorer', methods=['GET', 'POST'])
def explorer():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    form = ExplorerForm()
    if form.validate_on_submit():
        pass
    return render_template('explorer.html', user=user, balances=balances, 
                           form=form)


@app.route('/api', methods=['GET', 'POST'])
def api():
    return """
        <h1 align='center'>COMING SOON</h1>
        <a align='center' href='{{ url_for('index') }}'><h3>Back</h3></a>
        """
