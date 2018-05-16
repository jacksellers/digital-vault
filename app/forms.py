from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
                    FloatField, RadioField
from app.blockchain import get_from_electrum
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm
from app.models import User
import bitcoin


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    login = SubmitField('Login')


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    register = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('That username is taken')


class TradeForm(FlaskForm):
    option = RadioField('Trade Option', validators=[DataRequired()],
                        choices=[('Buy', 'Buy'), ('Sell', 'Sell')])
    btc_amount = FloatField('Amount (BTC)', validators=[DataRequired()])
    price = FloatField('Price')
    total = FloatField('Total')
    trade = SubmitField('Trade')


class ExplorerForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])

    def validate_search(self, search):
        search = search.data
        valid = False
        if is_address(search):
            valid = True
        elif search is int:
            valid = True
        
        """  THIS LOGIC CAN GO SOMEWHERE ELSE ONCE FORMAT HAS BEEN DETERMINED
        msT1xh5vQ6ZsT3XhdNXFJ4XvEzmvwVfNMS
        address_balance = \
            get_from_electrum('blockchain.address.get_balance', search)
        print(address_balance)
        print(type(address_balance))
        print(address_balance['error'])
        """
        if not valid:  # Replace this with a condition
            raise ValidationError('Invalid input')
