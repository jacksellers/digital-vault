from (digital-vault).app.models import User, Balance, Trade, Transfer
from app import db

users = User.query.all()
for u in users:
	db.session.delete(u)

balances = Balance.query.all()
for b in balances:
	db.session.delete(b)

trades = Trade.query.all()
for t in trades:
	db.session.delete(t)

transfers = Transfer.query.all()
for t in transfers:
	db.session.delete(t)

db.session.commit()
users = User.query.all()
balances = Balance.query.all()
trades = Trade.query.all()
transfers = Transfer.query.all()
success = True
for model in [users, balances, trades, transfers]:
	if model != []:
		success = False
if success:
	print('SUCCESSFULLY NUKED THE DATABASE :)')
else:
	print('Error :(')
