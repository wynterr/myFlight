from flask import Flask
from flask import request
from flask import make_response
import json
from spider.spider import Spider
from flask_cors import *
app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'/*')

@app.route("/")
def hello():
    return "Flight wherever you want!"

@app.route("/beta/register",methods = ['POST'])
def register():
    return 'successfully registered!'

@app.route("/beta/logIn",methods = ['POST'])
def logIn():
    return 'successfully loged in!'

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

if (__name__ == '__main__'):
    app.run(host='0.0.0.0')