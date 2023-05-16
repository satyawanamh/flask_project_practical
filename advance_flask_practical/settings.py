from flask_login import login_required,logout_user,LoginManager
from flask_mail import Mail,Message
from flask import Flask,Response,redirect,render_template,flash
from flask import Blueprint

from flask_mysqldb import MySQL 
import MySQLdb.cursors


app = Flask(__name__)

### login manager setup

login_manager =LoginManager(app)

## EMAIL SETUP HERE-----------
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'satyawan@simprosys.com'
app.config['MAIL_PASSWORD'] = 'xlksenwivdnmcclg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

## DATABASE SETUP
app.config["MYSQL_DB"]="flasktutdb"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PASSWORD"]="Satya@123"
mysql = MySQL(app)