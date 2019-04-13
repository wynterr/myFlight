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

def testSBFN():    #search by flight number
    body = {
        'op':1,
        'flightCode':'CA1234',
        'date':'20190409'
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
        'date':'20190405'
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
        'url':'http://www.variflight.com/schedule/BHY-CSX-CZ3147.html?AE71649A58c77=&fdate=20190402'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = DIUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testReg():  #test register
    body = {
        'username' : 'testUser2',
        'password' : '112233445',
        'email' : '111111111@qq.com'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = regUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testLogin():
    body = {
        'username' : 'testUser2',
        'password' : '112233445'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = loginUrl,headers = headers,data = json.dumps(body));
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
   testLogin()