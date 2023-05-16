from flask import Blueprint,jsonify
from flask_restful import Api,Resource,reqparse

import MySQLdb.cursors
import json
from flask import Flask,jsonify,Blueprint
from flask_mysqldb import MySQL
import MySQLdb.cursors
from flask_restful import Api,Resource,reqparse
import json

app =Flask(__name__)
api =Api(app)

## mysql setup
app.config["MYSQL_DB"]="flasktutdb"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PASSWORD"]="Satya@123"

mysqldb =MySQL(app)

class Productsfile(Resource):
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
    
    

class ProductsApi(Resource):
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
        #self.mysql.close()
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


products_blueprint = Blueprint("products_blueprint",__name__,url_prefix="/productsApi")

Product_get_post=Productsfile.as_view("Product_get_post")
product_get_with_delete = ProductsApi.as_view("product_get_with_delete")
products_blueprint.add_url_rule("/pr",view_func= Product_get_post)
products_blueprint.add_url_rule("/pr/<int:product_id>",view_func=Product_get_post)

app.register_blueprint(products_blueprint)

if __name__=="__main__":
    app.run(debug=True)