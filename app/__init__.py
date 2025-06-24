from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # ✅ Add this

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/app.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)  # ✅ Add this

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models  # ✅ Should be after db + migrate

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
