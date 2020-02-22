from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__)
api = Api(app)

clinet = MongoClient("mongodb://db:27017")
db = clinet.SimilarityDB
users = db["Users"]

def UserExist(username):
    ucount = users.count_documents({"username":username})
    if ucount == 0:
        return False
    else:
        return True

def verifyPassword(username, password):
    if not UserExist(username):
        return False
    hashed_pw = users.find({"username":username})[0]["password"]
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({"username": username})[0]["tokens"]
    return tokens

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]        
        if UserExist(username):
            retJson={"status": 301,
                     "msg": "Invalid Username as already exist"}
            return jsonify(retJson)
        
        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        users.insert_one({"username": username,
                          "password": hashed_pw,
                          "tokens":6})
        retJson={"status": 200,
                 "message": "Successfully register User"}
        return jsonify(retJson)

class Detect(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        text1 = postedData["text1"]
        text2 = postedData["text2"]
        if not UserExist(username):
            retJson={"status": 301,
                     "msg": "Invalid Username as already exist"}
            return jsonify(retJson)
        correct_pw = verifyPassword(username, password)
        if not correct_pw:
            retJson={"status": 302,
                     "msg": "Invalid password!"}
            return jsonify(retJson)
        num_tokens = countTokens(username)
        if num_tokens<=0:
            retJson={"status":303,
                     "msg":"You are out of tokens, Please refill"}
            return jsonify(retJson)
        text1 = nlp(text1)
        text2 = nlp(text2)
        ratio = text1.similarity(text2)
        retJson={"status": 200,
                 "similarity": ratio,
                 "msg": "Similarity calculates successfully!!!"}
        users.update_one({"username": username},
                         {"$set":{"tokens": num_tokens - 1}})
        return jsonify(retJson)
        
class Refill(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]        
        refill_amount = postedData["refill"]
        if not UserExist(username):
            retJson={"status": 301,
                     "msg": "Invalid Username as already exist"}
            return jsonify(retJson)
        correct_pw = "pass_123"
        if not correct_pw == password:
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
api.add_resource(Detect, '/detect')
api.add_resource(Refill, '/refill')

if __name__=="__main__":
    app.run(host='0.0.0.0', port='5000', debug=True)