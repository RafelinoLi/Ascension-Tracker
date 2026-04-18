from flask import Flask
from flask_login import LoginManager
from .models import User
from .db import get_db

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret-key'

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db()
        user_data = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        conn.close()

        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                password_hash=user_data['password_hash']
            )
        return None

    from .routes import main
    app.register_blueprint(main)

    return app