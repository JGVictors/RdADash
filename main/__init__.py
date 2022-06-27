from flask import Blueprint, render_template, Flask, url_for, jsonify
from flask_login import login_required
from datetime import datetime

main = Blueprint('main', __name__, template_folder='templates', static_folder='static', static_url_path='/main')


# Criando rotas
@main.route('/')
@login_required
def index():
    return render_template('index.html', time=datetime.now().strftime('%D %T'))


@main.route('/getTimenow', methods=['POST', 'GET'])
def get_timenow():
    return jsonify({'timenow': datetime.now().strftime('%D %T')})


def init_navbar_sidelist(app: Flask):
    @app.context_processor
    def base():
        sidelist = {
            'Acesso': {'icon': 'ui-radios-grid',
                       'perm': 'menu.acesso',
                       'items': {'Backlog': {'href': url_for('backlog.thebacklog'),
                                             'perm': 'backlog.view'}}},
            'Gerenciamento': {'icon': 'file-earmark-text',
                              'perm': 'menu.gerenciamento',
                              'items': {'Usuários': {'href': url_for('users.theusers'),
                                                     'perm': 'users.view'}}},
            'Perfil': {'icon': 'person',
                       'href': url_for('users.profile')}
        }
        return dict(sidelist=sidelist)


def init_errors_handlers(app):

    @app.errorhandler(403)
    @login_required
    def page_not_found(e):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    @login_required
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    @login_required
    def page_internal_error(e):
        return render_template('500.html'), 500
