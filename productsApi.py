from flask_restful import Api,Resource,reqparse

import MySQLdb.cursors
import json
from blueprintsflask import products_blueprint
from flaskapi import app,mysqldb

products_blueprint.route("/products")
class Products(Resource):
    try :
        def __init__(self):
            self.parser = reqparse.RequestParser()
            self.parser.add_argument("product_id",type=str , required=True)
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
            cursor = self.mysql.cursor()
            cursor.execute("select * from Products")
            if cursor.rowcount==0:
                return "sorry no data available in database"
            else :
                allstudentdata =cursor.fetchall()
                print(allstudentdata)
                #cursor.close()
                # if allstudentdata :
                #     return {"status":"success","data":allstudentdata},200   
                return allstudentdata 
                #return json.dumps(allstudentdata)
    except Exception as nl:
        print(nl)


       
    
    def post(self):
        args = self.parser.parse_args
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        sql="""insert into Products (product_id,Handle,Title,Body,Vendor,Type,Tags,Published,VariantSKU,VariantInventoryTracker,VariantPrice,ImageSrc)
          values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
        value = (args["product_id"],args["Handle"],args["Title"],args["Body"],args["Vender"],args["Type"],args["Tags"],args["Published"],
                 args["VariantSKU"],args["VariantInventoryTracker"],args["VariantPrice"],args["ImageSrc"])
        cursor.execute(sql,value)
        alldata =cursor.fetchone()
        self.mysql.commit()
        cursor.close()
        
        return {"status":"success","data":alldata}
    
    
@products_blueprint.route("/products/<int:product_id>")
class ProductsDetailsApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("product_id",type=str , required=True)
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
        cursor.execute("select * from Products where product_id=%s;",product_id)
        alldata =cursor.fetchone()        
        cursor.commit()
        if cursor.rowcount==0:
            return f"No record found on this particular id "
        self.mysql.close()
        return json.dumps(alldata),200
    
    def put(self,product_id):
        args = self.parser.parse_args
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        sql=""" update into Products set product_id=%s,Handle=%s,Title=%s,Body=%s,Vendor=%s,Type=%s,Tags=%s,Published=%s,VariantSKU=%s,VariantInventoryTracker=%s,
        VariantPrice=%s,ImageSrc=%s);"""
        value = (product_id,args["Handle"],args["Title"],args["Body"],args["Vender"],args["Type"],args["Tags"],args["Published"],
                 args["VariantSKU"],args["VariantInventoryTracker"],args["VariantPrice"],args["ImageSrc"])
        cursor.execute(sql,value)
        alldata =cursor.fetchone()
        if cursor.rowcount==0:
            return "Sorry , no data inserted successfully"
        cursor.commit()
        self.mysql.commit()
        self.mysql.close()
        
        return json.dumps(alldata),f"data successfully inserted {200}"
    
    def delete(self,product_id):
        
        cursor = self.mysql.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("delete from Products where product_id=%s;",product_id)
             
        cursor.commit()
        if cursor.rowcount==0:
            return f"No record found on this particular id "
        self.mysql.close()
        return f" data successfully deleted here {200}"

