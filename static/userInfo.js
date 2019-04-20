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
}
function notLogin() {
    alert("您尚未登录！");
}
function logout() {
    alert("您已登出！");
    document.cookie="islogin=0";
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
function toFlightNum(url){
    window.location.href = "flight_num.html";
}
function toTakeOff(url){
    window.location.href = "takeoff_land.html";
}
function toChangePwd(url){
    if(get_cookie("islogin") == 1){
        window.location.href = "changepwd.html";
    }
    else{
        notLogin();
        if(url != "flightInfo.html" && url != "detialInfo.html"){
            window.location.href = url;
        }
    }
}
function toMyInfo(url) {
    if(get_cookie("islogin") == 1){
        window.location.href = "personalinfo.html";
    }
    else{
        notLogin();
        if(url != "flightInfo.html" && url != "detialInfo.html"){
            window.location.href = url;
        }
    }
}
function toLogOff(url){
    if(get_cookie("islogin") == 1){
        logout();
        var jsonData = JSON.stringify({
            username:get_cookie("user"),
            token:deleteMark(get_cookie("token")),
        })
        var xhr = ajaxFunction();
        var str = "";
        if(xhr.readyState==4){
            responseData = JSON.parse(xhr.responseText);
            var length = responseData.length;
            for(var i = 0;i < length;i++){
                var followInfo = deleteMark(JSON.stringify(responseData[i].flightCode)) + "_" + deleteMark1(JSON.stringify(responseData[i].date));
                document.cookie = followInfo+"=0";
            }
        }
        xhr.open("POST","http://114.115.134.119:5000/beta/getFocusedFlights",true);
        xhr.setRequestHeader("Content-type","application/json");
        xhr.send(jsonData);
        window.location.href = "homepage.html";
    }
    else{
        notLogin();
        if(url != "flightInfo.html" && url != "detialInfo.html"){
            window.location.href = url;
        }
    }
}
function toFollowList(url) {
    if(get_cookie("islogin") == 1){
        window.location.href = "followlist.html";
    }
    else{
        notLogin();
        if(url != "flightInfo.html" && url != "detialInfo.html"){
            window.location.href = url;
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
