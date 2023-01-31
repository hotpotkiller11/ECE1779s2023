from werkzeug.serving import run_simple  # werkzeug development server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
"""IMPORT FLASK INSTANCES FROM FOLDER Memcache AND FrontEnd"""
from BackEnd import webapp as back
from FrontEnd import webapp as front

"""MERGE TWO FLASK INSTANCES: MEMCACHE AND FRONTEND"""

app = DispatcherMiddleware(front, {
    '/back': back
})

if __name__ == "__main__":
    """THREADED = TRUE FOR TWO INSTANCE WORKING TOGETHER"""
    back.debug = True
    front.debug = True
    run_simple('0.0.0.0', 5001, app,
               use_reloader=False,
               use_debugger=False,
               use_evalex=False,
               threaded=True)
    # back.run(host="127.0.0.1", port=5000)
    # front.run(host="127.0.0.1", port=5001)


