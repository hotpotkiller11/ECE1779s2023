
from werkzeug.serving import run_simple  # werkzeug development server
from werkzeug.middleware.dispatcher import DispatcherMiddleware
"""IMPORT FLASK INSTANCES FROM FOLDER Memcache AND FrontEnd"""
from BackEnd import webapp as back
from FrontEnd import webapp as front

"""MERGE TWO FLASK INSTANCES: MEMCAC
HE AND FRONTEDND"""
# 也就是说所有backend pages 是\mem开头的
app = DispatcherMiddleware(front, {
    '/back': back
})

if __name__ == "__main__":
    """THREADED = TRUE FOR TWO INSTANCE WORKING TOGETHER"""
    back.debug = True
    """front.debug = True"""
    """run_simple('0.0.0.0', 5000, app,
               use_reloader=False,
               use_debugger=True,
               use_evalex=False,
               threaded=True)"""
    back.run(host="127.0.0.1", port=5000)
    #   front.run(host="127.0.0.1", port=5001)


