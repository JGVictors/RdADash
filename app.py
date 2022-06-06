from flask import Flask, render_template
from main import main
from backlog import backlog

# Criando Instancia do Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ThatsMySecretFuckingSuperKey'

app.register_blueprint(main)
app.register_blueprint(backlog)


# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_internal_error(e):
    return render_template('500.html'), 500
