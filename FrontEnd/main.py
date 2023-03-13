from flask import render_template, request
from FrontEnd import webapp, key_path, db_connect, backend
from FrontEnd.key_path import get_path_by_key
from config import IMAGE_FORMAT
from botocore.config import Config
import base64
import os
import requests
import boto3

config = Config(
    region_name = 'us-east-1',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)
s3 = boto3.client('s3',config=config)
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
    """
    list all keys
    :return:  keys.html
    """
    keys = key_path.get_all_keys()
    n = len(keys)
    return render_template("keys.html", keys = keys, n = n)

@webapp.route('/keys/delete', methods=['GET'])
def all_key_delete():
    """
    clean up all key
    :return: error or success info html
    """
    result = key_path.delete_all_key_path_term()
    result2 = clear_figure_S3()
    res = requests.get(backend + '/clear') # get keys list
    if res.status_code != 200: print("memcache deletion failed")
    if result and result2 == True:
        # also call memcache to remove all cache terms
        return render_template("success.html", msg = "All keys deleted.")
    elif result == False:
        return render_template("error.html", msg = "Deletion failed, database issues!")
    else:
        return render_template("error.html", msg = "Deletion failed, local file system issues!")

@webapp.route('/upload_figure', methods = ['GET','POST'])
# returns the upload page
def upload_figure():
    """
    uploda figure to system
    :return: upload figure html page
    """

    if request.method == 'POST':
        key = request.form.get('key')
        # process the upload image request and add the image to the database
        status = process_figure(request, key)
        return render_template('upload_figure.html', status=status)
    return render_template('upload_figure.html')

def process_figure(request, key):
    """
    :param request: the request info
    :param key: the given key
    :return: success message
    """

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
                #file.save(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/static/figure', filename))
                base64_image = base64.b64encode(file.read())
                s3.put_object(Body=base64_image, Key=filename, Bucket='ece1779-ass2-bucket2', ContentType='image')
                key_path.add_key_and_path(key, filename)
                return 'SUCCESS'
            else:
                if key_path.delete_term_by_key(key):
                    # if deleteFile(original):
                    #     print("File replaced: %s" % original)
                    # file.save(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/static/figure', filename))
                    s3.delete_object (Bucket= 'ece1779-ass2-bucket2', Key=original)
                    base64_image = base64.b64encode(file.read())
                    s3.put_object(Body=base64_image, Key=filename, Bucket='ece1779-ass2-bucket2', ContentType='image')
                    key_path.add_key_and_path(key, filename)
                    request_json = {'key':key}
                    res = requests.get(backend + '/invalidatekey', json = request_json) # get keys list
                    if (res.status_code != 200):
                        print("memcache object deletion failed.")
                    return 'SUCCESS'
        except Exception as e:
            print(e)
            return 'UNSUCCESS'
    return 'INVALID'

@webapp.route('/show_figure',methods=['GET','POST'])
def show_figure():
    """
    show thenfigure by given key
    :return: show_figure.html
    """

    if request.method == 'POST':
        key = request.form.get('key')
        request_json = {'key':key}
        res = requests.post(backend + '/get', json = request_json)
        if res.json() == 'MISS':
            filename = get_path_by_key(key)
            if filename is None:
                return render_template('show_figure.html',exist = False, figure = 'No figure relate to this key!')
            else:
                #base64_figure = convertToBase64(filename)
                base64_figure = download_image(filename)
                request_json = {'key':key, 'value':base64_figure}
                res = requests.post(backend + '/put',json = request_json)
                print(res.json())               
                return render_template('show_figure.html',exist = True, figure = base64_figure)
        else:
            pic = res.json()["content"]
            return render_template('show_figure.html',exist = True, figure = pic)
    else:
        return render_template('show_figure.html')

def download_image(key):
    """
    download image according to key
    :param key: key entered
    :return: image content
    """

    try: 
        with open('Temp.txt', 'wb') as file:
            s3.download_fileobj('ece1779-ass2-bucket2', key, file)
        with open('Temp.txt', 'rb') as file:
            base64_image = file.read().decode('utf-8')
        file.close()
        os.remove("Temp.txt")
        return base64_image
    except:
        return 'Image Not Found in S3'

def convertToBase64(filename):
    """
    :param filename: the file's name and path
    :return: base64 figure content
    """
    with open(os.path.dirname(os.path.abspath(__file__)) + '/static/figure/'+filename,'rb') as figure:
        #encode the original binary code to b64 code
        base64_figure=base64.b64encode(figure.read())
    # decode the b64 byte code in utf-8 format
    base64_figure = base64_figure.decode('utf-8')
    return base64_figure

@webapp.errorhandler(404)
# returns the 404 page
def page_not_found(e):
    """
    handel 404 info page
    :param e: exception
    :return: 404.html
    """
    return render_template('404.html')

def clear_figure_S3():
    """
    clear all images in S3 bucket
    :return: bool
    """
    s3_clear = boto3.resource('s3',config=config)
    bucket = s3_clear.Bucket('ece1779-ass2-bucket2')
    bucket.objects.all().delete()
    return True

    


def save_conf_todb(capacity:float, policy:str):
    """_summary_

    Args:
        capacity (float): 
        policy (str): LRU/Random

    Raises:
        Exception: Database insertion failed
        Exception: Memcache update failed

    Returns:
        _type_: true/exception
    """
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
        raise Exception("Database insertion failed")
    res = requests.get(backend + '/refresh') # get keys list
    if (res.status_code == 200):
        return True
    else:
        raise Exception("Memcache update failed: error %d" % (res.status_code))