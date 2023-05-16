from flask import Flask,Response,redirect,render_template,flash

from views import blueprint_data
from settings import app

app.register_blueprint(blueprint_data)

if __name__=="__main__":
    app.run(debug=True)
