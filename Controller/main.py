
from flask import  request, Response
from Controller import webapp, control
import json
import requests

def forward_response(res: Response) -> Response:
    """ Get a new response that ready to be returned from another response

    Args:
        res (Response): The response from a request that to be forwarded

    Returns:
        Response: The ne response that ready to be returned
    """
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [
        (k,v) for k,v in res.raw.headers.items()
        if k.lower() not in excluded_headers
    ]
    return Response(res.content, res.status_code, headers)

@webapp.route('/put', methods=['POST', 'GET'])
def PUT():
    key = request.json["key"]
    node = control.get_node(key)
    res = requests.post(node + "/put", json = request.json)
    return forward_response(res)
    

@webapp.route('/get', methods=['POST', 'GET'])
def GET():
    key = request.json["key"]
    node = control.get_node(key)
    res = requests.post(node + "/get", json = request.json)
    return forward_response(res)

@webapp.route('/invalidatekey', methods=['POST', 'GET'])
def INVALIDATE():
    key = request.json["key"]
    node = control.get_node(key)
    res = requests.post(node + "/invalidatekey", json = request.json)
    return forward_response(res)

@webapp.route('/clear',methods=['POST', 'GET'])
def CLEAR():
    # clear all activated nodes
    nodes = control.activated_nodes()
    for node in nodes:
        requests.post(node + "/clear")
    # no matter what, return a valid feedback
    response = webapp.response_class(
        response=json.dumps('ok'),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/refresh',methods= ['POST' , 'GET'])
def REFRESH():
    nodes = control.activated_nodes()
    for node in nodes:
        requests.post(node + "/refresh")
    
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/keys',methods=['GET', 'POST'])
def keys():
    result = []
    active_nodes = control.activated_nodes()
    n = 0
    i = 0
    total_size = 0
    for node in active_nodes:
        res = requests.get(node + '/keys') # get keys list
        
        # if (res.status_code == 200):
        keys = res.json()['keys']
        n += len(keys)
        size = res.json()['size']
        total_size += size
        node_stat = {"id": i, "activate": True, "key": keys, "size": size}
        i += 1
        result.append(node_stat)
    
    not_active_nodes = control.not_activated_nodes()
    for node in not_active_nodes:
        node_stat = {"id": i, "activate": False}
        i += 1
        result.append(node_stat)
    
    # Return the response
    response = webapp.response_class(
        response=json.dumps({"count": n, "total_size": total_size, "nodes": result}),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/pool_size',methods=['GET', 'POST'])
def pool_size():
    response = webapp.response_class(
        response=json.dumps({"pool_size": control.pool_size}),
        status=200,
        mimetype='application/json',
    )
    return response
    

@webapp.route('/pool',methods=['POST'])
def pool_config():
    active = request.json["new_active"]
    control.modify_pool_size(active)
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    return response

@webapp.route('/pool_multi',methods=['POST'])
def pool_multi():
    parameter = request.json["parameter"]
    control.multi_pool_size(parameter)
    response = webapp.response_class(
        response=json.dumps("OK"),
        status=200,
        mimetype='application/json',
    )
    return response