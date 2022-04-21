from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ObjectAddEditForm(FlaskForm):
    object = StringField('Объект', validators=[DataRequired()])
    registry_number = StringField('Номер в реестре')
    address = StringField('Полный адрес', validators=[DataRequired()])
    category_of_significance = StringField('Категория историко-культурного значения', validators=[DataRequired()])
    type_of_object = StringField('Тип объекта')
    picture_src = StringField('Ссылка на изображение')
    is_unesco = BooleanField('Состоит в ЮНЕСКО')
    submit = SubmitField('Применить')
