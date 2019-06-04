function setUserName(username){
    document.cookie="user="+username;
}
function setPwd(pwd) {
    document.cookie="pwd="+pwd;
}
function setToken(token) {
    document.cookie="token="+token;
}
function setdate(date) {
    document.cookie="date="+date;
}
function setEmail(email){
    document.cookie="email="+email;
}
function login(){
    document.cookie="islogin=1";
    var str = '<div class="hint" id="hint">\n' +
        '            <p>登录成功，正在跳转</p>\n' +
        '        </div>';
    document.getElementById("hintWindow").innerHTML=str;
    hintStyle();
}
function notLogin() {
    document.cookie = "notlogin=false";
    var str = '<div class="hint" id="hint">\n' +
        '            <p>您尚未登录</p>\n' +
        '        </div>';
    document.getElementById("hintWindow").innerHTML=str;
    hintStyle();
    setTimeout("takeTrue('notlogin')",1500);
}
function logout() {
    document.cookie="islogin=0";
    var str = '<div class="hint" id="hint">\n' +
        '            <p>您已登出，正在跳转</p>\n' +
        '        </div>';
    document.getElementById("hintWindow").innerHTML=str;
    hintStyle();
}
function get_cookie(name){
    var strCookie=document.cookie;
    var arrCookie=strCookie.split("; ");
    for(var i=0;i<arrCookie.length;i++){
        var arr=arrCookie[i].split("=");
        if(arr[0]==name){
            return arr[1];
        }
    }
    return 0;
}
function toChangePwd(url){
    if(get_cookie("islogin") == 1){
        window.location.href = "changepwd.html";
    }
    else{
        if(get_cookie("notlogin") == "true"){
            notLogin();
            setTimeout("empty()",1500);
        }
    }
}
function toMyInfo(url) {
    if(get_cookie("islogin") == 1){
        window.location.href = "personalinfo.html";
    }
    else{
        if(get_cookie("notlogin") == "true"){
            notLogin();
            setTimeout("empty()",1500);
        }
    }
}
function toLogOff(url){
    if(get_cookie("islogin") == 1){
        logout();
        var jsonData = JSON.stringify({
            username:get_cookie("user"),
            token:DeleteMark(get_cookie("token")),
        })
        var xhr = AjaxFunction();
        var str = "";
        xhr.onreadystatechange = function(){
            if(xhr.readyState==4){
                responseData = JSON.parse(xhr.responseText);
                var length = responseData.length;
                for(var i = 0;i < length;i++){
                    var followInfo = DeleteMark(JSON.stringify(responseData[i].flightCode)) + "_" + DeleteMark(JSON.stringify(responseData[i].date));
                    document.cookie = followInfo+"=0";
                }
                setTimeout("skip('homepage.html')",800);
            }
        }
        xhr.open("POST","http://39.107.74.159:5000/beta/getFocusedFlights",true);
        xhr.setRequestHeader("Content-type","application/json");
        xhr.send(jsonData);
    }
    else{
        if(get_cookie("notlogin") == "true"){
            notLogin();
            setTimeout("empty()",1500);
        }
    }
}
function toFollowList(url) {
    if(get_cookie("islogin") == 1){
        window.location.href = "followlist.html";
    }
    else{
        if(get_cookie("notlogin") == "true"){
            notLogin();
            setTimeout("empty()",1500);
        }
    }
}
function DeleteMark(str){
    var newStr;
    newStr = str.replace(/"/g,'',);
    return newStr;
}
function AjaxFunction(){
    var xmlHttp;
    try{ // Firefox, Opera 8.0+, Safari
        xmlHttp=new XMLHttpRequest();
    }
    catch (e){
        try{// Internet Explorer
            xmlHttp=new ActiveXObject("Msxml2.XMLHTTP");
        }
        catch (e){
            try{
                xmlHttp=new ActiveXObject("Microsoft.XMLHTTP");
            }
            catch (e){}
        }
    }
    return xmlHttp;
}
function emptyFlightNum(){
    if(get_cookie("flight_num") == "true"){
        var str = '<div class="hint" id="hint">\n' +
            '            <p>请输入航班号</p>\n' +
            '        </div>';
        document.getElementById("hintWindow").innerHTML=str;
        hintStyle();
        document.cookie = "flight_num=false";
        setTimeout("takeTrue('flight_num')",1500);
    }
}
function emptyDepCity(){
    if(get_cookie("dep_city") == "true"){
        var str = '<div class="hint" id="hint">\n' +
            '            <p>请输入出发城市</p>\n' +
            '        </div>';
        document.getElementById("hintWindow").innerHTML=str;
        hintStyle();
        document.cookie = "dep_city=false";
        setTimeout("takeTrue('dep_city')",1500);
    }
}
function emptyArriveCity(){
    if(get_cookie("arrive_city") == "true"){
        var str = '<div class="hint" id="hint">\n' +
            '            <p>请输入到达城市</p>\n' +
            '        </div>';
        document.getElementById("hintWindow").innerHTML=str;
        hintStyle();
        document.cookie = "arrive_city=false";
        setTimeout("takeTrue('arrive_city')",1500);
    }
}
function empty(){
    var str = '';
    document.getElementById("hintWindow").innerHTML=str;
}
function hintStyle(){
    var a = document.getElementById("hint");
    var Height=document.documentElement.clientHeight;
    var Width=document.documentElement.clientWidth;
    var gao1 = a.offsetHeight;
    var gao2 = a.offsetWidth;
    var Sgao1= (Height - gao1)/2+"px";
    var Sgao2= (Width - gao2)/2+"px";
    a.style.top=Sgao1;
    a.style.left=Sgao2;
}
function identityStyle(){
    var a = document.getElementById("identityChoice");
    var Height=document.documentElement.clientHeight;
    var Width=document.documentElement.clientWidth;
    var gao1 = a.offsetHeight;
    var gao2 = a.offsetWidth;
    var Sgao1= (Height - gao1)/2+"px";
    var Sgao2= (Width - gao2)/2+"px";
    a.style.top=Sgao1;
    a.style.left=Sgao2;
}
function takeTrue(str) {
    document.cookie = str +"=true";
}
function skip(a){
    window.location.href = a;
}
function checkInfoStyle(a){
    var url = a;
    var op = 0;
    var user = "";
    var pwd = "";
    var email = "";
    var strs = url.split("&");
    if(strs[0].split(":")[1] == "1"){
        op = 1;
    }
    else{
        op = 2;
    }
    user = strs[1].split(":")[1];
    pwd = strs[2].split(":")[1];
    email = strs[3].split(":")[1];
    if(op == 1){
        if(user == "" || pwd == ""){
            if(get_cookie("login") == "true"){
                var str = '<div class="hint" id="hint">\n' +
                    '            <p>您的用户名或密码为空</p>\n' +
                    '        </div>';
                document.getElementById("hintWindow").innerHTML=str;
                hintStyle();
                setTimeout("empty()",1200);
                document.cookie = "login=false";
                setTimeout("takeTrue('login')",1200);
            }
        }
        else if(user.length < 6 || pwd.length < 6 || user.length > 13 || pwd.length > 13){
            if(get_cookie("login") == "true"){
                var str = '<div class="hint" id="hint">\n' +
                    '            <p>用户名或密码长度不规范</p>\n' +
                    '        </div>';
                document.getElementById("hintWindow").innerHTML=str;
                hintStyle();
                setTimeout("empty()",1200);
                document.cookie = "login=false";
                setTimeout("takeTrue('login')",1200);
            }
        }
        else{
            var test = /([a-z]|[A-Z]|[0-9]){6,13}/;
            if(test.test(user) && test.test(pwd)){
                var valid = "op:" + op + "&user:" + user + "&pwd:" + pwd + "&email:" + email;
                checkInfoValid(valid);
            }
            else{
                if(get_cookie("login") == "true"){
                    var str = '<div class="hint" id="hint">\n' +
                        '            <p>用户名或密码含有非法字符</p>\n' +
                        '        </div>';
                    document.getElementById("hintWindow").innerHTML=str;
                    hintStyle();
                    setTimeout("empty()",1200);
                    document.cookie = "login=false";
                    setTimeout("takeTrue('login')",1200);
                }
            }
        }
    }
    else{
        if(user == "" || pwd == "" || email == ""){
            if(get_cookie("register") == "true"){
                var str = '<div class="hint" id="hint">\n' +
                    '            <p>注册信息不能为空</p>\n' +
                    '        </div>';
                document.getElementById("hintWindow").innerHTML=str;
                hintStyle();
                setTimeout("empty()",1200);
                document.cookie = "register=false";
                setTimeout("takeTrue('register')",1200);
            }
        }
        else if(user.length < 6 || pwd.length < 6 || user.length > 13 || pwd.length > 13){
            if(get_cookie("register") == "true"){
                var str = '<div class="hint" id="hint">\n' +
                    '            <p>用户名或密码长度不正确</p>\n' +
                    '        </div>';
                document.getElementById("hintWindow").innerHTML=str;
                hintStyle();
                setTimeout("empty()",1200);
                document.cookie = "register=false";
                setTimeout("takeTrue('register')",1200);
            }
        }
        else{
            var test = /([a-z]|[A-Z]|[0-9]){6,13}/;
            var testemail = /\w+@\w+(\.\w{2,3})*\.\w{2,3}/;
            if(test.test(user) && test.test(pwd) && testemail.test(email)){
                var valid = "op:" + op + "&user:" + user + "&pwd:" + pwd + "&email:" + email;
                checkInfoValid(valid);
            }
            else if(!test.test(user) || !test.test(pwd)){
                if(get_cookie("register") == "true"){
                    var str = '<div class="hint" id="hint">\n' +
                        '            <p>用户名或密码含有非法字符</p>\n' +
                        '        </div>';
                    document.getElementById("hintWindow").innerHTML=str;
                    hintStyle();
                    setTimeout("empty()",1200);
                    document.cookie = "register=false";
                    setTimeout("takeTrue('register')",1200);
                }
            }
            else{
                if(get_cookie("register") == "true"){
                    var str = '<div class="hint" id="hint">\n' +
                        '            <p>您输入的邮箱不存在</p>\n' +
                        '        </div>';
                    document.getElementById("hintWindow").innerHTML=str;
                    hintStyle();
                    setTimeout("empty()",1200);
                    document.cookie = "register=false";
                    setTimeout("takeTrue('register')",1200);
                }
            }
        }
    }
    function checkInfoValid(a){
        var url = a;
        var op = 0;
        var user = "";
        var pwd = "";
        var email = "";
        var strs = url.split("&");
        if(strs[0].split(":")[1] == "1"){
            op = 1;
        }
        else{
            op = 2;
        }
        user = strs[1].split(":")[1];
        pwd = strs[2].split(":")[1];
        email = strs[3].split(":")[1];
        var xhr = AjaxFunction();
        var jsonData1 = JSON.stringify({
            username:user,
            password:pwd,
        })
        var jsonData2 = JSON.stringify({
            username:user,
            password:pwd,
            email:email,
        })
        if(op == 1){
            xhr.onreadystatechange = function(){
                if(xhr.readyState==4){
                    var responseData = JSON.parse(xhr.responseText);
                    if(JSON.stringify(responseData.statusCode) == 0){
                        if(get_cookie("login") == "true"){
                            var str = '<div class="hint" id="hint">\n' +
                                '            <p>用户名或密码错误</p>\n' +
                                '        </div>';
                            document.getElementById("hintWindow").innerHTML=str;
                            hintStyle();
                            setTimeout("empty()",1200);
                            document.cookie = "login=false";
                            setTimeout("takeTrue('login')",1200);
                        }
                    }
                    else if(JSON.stringify(responseData.statusCode) == -1){
                        if(get_cookie("login") == "true"){
                            var str = '<div class="hint" id="hint">\n' +
                                '            <p>账户未激活，请前往激活</p>\n' +
                                '        </div>';
                            document.getElementById("hintWindow").innerHTML=str;
                            hintStyle();
                            setTimeout("empty()",1200);
                            document.cookie = "login=false";
                            setTimeout("takeTrue('login')",1200);
                        }
                    }
                    else{
                        setUserName(user);
                        setPwd(pwd);
                        setToken(JSON.stringify(responseData.token));
                        login();
                        setTimeout("skip('homepage.html')",800);
                    }
                }
            }
            xhr.open("POST","http://39.107.74.159:5000/beta/login",true);
            xhr.setRequestHeader("Content-type","application/json");
            xhr.send(jsonData1);
        }
        else{
            xhr.onreadystatechange = function(){
                if(xhr.readyState==4){
                    var responseData = JSON.parse(xhr.responseText);
                    if(responseData.status == "Error:Failed to register!"){
                        if(get_cookie("register") == "true"){
                            var str = '<div class="hint3" id="hint">\n' +
                                '            <p>该账号已被注册或邮箱不存在</p>\n' +
                                '        </div>';
                            document.getElementById("hintWindow").innerHTML=str;
                            hintStyle();
                            setTimeout("empty()",1200);
                            document.cookie="register=false";
                            setTimeout("takeTrue('register')",1200);
                        }
                    }
                    else{
                        var str = '<div class="hint4" id="hint">\n' +
                            '            <p>注册成功，请前往邮箱激活！若长时间未收到邮件，请检查邮箱正确性</p>\n' +
                            '        </div>';
                        document.getElementById("hintWindow").innerHTML=str;
                        hintStyle();
                        setEmail(email);
                        setTimeout("skip('homepage.html')",1800);
                    }
                }
            }
            xhr.open("POST","http://39.107.74.159:5000/beta/register",true);
            xhr.setRequestHeader("Content-type","application/json");
            xhr.send(jsonData2);
        }
    }
}