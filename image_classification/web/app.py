from flask import Flask, jsonify
from flask import request as api_request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import subprocess
import json
import requests as web_request
import sys

app = Flask(__name__)
api = Api(app)

clinet = MongoClient("mongodb://db:27017")
db = clinet.ImageRecognitions
users = db["Users"]

def UserExist(username):
    ucount = users.count_documents({"username":username})
    if ucount == 0:
        return False
    else:
        return True

def generateReturnDictionary(status, msg):
    retJson = {"status":status,
               "msg": msg}
    return retJson

def verify_pw(username, password):
    if not UserExist(username):
        return False
    hashed_pw = users.find({"username":username})[0]["password"]
    print('password', password, hashed_pw, file=sys.stderr)
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False
    
    
def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Invalid Username"), True
    correct_pw = verify_pw(username, password)
    if not correct_pw:
        return generateReturnDictionary(302, "Invalid Password"), True
    return None, False

def countTokens(username):
    tokens = users.find({"username": username})[0]["tokens"]
    return tokens

class Register(Resource):
    def post(self):
        postedData = api_request.get_json()
        username = postedData["username"]
        password = postedData["password"]        
        if UserExist(username):
            retJson={"status": 301,
                     "msg": "Invalid Username as already exist"}
            return jsonify(retJson)
        
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        users.insert_one({"username": username,
                          "password": hashed_pw,
                          "tokens":5})
        retJson={"status": 200,
                 "message": "Successfully register User"}
        return jsonify(retJson)

class Classify(Resource):
    def post(self):
        postedData = api_request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        url_ = postedData["url"]
        
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        
        num_tokens = countTokens(username)
        if num_tokens<=0:
            status = 303
            msg = "You are out of tokens, Please refill"
            return jsonify(generateReturnDictionary(status, msg))
        
        r = web_request.get(url_)
        retJson = {}
        with open("temp.jpg", "wb") as f:
            f.write(r.content)
        proc = subprocess.Popen('python classify_image.py --model_dir=. --image_file = ./temp.jpg')
        proc.communication()[0]
        proc.wait()
        with open("text.txt") as g:
            retJson = json.load(g)
        users.update_one({"username": username},
                         {"$set":{"tokens": num_tokens - 1}})
        return jsonify(retJson)
        
class Refill(Resource):
    def post(self):
        postedData = api_request.get_json()
        username = postedData["username"]
        admin_pw = postedData["admin_pw"]        
        refill_amount = postedData["refill"]
        if not UserExist(username):
            retJson={"status": 301,
                     "msg": "Invalid Username as already exist"}
            return jsonify(retJson)
        correct_pw = "pass_123"
        if not correct_pw == admin_pw:
            retJson={"status": 304,
                     "msg": "Invalid admin password"}
            return jsonify(retJson)
        num_tokens = countTokens(username)
        users.update_one({"username": username},
                         {"$set":{"tokens": num_tokens + refill_amount}})
        retJson = {"status": 200,
                   "msg": "Refilled Successfully!!"}
        return jsonify(retJson)
    

api.add_resource(Register, '/register')
api.add_resource(Classification, '/classify')
api.add_resource(Refill, '/refill')

if __name__=="__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)