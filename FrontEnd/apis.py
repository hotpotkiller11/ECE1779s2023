from flask import render_template, request, json
from FrontEnd import webapp, key_path, db_connect, backend
from FrontEnd.key_path import get_path_by_key
from FrontEnd.config import IMAGE_FORMAT 
from FrontEnd.db_connect import get_db
import base64
import os
import requests

@webapp.route('/api/delete_all', methods=['POST'])
def delete_all():
    result = key_path.delete_all_key_path_term()
    result2 = deleteFile("")
    res = requests.get(backend + '/clear') # get keys list
    if res.status_code != 200: print("memcache deletion failed")
    if result and result2 == True:
        # also call memcache to remove all cache terms
        data = {
            "success": "true",
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json',
        )
        return response
    elif result == False:
        data = {
            "success": "false",
            "error": {
                "code": 404,
                "message": "database issues",
            }
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json',
        )
        return response
    else:
        data = {
            "success": "false",
            "error": {
                "code": 404,
                "message": "local file system issues",
            }
        }
        response = webapp.response_class(
            response=json.dumps(data),
            status=404,
            mimetype='application/json',
        )
        return response

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


@webapp.route('/api/upload', methods = ['GET','POST'])
# returns the upload page
def upload():
    if request.method == 'POST':
        key = request.form.get('key')
        # process the upload image request and add the image to the database
        status = process_figure(request, key)
        if status == 'SUCCESS':
            data = {
                "success": "true",
                "key": [key]
            }
            response = webapp.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json',
            )
            return response
        elif status == 'UNSUCCESS':
            data = {
                "success": "false",
                "error": {
                    "code": 404,
                    "message": "Exception happend"
                    },
            }
            response = webapp.response_class(
                response=json.dumps(data),
                status=404,
                mimetype='application/json',
            )
            return response
        else:
            data = {
                "success": "flase",
                "error": {
                    "code": 404,
                    "message": "Invalid file type"
                    },
            }
            response = webapp.response_class(
                response=json.dumps(data),
                status=404,
                mimetype='application/json',
            )
            return response
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
                    request_json = {'key':key}
                    res = requests.get(backend + '/invalidatekey', json = request_json) # get keys list
                    if (res.status_code != 200):
                        print("memcache object deletion failed.")
                    return 'SUCCESS'
        except Exception as e:
            print(e)
            return 'UNSUCCESS'
    return 'INVALID'

@webapp.route('/api/list_keys', methods=['POST'])
def list_keys():
    keys = key_path.get_all_keys()
    data = {
                "success": "true",
                "keys": keys
            }
    response = webapp.response_class(
                response=json.dumps(data),
                status=200,
                mimetype='application/json',
            )
    return response

@webapp.route('/api/key/<key_value>',methods=['GET','POST'])
def show_figure_by_key(key_value):
    if request.method == 'POST':
        key = key_value
        print(key)
        request_json = {'key':key}
        res = requests.post(backend + '/get', json = request_json)
        # print(res)
        if res.json() == 'MISS':
            filename = get_path_by_key(key)
            if filename is None:
                data = {
                        "success": "false",
                        "error": {
                        "code": "404",
                        "message":"No such file"
                        }
                }
                response = webapp.response_class(
                    response=json.dumps(data),
                    status=404,
                    mimetype='application/json',
                )
                return response
            else:
                base64_figure = convertToBase64(filename)
                request_json = {'key':key, 'value':base64_figure}
                res = requests.post(backend + '/put',json = request_json)
                print(res.json())               
                #return render_template('show_figure.html',exist = True, figure = base64_figure)
                data = {
                    "success": "true",
                    "key": [key],
                    "content": base64_figure
                }
                response = webapp.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json',
                )
                return response
        else:
            pic = res.json()["content"]
            data = {
                    "success": "true",
                    "key": key,
                    "content": pic
                }
            response = webapp.response_class(
                    response=json.dumps(data),
                    status=200,
                    mimetype='application/json',
                )
            return response
    else:
        response = webapp.response_class(
            response=json.dumps("use POST"),
            status=405,
            mimetype='application/json',
        )
        return response

def convertToBase64(filename):
    with open(os.path.dirname(os.path.abspath(__file__)) + '/static/figure/'+filename,'rb') as figure:
        #encode the original binary code to b64 code
        base64_figure=base64.b64encode(figure.read())
    #decode the b64 byte code in utf-8 format
    base64_figure = base64_figure.decode('utf-8')
    return base64_figure