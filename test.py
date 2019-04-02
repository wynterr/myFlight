import requests

regUrl = 'http://114.115.134.119:5000/beta/register';
logUrl = 'http://114.115.134.119:5000/beta/logIn';

def testReg():
    res = requests.post(regUrl);
    print(res.text);

def testLog():
    res = requests.post(logUrl);
    print(res.text);

if (__name__ == '__main__'):
   testReg(); 
   testLog();