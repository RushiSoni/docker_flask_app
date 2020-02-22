# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask_restful import Api, Resource
from flask import Flask, jsonify, request
app = Flask(__name__)
api = Api(app)

def checkPostedData(postedData, functionName):
    if functionName in ["add", "subtract", "multiply"]:
        if ("x" not in postedData) or ("y" not in postedData):
            return 301
        else:
            return 200
    elif functionName == "division":
        if ("x" not in postedData) or ("y" not in postedData):
            return 301
        elif int(postedData["y"]) == 0:
            return 302
        else:
            return 200
        
class Add(Resource):        
    def post(self):
        postedData = request.get_json()
        print('postedData')
        print(postedData)
        status_code = checkPostedData(postedData, "add")
        if status_code!=200:
            retMap = {
                    'Message ': "Error happen",
                    'Status code': status_code
                 }
        else:
            x = postedData["x"]
            y = postedData["y"]
            ret = int(x) + int(y)
            retMap = {
                        'Message ': ret,
                        'Status code': 200
                     }
        
        return jsonify(retMap)
    
class Subtract(Resource):
    def post(self):
        postedData = request.get_json()
        print('postedData')
        print(postedData)
        status_code = checkPostedData(postedData, "subtract")
        if status_code!=200:
            retMap = {
                    'Message ': "Error happen",
                    'Status code': status_code
                 }
        else:
            x = postedData["x"]
            y = postedData["y"]
            ret = int(x) + int(y)
            retMap = {
                        'Message ': ret,
                        'Status code': 200
                     }
        
        return jsonify(retMap)
    
class Multiply(Resource):
    def post(self):
        postedData = request.get_json()
        print('postedData')
        print(postedData)
        status_code = checkPostedData(postedData, "multiply")
        if status_code!=200:
            retMap = {
                    'Message ': "Error happen",
                    'Status code': status_code
                 }
        else:
            x = postedData["x"]
            y = postedData["y"]
            ret = int(x) * int(y)
            retMap = {
                        'Message ': ret,
                        'Status code': 200
                     }
        
        return jsonify(retMap)
    
class Divide(Resource):
    def post(self):
        postedData = request.get_json()
        print('postedData')
        print(postedData)
        status_code = checkPostedData(postedData, "division")
        if status_code!=200:
            retMap = {
                    'Message ': "Error happen",
                    'Status code': status_code
                 }
        else:
            x = postedData["x"]
            y = postedData["y"]
            ret = (int(x)*1.0) / int(y)
            retMap = {
                        'Message ': ret,
                        'Status code': 200
                     }
        
        return jsonify(retMap)

class HelloWorld(Resource):
    def post(self):
        return "Hello World!!!"
    
api.add_resource(Add, "/add")
api.add_resource(Subtract, "/subtract")
api.add_resource(Multiply, "/multiply")
api.add_resource(Divide, "/division")
api.add_resource(HelloWorld, "/")

@app.route('/')
def hello_world():
    return "Hello World"

if __name__=="__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
