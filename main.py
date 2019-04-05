from flask import Flask
from flask import request
import json
from spider.spider import Spider
app = Flask(__name__)

@app.route("/")
def hello():
    return "Flight wherever you want!"

@app.route("/beta/register",methods = ['POST'])
def register():
    return 'successfully registered!'

@app.route("/beta/logIn",methods = ['POST'])
def logIn():
    return 'successfully loged in!'

@app.route("/beta/byFlightNumber",methods = ['POST'])
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
                    'flight_status':thisRecord['flight_status']
                }
            )
        return json.dumps(flightData)
    except Exception as e:
        raise(e)
        print('Error:',e)
        return 'Error%s'%str(e)
    return('111')

if (__name__ == '__main__'):
    app.run(host='0.0.0.0')