from flask import Flask
import mysql.connector
from FrontEnd.config import db_config

webapp = Flask(__name__)

from FrontEnd import main, apis, stat
