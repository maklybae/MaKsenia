from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):
    content = TextAreaField('Комментарий', validators=[DataRequired()])
    submit = SubmitField('Отправить')


