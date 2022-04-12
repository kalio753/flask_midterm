from enum import unique
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
 
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///midterm.db'
app.config['SECRET_KEY'] = '18a29538cdd94979294afa64'   #secret de co the hien thi form, python-->import os-->os.urandom(12).hex()
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'         #tên của method trong view để dẫn đến trang login
login_manager.login_message_category = 'info'       #tạo category cho flash

from . import views
