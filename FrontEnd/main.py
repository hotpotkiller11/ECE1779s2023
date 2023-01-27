from flask import render_template, request
from FrontEnd import webapp, db
import os

def get_all_keys() -> list[str]:
    ''' Return all keys stored in the database
        If the table is currently empty, an empty list will be returned.
    '''
    query = 'SELECT `path` FROM `key_picture`' # instantiate query statement
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    result_list = []
    for s in result:
        result_list.append(s[0])
    return result_list

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

def delete_term_by_key(key: str) -> bool:
    ''' Delete a term with a specified key in the database.
        Return true if the deletion succeed.
    '''
    query = 'DELETE FROM `key_picture` WHERE `key` = "%s"' % (key) # instantiate query statement
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

def delete_all_key_path_term() -> bool:
    ''' Delete all terms in the key_picture table.
        Return true if the deletion succeed. 
        (If the table was initially empty, true will also returned)
    '''
    query = 'DELETE FROM `key_picture`' # instantiate query statement
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

@webapp.route('/upload_figure', methods = ['GET','POST'])
# returns the upload page
def upload_figure():
    if request.method == 'POST':
        key = request.form.get('key')
        # process the upload image request and add the image to the database
        status = process_figure(request, key)
        return render_template('upload_figure.html', status=status)
    return render_template('upload_figure.html')

def process_figure(request, key):
    # get the figure file
    file = request.files['file']
    _, extension = os.path.splitext(file.filename)
    print(extension)
    # if the figure is one of the allowed extensions
    if extension.lower() in {'.png', '.jpg', '.jpeg', '.gif'}:
        filename = key + extension
        # save the figure in the local file system
        file.save(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/static/figure', filename))
        print(filename)
        return 'SUCCESS'
    return 'INVALID'

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

"""The function used to store file in to static"""
def saveDataToFile(filename:str, input:bytes):
    filepath = "./FrontEnd/static/figure/"+filename
    print(filepath)
    try:
        with open(filepath, "wb") as f:
            #print("open success")
            f.write(input)
            f.close()
        return "save success"
    except Exception as e:
        return "save unsuccess"

#print(saveDataToFile('hello.txt','11111'))

def getDataFromFile(filename:str)->bytes:
    """The function used to read a file in to static index by its filename, if no such file, return None"""
    filepath = "./FrontEnd/static/figure/"+filename
    try:
        f = open(filepath, 'rb')
        output = (f.read())
        f.close()
        return output
    except Exception as e:
        return None

#print(getDataFromFile('hel.txt'))

def listFileDictionary(dicname:str)->list[str]:
    """This function return the list of files in a specific dictionary name"""
    filepath = "./FrontEnd/static/"+dicname
    return os.listdir(filepath)
    
#print(listFileDictionary('static'))
#print(getDataFromFile('testfig.jpg'))
#print(saveDataToFile('testfig2.jpg',getDataFromFile('testfig.jpg')))


def deleteFile(filename:str)->bool:
    '''This function is used to delete all data in a specific document under static'''
    filepath = "./FrontEnd/static/"+filename
    try:
        del_list = os.listdir(filepath)
        print(del_list)
        for f in del_list:
            file_path = os.path.join(filepath, f)
            if os.path.isfile(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        return False
#print(deleteFile('figure'))

