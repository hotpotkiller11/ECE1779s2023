from flask import Flask
import mysql.connector
from FrontEnd.config import db_config

webapp = Flask(__name__)

db = mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   database=db_config['database'])

from FrontEnd import main