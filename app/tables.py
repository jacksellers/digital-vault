from app.models import User, Trade, Transfer
from app.blockchain import get_from_bitcoind
from operator import itemgetter
from app import db
import time


def format_id(id, tx_type):
    if tx_type in ['Buy', 'Sell']:
        return 'T' + str(id)
    else:
        return 'F' + str(id)


def format_time(timestamp):
    hour_string = timestamp.strftime("%I")
    minute_string = timestamp.strftime("%M")
    am_pm_string = timestamp.strftime("%p")
    return hour_string + ':' + minute_string + ' ' + am_pm_string


def format_date(timestamp):
    day_string = timestamp.strftime("%d")
    month_string = timestamp.strftime("%b")
    year_string = timestamp.strftime("%Y")
    return day_string + '-' + month_string + '-' + year_string


def format_amount(amount, price=None, currency=None):
    if price is not None:
        return str(clean(amount)) + ' BTC @ $' + str(clean(price))
    elif currency == 'BTC':
        return str(clean(amount)) + ' BTC'
    else:
        return '$' + str(clean(amount))


def usd(x):
    return '$' + str(clean(x))


def clean(x):
    x_commas = '{:,}'.format(x)
    x_clean = x_commas.rstrip('0')
    if x_clean[-1] == '.':
        return x_clean[:-1]
    else:
        return x_clean


def grid(user, rows='all'):
    trades = Trade.query.filter_by(user_id=user.id).all()
    transfers = Transfer.query.filter_by(user_id=user.id).all()
    table = []
    for event in trades + transfers:
        if event.tx_type in ['Buy', 'Sell']:
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          format_amount(event.amount, price=event.price), ''])
        elif event.currency == 'BTC':
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          format_amount(event.amount, currency=event.currency),
                          event.tx_id])
        else:
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          format_amount(event.amount, currency=event.currency),
                          ''])
    table = sorted(table, key=itemgetter(1), reverse=True)
    if rows == 'all':
        return table
    else:
        return table[:rows]


def big_grid(user, rows='all'):
    trades = Trade.query.filter_by(user_id=user.id).all()
    transfers = Transfer.query.filter_by(user_id=user.id).all()
    table = []
    for event in trades + transfers:
        if event.tx_type in ['Buy', 'Sell']:
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          clean(event.amount), 'BTC', usd(event.price),
                          usd(event.amount * event.price), ''])
        elif event.currency == 'BTC':
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          clean(event.amount), event.currency, '', '',
                          event.tx_id])
        else:
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          usd(event.amount), event.currency, '',
                          usd(event.amount), ''])
    table = sorted(table, key=itemgetter(1), reverse=True)
    for row in table:
        del row[1]
    table.insert(0, ['ID', 'Date', 'Time', 'Type', 'Amount', 'Currency',
                     'Price', 'USD Total', 'TXID'])
    if rows == 'all':
        return table
    else:
        return table[:rows]


def export(user, rows='all'):
    trades = Trade.query.filter_by(user_id=user.id).all()
    transfers = Transfer.query.filter_by(user_id=user.id).all()
    table = []
    for event in trades + transfers:
        if event.tx_type in ['Buy', 'Sell']:
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          event.amount, 'BTC', event.price,
                          event.amount * event.price, ''])
        elif event.currency == 'BTC':
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          event.amount, event.currency, '', '',
                          event.tx_id])
        else:
            table.append([format_id(event.id, event.tx_type), event.timestamp,
                          format_date(event.timestamp),
                          format_time(event.timestamp), event.tx_type,
                          event.amount, event.currency, '', event.amount,
                          ''])
    table = sorted(table, key=itemgetter(1), reverse=True)
    for row in table:
        del row[1]
    table.insert(0, ['ID', 'Date', 'Time', 'Type', 'Amount', 'Currency',
                     'Price', 'USD Total', 'TX_ID'])
    if rows == 'all':
        return table
    else:
        return table[:rows]


def blocks_table(n):
    table = []
    previous_block_hash = ''
    for m in range(0, n):
        if m == 0:
            block_hash = get_from_bitcoind('getbestblockhash')
        else:
            block_hash = previous_block_hash
        block = get_from_bitcoind('getblock', [block_hash])
        block_hash = block_hash
        block_height = block['height']
        block_time = int(time.time()) - block['time']
        if block_time < 60:
            block_time = '0m ' + str(block_time) + 's'
        elif 60 < block_time < 3600:
            block_minutes = int(block_time / 60)
            block_time = str(block_minutes) + 'm ' + str(int(block_time - (block_minutes * 60))) + 's'
        else:
            block_hours = int(block_time / 3600)
            block_minutes = int(block_time / 60)
            block_time = str(block_hours) + 'h ' + str(int(block_minutes - (block_hours * 60))) + 'm'
        block_txs = len(block['tx'])
        block_size = block['size'] / 1000
        previous_block_hash = block['previousblockhash']
        table.append({'block_hash': block_hash,
                      'block_height': '{:,}'.format(block_height),
                      'block_time': block_time, 'block_txs': block_txs,
                      'block_size': block_size})
    return table
