from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Regexp


class LoginForm(FlaskForm):
    username = StringField('Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar!')


class UserUpdateForm(FlaskForm):
    nome = StringField('Insira um nome', validators=[DataRequired()])
    email = EmailField('Insira um e-mail', validators=[DataRequired(), Email(message='Informe um e-mail valido.')])
    submit = SubmitField('Concluir!')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Senha',
                             validators=[DataRequired(), EqualTo('password2', message='Senhas precisam ser iguas.')])
    password2 = PasswordField('Confirme sua Senha', validators=[DataRequired()])
    submit = SubmitField('Alterar Senha!')


class UserCreate(UserUpdateForm, ChangePasswordForm):
    username = StringField('Insira um nome de usuário', validators=[DataRequired(), Regexp('[A-z0-9]')])
    submit = SubmitField('Cadastrar Usuário!')


class PermissionForm(FlaskForm):
    permission = StringField('Informe a permissão a ser adicionada', validators=[DataRequired(), Regexp('[A-z0-9.*]')])
    submit = SubmitField('Adicionar!')
