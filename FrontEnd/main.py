from flask import render_template, request, json
from FrontEnd import webapp, key_path, db_connect
from FrontEnd.key_path import get_path_by_key
from FrontEnd.config import IMAGE_FORMAT 
from FrontEnd.db_connect import get_db
import base64
import os
import requests

@webapp.route('/')
def home():
    print("to home")
    return render_template("home.html")

# msg pages
@webapp.route('/success')
def success():
    # msg = request.args.get('msg')
    # return render_template("success.html", msg=msg)
    return render_template("success.html")

@webapp.route('/failure')
def failure():
    # msg = request.args.get('msg')
    # return render_template("failure.html", msg=msg)
    return render_template("error.html")

# favicon

@webapp.route('/favicon.ico')
def favicon():
    return webapp.send_static_file('favicon.ico')

# function 1: show all keys

@webapp.route('/keys', methods=['GET'])
def all_key():
    keys = key_path.get_all_keys()
    n = len(keys)
    return render_template("keys.html", keys = keys, n = n)

@webapp.route('/keys/delete', methods=['GET'])
def all_key_delete():
    result = key_path.delete_all_key_path_term()
    result2 = deleteFile("")
    if result and result2 == True:
        # also call memcache to remove all cache terms
        return render_template("success.html", msg = "All keys deleted.")
    else:
        return render_template("error.html", msg = "Deletion failed.")

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
    # print(extension)
    # if the figure is one of the allowed extensions
    if extension.lower() in IMAGE_FORMAT:
        filename = key + extension
        original = key_path.get_path_by_key(key)
        # save the figure in the local file system
        try:
            if original is None:
                file.save(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/static/figure', filename))
                key_path.add_key_and_path(key, filename)
                return 'SUCCESS'
            else:
                if key_path.delete_term_by_key(key):
                    if deleteFile(original):
                        print("File replaced: %s" % original)
                    file.save(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/static/figure', filename))
                    key_path.add_key_and_path(key, filename)
                    return 'SUCCESS'
        except Exception as e:
            print(e)
            return 'UNSUCCESS'
    return 'INVALID'

@webapp.route('/show_figure',methods=['GET','POST'])
def show_figure():
    if request.method == 'POST':
        key = request.form.get('key')
        request_json = {'key':key}
        res = requests.post('127.0.0.1/back'+'/get',json = request_json)
        if json.load(res) == 'MISS':
            filename = get_path_by_key(key)
            if filename is None:
                return render_template('show_figure.html',exist = False, figure = 'No figure relate to this key!')
            else:
                base64_figure = convertToBase64(filename)
                return render_template('show_figure.html',exist = True, figure = base64_figure)
        else:
            return render_template('show_figure.html',exist = True, figure = json.load(res))
    else:
        return render_template('show_figure.html')

def convertToBase64(filename):
    with open(os.path.dirname(os.path.abspath(__file__)) + '/static/figure/'+filename,'rb') as figure:
        #encode the original binary code to b64 code
        base64_figure=base64.b64encode(figure.read())
    #decode the b64 byte code in utf-8 format
    base64_figure = base64_figure.decode('utf-8')
    return base64_figure


@webapp.route('/Function2', methods=['GET'])
def Function2():
    print("do shit2")
    return "do shit2"

@webapp.route('/Function3', methods=['GET'])
def Function3():
    print("do shit3")
    return "do shit3"

@webapp.route('/memory', methods=['GET'])
def memory_inspect():
    res = requests.get('http://127.0.0.1:5001/back/keys') # get keys list
    if (res.status_code == 200):
        keys = res.json()['keys']
        n = len(keys)
        size = res.json()['size']
    else:
        return render_template("error.html", msg = "Cannot connect to the memcache server.")
    try:
        db = get_db()
        query = '''SELECT capacity, policy
                        FROM backend_config where id = (
            select max(id) FROM backend_config);'''
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        capacity = rows[0][0]
        policy = rows[0][1]
    except Exception as e:
        print(e)
        return render_template("error.html", msg = "Cannot connect to the memcache server.")
    return render_template("memory.html", keys = keys, n = n, size = size,
        capacity = capacity, policy = policy)

    

@webapp.route('/memory/clear')
def mem_key_delete():
    res = requests.get('http://127.0.0.1:5001/back/clear') # get keys list
    if (res.status_code == 200):
        return render_template("success.html", msg = "Cache deleted.")
    else:
        return render_template("error.html", msg = "Cache clear failed: error %d" % res.status_code)

@webapp.route('/memory/set', methods=['POST'])
def mem_config_set():
    capacity = float(request.form.get('capacity'))
    unit = request.form.get('unit')
    if unit == "KB": capacity *= 1024
    elif unit == "MB": capacity *= 1024 * 1024
    policy = request.form.get('policy')
    db = db_connect.get_db()
    query = 'INSERT INTO `backend_config` (`capacity`, `policy`) VALUES (%d, "%s")' % (capacity, policy)
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit() # Try to commit (confirm) the insertion
        cursor.close()
        # db.close()
    except:
        db.rollback() # Try to rollback in case of error
        cursor.close()
        # db.close()
        return render_template('error.html', msg = "Database insertion failed")
    res = requests.get('http://127.0.0.1:5001/back/refresh') # get keys list
    if (res.status_code == 200):
        return render_template("success.html", msg = "Configuration updated")
    else:
        return render_template("error.html", msg = "Memcache update failed: error %d" % res.status_code)

@webapp.route('/Function5', methods=['GET'])
def Function5():
    print("do shit5")
    return "do shit5"

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
        return "save unsuccess (%s)"

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
        print(e)
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
    filepath = "./FrontEnd/static/figure/"+filename
    print(filepath)
    try:
        if os.path.isdir(filepath):
            print(os.path.isdir(filepath))
            del_list = os.listdir(filepath)
            print(del_list)
            for f in del_list:
                file_path = os.path.join(filepath, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            return True
        else:
            os.remove(filepath)
            print("remove is done")
            return True
    except Exception as e:
        print(e)
        return False
#print(os.remove("./FrontEnd/static/figure/"+"123.jpg"))
print(os.path.isdir("./FrontEnd/static/figure/"+"123.jpg"))

