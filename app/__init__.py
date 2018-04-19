from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
from flask import Flask


app = Flask(__name__)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = ''
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
