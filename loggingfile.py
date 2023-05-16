import logging
import os
from datetime import datetime 
from logging.handlers import TimedRotatingFileHandler

dd=datetime.today()
today_date = f"{dd.day}-{dd.month}-{dd.year}"
BASE_DIR =os.getcwd()
log_dir = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

handler = TimedRotatingFileHandler(os.path.join(log_dir, f'{today_date}error.log'), when='midnight', backupCount=7  )
handler.setLevel(logging.ERROR)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

# Add the handler to the logger

handler1 = TimedRotatingFileHandler(os.path.join(log_dir, f'{today_date}debug.log'), when='midnight', backupCount=7  )
handler1.setLevel(logging.DEBUG)
handler1.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

# Add the handler to the logger

handler2 = TimedRotatingFileHandler(os.path.join(log_dir, f'{today_date}info.log'), when='midnight', backupCount=7  )
handler2.setLevel(logging.INFO)
handler2.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

# Add the handler to the logger
logger = logging.getLogger()
logger.addHandler(handler1)#debug
logger.addHandler(handler2)#info
logger.addHandler(handler)#error
