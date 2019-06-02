function setUserName(username){
    document.cookie="Admuser="+username;
}
function setToken(token) {
    document.cookie="Admtoken="+token;
}
function login(){
    document.cookie="Admislogin=1";
}
function notLogin() {
    document.cookie = "Admnotlogin=false";
    var str = '<div class="hint" id="hint">\n' +
        '            <p>您尚未登录</p>\n' +
        '        </div>';
    document.getElementById("hintWindow").innerHTML=str;
    hintStyle();
    setTimeout("takeTrue('Admnotlogin')",1200);
}
function logout() {
    document.cookie="Admislogin=0";
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
function toAdmLogOff(){
    if(get_cookie("Admtoken") == 0){
        alert(1);
    }
    else{
        var xhr = AjaxFunction();
        var jsonData = JSON.stringify({
            adminname:get_cookie("Admuser"),
            token:DeleteMark(get_cookie("Admtoken")),
        })
        xhr.onreadystatechange = function(){
            if(xhr.readyState==4){
                var responseData = JSON.parse(xhr.responseText);
                if(responseData.status == "success!"){
                    logout();
                    setTimeout("skip('AdmHomePage.html')",800);
                }
                else{
                    if(get_cookie("Admlogout") == "true"){
                        document.cookie='Admlogout=false';
                        var str = '<div class="hint" id="hint">\n' +
                            '            <p>登出失败</p>\n' +
                            '        </div>';
                        document.getElementById("hintWindow").innerHTML=str;
                        hintStyle();
                        setTimeout("empty()",1200);
                        setTimeout("takeTrue('Admlogout')",1200);
                    }

                }
            }
        }
        xhr.open("POST","http://114.115.134.119:5000/beta/manaLogout",true);
        xhr.setRequestHeader("Content-type","application/json");
        xhr.send(jsonData);
    }
}
function toUserPushMes() {
    if(get_cookie("Admislogin") == 1){
        window.location.href = "userPushMessage.html";
    }
    else{
        if(get_cookie("Admnotlogin") == "true"){
            notLogin();
            setTimeout("empty()",1200);
        }
    }
}
function toFlightPush() {
    if(get_cookie("Admislogin") == 1){
        window.location.href = "flightPushMessage.html";
    }
    else{
        if(get_cookie("Admnotlogin") == "true"){
            notLogin();
            setTimeout("empty()",1200);
        }
    }
}

function toUserLogOff() {
    if(get_cookie("Admislogin") == 1){
        window.location.href = "userLogOff.html";
    }
    else{
        if(get_cookie("Admnotlogin") == "true"){
            notLogin();
            setTimeout("empty()",1200);
        }
    }
}
function toAddFlight() {
    if(get_cookie("Admislogin") == 1){
        window.location.href = "addFlightInfo.html";
    }
    else{
        if(get_cookie("Admnotlogin") == "true"){
            notLogin();
            setTimeout("empty()",1200);
        }
    }
}
function toDeleteFlight() {
    if(get_cookie("Admislogin") == 1){
        window.location.href = "deleteFlightInfo.html";
    }
    else{
        if(get_cookie("Admnotlogin") == "true"){
            notLogin();
            setTimeout("empty()",1200);
        }
    }
}
function toModifyFlight() {
    if(get_cookie("Admislogin") == 1){
        window.location.href = "modifyFlightInfo.html";
    }
    else{
        if(get_cookie("Admnotlogin") == "true"){
            notLogin();
            setTimeout("empty()",1200);
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
function takeTrue(str) {
    document.cookie = str +"=true";
}
function skip(a){
    window.location.href = a;
}