from MemCache import webapp
import sys

if (len(sys.argv) != 2): 
    print("Please identify port number")
    sys.exit(1)
port = int(sys.argv[1])
webapp.run('0.0.0.0', port, debug=False)