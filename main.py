from flask import Flask,render_template
from flask import request
from flask import make_response
import json
from spider.spider import Spider
from flask_cors import *
from connect import DataBase
import time
import datetime
from flask_bootstrap import Bootstrap
from flask_apscheduler import APScheduler
from random import randint
class Config(object):  # 创建配置，用类
    JOBS = [  # 任务列表
        
        {  
            'id': 'job',
            'func': '__main__:check',
            'args': None,
            'trigger': 'interval',
            'seconds': 120,
        }
    ]
app = Flask(__name__,static_url_path='',root_path='/root/flight')
app.config.from_object(Config())
bootstrap=Bootstrap(app)
CORS(app, supports_credentials=True, resources=r'/*')
db = DataBase()

@app.route("/")
def hello():
    return app.send_static_file('homepage.html')

@app.route("/admin")
def adminPage():
    return app.send_static_file('HomePage.html')

@app.route("/beta/modifyPassword/<username>/<token>",methods = ['POST','GET'])
@cross_origin()
def modifyPassword(username='',token=''):
    try:
        if request.method == 'POST':
            print(request.form)
            newPassword = request.form['new']
            comfirm = request.form['confirm']
            if (newPassword != comfirm):
                return '两次密码不一致，请重新输入'
            else:
                success = db.updateMessage(username,newPassword)
                if (success):
                    return '密码修改成功！'
                else:
                    return '修改密码失败，请重试'
        else:
            if (db.is_modifiable(username,token)):
                return render_template('base.html')
            else:
                return '链接已失效'
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/byFlightNumber",methods = ['POST','OPTIONS'])
@cross_origin()
def searchByFlightNumber():
    try:
        print("byFlightNumber",request.json)
        data = request.json
        date = data['date']
        spd = Spider()
        if (data['op'] == 1):
            flightNumber = data['flightCode']
            allData = spd.get_base_info(flightNumber,date)
             
        elif (data['op'] == 2):
            cityFrom = data['cityFrom']
            cityTo = data['cityTo']
            allData = spd.get_base_info(cityFrom,cityTo,date)
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
                    'flight_detailed_info_url':thisRecord['flight_detailed_info_url'],
                    'ontime_rate':thisRecord['ontime_rate']
                }
            )
        print("Get flight data:",json.dumps(flightData))
        return json.dumps(flightData)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/detailedInfo",methods = ['POST','OPTIONS'])
@cross_origin()
def getDetailedInfo():
    try:
        print("detailedInfo",request.json)
        data = request.json
        spd = Spider()
        if ('url' in data):
            resData = spd.get_detailed_info(data['url'])
        else:
            date = data['date']
            code = data['flightCode']
            cityFrom = data['cityFrom']
            cityTo = data['cityTo']
            resData = spd.get_detailed_info(cityFrom,cityTo,code,date)
        print("Get flight detail data:",json.dumps(resData))
        return json.dumps(resData)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/comfortInfo",methods = ['POST','OPTIONS'])
@cross_origin()
def getComfortInfo():
    try:
        print("comfortInfo",request.json)
        data = request.json
        date = data['date']
        code = data['flightCode']
        cityFrom = data['cityFrom']
        cityTo = data['cityTo']
        spd = Spider()
        resData = spd.get_detailed_info(code,cityFrom,cityTo,date)
        return json.dumps(resData)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/register",methods = ['POST'])
@cross_origin()
def register():
    try:
        print("register",request.json)
        data = request.json
        db.dbConnect()
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
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/login",methods = ['POST'])
@cross_origin()
def login():
    try:
        print("login",request.json)
        data = request.json
        db.dbConnect()
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
            msg['status'] = 'success!'
            msg['token'] = res['code']
            return json.dumps(msg)
        else:
            msg['status'] = 'Unknown error!'
            return json.dumps(msg)    
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/active/<username>/<token>")
@cross_origin()
def active(username,token):
    try:
        success = db.activate(username,token)
        if (success == 0):
            raise(Exception("Failed to activate!"))
        else:
            return "Account successfully activated!"
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/focus",methods = ['POST'])
@cross_origin()
def focus():
    try:
        print("focus",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['username'],data['token'])
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            spd = Spider()
            allData = spd.get_base_info(data['flightCode'],data['date'])
            if (len(allData) < 1):
                raise(Exception("Flight doesn't exist!"))
            success = db.focus(data['username'],data['flightCode'],data['date'],allData[0]['flight_status'])
            if (success == 0):
                raise(Exception("Error occured when focusing the flight!"))
            else:
                msg = {}
                msg['status'] = 'success!'
                return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/unfocus",methods = ['POST'])
@cross_origin()
def unfocus():
    try:
        print("unfocus",request.json)
        data = request.json
        db.dbConnect()
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
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/getFocusedFlights",methods = ['POST'])
@cross_origin()
def getFocusedFlights():
    try:
        print("getFocusedFlights",request.json)
        data = request.json
        db.dbConnect()
        username = (data['adminname'] if 'adminname' in data else data['username']) 
        logedIn = db.isLogedIn(username,data['token'])
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
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/logout",methods = ['POST'])
@cross_origin()
def logout():
    try:
        print("logout",request.json)
        data = request.json
        db.dbConnect()
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
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/modifyPasswordEmail",methods = ['POST'])
@cross_origin()
def modifyPasswordEmail():
    try:
        print("modifyPasswordEmail",request.json)
        data = request.json
        db.dbConnect()
        logedIn = 1
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            success = db.email_for_pwd(data['username'])
            if (success == 0):
                raise(Exception("Error occured when sending modify password email!"))
            else:
                msg = {}
                msg['status'] = 'success!'
                return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/manaLogin",methods = ['POST'])
@cross_origin()
def manaLogin():
    try:
        print("ManaLogin",request.json)
        data = request.json
        db.dbConnect()
        res = db.login(data['adminname'],data['password'])
        success = res['status']
        msg = {}
        msg['statusCode'] = success
        if (success == 0):
            msg['status'] = 'Wrong username or password!'
            return json.dumps(msg)
        elif (success == 1):
            msg['status'] = 'success!'
            msg['token'] = res['code']
            return json.dumps(msg)
        else:
            msg['status'] = 'Unknown error!'
            return json.dumps(msg)    
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/manaLogout",methods = ['POST'])
@cross_origin()
def manaLogout():
    try:
        print("manaLogout",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("User hasn't loged in!"))
        else:
            success = db.logout(data['adminname'],data['token'])
            if (success == 0):
                raise(Exception("Error occured when manager logging out!"))
            else:
                msg = {}
                msg['status'] = 'success!'
                return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/getUser",methods = ['POST'])
@cross_origin()
def getUser():
    try:
        print("getUser",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        userList = db.get_user_list()
        print(userList)
        for user in userList:
            if (user[0] == data['username']):
                return json.dumps({'userID':user[0],'email':user[1]})
        return json.dumps([])
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/deleteUser",methods = ['POST'])
@cross_origin()
def deleteUser():
    try:
        print("deleteUser",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        success = db.delete_user(data['username'])
        if (success == 0):
            raise(Exception("Unknown error when deleting user %s!"%data['username']))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/sendEmail",methods = ['POST'])
@cross_origin()
def sendEmail():
    try:
        print("sendEmail",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        success = db.send_test_email(data['username'],data['flightCode'],data['date'])
        if (success == 0):
            raise(Exception("Unknown error when sending email to %s!"%data['username']))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/addFlight",methods = ['POST'])
@cross_origin()
def addFlight():
    try:
        print("addFlight",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        success = db.add_flight(data['airline'],data['flightCode'],data['date'],data['planTakeOff'],\
                    data['actualTakeOff'],data['departure'],data['planArrival'],data['actualArrival'],\
                    data['destination'],data['currentStatus'])
        if (success == 0):
            raise(Exception("Unknown error when adding flight data!"))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/deleteFlight",methods = ['POST'])
@cross_origin()
def deleteFlight():
    try:
        print("deleteFlight",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        success = db.delete_flight(data['flightCode'],data['date'])
        if (success == 0):
            raise(Exception("Unknown error when deleting flight data!"))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/modifyFlight",methods = ['POST'])
@cross_origin()
def modifyFlight():
    try:
        print("modifyFlight",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        success = db.modify_flight(data['airline'],data['flightCode'],data['date'],data['planTakeOff'],\
                    data['actualTakeOff'],data['departure'],data['planArrival'],data['actualArrival'],\
                    data['destination'],data['currentStatus'])
        if (success == 0):
            raise(Exception("Unknown error when modifying flight data!"))
        else:
            msg = {}
            msg['status'] = 'success!'
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

@app.route("/beta/searchFlight",methods = ['POST'])
@cross_origin()
def searchFlight():
    try:
        print("searchFlight",request.json)
        data = request.json
        db.dbConnect()
        logedIn = db.isLogedIn(data['adminname'],data['token'])
        if (logedIn == 0):
            raise(Exception("Manager hasn't loged in!"))
        success = db.searchFlight(data['flightCode'],data['date'])
        if (success == 0):
            raise(Exception("Unknown error when searching for flight data!"))
        else:
            if (success is None):
                raise(Exception("No flight found!"))
            msg = {}
            corresKey = ['airline','flightCode','date','planTakeOff','actualTakeOff','departure','planArrival',\
                        'actualArrival','destination','currentStatus']
            for i in range(len(success)):
                msg[corresKey[i]] = success[i]
            msg['date'] = msg['date'].strftime('%Y%m%d')
            return json.dumps(msg)
    except Exception as e:
        print('Error:',e)
        error = {}
        error['status'] = 'Error:%s'%str(e)
        return json.dumps(error)

def check():
    #db.send_warning_email()
    time.sleep(randint(60,180))


if (__name__ == '__main__'):
    scheduler=APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0')
