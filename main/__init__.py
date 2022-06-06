from flask import Blueprint, render_template
from datetime import datetime

main = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main')


# Criando rotas
@main.route('/')
def index():
    return render_template('index.html', time=datetime.now().strftime("%D %T"))


@main.route('/getTimenow', methods=['POST', 'GET'])
def get_timenow():
    return {"timenow": datetime.now().strftime("%D %T")}
