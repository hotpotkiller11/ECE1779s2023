from flask import render_template
from FrontEnd import webapp, db

def get_path_by_key(key: str) -> str:
    ''' Return the path of the indexed key from the database.
        If no valid term match, return None.
    '''
    query = 'SELECT `path` FROM `key_picture` WHERE `key` = "%s"' % key # instantiate query statement
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        return None
    return result[0][0]

def add_key_and_path(key: str, path: str) -> bool:
    ''' Record the key and path into the database.
        Return if the key and path stored successfully.
    '''
    query = 'INSERT INTO `key_picture` (`key`, `path`) VALUES ("%s", "%s");' % (key, path) # instantiate query statement
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit() # Try to commit (confirm) the insertion
        cursor.close()
    except:
        db.rollback() # Try to rollback in case of error
        cursor.close()
        return False
    return True

@webapp.teardown_appcontext
def teardown_db(exception):
    db.close()

@webapp.route('/')
def home():
    print("to home")
    return render_template("home.html")

"""msg pages"""
@webapp.route('/success')
def success():
    # msg = request.args.get('msg')
    # return render_template("success.html", msg=msg)
    return render_template("success.html")

@webapp.route('/failure')
def failure():
    """msg = request.args.get('msg')
    return render_template("failure.html", msg=msg)"""
    return render_template("error.html")

@webapp.route('/Function1', methods=['GET'])
def Function1():
    print("do sth1")
    return "do sth"

@webapp.route('/Function2', methods=['GET'])
def Function2():
    print("do shit2")
    return "do shit2"

@webapp.route('/Function3', methods=['GET'])
def Function3():
    print("do shit3")
    return "do shit3"

@webapp.route('/Function4', methods=['GET'])
def Function4():
    print("do shit4")
    return "do shit4"

@webapp.route('/Function5', methods=['GET'])
def Function5():
    print("do shit5")
    return "do shit5"

print(get_path_by_key('a'))
print(add_key_and_path('d', 'ddd'))

