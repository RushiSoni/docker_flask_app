# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from flask_restful import Api, Resource
from flask import Flask, jsonify, request
app = Flask(__name__)
api = Api(app)

class Add(Resource):
    def post(self):
        postedData = request.get_json()
        x = int(postedData["x"])
        y = int(postedData["y"])
        ret = x + y
        retMap = {
                    'Message ': ret
                    'Status code': 200
                 }
        return jsonify(retMap)
    
class Subtract(Resource):
    def post(self):
        postedData = request.get_json()
        x = int(postedData["x"])
        y = int(postedData["y"])
        ret = x - y
        retMap = {
                    'Message ': ret
                    'Status code': 200
                 }
        return jsonify(retMap)
    
class Multiply(Resource):
    def post(self):
        postedData = request.get_json()
        x = int(postedData["x"])
        y = int(postedData["y"])
        ret = x * y
        retMap = {
                    'Message ': ret
                    'Status code': 200
                 }
        return jsonify(retMap)
    
class Divide(Resource):

@app.route('/')
def hello_world():
    return "Hello World"

@app.route('/hithere')
def func_hi_there():
    return "Hi There!"

@app.route('/json_output')
def json_output():
    cals = 8*10
    result={"hello":"world", "calculated":cals}
    return jsonify(result)

@app.route('/calculate', methods=["POST"])
def calculate():
    dataDict = request.get_json(force=True)
    #dataDict = request.json
    print(dataDict)
    dataDict["Z"] = dataDict["X"] + dataDict["Y"]
    return jsonify(dataDict)

if __name__=="__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
