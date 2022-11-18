from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from config import Config

# application instance
app = Flask(__name__)
# loading application configurations
app.config.from_object(Config)
# create database instance
db = SQLAlchemy(app)
# set up application for migration
migrate = Migrate(app, db)
# configure application for enabling smart login state
login = LoginManager(app)
# register the login endpoint
login.login_view = 'login'


from app import routes, models
