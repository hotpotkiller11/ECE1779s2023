from flask import Flask
import mysql.connector
from ManagerApp.config import db_config

webapp = Flask(__name__)
backend = "http://127.0.0.1:5000/controller"

from ManagerApp import main, stat