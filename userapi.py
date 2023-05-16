from flask import Flask,request,make_response,jsonify,render_template,redirect,flash,url_for
from flask_jwt_extended import JWTManager,create_access_token,create_refresh_token,jwt_required,get_jwt_identity
from functools import wraps
from flask_restful import Api , Resource,reqparse
import jwt
import MySQLdb.cursors
from datetime import datetime,timedelta
from flask_mail import Mail,Message
from flask_mysqldb import MySQL

import uuid
app =Flask(__name__)
app.config["JWT_SECRET_KEY"]= "jjdkjads834dmdk7"
app.config['SECRET_KEY']= b"jkckjkcxnd8e4hjxcz87"

#######email setup in flask
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'satyawan@simprosys.com'
app.config['MAIL_PASSWORD'] = 'xlksenwivdnmcclg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

##mysql setup 
app.config["MYSQL_DB"]="flasktutdb"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PASSWORD"]="Satya@123"

##mysql initialize
mysqldb =MySQL(app)

import mysql.connector
mysql =mysql.connector.connect(username="root",database="flasktutdb",password="Satya@123",host="localhost")
cursor =mysql.cursor(MySQLdb.cursors.DictCursor)

## jwt intialize
jwt = JWTManager(app)

@app.route("/token",methods=["POST"])
def login():
    #wraps(f)
    email =request.json.get("email")
    password = request.json.get("password")

    sql = "select * from student where email=%s and password=%s "
    value = (email,password)
    cursor.execute(sql,value)
    student = cursor.fetchone()
    if cursor.rowcount==0:
        return jsonify({"message":"bad request ,username or password"}),401
    elif cursor.rowcount == 1:
        access_token = create_access_token(identity=student[0])
        refresh_token = create_refresh_token(identity=student[0])
        #return  f(current_user, *args, **kwargs)
        return jsonify({ "token": access_token, "user_id": student[0] ,"refresh_token":refresh_token})   
    cursor.close()  

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    # Get the identity of the authenticated user from the JWT token
    current_user = get_jwt_identity()

    return jsonify({'msg': f'Hello {current_user}! This endpoint is protected by JWT authentication.'}), 200


@app.route("/hello",methods=["GET"])
@jwt_required()
def hello():
    return jsonify({"msg":f"welcome in postral ,api working here "}),200


@app.route("/postdata",methods=["POST"])
@jwt_required()
def postdata():
    data =request.get_json()
    key =data["email"]
    email =data["email"]
    password  = data["password"]
    return jsonify({"data":data,"allkeys":key,"combo_data":(email,password)})


@app.route("/createtoken",methods=["POST"])
def createtoken():
    access_token = create_access_token(identity=True, expires_delta= timedelta(minutes=20))
    return jsonify({ "createtoken": access_token})   
    
##Api initialize here
api = Api(app)

class Register_student(Resource):
    @jwt_required()
    def post(self):
        data =request.get_json()
        return jsonify({"json data":data})

 
class Student(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("id",type=int,required=True)
        self.parser.add_argument("username",type=str,required=True)
        self.parser.add_argument("email",type=str,required=True)
        self.parser.add_argument("password",type=str,required=True)

    @jwt_required()
    def get(self):
        sql = "Select * from student ; "
        cursor.execute(sql)
        data =cursor.fetchall()
        return jsonify({"data_file":data})
    
    @jwt_required()
    def post(self):
        #data = request.get_json()
        args = self.parser.parse_args()
        sql = "insert into student (id,username,email,password) values (%s,%s,%s,%s) ;"
        # value =(data["id"],data["username"],data["email"],data["password"])
        value = (args["id"],args["username"],args["email"],args["password"])        
        cursor.execute(sql,value)        
        cursor.close()
        mysql.commit()
        return jsonify({"inserted_data":"successfully inserted"})


## addinng class based resource here
api.add_resource(Register_student,"/add")
api.add_resource(Student,"/stu_data")


@app.route("/login_user",methods=["GET","POST"])
def login_user():
    if request.method=="POST" and "email" in request.form and "password" in request.form:
        email = request.form["email"]
        password = request.form["password"]
        sql = "select * from student where email=%s and password =%s ; "
        value =(email,password)
        cursor.execute(sql,value)
        data = cursor.fetchone()
        if data:
            return jsonify({"message":"login successfully"})
        else :
            return jsonify({"message":"Sorry , you have not login"})
    return render_template("login_user.html")


@app.route("/changepass",methods =["GET","POST"])
def changepass():
    if request.method=="POST" and "email" in request.form :
        mysql_data = mysqldb.connection
        mysql_cursor =mysql_data.cursor(MySQLdb.cursors.DictCursor)
        email = request.form["email"]        
        sql = "select * from student where email=%s ; "
        value =(email,)
        mysql_cursor.execute(sql,value)
        data = mysql_cursor.fetchone()
        print("data ----------------",data)
        if data:    
            token = str(uuid.uuid4())   
            print(token)     
            date  = datetime.now()+timedelta(minutes=5)            
            print(datetime.timestamp(date))
            expire_time = int(datetime.timestamp(date))
            print(expire_time)
            sql = "update  student set expiretime=%s , token=%s where email=%s"
            value = (expire_time,token,email)
            mysql_cursor.execute(sql,value)
            expdata =mysql_cursor.fetchone()
            mysql_cursor.close()
            mysql_data.commit()
            print("cursor data here ",expdata) 
            print("cursor data here ",expdata)       

            msg = Message("password reset link ",sender="satyawan@simprosys.com",recipients=[email])
            msg.body =f"password reset link clich here http://127.0.0.1:5000/updatepass/{token} "
            mail.send(msg)            
            return jsonify({"message":"email send successfully "})    
        else :
            return jsonify({"message":"Sorry , no user detail found"})    
    return render_template("/changepassword_user.html")


@app.route("/updatepass/<token>",methods=["GET","POST"])
def updatepassword(token):
    mysql_data = mysqldb.connection
    mysql_cursor =mysql_data.cursor(MySQLdb.cursors.DictCursor)
    sql = "select * from student where token=%s"
    mysql_cursor.execute(sql,(token,))
    data =mysql_cursor.fetchone()
    date =datetime.now()
    current_time = int(datetime.timestamp(date))
    if current_time < int(data["expiretime"]):
        if request.method=="POST" and "password" in request.form:
            password = request.form["password"]
            print("update password here-------",password)
            sql ="update  student set password=%s where token=%s ;"
            value =(password,token)
            mysql_cursor.execute(sql,value)
            updatedata =mysql_cursor.fetchone()
            mysql_cursor.close()
            mysql_data.commit()
            return redirect('/login_user')
    else :
        flash("Sorry link has been expired ")
        return redirect("/changepass")    
    return render_template("updatepassword_user.html")


## run app 
if __name__=="__main__":
    app.run(debug=True)

