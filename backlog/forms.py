from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField
from wtforms.validators import DataRequired


class FileForm(FlaskForm):
    arquivo = FileField('Selecione um Arquivo...', validators=[DataRequired()])
    submit = SubmitField('Importar')
