from werkzeug.serving import run_simple  # werkzeug development server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
"""IMPORT FLASK INSTANCES FROM FOLDER Memcache AND FrontEnd"""
from FrontEnd import webapp as front
from Controller import webapp as controller


app = DispatcherMiddleware(front, {
    '/controller': controller
})

if __name__ == "__main__":
    """THREADED = TRUE FOR TWO INSTANCE WORKING TOGETHER"""
    # back.debug = True
    # front.debug = True
    run_simple('0.0.0.0', 5001, app,# required to run at 5000
               use_reloader=False,
               use_debugger=False,
               use_evalex=False,
               threaded=True)
