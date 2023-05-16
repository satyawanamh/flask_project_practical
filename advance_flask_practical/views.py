from flask_login import login_manager,login_required,logout_user
from flask_mail import Mail,Message
from flask import Flask,Response,redirect,render_template,flash
from flask import Blueprint

from flask_mysqldb import MySQL 
import MySQLdb.cursors
from settings import mail,mysql,login_manager



## blueprint setup here
blueprint_data = Blueprint("blueprint_data",__name__,url_prefix="/advance")

## login manager loader initializer

@login_manager.user_loader
def loader_user(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from usertable  where id=%s ;",(id,))
    data = cursor.fetchone()
    if data :
        cursor.close()
        return data
    else :
        return {"message":"no user detail found"}

	#return Users.query.get(user_id)



@blueprint_data.route("/hello")
def checktest():
    print("in testing data here")
    return "in first app testing here--------"

@blueprint_data.route("/getdata")
def getdata():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("select * from usertable ;")
    data = cursor.fetchall()
    cursor.close()
    return {"data":data}

@blueprint_data.route("/getdata/<int:id>")
def getdata_byid(id):
    try :
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    except Exception as ee :
        print("Database conectivity issue ",ee)
    try :

        cursor.execute("select * from usertable  where id=%s ;",(id,))
        data = cursor.fetchall()
    except Exception as nx:
        print("database query issue here ---",nx)
    cursor.close()
    return {"data":data}

## password encryption in flask

#### password hashing here-------
from werkzeug.security import generate_password_hash, check_password_hash
password = 'password123'
print("the password here-------",password)
hashed_password = generate_password_hash(password)
print("hashed password is here",hashed_password)
password_entered = 'password1234'

@blueprint_data.route("/ps",methods=["GET","POST"])
def password_mapper():
    if check_password_hash(hashed_password, password_entered):
        return {"data":"you  have successfully login"}
    else:
        return {"data":"Sorry you have not login here"}




