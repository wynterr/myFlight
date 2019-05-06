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
listUrl = 'http://' + IP + ':5000/beta/getFocusedFlights';
smeUrl = 'http://' + IP + ':5000/beta/modifyPasswordEmail';
guUrl = 'http://' + IP + ':5000/beta/getUser';
msemUrl = 'http://' + IP + ':5000/beta/sendEmail';
afUrl = 'http://' + IP + ':5000/beta/addFlight';
tmfUrl = 'http://' + IP + ':5000/beta/modifyFlight';
tdfUrl = 'http://' + IP + ':5000/beta/deleteFlight';
tsfUrl = 'http://' + IP + ':5000/beta/searchFlight';

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
        'username' : 'xwttt',
        'password' : '11223344',
        'email' : '786311041@qq.com'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = regUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testLogin():
    body = {
        'username' : 'testUser222',
        'password' : '11223344'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = loginUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testFocus():
    body = {
        'username' : 'testUser',
        'token' : 'lgqJrGxZt6',
        'flightCode':'CA1234',
        'date':'20190414'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = focusUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testUnfocus():
    body = {
        'username' : 'testUser',
        'token' : 'lgqJrGxZt6',
        'flightCode':'CA1234',
        'date':'20190414'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = unfocusUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testGetList():
    body = {
        'username' : 'testUser',
        'token' : 'lgqJrGxZt6'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = listUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSendModifyEmail():
    body = {
        'username' : 'xwttt'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = smeUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testGetUser():
    body = {
        'username' : 'test001'
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
        'airline':'中国国际航空',
        'flightCode':'CA911',
        'date':'20180823',
        'planTakeOff':'13:50',
        'actualTakeOff':'13:55',
        'departure':'北京首都机场',
        'planArrival':'17:10',
        'actualArrival':'17:01',
        'destination':'斯德哥尔摩阿兰达机场',
        'currentStatus':'到达'
}
    headers = {'content-type': "application/json"}
    res = requests.post(url = afUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testModiftFlight():
    body = {
        'adminname':'admin',
        'token':'justtest',
        'airline':'中国国际航空',
        'flightCode':'CA911',
        'date':'20180823',
        'planTakeOff':'13:50',
        'actualTakeOff':'13:55',
        'departure':'北京首都机场',
        'planArrival':'17:10',
        'actualArrival':'17:02',
        'destination':'斯德哥尔摩阿兰达机场',
        'currentStatus':'到达'
}
    headers = {'content-type': "application/json"}
    res = requests.post(url = tmfUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testDeleteFlight():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'flightCode':'CA911',
        'date':'20180823'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = tdfUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSearchFlight():
    body = {
        'adminname' : 'admin',
        'token':'justtest',
        'flightCode':'CA911',
        'date':'20180823'
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
    
if (__name__ == '__main__'):
   #testReg(); 
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
    #testGetUser()
    #testSendEmail()
    #testAddFlight()
    #testModiftFlight()
    #testDeleteFlight()
    #testSearchFlight()
    testGetFocus()