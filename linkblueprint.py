from flask import Blueprint,render_template,url_for,redirect,request,Flask,session,flash,make_response,Response,jsonify
from flask_mysqldb import MySQL
from flask_mail import Mail,Message
import MySQLdb.cursors
import string 
import random
import logging
from io import BytesIO,StringIO
import csv
import pandas as pd
import os
import pdfkit
from threading import Thread
from loggingfile import logger
import jwt
from datetime import datetime,timedelta
from functools import wraps
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import current_user,LoginManager
app = Flask(__name__)
app.secret_key=b"hdhjhjsdhbhu887452nb"

## mysql setup
app.config["MYSQL_DB"]="flasktutdb"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PASSWORD"]="Satya@123"

# initialize mysql db
mysqldb =MySQL(app)

#######email setup in flask
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'satyawan@simprosys.com'
app.config['MAIL_PASSWORD'] = 'xlksenwivdnmcclg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

mainlink = Blueprint("mainlink",__name__,url_prefix="/web")

try :    
    import mysql.connector
    mysql =mysql.connector.connect(username="root",database="flasktutdb",password="Satya@123",host="localhost")
    cursor =mysql.cursor()
    sql = """create table if not exists Usertable (id int NOT NULL AUTO_INCREMENT , 
    username varchar(100) not null,password Text not null,email varchar(100) not null,      
    primary key (id),
    UNIQUE (email));"""
    cursor.execute(sql)        
    mysql.close()
except Exception as exp :
    print("Can not create table exception occur")
    logger.error(f"error in usertable creation here  ",exp)


############ token generation 
def login_required(func):
    wraps(func)
    def decorated():
        token =request.args.get("token")
        if not token :
            return jsonify({"Alert":"Token is missing"})
        try :
            payload =jwt.decode(token,app.secret_key)

        except Exception :
            return jsonify({"Alert":"invalid token"})
    return decorated


@mainlink.route("/signup",methods=["GET","POST"])
def signup():
    if request.method=="POST" and "username" in request.form and "password" in request.form and "email" in request.form:
        username = request.form["username"]
        email = request.form["email"]
        print("eeeeeeeeeeeeee",email)
        password1 = request.form["password"]
        password =generate_password_hash(password1)
        try :
            cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
        except Exception as nx:
            print("connectivity issue in database")
            logger.error(f"connectivity issue in database ",nx)
        if not username or not password or not email:            
            return redirect("/web/signup")        
        else :
            try :
                sql="insert into usertable (username,password,email) values(%s,%s,%s)"
                value = (username,password,email)
                print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj",username,password,email)
                cursor.execute(sql,value)   
                data =cursor.fetchone()   
                cursor.close()
                mysqldb.connection.commit()
                flash("user register successfully ")       
            except Exception as nx:
                print("No data inserted successfully here please check in signup function ")
                logger.error(f"No data inserted successfully here please check in signup function ",nx)
            msg=Message("User registration message",sender="satyawan@simprosys.com",recipients=[email])
            try :
                msg.body = f"thank you for registration here {username} "
                mail.send(msg)
                message = f'You have successfully registered !{username}'
            except Exception as er:
                print("error in sending email",er)
                logger.error(f"error in sending email {er}")
            
            return redirect("/web/signin")  

    return render_template("signup.html")


@mainlink.route("/signin",methods=["GET","POST"])
#@login_required
def signin():
    if request.method=="POST"  and "password" in request.form and "email" in request.form:    
        email = request.form["email"]
        password = request.form["password"]
        cursor =mysqldb.connection.cursor()
        #mysql = mysqldb.connection
        if  not password or not email:            
            return redirect("/web/signin")        
        else :            
            try :         
                cursor.execute("select * from usertable where email =%s ;",(email,))  
            except Exception as nx:
                print("can not get email and password in signin function")
                logger.error(f"can not get email and password in signin function ",nx)
            #if cursor.rowcount != 0 :   
            if cursor.rowcount==0:
                flash("email or password not matched")
                #cursor.close()
                return redirect("/web/signin")     
            else :
                data = cursor.fetchone()
                if data :
                    try :
                        if check_password_hash(data[2],password):
                            session['is_authenticated']=True
                            session["loggedin"]=True
                            session["email"] = data[3]                    
                            cursor.close()
                            mysqldb.connection.commit()
                            flash("user successfully login")
                            return redirect("/web/home")
                    except Exception as nx:
                        print("session can not store successfully here")
                        logger.error(f"session can not store successfully here ",nx)
    return render_template("signin.html")


## declare home function
@mainlink.route("/home",methods=["GET","POST"])
def home():
    return render_template("home.html")


@mainlink.route("/logout",methods=["GET","POST"])
def logout():
    try :
        session.pop("loggedin",None)
        session.pop("email",None)
        session.pop("is_authenticated",None)
        session.pop("token",None)
        return redirect("/web/signin")
    except Exception as nx:
        print("session can not successfully deleted")
        logger.error(f"session can not successfully deleted ",nx)
        return redirect("/web/home")


@mainlink.route("/changepassword",methods=["GET","POST"])
def changepassword():
    message=""
    if request.method=="POST" and "oldpassword" in request.form and "newpassword" in request.form:       
        password = request.form["oldpassword"]        
        newpassword = request.form["newpassword"]
        try :
            email = session["email"]
            if len(email)==0:            
                message ="please fill correct details"          
                return redirect(url_for("/web/home",message=message))   
            else :
                print("----------------email ",email)
        except Exception as nx:
            print("email not found in session")
            logger.error(f"email not found in session ",nx)    
        try :            
            cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
        except Exception as nx:
            print("database connection issue in changepassword ")
            logger.error(f"database connection issue in changepassword  ",nx)
        if not password  or not newpassword:  
            message ="please fill correct details"          
            return redirect(url_for("/web/home",message=message))  
        else :
            try :
                cursor.execute("select * from usertable where email=%s",(email,))
                data = cursor.fetchone()
            except Exception as nx:
                print("sorry no record found here")
                logger.error(f"sorry no record found here ",nx)
            if data :     
                try :            

                    sql="update  usertable set password=%s where email= %s ; "
                    value = (newpassword,email)
                    print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj",)
                    cursor.execute(sql,value)
                    #if cursor.rowcount != 0 :      
                    data =cursor.fetchone()   
                    cursor.close()
                    mysqldb.connection.commit()
                    message = "password change successfully"
                    return redirect(url_for("mainlink.home"))  
                except Exception as nx:
                    print("sorry , can not update data -- check sql query")
                    logger.error(f"sorry , can not update data -- check sql query ",nx)

    return render_template("changepass.html",message=message)


@mainlink.route("/forgetpassword",methods=["GET","POST"])
def forgetpassword():
    if request.method=="POST":
        email =request.form["email"]
        if email is None:
            message = "please enter user email"
            return redirect(url_for("mainlink.forgetpassword"),message=message)
        try :
            cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select * from usertable where email=%s",(email,))
            data = cursor.fetchone()
        except Exception as nx:
            print("email address not found ")
            flash("email address not found ")
            logger.error(f"email address not found  ",nx)
            return redirect(url_for('mainlink.forgetpassword'))
        
        if data is not None:      
            newpassword = "".join(random.choices(string.ascii_letters+string.digits,k=8))  
            print("newwwwwwwwwwwwwww",newpassword)
            sql="update  usertable set password=%s where email= %s ; "
            value = (newpassword,email)
            print("jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj",)
            cursor.execute(sql,value)
            cursor.close()
            mysqldb.connection.commit()
            try :
                msg=Message("User registration message",sender="satyawan@simprosys.com",recipients=[email])   

                msg.body = f"""thank you for registration here \
                    your password  {newpassword} """
                mail.send(msg)
                flash("please check email auto generated password send successfully")
                return redirect("/web/signin")   
            except Exception as nx:
                print("email can not send successfully ")
                logger.error(f"email can not send successfully ",nx)
        else :
            flash("Sorry , email content not found on database")
            return redirect("/web/signup")  

    return render_template("forgetpassword.html")

@mainlink.route("/savecsv",methods=["GET","POST"])
def savecsv():  
    if request.method=="POST":
        try :
            file =request.files['csvfile']   
            csv_data = file.read().decode('utf-8').splitlines()
            reader = csv.reader(csv_data)
            columns = next(reader)
        except Exception as nx:
            print("cant not read csv file successfuly here")
            logger.error(f"cant not read csv file successfuly here ",nx)
        columns = [column.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_') for column in columns]
        headers = {'Content-Type': 'application/json'}
        try :                
            table_name = 'CSVTABLE'
            create_table_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ("
            for column in columns:
                create_table_stmt += f"{column} Text,"
            create_table_stmt = create_table_stmt[:-1] + ");"
            # Create the table
            cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)            
            cursor.execute(create_table_stmt)
        except Exception as nx:
            print("Can not create table successfully ")
            logger.error(f"Can not create table successfully ",nx)

        try :            
            insert_stmt = f"INSERT INTO {table_name} ({','.join([column.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_') for column in columns])}) VALUES ({','.join(['%s']*len(columns))})"

            print("inserting data",insert_stmt)
            for row in reader:
                cursor.execute(insert_stmt, row)
                print(row)
            cursor.close()
            mysqldb.connection.commit()
            flash("inserted data successfully ")
            return redirect(url_for('mainlink.home'))
        except Exception as ex:
            print("can not insert data",ex)   
            logger.error(f"can not insert data ",ex)           
    return render_template("savecsv.html")

def savecsv_thread(file):  
    try :            
        csv_data = file.read().decode('utf-8').splitlines()
        reader = csv.reader(csv_data)
        columns = next(reader)
    except Exception as nx:
        print("can not read csv file in savecsv_thread function here ")
        logger.error(f"can not read csv file in savecsv_thread function here ",nx)
    columns = [column.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_') for column in columns]
    headers = {'Content-Type': 'application/json'}
    try :
        table_name = 'CSVTABLE_thread'
        create_table_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for column in columns:
            create_table_stmt += f"{column} Text,"
        create_table_stmt = create_table_stmt[:-1] + ");"
    except Exception as nx:
        print("create table syntax issue in savecsv_thread function ")
        logger.error(f"create table syntax issue in savecsv_thread function ",nx)
    try :
        import mysql.connector
        mysqlcsv =mysql.connector.connect(username="root",database="flasktutdb",password="Satya@123",host="localhost")
        cursorcsv =mysqlcsv.cursor()
        cursorcsv.execute(create_table_stmt)
    except Exception as nx:
        print("can not create table , or connection issue ")
        logger.error(f"can not create table , or connection issue  ",nx)
    try :    
        insert_stmt = f"INSERT INTO {table_name} ({','.join([column.strip().replace(' ', '_').replace('(', '').replace(')', '').replace('/', '_').replace('-', '_') for column in columns])}) VALUES ({','.join(['%s']*len(columns))})"
        
        for row in reader:
            cursorcsv.execute(insert_stmt, row)        
        cursorcsv.fetchall()
        cursorcsv.close()
        mysqlcsv.commit()    
        flash("data inserted successfully ")
        return redirect(url_for('mainlink.home'))
    except Exception as ex:
        print("can not insert data successfully ",ex)   
        logger.error(f"can not insert data successfully {ex}")    
    return redirect(url_for('mainlink.home'))

    
@mainlink.route("/savethreadcsv",methods=["GET","POST"])
def savethreadcsv():
    if request.method=="POST":
        try :
            file =request.files['csvfile']
            threadfile = Thread(target=savecsv_thread,args=(file,))
            threadfile.start()
            threadfile.join()   
        except Exception as nx:
            print("can not create thread successfully ") 
            logger.error(f"can not create thread successfully ",nx)
    return render_template("savecsv.html")


@mainlink.route("/exportcsv",methods=["GET","POST"])
def exportcsv():
    try :    
        import pandas as pd
        import os
        cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "Select * from csvtable ;" 
        cursor.execute(sql)
        datafile =cursor.fetchall()
        if datafile is None :
            flash("sorry no content found in database")
    except Exception as nx:
        print("can not get any data in csv table ")
        logger.error(f"can not get any data in csv table ",nx)
    datafm = pd.DataFrame(datafile)
    datafm.to_csv('data.csv', index=False)
    try :
        response = make_response()
        response.data = open('data.csv', 'rb').read()
        response.headers['Content-Disposition'] = 'attachment; filename=data.csv'
        response.headers['Content-Type'] = 'text/csv' 
        os.remove("data.csv")
        return response
    except Exception as nx:
        print("No response csv file generated here")
        logger.error(f"No response csv file generated here ",nx)

        
@mainlink.route("/exportexcel",methods=["GET","POST"])
def exportexcel():    
    import pandas as pd
    import os
    try :
        cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "Select * from csvtable ;"  
        cursor.execute(sql)
        datafile =cursor.fetchall()
    except Exception as nx:
        print("database connection issue in exportexcel file function")
        logger.error(f"database connection issue in exportexcel file function ",nx)
    datafm = pd.DataFrame(datafile)
    datafm.to_excel('data.xlsx', index=False)
    try :            
        response = make_response()
        response.data = open('data.xlsx', 'rb').read()
        response.headers['Content-Disposition'] = 'attachment; filename=data.xlsx'
        response.headers['Content-Type'] = 'text/ms-excel' 
        os.remove("data.xlsx")
        return response
    except Exception as nx:
        print("can not create excel file , please check here exportexcel() : ")
        logger.error(f"can not create excel file , please check here exportexcel() : ",nx)


@mainlink.route("/exportpdf",methods=["GET","POST"])
def exportpdf():    
    try :
        cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "select * from csvtable;"  
        cursor.execute(sql)
        datafile =cursor.fetchall() 
    except Exception as nx:
        print("database connection issue in exportpdf() ")
        logger.error(f"database connection issue in exportpdf() ",nx)    
    if datafile is None:
        flash("sorry no content available here ")    
    cursor.close()
    mysqldb.connection.commit()
    try :
        template = render_template("pdftemplate.html",data=datafile)
        print("in here ")
    except Exception as nx:
        print("can not render template successfully")
        logger.error(f"can not render template successfully ",nx)
    try :
        pdf = pdfkit.from_string(template ,False, configuration=config)
        print("in pdf")
    except Exception as nx:
        print("can not convert template to string in exportpdf() ")
        logger.error(f"can not convert template to string in exportpdf() ",nx)
    try :
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf' 
        response.headers['Content-Disposition'] = 'attachment; filename=data.pdf'
        return response
    except Exception as nx:
        print("can not create pdf file here exportpdf() ")
        logger.error(f"can not create pdf file here exportpdf() ",nx)

@mainlink.route("/paginationdata",methods=["GET","POST"])
def paginationdata():   
    try :
        cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
    except Exception as nx:
        print("Database connectivity issue here paginationdata ")
        logger.error(f"Database connectivity issue here paginationdata ",nx)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    cursor.execute('SELECT COUNT(*) FROM products')
    total_items = cursor.fetchone()['COUNT(*)']
    total_pages = int(total_items / per_page) + (total_items % per_page > 0)
    start_index = (page - 1) * per_page
    cursor.execute('SELECT * FROM products LIMIT %s, %s', (start_index, per_page))
    data = cursor.fetchall()
    cursor.close()
    mysqldb.connection.commit()
    return render_template("productpagination.html",data=data, current_page=page, total_pages=total_pages,)

 
@mainlink.route("/singledelete",methods=["GET","POST"])
def singledelete():
    try :
        cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
    except Exception as nx:
        print("database connectivity issue in singledelete():")
        logger.error(f"database connectivity issue in singledelete(): ",nx)
    cursor.execute('SELECT * FROM products ;')
    data = cursor.fetchall()    
    if request.method=="POST":
        product_id = request.form["user_id"]
        print("single data id get here",product_id)
        try :                
            sql = "delete from products where product_id = %s ;"  
            value = (product_id)
            cr = cursor.execute(sql,value)    
        except Exception as nx:
            print("some issue in singledelete() ")
            logger.error(f"some issue in singledelete(): ",nx)
        if cr :                        
            cursor.close()
            mysqldb.connection.commit()
            return redirect(url_for('mainlink.singledelete'))
    return render_template("singledelete.html",data=data)

    
@mainlink.route("/multipledelete",methods=["GET","POST"])
def multipledelete():    
    try :
        cursor =mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
    except Exception as nx:
        print("Connectivity issue here multipledelete() ")
        logger.error(f"Connectivity issue here multipledelete(): ",nx)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    try :
        cursor.execute('SELECT COUNT(*) FROM products')
        total_items = cursor.fetchone()['COUNT(*)']
    except Exception as ni :
        logger.error(f"products table content not found",ni)
        flash("Sorry no conetent found")
        return redirect(url_for('mainlink.home'))    
    total_pages = int(total_items / per_page) + (total_items % per_page > 0)
    start_index = (page - 1) * per_page
    cursor.execute('SELECT * FROM products LIMIT %s, %s', (start_index, per_page))
    data = cursor.fetchall()
    if request.method=="POST":
        product_id = request.form.getlist("multipledata")
        if len(product_id)==0:
            pass
        if len(product_id)==1 :
            try :
                cursor = mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "delete from products where product_id=%s ;" 
                value = (product_id,)
                cr = cursor.execute(sql,value)
                if cr :                    
                    cursor.close
                    mysqldb.connection.commit()
                    flash("single  data deleted successfully here")
                    return redirect(url_for('mainlink.multipledelete'))    
            except Exception as nx:
                logger.error(f"check the sql syntax in multipledelete : ",nx)       
        else :
            try :                
                cursor = mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "delete from products where product_id in %s;"
                value = (product_id,)
                cr = cursor.execute(sql,value)
            except Exception as nx:
                print("some issue is here ")
                logger.error(f"some issue is here ",nx)
            if cr :                    
                cursor.close
                mysqldb.connection.commit()
                flash("single  data deleted successfully here")
                return redirect(url_for('mainlink.multipledelete'))
    return render_template ("multidelete.html" ,data=data, current_page=page, total_pages=total_pages)
        




