import os

from flask import Flask, render_template, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import abort
from werkzeug.utils import redirect

from data import db_session
from config import *
from data.comments import Comment
from data.objects import Object
from data.users import User
from forms.authorisation import AuthorisationForm
from forms.comments import CommentsForm
from forms.object_add_edit import ObjectAddEditForm
from forms.register import RegisterForm

from map_tools import *

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/index')
@app.route("/")
def index():
    db_sess = db_session.create_session()
    request = db_sess.query(Object).order_by(Object.id.desc()).all()
    return render_template("index.html", objects=request, title='Объекты культурного наследия')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = AuthorisationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('authorisation.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if form.admin_key.data != ADMIN_KEY:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Неверный ключ администратора")
        is_admin = True if form.admin_key.data else False
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            first_name=form.first_name.data,
            surname=form.surname.data,
            email=form.email.data,
            is_admin=is_admin
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/addobject',  methods=['GET', 'POST'])
@login_required
def add_object():
    form = ObjectAddEditForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            object = Object(object=form.object.data,
                            registry_number=form.registry_number.data,
                            address=form.address.data,
                            category_of_significance=form.category_of_significance.data,
                            type_of_object=form.type_of_object.data,
                            picture_src=form.picture_src.data,
                            creator_id=current_user.id,
                            is_unesco=form.is_unesco.data, **get_object_coords_region(form.address.data))
        except AddressError as error:
            return render_template('object_add_edit.html', title='Добавление объекта',
                                   form=form, message=error)
        db_sess.add(object)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('object_add_edit.html', title='Добавление объекта',
                           form=form)


@app.route('/editobject/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_object(id):
    form = ObjectAddEditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        object = db_sess.query(Object).filter(Object.id == id).first()
        if object:
            form.object.data = object.object
            form.registry_number.data = object.registry_number
            form.address.data = object.address
            form.category_of_significance.data = object.category_of_significance
            form.type_of_object.data = object.type_of_object
            form.is_unesco.data = object.is_unesco
            form.picture_src.data = object.picture_src
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        object = db_sess.query(Object).filter(Object.id == id).first()
        try:
            geodata = get_object_coords_region(form.address.data)
            object.object = form.object.data
            object.registry_number = form.registry_number.data
            object.address = form.address.data
            object.category_of_significance = form.category_of_significance.data
            object.type_of_object = form.type_of_object.data
            object.is_unesco = form.is_unesco.data
            object.longitude = geodata["longitude"]
            object.latitude = geodata["latitude"]
            object.region = geodata["region"]
            object.picture_src = form.picture_src.data
            object.creator_id = current_user.id
        except AddressError as error:
            return render_template('news.html',
                                   title='Редактирование новости',
                                   form=form,
                                   message=error
                                   )
        db_sess.commit()
        return redirect(f'/object/{id}')
    return render_template('object_add_edit.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/deleteobject/<int:id>', methods=['GET', 'POST'])
@login_required
def object_delete(id):
    db_sess = db_session.create_session()
    object = db_sess.query(Object).filter(Object.id == id).first()
    if object:
        db_sess.delete(object)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/object/<int:id>', methods=['GET', 'POST'])
def object(id):
    form = CommentsForm()
    if request.method == 'GET':
        db_sess = db_session.create_session()
        object = db_sess.query(Object).filter(Object.id == id).first()
        comments = db_sess.query(Comment).filter(Comment.object_id == id).order_by(Comment.id.desc()).all()
        if object:
            return render_template('object.html',
                                   title=object.object,
                                   object=object,
                                   img_src=static_map_href(object.longitude, object.latitude),
                                   form=form,
                                   comments=comments)

        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = Comment(content=form.content.data, object_id=id)
        current_user.comments.append(comment)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/object/{id}')


def main():
    db_session.global_init("database/main_db.db")
    port = int(os.environ.get("PORT", PORT))
    app.run(host=HOST, port=port)


if __name__ == '__main__':
    main()
