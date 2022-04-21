from . import db, bcrypt, login_manager
from flask_login import UserMixin
from datetime import datetime
import json
from datetime import datetime
from flask import current_app, flash
import authlib.jose.errors
from authlib.jose import JsonWebSignature

#import class UserMixin để class User kế thừa
#nếu kế thừa thì trong User đỡ phải implement các method mà flask_login đòi
#kh kế thừa thì phải có cái method trong link:  https://flask-login.readthedocs.io/en/latest/#how-it-works

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)        #phải để id vì đang có lỗi import, mà hàm get_id của flask_login đòi column tên là id
    user_name = db.Column(db.String(20), nullable=False, unique=True)
    user_fullname = db.Column(db.String(20), nullable=False)
    user_phone = db.Column(db.String(12), nullable=False)
    user_email = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(60), nullable=False)            #phải để 60 vì hash ra sẽ gất dài
    user_budget = db.Column(db.Integer(), nullable=False, default=1000)
    user_status = db.Column(db.Boolean, default=True)
    user_paid_list = db.relationship('Student', backref = 'owned_user', lazy=True)

    #tạo ra 1 property tên password 
    @property
    def password(self):
        return self.password

    #và password sẽ là input được hash sau đó gắn vô user_password
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    @property
    def prettier_budget(self):
        if len(str(self.user_budget)) >= 4:
            return f'{str(self.user_budget)[:-3]},{str(self.user_budget)[-3:]}$'
        else:
            return f"{self.user_budget}$"

    def can_purchase(self, item_obj):
        return self.user_budget >= item_obj.student_price

    def generate_confirmation_token(self):
        jws = JsonWebSignature()
        protected = {'alg': 'HS384'}  
        payload = '{"confirm":' + str(self.id) + ',"timestamp":"' + str(datetime.now()) + '"}'
        secret = current_app.config['SECRET_KEY']
        token = jws.serialize_compact(protected, payload, secret)
        return token
    
    def confirm(self, token, expiration=300):
    # Deserialize a JWS Compact Serialization
        jws = JsonWebSignature()
        try:
            data = jws.deserialize_compact(token, key=current_app.config['SECRET_KEY'])
        except authlib.jose.errors.BadSignatureError:       #KHI TOKEN BỊ TOUCH(CHỈNH SỬA)
            return 'TOUCHED'
        except:
            return 'OTHERS'
        # Validate timestamp and token
        decoded_payload = json.loads(data.get('payload'))
        timestamp = datetime.strptime(decoded_payload.get('timestamp'), '%Y-%m-%d %H:%M:%S.%f')
        duration_in_second = (datetime.now() - timestamp).total_seconds()
        user_id = decoded_payload.get('confirm')
        if duration_in_second < 0 or duration_in_second > expiration or user_id != self.id:
            return 'EXPIRED'
        else:
            return 'TRUE'
        

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(10), nullable=False, unique=True)
    student_name = db.Column(db.String(50), nullable=False)
    student_price = db.Column(db.Integer(), nullable=False)
    student_date = db.Column(db.String(40), nullable=False, default=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    student_owner = db.Column(db.Integer, db.ForeignKey('user.id')) 

    # def __repr__(self):
    #     return f'id {self.item_id}, name {self.item_name}'

    def buy(self, user):
        if(self.student_owner==None):
            self.student_owner = user.id
            self.student_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            user.user_budget -= self.student_price
            db.session.commit()
            flash(f"Congratulations! You just paid {self.student_id}'s tuition for {self.student_price}$", category='success')
            return True
        else:
            flash(f'Already paid by another user.' , category='danger')
            return False
    # def sell(self, user):
    #     self.item_owner = None
    #     user.user_budget += self.item_price
    #     db.session.commit()