from flask import Flask
import mysql.connector
from FrontEnd.config import db_config

webapp = Flask(__name__)
backend = "http://127.0.0.1:5000/back"

from FrontEnd import main, apis, stat
