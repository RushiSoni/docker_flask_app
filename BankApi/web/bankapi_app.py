"""
Registration of a user 0 tokens
Each user gets 10 tokens
Store a sentence on our database for 1 token
Retrieve his stored sentence on out database for 1 token
"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import sys

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.BankAPI
users = db["Users"]

def UserExist(username):
    ucount = users.count_documents({"Username":username})
    print('UserExist:', username, ucount, file=sys.stderr)
    if ucount == 0:
        return False
    else:
        return True

def verifyPw(username, password):
    if not UserExist(username):
        return False
    hashed_pw = users.find({"Username":username})[0]["Password"]
    print('verifyPw hashed_pw#### ', hashed_pw, file=sys.stderr)
    if bcrypt.hashpw(password.encode('utf8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def cashWithUser(username):
    cash = users.find({
        "Username":username
    })[0]["Own"]
    return cash

def deptWithUser(username):
    dept = users.find({
        "Username":username
    })[0]["Debt"]
    return dept

def generateReturnDictionary(status, msg):
    retJson = {"status": status,
               "Message": msg}
    return retJson

def verifyCredentials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Invalid Username"), True
    correct_pw = verifyPw(username, password)
    if not correct_pw:
        print('correct_pw###', correct_pw, file = sys.stderr)
        return generateReturnDictionary(302, "Invalid Password"), True
    return None, False

def updateAccount(username, balance):
        users.update_one({
            "Username":username
        }, {
            "$set":{
                "Own": balance
                }
        })

def updateDept(username, balance):
        users.update_one({
            "Username":username
        }, {
            "$set":{
                "Debt": balance
                }
        })
        
class Register(Resource):
    def post(self):
        #Step 1 is to get posted data by the user
        postedData = request.get_json()

        #Get the data
        username = postedData["username"]
        password = postedData["password"] #"123xyz"
        
        if UserExist(username):
            retJson = {"status": 301,
                       "msg":"User already exists!"}
            return jsonify(retJson)

        hashed_pw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())
        print('added hashed_pw#### ', hashed_pw, file=sys.stderr)

        #Store username and pw into the database
        users.insert_one({
            "Username": username,
            "Password": hashed_pw,
            "Own": 0,
            "Debt": 0
        })

        retJson = {
            "status": 200,
            "msg": "You successfully open bank account!"
        }
        return jsonify(retJson)



class Add(Resource):
    def post(self):
        #Step 1 get the posted data
        postedData = request.get_json()

        #Step 2 is to read the data
        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amount"]
        
        retJson, error = verifyCredentials(username, password)
        if error:
            print(username, password, file=sys.stderr)
            return jsonify(retJson)
        
        if money<=0:
            status = 304
            msg = "The amount entered must be >0"
            return jsonify(generateReturnDictionary(status, msg))
        
        cash = cashWithUser(username)
        money = money - 1
        bank_cash = cashWithUser('BANK')
        updateAccount('BANK', bank_cash + 1)
        updateAccount(username, cash + money)
        status = 200
        msg = "Amount added Successfully"
        return jsonify(generateReturnDictionary(status, msg))


class Transfer(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        to = postedData["to"]
        money = postedData["amount"]
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        cash = cashWithUser(username)
        if cash<=0:
            status = 304
            msg = "You are out of money"
            return jsonify(generateReturnDictionary(status, msg))
        if not UserExist(to):
            status = 301
            msg = "Reciever username is Invalid"
            return jsonify(generateReturnDictionary(status, msg))
        cash_from = cashWithUser(username)
        cash_to = cashWithUser(to)
        bank_cash = cashWithUser('BANK')
        updateAccount('BANK', bank_cash + 1)
        updateAccount(to, cash_to + money - 1)
        updateAccount(username, cash - money)
        status = 200
        msg = "Amount transfered Successfully"
        return jsonify(generateReturnDictionary(status, msg))

class Balance(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        retJson = users.find({"Username":username},
                          {"Password":0, "_id":0})[0]
        return jsonify(retJson)

class TakeLoan(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amount"]
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        cash = cashWithUser(username)
        debt = debtWithUser(username)
        updateAccount(username, cash + money)
        updateDept(username, debt + money)
        status = 200
        msg = "Loan added Successfully"
        return jsonify(generateReturnDictionary(status, msg))
    
class PayLoan(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        money = postedData["amount"]
        retJson, error = verifyCredentials(username, password)
        if error:
            return jsonify(retJson)
        cash = cashWithUser(username)
        if cash<money:
            status = 303
            msg = "Not enough money in account"
            return jsonify(generateReturnDictionary(status, msg))
        debt = debtWithUser(username)
        updateAccount(username, cash - money)
        updateDept(username, debt - money)
        status = 200
        msg = "Loan payed Successfully"
        return jsonify(generateReturnDictionary(status, msg))

api.add_resource(Register, '/register')
api.add_resource(Add, '/add')
api.add_resource(Transfer, '/transfer')
api.add_resource(Balance, '/balance')
api.add_resource(TakeLoan, '/takeloan')
api.add_resource(PayLoan, '/payloan')

if __name__=="__main__":
    app.run(host='0.0.0.0', debug = True)
