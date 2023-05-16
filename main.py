from flask import Flask
from flask_mysqldb import MySQL
from linkblueprint import mainlink

from linkblueprint import app


app.register_blueprint(mainlink)

if __name__=="__main__":
    app.run(debug=True)

    