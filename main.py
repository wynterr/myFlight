from flask import Flask
from flask import request
from flask import make_response
import json
from spider.spider import Spider
from flask_cors import *
from connect import DataBase
import time
import datetime
app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'/*')
db = DataBase();

@app.route("/")
def hello():
    return "Flight wherever you want!"

@app.route("/beta/byFlightNumber",methods = ['POST','OPTIONS'])
@cross_origin()
def searchByFlightNumber():
    try:
        print(request.json)
        data = request.json
        date = data['date']
        if (data['op'] == 1):
            flightNumber = data['flightCode']
            allData = Spider().get_base_info(flightNumber,date)
             
        elif (data['op'] == 2):
            cityFrom = data['cityFrom']
            cityTo = data['cityTo']
            allData = Spider().get_base_info(cityFrom,cityTo,date)
        else:
            error = {}
            error['status'] = 'Wrong op!'
            return json.dumps(error)
        flightData = []
        for i in range(len(allData)):
            thisRecord = allData[i]
            if ('%' not in thisRecord['ontime_rate']):
                continue;
            flightData.append({
                    'corp_name':thisRecord['corp_name'],
                    'flight_code':thisRecord['flight_code'],
                    'dep_time_plan':thisRecord['dep_time_plan'],
                    'dep_time_act':thisRecord['dep_time_act'],
                    'dep_airp':thisRecord['dep_airp'],
                    'arri_time_plan':thisRecord['arri_time_plan'],
                    'arri_time_act':thisRecord['arri_time_act'],
                    'arri_airp':thisRecord['arri_airp'],
                    'flight_status':thisRecord['flight_status'],
                    'flight_detailed_info_url':thisRecord['flight_detailed_info_url']
                }
            )
        print(json.dumps(flightData))
        return json.dumps(flightData)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/detailedInfo",methods = ['POST','OPTIONS'])
@cross_origin()
def getDetailedInfo():
    try:
        print(request.json)
        data = request.json
        if ('url' in data):
            print(data['url'])
            resData = Spider().get_detailed_info(data['url'])
        else:
            date = data['date']
            code = data['flightCode']
            cityFrom = data['cityFrom']
            cityTo = data['cityTo']
            resData = Spider().get_detailed_info(cityFrom,cityTo,code,date)
        return json.dumps(resData)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/comfortInfo",methods = ['POST','OPTIONS'])
@cross_origin()
def getComfortInfo():
    try:
        print(request.json)
        data = request.json
        date = data['date']
        code = data['flightCode']
        cityFrom = data['cityFrom']
        cityTo = data['cityTo']
        resData = Spider().get_detailed_info(code,cityFrom,cityTo,date)
        return json.dumps(resData)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/register",methods = ['POST'])
@cross_origin()
def register():
    try:
        data = request.json
        success = db.register(data['username'],data['password'],data['email'])
        if (success == 0):
            raise(Exception("Failed to register!"))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/login",methods = ['POST'])
@cross_origin()
def login():
    try:
        data = request.json
        res = db.login(data['username'],data['password'])
        success = res['status']
        msg = {}
        msg['statusCode'] = success
        if (success == 0):
            msg['status'] = 'Wrong username or password!'
            return json.dumps(msg)
        elif (success == -1): 
            msg['status'] = 'Account inactivated!'
            return json.dumps(msg)
        elif (success == 1):
            msg['status'] = 'Success!'
            msg['token'] = res['code']
            return json.dumps(msg)
        else:
            msg['status'] = 'Unknown error!'
            return json.dumps(msg)    
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/active/<username>/<token>")
@cross_origin()
def active(username,token):
    try:
        success = db.activate(username,token)
        if (success == 0):
            raise(Exception("Failed to activate!"))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/focus",methods = ['POST'])
@cross_origin()
def focus():
    try:
        data = request.json
        logedIn = db.isLogedIn(data['username'],data['token'])
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            success = db.focus(data['username'],data['flightCode'],data['date'])
            if (success == 0):
                raise(Exception("Error occured when focusing the flight!"))
            else:
                msg = {}
                msg['status'] = 'success!'
                return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/unfocus",methods = ['POST'])
@cross_origin()
def unfocus():
    try:
        data = request.json
        logedIn = db.isLogedIn(data['username'],data['token'])
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            success = db.unfocus(data['username'],data['flightCode'],data['date'])
            if (success == 0):
                raise(Exception("Error occured when unfocusing the flight!"))
            else:
                msg = {}
                msg['status'] = 'success!'
                return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/getFocusedFlights",methods = ['POST'])
@cross_origin()
def getFocusedFlights():
    try:
        data = request.json
        logedIn = db.isLogedIn(data['username'],data['token'])
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            flights = db.getList(data['username'])
            for i in range(len(flights)):
                dic = {}
                dic['flightCode'] = flights[i][0]
                dic['date'] = flights[i][1].strftime("%Y%m%d")
                flights[i] = dic
            print(flights)
            return json.dumps(flights)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

@app.route("/beta/logout",methods = ['POST'])
@cross_origin()
def logout():
    try:
        data = request.json
        logedIn = db.isLogedIn(data['username'],data['token'])
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            success = db.logout(data['username'],data['token'])
            if (success == 0):
                raise(Exception("Error occured when logging out!"))
            else:
                msg = {}
                msg['status'] = 'success!'
                return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error%s'%str(e)
        return json.dumps(error)

if (__name__ == '__main__'):
    app.run(host='0.0.0.0')