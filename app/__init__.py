from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.models import User  # ✅ Add this

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

@login_manager.user_loader  # ✅ This part is critical
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all()

    return app
