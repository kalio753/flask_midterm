from unicodedata import category
from .. import mail
from flask import render_template, redirect, url_for, flash, request
from ..models import Student, User
from .forms import RegisterForm, LoginForm
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from . import auth


@auth.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(user_name=form.username.data,
                        user_fullname=form.fullname.data,
                        user_phone=form.phone.data,
                        user_email=form.email.data,
                        password=form.password1.data)   
                        #không truyền password_hash mà truyền password, để hàm setter trong model generate tự hash password_hash
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Welcome !!', category='success')
        return redirect(url_for('main.ibanking_page'))
    if form.errors != {}:       #if there are errors
        for error in form.errors.values():
            flash(f'{error}', category='danger')
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(user_name=form.username.data).first()
        if attempted_user and attempted_user.check_password(form.password.data):
            login_user(attempted_user)
            flash('Success!!', category='success')
            return redirect(url_for('main.ibanking_page'))
        else:
            flash('Log In Error!!', category='danger')      

    return render_template('login.html', form=form)

@auth.route('/logout')
def logout_page():
    logout_user()
    flash('Logged Out!!', category='info')
    return redirect(url_for('main.home_page'))