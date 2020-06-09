from flask import Flask
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'heyyyyvsaucehere'

    login_manger = LoginManager()
    login_manger.login_view = 'auth.login'
    login_manger.init_app(app)

    from .user import User

    @login_manger.user_loader
    def load_user(id):
        return User.find_by_id(id)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

