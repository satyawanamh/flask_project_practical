from flask import Flask,jsonify,Blueprint,request
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_restful import Api,Resource,reqparse
import json
import jwt
from functools import wraps
from datetime import datetime ,timedelta
app =Flask(__name__)
app.secret_key = b"fjkdifieie34jdk439"

api =Api(app)

## mysql setup
app.config["MYSQL_DB"]="flasktutdb"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PASSWORD"]="Satya@123"

mysqldb =MySQL(app)

############ token generation 
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'token' in request.headers:
            token = request.headers['token']
        # return 401 if token is not passed
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401  
        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.secret_key)           
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        return  f(*args, **kwargs)
  
    return decorated


@app.route("/gen_token",methods=['GET',"POST"])
def generte_token():
    token = jwt.encode({"expire":str(datetime.now()+timedelta(minutes=6))},app.secret_key ,algorithm="HS256")
    return jsonify({"token":token})


try :
    import mysql.connector
    mysql =mysql.connector.connect(username="root",database="flasktutdb",password="Satya@123",host="localhost")
    cursor =mysql.cursor()
    sql = """create table if not exists Products (product_id int not null , Handle varchar(400), Title varchar(400), Body varchar(400),
      Vendor varchar(400), Type varchar(400), Tags varchar(400), Published varchar(400),
    VariantSKU varchar(400), VariantInventoryTracker varchar(400), VariantPrice varchar(400), ImageSrc varchar(400) , primary key (product_id));"""
    cursor.execute(sql)    
    mysql.close()
except Exception as exp :
    print("Can not create table exception occur")


class Products(Resource):
    try :
        def __init__(self):
            self.parser = reqparse.RequestParser()
            self.parser.add_argument("product_id",type=int , required=True)
            self.parser.add_argument("Handle",type=str , required=True)
            self.parser.add_argument("Title",type=str , required=True)
            self.parser.add_argument("Body",type=str , required=True)
            self.parser.add_argument("Vendor",type=str , required=True)
            self.parser.add_argument("Type",type=str , required=True)
            self.parser.add_argument("Tags",type=str , required=True)
            self.parser.add_argument("Published",type=str , required=True)
            self.parser.add_argument("VariantSKU",type=str , required=True)
            self.parser.add_argument("VariantInventoryTracker",type=str , required=True)
            self.parser.add_argument("VariantPrice",type=str , required=True)
            self.parser.add_argument("ImageSrc",type=str , required=True)
            self.mysql = mysqldb.connection 
    except Exception as nk:
        print(nk)

    try :
        def get(self):
            cursor =self.mysql.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("select * from Products;")
            allstudentdata =cursor.fetchall()
            #cursor.close()
            return jsonify({"data":allstudentdata})
    except Exception as nl:
        print(nl)       
    
    def post(self):
        args = self.parser.parse_args()        
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        sql="""insert into Products (product_id,Handle,Title,Body,Vendor,Type,Tags,Published,VariantSKU,VariantInventoryTracker,VariantPrice,ImageSrc)
          values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        value = (args["product_id"],args["Handle"],args["Title"],args["Body"],args["Vendor"],args["Type"],args["Tags"],args["Published"],args["VariantSKU"],args["VariantInventoryTracker"],args["VariantPrice"],args["ImageSrc"])
        cursor.execute(sql,value)
        self.mysql.commit()
        cursor.close()        
        return {"status":"success"}


class ProductsDetailsApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("product_id",type=int , required=True)
        self.parser.add_argument("Handle",type=str , required=True)
        self.parser.add_argument("Title",type=str , required=True)
        self.parser.add_argument("Body",type=str , required=True)
        self.parser.add_argument("Vendor",type=str , required=True)
        self.parser.add_argument("Type",type=str , required=True)
        self.parser.add_argument("Tags",type=str , required=True)
        self.parser.add_argument("Published",type=str , required=True)
        self.parser.add_argument("VariantSKU",type=str , required=True)
        self.parser.add_argument("VariantInventoryTracker",type=str , required=True)
        self.parser.add_argument("VariantPrice",type=str , required=True)
        self.parser.add_argument("ImageSrc",type=str , required=True)
        self.mysql = mysqldb.connection

    def get(self,product_id):        
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        args = self.parser.parse_args()
        cursor.execute("select * from Products where product_id=%s;",(product_id,))
        alldata =cursor.fetchone()     
        
        if cursor.rowcount==0:
            return f"No record found on this particular id "
        return {"data": alldata},200
    
    def put(self,product_id):
        args = self.parser.parse_args()
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        sql=" update  Products set Handle=%s,Title=%s,Body=%s,Vendor=%s,Type=%s,Tags=%s,Published=%s,VariantSKU=%s,VariantInventoryTracker=%s,VariantPrice=%s,ImageSrc=%s where product_id=%s"
        value = (args["Handle"],args["Title"],args["Body"],args["Vendor"],args["Type"],args["Tags"],args["Published"],args["VariantSKU"],args["VariantInventoryTracker"],args["VariantPrice"],args["ImageSrc"],args["product_id"])
        cursor.execute(sql,value)
        alldata =cursor.fetchone()
        if cursor.rowcount==0:
            return "Sorry , no data inserted successfully"      
        self.mysql.commit()       
        return json.dumps(alldata),f"data successfully inserted {200}"
    
    def delete(self,product_id):        
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("delete from Products where product_id=%s;",(product_id,))
        self.mysql.commit()
             
        if cursor.rowcount==0:
            cursor.close() 
            return {"status":"No record found here"}
        else :                              
            cursor.close()
            return "deleted successfully"       


#this is class baesd 
api.add_resource(Products,"/products")
api.add_resource(ProductsDetailsApi,"/products/<int:product_id>")


if __name__=="__main__":
    app.run(debug=True)
