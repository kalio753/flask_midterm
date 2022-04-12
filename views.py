from unicodedata import category
from . import app
from flask import render_template, redirect, url_for, flash, request
from .models import Student, User
from .forms import AddForm, RegisterForm, LoginForm, PurchaseForm
from . import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
    return render_template("home.html")

@app.route('/ibanking', methods=['GET', 'POST'])
@login_required             #yêu cầu user phải đăng nhập mới được vô trang market ==> file init phải có thêm dòng 13,14
def ibanking_page():
    purchaseForm = PurchaseForm()
    addForm = AddForm()
    
    if request.method == 'POST':
        # Add Student
        if addForm.validate_on_submit:
            student_to_add = Student.query.filter_by(student_id=addForm.studentID.data).first()
            if student_to_add:
                flash('This item already existed !!', category='danger')
            else:
                add_student = Student(student_id=addForm.studentID.data,
                                student_name=addForm.fullname.data,
                                student_price=addForm.price.data)
                db.session.add(add_student)
                db.session.commit()
                flash(f'{addForm.studentID.data} is added to the board !!' , category='success')

        # Purchase function
        if purchaseForm.validate_on_submit:
            purchased_item = request.form.get('purchased_item')      #này chỉ lấy tên của item được bấm mua (đọc cục cmt dưới)(này là id trong file html)
            student_obj = Student.query.filter_by(student_id=purchased_item).first()   #dùng tên lấy ra item obj trong db
            if student_obj:
                if current_user.can_purchase(student_obj):
                    student_obj.buy(current_user)
                    flash(f"Congratulations! You purchased {student_obj.student_id} for {student_obj.student_price}$", category='success')
                else:
                    flash(f"Unfortunately, you don't have enough money to purchase {student_obj.student_id}!", category='danger')
        return redirect(url_for('ibanking_page'))

        # # Sell function
        # sold_item = request.form.get('sold_item') 
        # item_obj2 = Item.query.filter_by(item_name=sold_item).first()   #dùng tên lấy ra item obj trong db
        # if item_obj2:
        #     if current_user.can_sell(item_obj2):
        #         item_obj2.sell(current_user)
        #         flash(f"Congratulations! You sold {item_obj2.item_name} for {item_obj2.item_price}$", category='success')
        # return redirect(url_for('market_page'))

    if request.method == 'GET':
        students = Student.query.filter_by(student_owner=None)    #return all the items in the db MÀ CHƯA CÓ OWNER

        owned_students = Student.query.filter_by(student_owner=current_user.id) 
        return render_template('ibanking.html', items=students, purchaseForm=purchaseForm, owned_items = owned_students, addForm= addForm)


@app.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('ibanking_page'))
    if form.errors != {}:       #if there are errors
        for error in form.errors.values():
            flash(f'{error}', category='danger')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(user_name=form.username.data).first()
        if attempted_user and attempted_user.check_password(form.password.data):
            login_user(attempted_user)
            flash('Success!!', category='success')
            return redirect(url_for('ibanking_page'))
        else:
            flash('Log In Error!!', category='danger')      

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash('Logged Out!!', category='info')
    return redirect(url_for('home_page'))
