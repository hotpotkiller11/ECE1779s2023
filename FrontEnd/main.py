from flask import render_template
from FrontEnd import webapp, db
import os
def get_path_by_key(key: str) -> str:
    query = 'SELECT path FROM key_picture WHERE key_picture.key = "' + key + '"'
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        return ""
    return result[0][0]

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

"""The function used to store file in to static"""
def saveDataToFile(filename:str, input:str):
    filepath = "./FrontEnd/static/"+filename
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
"""The function used to read a file in to static index by its filename, if no such file, return None"""
def getDataFromFile(filename:str):
    filepath = "./FrontEnd/static/"+filename
    try:
        f = open(filepath, 'rb')
        output = (f.read())
        f.close()
        return output
    except Exception as e:
        return None

#print(getDataFromFile('hel.txt'))
"""This function return the list of files in a specific dictionary name"""
def listFileDictionary(dicname:str):
    filepath = "./FrontEnd/"+dicname
    return os.listdir(filepath)
    
#print(listFileDictionary('static'))
#print(getDataFromFile('testfig.jpg'))
#print(saveDataToFile('testfig2.jpg',getDataFromFile('testfig.jpg')))
