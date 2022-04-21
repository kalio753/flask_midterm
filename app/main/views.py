from flask import render_template, redirect, url_for, flash, request
from ..models import Student, User
from .forms import AddForm, PurchaseForm, SearchForm
from .. import db
from flask_login import login_required, current_user
from . import main
from ..email import send_email, send_congrat_email
from datetime import datetime


@main.route('/')
@main.route('/home')
def home_page():
    return render_template("home.html")

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    addForm = AddForm()
    # purchaseForm = PurchaseForm()
    if request.method == 'POST':
        student_to_add = Student.query.filter_by(student_id=addForm.studentID.data).first()
        if student_to_add:
            flash('This student already existed !!', category='danger')
        elif (addForm.price.data.isnumeric() == False):
            flash('Please enter a correct price format !!', category='danger')
        else:
            add_student = Student(student_id=addForm.studentID.data,
                            student_name=addForm.fullname.data,
                            student_price=addForm.price.data)
            db.session.add(add_student)
            db.session.commit()
            flash(f'Student {addForm.studentID.data} is added to the board !!' , category='success')
    return redirect(url_for('main.ibanking_page'))

@main.route('/purchase', methods=['POST'])
@login_required
def purchase():
    if request.method == 'POST':
        if current_user.user_status == False:
            flash("Another transaction is being executed at the moment. Please try again later !!", category='info')
        else:
        # Purchase function
            purchased_item = request.form.get('purchased_item')      #này chỉ lấy tên của item được bấm mua (đọc cục cmt dưới)(này là id trong file html)
            student_obj = Student.query.filter_by(student_id=purchased_item).first()   #dùng tên lấy ra item obj trong db
            if student_obj:
                if current_user.can_purchase(student_obj):
                    # student_obj.buy(current_user)
                    user = current_user
                    if user is not None :
                        user.user_status = False
                        db.session.commit()
                        token = user.generate_confirmation_token()          
                        email_subject = 'Confirm Your Purchase [' + str(datetime.now().strftime("%d-&m-%Y %H:%M:%S")) + ']'
                        send_email(user.user_email, 'mail/confirm_email', user=user, token=token, student=student_obj)
                        flash("Please check your email to confirm your purchase. ", category='success')
                else:
                    flash(f"Unfortunately, you don't have enough money to paid for {student_obj.student_id} tuition!", category='danger')
    return redirect(url_for('main.ibanking_page'))

@main.route('/confirm_email/<student_id>/<token>')
@login_required
def confirm_email(student_id,token):
    if current_user.confirm(token) == 'TRUE':
        current_user.user_status = True
        db.session.commit()
        student_obj = Student.query.filter_by(student_id=student_id).first()   #dùng tên lấy ra item obj trong db
        if student_obj.buy(current_user) == True:
            mail_body = f"Congratulations! You just paid {student_obj.student_id} tuition for {student_obj.student_price}$"
            send_congrat_email(current_user.user_email, mail_body)
    elif current_user.confirm(token) == 'TOUCHED':
        flash('The confirmation link is invalid. ', category='danger')
    elif current_user.confirm(token) == 'EXPIRED':
        current_user.user_status = True
        db.session.commit()
        flash('The confirmation link is expired. ', category='danger')
    else:
        flash('Something went wrong. ', category='danger')
    return redirect(url_for('main.ibanking_page'))

@main.route('/ibanking', methods=['GET', 'POST'])
@login_required             #yêu cầu user phải đăng nhập mới được vô trang market ==> file init phải có thêm dòng 13,14
def ibanking_page():
    purchaseForm = PurchaseForm()
    addForm = AddForm()
    searchForm = SearchForm()
    stuId = ""
    if request.method == 'POST':
        student_to_search = Student.query.filter_by(student_id=searchForm.keyword.data,student_owner=None).first()
        if student_to_search:
            stuId = (searchForm.keyword.data).strip()
        else:
            flash(f"Student Not Found !!", category='danger')
        
        students = Student.query.filter_by(student_owner=None, student_id=stuId)    #return all the items in the db MÀ CHƯA CÓ OWNER
        owned_students = Student.query.filter_by(student_owner=current_user.id) 
        return render_template('ibanking.html', 
                                items=students, 
                                purchaseForm=purchaseForm, 
                                owned_items = owned_students, 
                                addForm= addForm, 
                                searchForm=searchForm)

    if request.method == 'GET':
        students = Student.query.filter_by(student_owner=None, student_id=stuId)    #return all the items in the db MÀ CHƯA CÓ OWNER
        owned_students = Student.query.filter_by(student_owner=current_user.id) 
        return render_template('ibanking.html', 
                                items=students, 
                                purchaseForm=purchaseForm, 
                                owned_items = owned_students, 
                                addForm= addForm, 
                                searchForm=searchForm)