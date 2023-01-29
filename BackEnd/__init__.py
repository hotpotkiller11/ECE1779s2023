from flask import Flask

webapp = Flask(__name__)

from BackEnd import main

main.Config = {'capacity': 400, 'policy': "random"}
main.filesize = 0
main.miss = 0
main.hit = 0
main.numOfreq = 0