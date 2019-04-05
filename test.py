import requests,json
#114.115.134.119
IP = '114.115.134.119'
regUrl = 'http://' + IP + ':5000/beta/register';
logUrl = 'http://' + IP + ':5000/beta/logIn';
SBFNUrl = 'http://' + IP + ':5000/beta/byFlightNumber';

def testReg():
    res = requests.post(regUrl);
    print(res.text);

def testLog():
    res = requests.post(logUrl);
    print(res.text);

def testSBFN():    #search by flight number
    body = {
        'op':1,
        'flightCode':'CA911',
        'date':'20190329'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = SBFNUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)

def testSBC():  #search by city
    body = {
        'op':2,
        'cityFrom':'PEK',
        'cityTo':'ARN',
        'date':'20190329'
    }
    headers = {'content-type': "application/json"}
    res = requests.post(url = SBFNUrl,headers = headers,data = json.dumps(body));
    data = json.loads(res.text)
    print(data)
if (__name__ == '__main__'):
   #testReg(); 
   #testLog();
   #testSBFN();
   testSBC()