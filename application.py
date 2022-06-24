from dotenv import load_dotenv, find_dotenv
from flask import Flask
from extentions import init_extetions

from main import main, init_errors_handlers, init_navbar_sidelist
from users import users, init_system_user
from backlog import backlog


# Setando Variaveis de Ambiente
load_dotenv(find_dotenv())

# Criando Instancia do Flask
application = app = Flask(__name__)
app.config.from_pyfile("settings.py")

with app.app_context():
    init_extetions(app)

    app.register_blueprint(main)
    init_navbar_sidelist(app)
    init_errors_handlers(app)

    app.register_blueprint(users)
    init_system_user(app)
    app.register_blueprint(backlog)
