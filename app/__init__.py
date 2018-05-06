from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sslify import SSLify
import flask_excel as excel
from config import Config
from flask import Flask


app = Flask(__name__)
excel.init_excel(app)
sslify = SSLify(app)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = ''
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
