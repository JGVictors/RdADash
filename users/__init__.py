import flask_sqlalchemy.model
from flask import Blueprint, render_template, flash, url_for, request, redirect
from extentions import login_manager, db, permission_required, is_safe_url
from users.models import Users, Permissions
from users.forms import LoginForm, UserCreate, UserUpdateForm, PermissionForm, ChangePasswordForm
from flask_login import login_required, current_user, login_user, logout_user
from re import sub


users = Blueprint('users', __name__, template_folder='templates', static_folder='static')


@login_manager.user_loader
def load_user(user_id: str):
    return Users.query.get(user_id)


def init_system_user(app):
    active = bool(int(app.config['SYSTEM_USER_ACCESSIBLE']))
    if active:
        user = Users.query.get('SYSTEM')
        if not user:
            user = Users('SYSTEM', 'Usuário Sistêmico', '', app.config['SYSTEM_USER_PASSWORD'])
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                print('Erro ao criar usuário sistêmico!', flush=True)
                raise e
        else:
            try:
                user.password = app.config['SYSTEM_USER_PASSWORD']
                db.session.commit()
            except Exception as e:
                print('Erro ao definir a senha do usuário sistêmico!', flush=True)
                raise e
        if not user.has_permission('*'):
            perm = Permissions('SYSTEM', 'SYSTEM', '*')
            try:
                db.session.add(perm)
                db.session.commit()
            except Exception as e:
                print('Erro ao dar permissão ao usuário sistêmico', flush=True)
                raise e
        print('Usuário Sistêmico está ativo!')
    else:
        user_to_delete = Users.query.get('SYSTEM')
        if user_to_delete:
            try:
                db.session.delete(user_to_delete)
                db.session.commit()
            except Exception as e:
                print('Erro ao desativar usuário sistêmico, o mesmo permanece ativo!', flush=True)
                raise e


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect("/")
    elif request.method == 'POST':
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!')
            next_url = request.args.get('next')
            return redirect(next_url) if next_url and is_safe_url(next_url) else redirect(url_for('main.index'))
        else:
            flash('Usuário e senha não conferem!')
    return render_template('login.html', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!')
    return redirect(url_for('users.login'))


@users.route('/users', methods=['GET', 'POST'])
@permission_required('users.view')
def theusers():
    form = UserCreate()
    print(form.password, flush=True)
    if form.validate_on_submit():
        user = Users.query.get(form.username.data)
        if user:
            flash('Já tem alguém registrado com esse usuário!')
            return redirect(url_for('users.theusers'))
        else:
            user = Users(sub('[^A-Z0-9]', '', form.username.data.upper()),
                         form.nome.data, form.email.data, form.password.data)
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as e:
                flash(f'Erro! Usuário não foi adicionado.')
                return render_template('/500', e=e), 500
            flash('Usuário adicionado com sucesso!')
    users = Users.query.order_by(Users.date_added)

    return render_template('users.html', form=form, users=users)


@users.route('/profile')
def profile():
    password_form = ChangePasswordForm()
    return render_template('profile.html', form=password_form)


@users.route('/users/update/<username>', methods=['GET', 'POST'])
@permission_required('users.update')
def update(username: str):
    form = UserUpdateForm()
    password_form = ChangePasswordForm()
    perm_form = PermissionForm()
    user_to_update = Users.query.get_or_404(username)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user_to_update.nome = form.nome.data
                user_to_update.email = form.email.data
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao realizar alteração...')
                return render_template('/500.html', e=e), 500
            flash('Alteração realizado com sucesso!')
        elif password_form.validate_on_submit():
            try:
                user_to_update.password = password_form.password.data
                user_to_update.last_password_change = None
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao realizar alteração...')
                return render_template('/500.html', e=e), 500
            flash('Alteração realizado com sucesso!')
        elif perm_form.validate_on_submit() and current_user.has_permission('users.update.permissions'):
            perm_form.permission.data = sub('[^A-z0-9.*]', '', perm_form.permission.data).lower()
            if not current_user.has_permission(perm_form.permission.data) or \
                    perm_form.permission.data == '*' and current_user.username != 'SYSTEM':
                flash('Você não pode adicionar essa permissão.')
            elif user_to_update.has_permission(perm_form.permission.data):
                flash('Este usuário já tem essa permissão.')
            elif len(perm_form.permission.data) > 0:
                perm = Permissions(username, current_user.username, perm_form.permission.data)
                try:
                    db.session.add(perm)
                    db.session.commit()
                except Exception as e:
                    flash(f'Erro ao tentar adicionar a permissão...')
                    return render_template('500.html', e=e), 500
                flash('Permissão adicionada com sucesso!')

    form.username.data = user_to_update.username
    form.nome.data = user_to_update.nome
    form.email.data = user_to_update.email

    perm_form.permission.data = None
    perms = user_to_update.permissions

    fs = int(request.args.get('f')) if 'f' in request.args else None

    return render_template('update.html', forms=[form, password_form, perm_form], fs=fs, username=username, perms=perms)


@users.route('/users/update/delete_perm/<id>')
@permission_required('users.update.permissions')
def delete_perm(permid: int):
    perm_to_delete = Permissions.query.get_or_404(permid)
    if perm_to_delete.owner_username == current_user.username and not current_user.has_permission('*'):
        flash('Não é possível remover permissões de você mesmo!')
    elif perm_to_delete.owner.has_permission('*') and \
            perm_to_delete.owner_username != current_user.username and current_user.username != 'SYSTEM':
        flash('Não é possível remover permissões deste usuário!')
    elif perm_to_delete.permission == '*' and current_user.username != 'SYSTEM':
        flash('Não é possivel remover está permissão!')
    else:
        try:
            db.session.delete(perm_to_delete)
            db.session.commit()
        except Exception as e:
            flash(f'Erro ao tentar remover permissão...')
            return render_template('500.html', e=e), 500
        flash(f'Removido permissão "{perm_to_delete.permission}" do usuário {perm_to_delete.owner} com sucesso!')
    return redirect(url_for('users.update', username=perm_to_delete.owner_username))


@users.route('/users/delete/<username>')
@permission_required('users.delete')
def delete(username: str):
    user_to_delete = Users.query.get_or_404(username)
    if user_to_delete.username == current_user.username:
        flash('Não é possivel deletar você mesmo!')
    elif user_to_delete.has_permission('*'):
        flash('Não é possivel deletar este usuário!')
    else:
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
        except Exception as e:
            flash(f'Erro ao tentar deletar usuário...')
            return render_template('500.html', e=e), 500
        flash(f'Usuário {user_to_delete.username} "{user_to_delete.nome}", deletado com sucesso!')
    return redirect(url_for('users.theusers'))
