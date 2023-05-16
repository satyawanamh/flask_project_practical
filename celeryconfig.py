##########
#celery setup configuration in flask

import os
from celery import Celery
from flask import Flask
from flask_mysqldb import MySQL
from celery.schedules import crontab
from flask_mail import Mail,Message
from datetime import timedelta
from celery import shared_task
import MySQLdb.cursors



app = Flask(__name__)

#app.secret_key=b"hdhjhjsdhbhu887452nb"


## mysql setup
app.config["MYSQL_DB"]="flasktutdb"
app.config["MYSQL_USER"]="root"
app.config["MYSQL_HOST"]="localhost"
app.config["MYSQL_PASSWORD"]="Satya@123"
# app.config["MYSQL_PORT"]=3306

mysqldb =MySQL(app)

#######email setup in flask
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'satyawan@simprosys.com'
app.config['MAIL_PASSWORD'] = 'xlksenwivdnmcclg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_TIMEZONE'] = 'Asia/Kolkata'
def make_celery(app):
    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL']
                    
                    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    ## declare calling class
    class ContextTask(TaskBase):
        abstract = True

        def __call__(self,*args,**kwargs):
            with app.app_context():
                return TaskBase.__call__(self,*args,**kwargs)
            
    celery.Task = ContextTask
    return celery

celery = make_celery(app)


@shared_task()
def send_email_all_user():
    #token=str(uuid.uuid4)
    print("in running task here -----------------------")
    cursor = mysqldb.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = "Select email from usertable ;"
    cursor.execute(sql)
    alldata =cursor.fetchall()
    cursor.close()
    for senddata in alldata :
        print("user email here --------------------")
        msg=Message("User registration message",sender="satyawan@simprosys.com",recipients=[senddata["email"]])
        msg.body = "Thank you for registration on this Flask tutorial portal"
        mail.send(msg)        
    return True

CELERY_IMPORTS = ["app.tasks"]
CELERY_TASK_RESULT_EXPIRES = 3
CELERY_TIMEZONE = 'UTC'

# CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
# CELERY_TASK_SERIALIZER = 'json'
# CELERY_RESULT_SERIALIZER = 'json'

CELERY_IMPORTS = ["app.tasks"]
CELERY_BROKER_URL =  'redis://localhost:6379/0'
CELERY_RESULT_BACKEND =  'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

celery.conf["CELERYBEAT_SCHEDULE"] = {
    'add-every-30-seconds': {
        'task': 'celeryconfig.send_email_all_user',
        'schedule': crontab(minute='*/1')
        
    },
}



if __name__=="__main__":
    celery.conf.timezone = 'Asia/Kolkata'
    with app.app_context():
        celery.conf.update(app.config)
    app.run(debug=True)
            
