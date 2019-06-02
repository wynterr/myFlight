import requests,json
#114.115.134.119
IP = '114.115.134.119'
regUrl = 'http://' + IP + ':5000/beta/register';
logUrl = 'http://' + IP + ':5000/beta/logIn';
SBFNUrl = 'http://' + IP + ':5000/beta/byFlightNumber';
DIUrl = 'http://' + IP + ':5000/beta/detailedInfo';
CIUrl = 'http://' + IP + ':5000/beta/comfortInfo';
regUrl = 'http://' + IP + ':5000/beta/register';
loginUrl = 'http://' + IP + ':5000/beta/login';
focusUrl = 'http://' + IP + ':5000/beta/focus';
unfocusUrl = 'http://' + IP + ':5000/beta/unfocus';
loUrl = 'http://' + IP + ':5000/beta/logout';
listUrl = 'http://' + IP + ':5000/beta/getFocusedFlights';
smeUrl = 'http://' + IP + ':5000/beta/modifyPasswordEmail';
guUrl = 'http://' + IP + ':5000/beta/getUser';
msemUrl = 'http://' + IP + ':5000/beta/sendEmail';
afUrl = 'http://' + IP + ':5000/beta/addFlight';
tmfUrl = 'http://' + IP + ':5000/beta/modifyFlight';
tdfUrl = 'http://' + IP + ':5000/beta/deleteFlight';
tsfUrl = 'http://' + IP + ':5000/beta/searchFlight';
sebfUrl = 'http://' + IP + ':5000/beta/sendEmailByFlight';
guiUrl = 'http://' + IP + ':5000/beta/getUserInfo';
def testSBFN():    #search by flight number
    body = {
        'op':1,
        'flightCode':'CA1234',
        'date':'20190420'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = SBFNUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(res.headers)
    print(data)

def testSBC():  #search by city
    body = {
        'op':2,
        'cityFrom':'PEK',
        'cityTo':'SHA',
        'date':'20190420'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = SBFNUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testDI():  #search for detailed imformation
    body = {
        'flightCode':'CA911',
        'cityFrom':'PEK',
        'cityTo':'ARN',
        'date':'20190406'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = DIUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testCI():  #search for comfort imformation
    body = {
        'flightCode':'CA911',
        'cityFrom':'PEK',
        'cityTo':'ARN',
        'date':'20190406'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = CIUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testDIBU():  #search for detailed imformation by url
    body = {
        'url':'http://www.variflight.com/schedule/KRY-PEK-CA1234.html?AE71649A58c77=&fdate='
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = DIUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testReg():  #test register
    body = {
        'username' : 'test0519',
        'password' : '111222333444',
        'email' : '786311041@qq.com'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = regUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testLogin():
    body = {
        'username' : 'test0519',
        'password' : '111222333444'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = loginUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testFocus():
    body = {
        'username' : 'test0519',
        'token' : 'tMQeVzhfx3',
        'flightCode':'CA1234',
        'date':'20190414',
        'identity':0
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = focusUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testUnfocus():
    body = {
        'username' : 'test0519',
        'token' : 'tMQeVzhfx3',
        'flightCode':'CA1234',
        'date':'20190414'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = unfocusUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testGetList():
    body = {
        'username' : 'test0519',
        'token' : 'tMQeVzhfx3'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = listUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSendModifyEmail():
    body = {
        'username' : 'test0519'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = smeUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testLogOut():
    body = {
        'username' : 'test0519',
        'token' : 'tMQeVzhfx3'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = loUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testGetUser():
    body = {
        'adminname':'admin',
        'token':'justtestt',
        'username' : 'test0519'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = guUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSendEmail():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'username':'xwttt',
        'flightCode':'CA911',
        'date':'20180823'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = msemUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testAddFlight():
    body = {
        'adminname':'admin',
        'token':'justtest',
        'corp_name':'中国国际航空',
        'flight_code':'CA911',
        'flight_date':'20180823',
        'dep_time_plan':'13:50',
        'dep_time_act':'13:55',
        'dep_airp_name':'北京首都机场',
        'dep_airp_code':'PEK',
        'arri_time_plan':'17:10',
        'arri_time_act':'17:01',
        'arri_airp_name':'斯德哥尔摩阿兰达机场',
        'arri_airp_code':'ARN',
        'flight_status':'到达'
}
    headers = {'content-type': "application/json"}
    res = requests.post(url = afUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testModifytFlight():
    body = {
        'adminname':'admin',
        'token':'justtest',
        'corp_name':'中国国际航空',
        'flight_code':'CA911',
        'flight_date':'20180823',
        'dep_time_plan':'13:50',
        'dep_time_act':'13:55',
        'dep_airp_code':'PEK',
        'arri_time_plan':'17:10',
        'arri_time_act':'17:02',
        'arri_airp_code':'ARN',
        'flight_status':'到达'
}
    headers = {'content-type': "application/json"}
    res = requests.post(url = tmfUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testDeleteFlight():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'flight_code':'CA911',
        'flight_date':'20180823',
        'dep_airp_code':'PEK',
        'arri_airp_code':'ARN'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = tdfUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSearchFlight():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'flight_code':'CC444',
        'flight_date':'20190513'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = tsfUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testGetFocus():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'username':'xwttt'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = listUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSendByFlight():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'flight_code':'CA911',
        'flight_date':'20190420'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = sebfUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testGetUserInfo():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'username':'asd130530'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = guiUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)
if (__name__ == '__main__'):
   #testLog();
   #testSBFN();
   #testSBC()
   #testDI();
   #testCI();
   #testDIBU();
   #testReg()
   #testLogin()
   #testFocus()
    #testGetList()
    #testUnfocus()
    #testSendModifyEmail()
    #testLogOut()
    #testGetUser()
    #testSendEmail()
    #testAddFlight()
    #testModifytFlight()
    #testDeleteFlight()
    #testSearchFlight()
    #testGetFocus()
    #testSendByFlight()
    testGetUserInfo()