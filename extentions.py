from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from flask import render_template, request
from functools import wraps
from urllib.parse import urlparse, urljoin

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def init_extetions(app):
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    login_manager.login_message = "Autenticação é necessário para continuar!"

    if bool(int(app.config['CREATE_DBTABLES'])):
        db.create_all()


def permission_required(perm: str):
    def decorator_func(func):
        @login_required
        @wraps(func)
        def wrapper_func(*args, **kwargs):
            if current_user.has_permission(perm):
                return func(*args, **kwargs)
            else:
                return render_template("403.html"), 403
        return wrapper_func
    return decorator_func


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc
