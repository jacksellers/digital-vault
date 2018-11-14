from flask_login import current_user, login_user, logout_user, login_required
from flask import render_template, flash, redirect, url_for, request, \
                  jsonify, session
from app.forms import LoginForm, RegistrationForm, TradeForm, ExplorerForm
from app.blockchain import get_from_bitcoind, search_blockchain, get_raw_mempool
from app.models import User, Balance, Trade, Transfer
from app.tables import clean, grid, big_grid, export, blocks_table
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
        address = get_from_bitcoind('getnewaddress', [])
        dumpPri = get_from_bitcoind('dumpprivkey', [address])
        impoPri = get_from_bitcoind('importprivkey', [dumpPri])

        user = User(first_name=form.first_name.data,
                    last_name=form.last_name.data, username=form.username.data, address=address)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        transfer = Transfer(tx_type='Deposit', amount=500000, currency='USD',
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
        try:
            price = session['price']
            total = price * amount
            # session.pop('price', None)
        except KeyError:
            price = 'N/A'
            total = 'N/A'
        print("Amount: ", amount)
        print("Price: ", price)
        print("Total: ", total)
        if all(isinstance(i, float) for i in [amount, price, total]):
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
        else:
            return redirect(url_for('trade'))
    return render_template('trade.html', user=user, balances=balances,
                           form=form)


@app.route('/get_price')
@login_required
def get_price():
    price = request.args.get('price', 0, type=float)
    session['price'] = price
    return jsonify(result=price)


@app.route('/funding', methods=['GET', 'POST'])
@login_required
def funding():
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    form = TradeForm()
    return render_template('funding.html', user=user, balances=balances, form=form)


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
@app.route('/explorer/<category>', methods=['GET', 'POST'])
@app.route('/explorer/<category>/<search_id>', methods=['GET', 'POST'])
def explorer(category=None, search_id=None):
    user = current_user
    balances = Balance.query.filter_by(user_id=user.id).first()
    form = ExplorerForm()
    if form.validate_on_submit():
        category, search_id, data = search_blockchain(form.search.data)
        session['data'] = data
        if category is not None and search_id is None:
            return redirect('/explorer/{}'.format(category))
        if category is not None and search_id is not None:
            return redirect('/explorer/{}/{}'.format(category, search_id))
    else:
        category, search_id, data = search_blockchain(search_id)
        session['data'] = data
    return render_template('explorer.html', user=user, balances=balances,
                           form=form, category=category, search_id=search_id)


@app.route('/get_blocks')
@login_required
def get_blocks():
    latest_blocks = blocks_table(6)
    return jsonify(result=latest_blocks)


@app.route('/get_mempool')
@login_required
def get_mempool():
    if 'txs' not in session:
        txs = []
        session['txs'] = txs
    else:
        txs = session['txs']
    if 'previous_mempool' not in session:
        previous_mempool = get_from_bitcoind('getrawmempool')
        session['previous_mempool'] = previous_mempool
    else:
        previous_mempool = session['previous_mempool']
    mempool = get_from_bitcoind('getrawmempool')
    if len(mempool) > len(previous_mempool):
        for tx in mempool:
            if tx not in previous_mempool:
                txs.insert(0, tx)
                txs = txs[0:6]
    previous_mempool = mempool
    session['txs'] = txs
    session['previous_mempool'] = previous_mempool
    return jsonify(result=txs)


@app.route('/get_data')
@login_required
def get_data():
    data = session['data']
    return jsonify(result=data)


@app.route('/api', methods=['GET', 'POST'])
def api():
    return """
        <h1 align='center'>COMING SOON</h1>
        <a align='center' href='{{ url_for('index') }}'><h3>Back</h3></a>
        """

@app.route('/get_address')
@login_required
def get_address():    
    user = current_user
    print("user............",user.username)
    users = User.query.filter(User.username==user.username).first()
    return jsonify(result=users.address)


@app.route('/get_deposit')
@login_required
def get_deposit():
    user = current_user
    address = get_address()
    unspentlist = get_from_bitcoind('listunspent',[6,9999999,[address]])
    print("unspentlist....................",unspentlist)
    return unspentlist