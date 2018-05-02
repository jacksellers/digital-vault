from app.models import User, Trade, Transfer
from operator import itemgetter
from app import db


def format_id(id, tx_type):
    if tx_type in ['Buy', 'Sell']:
        return 'T' + str(id)
    else:
        return 'F' + str(id)


def format_time(timestamp):
    hour_string = timestamp.strftime("%-I")
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


def clean(x):
    x_commas = '{:,}'.format(x)
    x_clean = x_commas.rstrip('0')
    if x_clean[-1] == '.':
        return x_clean[:-1]
    else:
        return x_clean


def Table(user, rows='all'):
    trades = Trade.query.filter_by(user_id=user.id).all()
    transfers = Transfer.query.filter_by(user_id=user.id).all()
    table = []
    for event in trades + transfers:
        if event.tx_type in ['Buy', 'Sell']:
            table.append([format_id(event.id, event.tx_type), event.timestamp, format_date(event.timestamp), format_time(event.timestamp), event.tx_type, format_amount(event.amount, price=event.price), ''])
        elif event.currency == 'BTC':
            table.append([format_id(event.id, event.tx_type), event.timestamp, format_date(event.timestamp), format_time(event.timestamp), event.tx_type, format_amount(event.amount, currency=event.currency), event.tx_id])
        else:
            table.append([format_id(event.id, event.tx_type), event.timestamp, format_date(event.timestamp), format_time(event.timestamp), event.tx_type, format_amount(event.amount, currency=event.currency), ''])
    table = sorted(table, key=itemgetter(1), reverse=True)
    if rows == 'all':
        return table
    else:
        return table[:rows]
