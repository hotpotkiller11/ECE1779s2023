from flask import Flask

webapp = Flask(__name__)

from BackEnd import main

main.Config = {'capacity': 400, 'policy': "random"}
