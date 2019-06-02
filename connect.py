import pymysql
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import random,string
from newTable import createTable
import datetime,time
from spider.spider import Spider
class DataBase:
#init中修改连接的参数，  email_for_pwd中 URL未修改
    def __init__(self):
        self.codeSource = string.ascii_letters + string.digits  # 字母及数字，用来生成验证码
        #self.activated = 0  # 账号是否被激活，若无则为0
        self.sender = 'buaamyflight@163.com'  # 服务器邮箱
        pwd = '2019flight'  # 密码
        # self.connect = pymysql.connect(host="localHost", port=3306, user="root", passwd="se2019flight", db="flight")
        self.para = {  #数据库连接参数
            'host': 'localHost',
            'port': 3306,
            'user': 'root',
            'password':'se2019flight',
            'db': 'flight'
        }
        self.para2 = { #邮箱连接参数
            'mail_host' : 'smtp.qq.com',
            'sender' : '1129720379@qq.com',
            'pwd' : 'npozgmigvhnhjbaa'   #授权码
        }
        # 初始化邮箱连接
        self.mailConnect()

        # 建立数据库连接
        self.dbConnect()

        # createTable(self.cur)     #创建表

    #建立数据库连接
    def dbConnect(self):
        try:
            self.connect = pymysql.connect(host=self.para['host'], port=self.para['port'], user=self.para['user'], passwd=self.para['password'], db=self.para['db'],charset = 'utf8')
            self.cur = self.connect.cursor()
        except Exception as e:
            print(e)
        else:
            print("数据库连接成功")

    #建立邮箱连接
    def mailConnect(self):
        try:
            self.smtpObj = smtplib.SMTP_SSL(self.para2['mail_host'], 465)  # 启用SSL发信, 端口一般是465
            self.smtpObj.login(self.para2['sender'],self.para2['pwd'])  # 登录验证
        except Exception as e:
            print(e)
        else:
            print("邮箱连接成功")
    # 登记用户信息，并发送激活邮件，登记失败（如账号已存在）返回0，成功返回1

    def register(self,userID, pwd, email):
        sql1 = "select count(*) from userMessage where userID = %s"
        sql2 = "insert into userMessage values (%s,%s,%s,%s,'110',%s)"
        self.cur.execute(sql1, 'userID')  # 查询是否账号已存在
        count = self.cur.fetchone()[0]
        if (count == 1):
            print("用户名已存在")
            return 0
        else:  # 添加信息至数据库，并发送激活邮件
            urlHead = 'http://114.115.134.119:5000/beta/active/'  # username/token
            Code = ''.join(random.sample(self.codeSource, 10))
            activateCode = urlHead + userID + '/' + Code   # 生成激活链接

            try:
                res = [userID, pwd, email, Code, 0]
                self.cur.execute(sql2, res)
                self.connect.commit()  # 提交数据库事务

                # 生成邮件
                msg = MIMEText('点击下面链接来激活账号: ' + activateCode, 'plain', 'utf-8')
                msg['Subject'] = "激活账号"  # Header('确认注册', 'utf-8')
                msg['From'] = formataddr(["flight", self.para2['sender']])
                msg['To'] = formataddr(["client", email])
                #print("com")
                print("activate url:",activateCode)
                self.mailConnect()
                self.smtpObj.sendmail(self.para2['sender'], email, msg.as_string())  # 发送邮件

            except Exception as e:
                print(e)
                return 0
            else:
                print(userID + " 的激活邮件已发送")
        return 1

    # 根据收到的激活信息，激活账号，激活成功返回1，不成功返回0
    def activate(self,userID, ident_code):
        sql = "select count(*) from userMessage where userID = %s and activateCode = %s"
        sql1 = "update userMessage set activate = 1 where userID = %s"
        res = [userID, ident_code]
        try:
            self.cur.execute(sql, res)
            count = self.cur.fetchone()[0]
            if (count == 1):
                self.cur.execute(sql1, userID)  # 将activate改为1，变为激活状态
                self.connect.commit()
                print("激活成功")
                return 1
            else:
                return 0
        except Exception as e:
            print(e)
            return 0

    # 登录，返回字典，status值：1,0，-1  code为正确登录收到的状态码
    def login(self,userID, pwd):
        # sql1 = "select count(*) from userMessage where userID = %s and password = %s"
        sql = "select activate from userMessage where userID = %s and pwd = %s"
        sql2 = "insert into state values(%s,%s)"
        ret = {}
        ret['status'] = 0
        try:
            res = [userID, pwd]
            self.cur.execute(sql, res)
            count = self.cur.fetchone()
            if (count is None):
                print("密码错误")
                return ret
            print("Activate records find:",int.from_bytes(count[0], byteorder="big"))
            if (int.from_bytes(count[0], byteorder="big") == 1):
                print("密码正确且账号已激活")
                stateCode = ''.join(random.sample(self.codeSource, 10))
                ret['status'] = 1
                ret['code'] = stateCode
                res = [userID,stateCode]
                self.cur.execute(sql2,res)
                self.connect.commit()
                return ret
            else:
                print("账号未激活")
                ret['status'] = -1
                return ret
        except Exception as e:
            print(e)
        return 0

    
    #判断账号是否是登录状态
    def isLogedIn(self,userID,stateCode):
        sql2 = "select count(*) from state where userID = %s and s_code = %s"
        try:
            res2 = [userID, stateCode]
            self.cur.execute(sql2, res2)
            count = self.cur.fetchone()[0]
            if (count == 0):  # 状态码匹配失败
                return 0
            else:
                return 1
        except Exception as e:
            print(e)
        return 0

    #获取用户详细信息：邮箱，
    def get_user_info(self,userID):
        sql = 'select email from userMessage where userID = %s'
        try:
            self.cur.execute(sql,userID)
            ret = self.cur.fetchone()[0]
            return ret
        except Exception as e:
            print(e)
        return 0

    #判断用户修改码是否有效
    def is_modifiable(self,userID,Code):
        sql = "select count(*) from userMessage where userID = %s and modifyCode = %s"
        res = [userID,Code]
        try:
            self.cur.execute(sql,res)
            count = self.cur.fetchone()[0]
            if(count == 1):
                print('可修改')
                return 1
            else:
                print('修改码失效')
        except Exception as e:
            print (e)
        return 0
    # 修改个人信息
    def updateMessage(self,userID,pwd):
        # print(args)
        if(len(pwd) <6 or len(pwd)>13):
            print('密码过短或过长')
            return 0
        sql1 = "update userMessage set pwd = %s , modifyCode = '110' \
               where userID = %s "

        res = [pwd, userID]
        try:
            self.dbConnect()
            line = self.cur.execute(sql1, res)
            self.connect.commit()
        except Exception as e:
            print(e)
        if (line == 1):
            print("修改成功")
            return 1
        print("修改失败")
        return 0

    # 关注函数，成功插入返回1，失败返回0，账号未登录返回-1 时间数据如：2019-08-12
    def focus(self,userID, flightID, f_date,current_status,identity:int):
        sql = "insert into map values(%s,%s,%s,%s,%s,0)"
        try:
            res = [userID, flightID, f_date,current_status,identity]
            self.cur.execute(sql, res)
            self.connect.commit()
            print("关注建立成功")
        except Exception as e:
            print(e)
            return 0
        return 1
     # 取消关注的航班
    def unfocus(self,userID, flightID, f_date):
        sql = "delete from map where userID = %s and flightID = %s and date = %s"
        try:
            res = [userID, flightID, f_date]
            self.cur.execute(sql, res)
            self.connect.commit()
            print("取消关注成功")
        except Exception as e:
            print(e)
            return 0
        return 1
    #获取关注列表,返回一个列表，每个元素是一个元组，为航班号和时间
    def getList(self,userID):
        sql2 = "select flightID ,date from map where userID = %s"
        try:
            self.cur.execute(sql2, userID)
            flist = self.cur.fetchall()
            # print(flist)
            flist = list(flist)
            return flist
        except Exception as e:
            print(e)
        return []

    #退出登录
    def logout(self,userID,stateCode):
        sql = "delete from state where userID = %s and s_code = %s"
        try:
            res = [userID, stateCode]
            count = self.cur.execute(sql, res)
            self.connect.commit()
            if(count == 1):
                print("注销成功")
                return 1
        except Exception as e:
            print(e)
        print("注销失败")
        return 0

    #发送修改密码的邮件
    def email_for_pwd(self,userID):
        sql = 'select email from userMessage where userID = %s'
        sql2 = 'update userMessage set modifyCode = %s where userID = %s'
        urlHead = 'http://114.115.134.119:5000/beta/modifyPassword'  # username/token
        Code = ''.join(random.sample(self.codeSource, 10))
        changeUrl = urlHead + '/' + userID + '/' + Code  # 生成修改密码链接

        try:
            self.cur.execute(sql,userID)
            email = self.cur.fetchone()[0]
            print(email)
            msg = MIMEText('请点击下面链接来修改密码: ' + changeUrl, 'plain', 'utf-8')
            msg['Subject'] = "密码修改"  # Header('确认注册', 'utf-8')
            msg['From'] = formataddr(["flight", self.para2['sender']])
            msg['To'] = formataddr(["client", email])
            self.mailConnect()
            self.smtpObj.sendmail(self.para2['sender'], email, msg.as_string()) #发送邮件

            res = [Code,userID]
            self.cur.execute(sql2,res)
            self.connect.commit()
            print(userID + ' 的修改链接发送成功')
            return 1
        except Exception as e:
            print(e)
            print('修改链接发送失败')
        return 0

    #根据航班号获取关注它的所有用户列表 并向用户发送提醒邮件    暂时没用
    def send_warning_email1(self,flightID,time):
        print(flightID,time)
        sql =" select map.userID,email from map \
            left JOIN userMessage on map.userID = userMessage.userID \
            where flightID = %s and date = %s"
        res = [flightID, time]
        try:
            self.cur.execute(sql, res)
            user_list = self.cur.fetchall()
            user_list = list(user_list)
            print(user_list)
            # return user_list
        except Exception as e:
            print(e)
        else:
            print('获取用户列表成功')

        for info in user_list:
            self.send_one_warning(info[0],info[1],flightID)

    #遍历关注列表，查看航班状态是否发生变化
    def send_warning_email(self):
        print("开始检查延误")
        sql = 'select map.userID,flightID,date,f_status,email from map \
               left JOIN userMessage on map.userID = userMessage.userID'

        try:
            self.cur.execute(sql)
            records = self.cur.fetchall()
            for record in records:
                # record[0]:userID  [1]:flightID [2]:date [3]:f_state  [4]:email

                time = record[2].strftime('%Y%m%d')

                allData = Spider().get_base_info(record[1],time)
                for i in range(1):
                    thisRecord = allData[i]
                    if (thisRecord['flight_status'] != record[3]):
                        # print(record[0], record[4], record[1])
                        self.send_one_warning(record[0], record[4], record[1],thisRecord['flight_status'],record[2])
                        break

        except Exception as e:
            print("发送失败")
            print(e)
    #根据用户ID 和邮件发送提醒邮件,并修改记录状态
    def send_one_warning(self,userID,email,flightID,status,time):
        content = '尊敬的航班助手用户 ' + userID + ' :您关注的航班 ：' + flightID +'状态改变为' + status + '，具体情况请登录航班助手进行查看'
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = "航班状态改变提醒"  # Header('确认注册', 'utf-8')
        msg['From'] = formataddr(["flight", self.para2['sender']])
        msg['To'] = formataddr(["client", email])
        self.mailConnect()
        self.smtpObj.sendmail(self.para2['sender'], email, msg.as_string())

        sql = 'update map set f_status = %s where userID = %s and flightID = %s and date = %s'
        res = [status,userID,flightID,time]
        self.cur.execute(sql,res)
        self.connect.commit()
        print(userID + '的提示邮件已发送,关注状态已修改')

    # 检查航班时间，以便发送相关信息
    def send_information(self):
        current_day = datetime.datetime.now().strftime('%Y-%m-%d')
        print(current_day)
        #获取今天起飞且未被通知信息的关注记录
        sql = "select map.userID,flightID,date,email , map.identity from map \
            left JOIN  userMessage on map.userID = userMessage.userID\
            where informed = 0 and date = '%s'"%current_day
        print(sql)
        try:
            self.cur.execute(sql)

            records = self.cur.fetchall()
            print(1)
            for record in records:  # [0]:userID  [1]:flightID,[2]:date [3]:email  [4]:identity []:
                plan_date = record[2].strftime("%Y%m%d")

                allData = Spider().get_base_info(record[1], plan_date)
                plan_time =plan_date + ' 19:20'
                plan_time = time.strptime(plan_time,"%Y%m%d %H:%M")
                un_time = time.mktime(plan_time)  #转为时间戳
                seconds = int(un_time - time.time())
                print('time %d',seconds )
                if(seconds <=0 ):  #已起飞
                    if(record[4] == 2): #接机人
                        content = '尊敬的航班助手用户 ' + record[0] + ' :您关注的航班 ：' + record[1] + '已经起飞，预计在' + allData['arri_time_act'] +'到达，更多信息，请登录航班助手查看'
                        self.send_information_email(record[0],record[3],record[1],record[2],content)
                elif(seconds <=14400):#间隔小于四小时,开始通知
                    if (record[4] == 0):  # 乘客，
                        content = '尊敬的航班助手用户 ' + record[0] + ' :您关注的航班 ：' + record[1] + '将于' + allData['dep_time_plan'] + '起飞，请提前规划好您的行程，更多信息，请登录航班助手查看'
                    elif (record[4] == 1):  # 送机人
                        content = '尊敬的航班助手用户 ' + record[0] + ' :您关注的航班 ：' + record[1] + '将于' + allData['dep_time_plan'] + '起飞，请提前规划好您的行程，更多信息，请登录航班助手查看'
                    else:
                        return 0
                    self.send_information_email(record[0], record[3], record[1], record[2], content)
        except Exception as e:
            print(e)

    #为某个客户发送提醒信息
    def send_information_email(self,userID,email,flightID,time,content):
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['Subject'] = "航班提醒"  #
        msg['From'] = formataddr(["flight", self.para2['sender']])
        msg['To'] = formataddr(["client", email])
        self.mailConnect()
        self.smtpObj.sendmail(self.para2['sender'], email, msg.as_string())

        sql = 'update map set informed =1 where userID = %s and flightID = %s and date = %s'
        try:
            self.cur.execute(sql,[userID,flightID,time])
            self.connect.commit()
            return 1
        except Exception as e:
            print(e)
        return 0

    #管理员登录，
    def login_mana(self,userID,pwd):
        sql = 'select count(*) from manager where userID = %s and pwd = %s'
        sql2 = "insert into state values(%s,%s)"
        res = [userID,pwd]
        stateCode = ''.join(random.sample(self.codeSource, 10))
        ret = {}  #返回值
        try:
            self.cur.execute(sql,res)
            count = self.cur.fetchone()[0]
            if(count == 1):
                res = [userID,stateCode]
                self.cur.execute(sql2,res)
                self.connect.commit()
                print("管理员登录成功")
                ret['status'] = 1
                ret['code'] = stateCode
                return ret
        except Exception as e:
            print(e)
            print("管理员账号或密码错误")
        ret['status'] = 0
        return ret
    def get_user_list(self):
        sql = 'select userID,email from userMessage'
        try:
            self.cur.execute(sql)
            userList = self.cur.fetchall()
            userList = list(userList)
            return userList
        except Exception as e:
            print(e)
        return []

    #管理员模块，删除用户账号
    def delete_user(self,userID):
        sql = 'delete from userMessage where userID = %s '
        sql2 = 'delete from map where userID = %s'
        sql3 = 'delete from state where userID = %s'
        # sql4 = 'delete from focus_records where userID = %s'
        try:
            self.cur.execute(sql,userID)
            self.cur.execute(sql2, userID)
            self.cur.execute(sql3, userID)
            # self.cur.execute(sql4, userID)
            self.connect.commit()
            return 1
        except Exception as e:
            print(e)
        return 0
    #管理员手动发送测试邮件
    def send_test_email(self,userID,flightID,date):
        sql = "select email from userMessage where userID = %s"

        try:
            self.cur.execute(sql,userID)
            email = self.cur.fetchone()[0]

            content = '尊敬的航班助手用户 ' + userID + ' :您关注的航班 ：' + flightID + '状态改变，具体情况请登录航班助手进行查看'
            msg = MIMEText(content, 'plain', 'utf-8')
            msg['Subject'] = "航班状态改变提醒"  # Header('确认注册', 'utf-8')
            msg['From'] = formataddr(["flight", self.para2['sender']])
            msg['To'] = formataddr(["client", email])
            self.mailConnect()
            self.smtpObj.sendmail(self.para2['sender'], email, msg.as_string())
            return 1
        except Exception as e:
            print(e)
        return 0

    #添加静态航班
    def add_flight(self,*args):
        sql = "insert into staticflight values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            self.cur.execute(sql,args)
            self.connect.commit()
            return 1
        except Exception as e:
            print(e)
        return 0

    #删除航班
    def delete_flight(self,flightID,date):
        sql = "delete from staticflight where flightID = %s and f_date = %s"
        date = time.strptime(date,'%Y%m%d')
        date = time.strftime('%Y-%m-%d', date)
        try:
            res = [flightID,date]
            self.cur.execute(sql,res)
            self.connect.commit()
            return 1
        except Exception as e:
            print(e)
        return 0
    #修改航班
    def modify_flight(self,*args):
        sql = "update staticflight set airlines = %s,flightID= %s,f_date = %s,p_takeoff = %s,a_takeoff = %s,departurePlace =%s,\
              p_arrival = %s,a_arrival = %s,arrivalPlace = %s,currentStatus = %s where flightID = %s and f_date = %s"
        try:
            f_list = list(args)
            f_list.append(args[1])
            f_list.append(args[2])
            print(f_list)
            self.cur.execute(sql,f_list)
            self.connect.commit()
            return 1
        except Exception as e:
            print(e)
        return 0
    #查航班
    def searchFlight(self,flightID,date):
        sql = " select * from staticflight where flightID = %s and f_date = %s  "
        date = time.strptime(date, '%Y%m%d')
        date=time.strftime('%Y-%m-%d', date)
        try:
            res = [flightID,date]
            self.cur.execute(sql,res)
            record = self.cur.fetchone()
            return record
        except Exception as e:
            print(e)
        return 0

    #根据字典，转换为字符串
    def switch_to_list(self,dic):
        cols = ''
        values = ''
        for key,value in dic.items():
            if value != '--':
                cols += key + ','
                if isinstance(value, str):
                    values += value.__repr__() + ','
                else:
                    values += str(value) + ','

        return cols,values

    #根据航班号发送预警邮件
    def send_email_code(self,flightCode,f_date):
        sql = """select map.userID,email from map 
            left JOIN userMessage on userMessage.userID = map.userID
            where flightID = %s and date = %s"""
        try:
            res = [flightCode,f_date]
            self.cur.execute(sql,res)
            user_list = self.cur.fetchall()
            for record in user_list:
                self.send_test_email(record[0],flightCode,f_date)
            return 1
        except Exception as e:
            print(e)
        return 0

    #添加详细静态航班
    def add_flight_detail(self,dic):
        #转化日期格式
        if ('flight_date' in dic.keys()):
            t = dic['flight_date']
            ttime = time.strptime(t, "%Y%m%d")
            dic['flight_date'] = time.strftime('%Y-%m-%d', ttime)

        # sql = "insert into map(%s) values(%s)"
        cols,values = self.switch_to_list(dic)
        # res = [cols[:-1], values[:-1]]
        sql = "insert into flightdetail(%s) values(%s)"%(cols[:-1],values[:-1])
        # print(res)
        try:
            self.cur.execute(sql)
            self.connect.commit()
            return 1
        except Exception as e:
            print(e)
        return 0

    #更新航班数据
    def update_flight_detail(self,dic:dict):
        sql = """update flightdetail set %s where flight_code = %s and flight_date = %s and dep_airp_code = %s and arri_airp_code = %s"""
        sql2 = 'select flight_status from flightdetail where flight_code = %s and flight_date = %s and dep_airp_code = %s and arri_airp_code = %s'

        if ('flight_date' in dic.keys()):
            t = dic['flight_date']
            ttime = time.strptime(t, "%Y%m%d")
            dic['flight_date'] = time.strftime('%Y-%m-%d', ttime)


        s_str = ''
        for key,value in dic.items():  #将字典转化为 key = value,。。。的形式
            if value!= '--':
                s_str += key + '='
                if isinstance(value, str):
                    s_str += '\''+value + '\','
                else:
                    s_str += str(value) + ','


        try:
            # res = [s_str,dic['flight_code'] ,dic['flight_date']]
            #获取原来状态
            print('22')
            self.cur.execute(sql2,[dic['flight_code'],dic['flight_date'],dic['dep_airp_code'],dic['arri_airp_code']])
            print('11')
            pre_status = self.cur.fetchone()[0]

            #更新航班信息
            sql = sql%(s_str[:-1],dic['flight_code'].__repr__() ,dic['flight_date'].__repr__(),dic['dep_airp_code'].__repr__(),dic['arri_airp_code'].__repr__())
            print(sql)
            self.cur.execute(sql)
            self.connect.commit()

            #比较
            if( 'flight_status' in dic.keys()  and pre_status != dic['flight_status']):
                self.send_email_code(dic['flight_code'],dic['flight_date'])

            return 1
        except  Exception as e:
            print(e)
        return 0

    #删除某条航班
    def delete_flight_detail(self,dic:dict):
        sql = "delete from flightdetail where flight_code = %s and flight_date = %s and dep_airp_code = %s and arri_airp_code = %s"
        #修改日期格式
        if ('flight_date' in dic.keys()):
            t = dic['flight_date']
            ttime = time.strptime(t, "%Y%m%d")
            dic['flight_date'] = time.strftime('%Y-%m-%d', ttime)

        try:
            res = [dic['flight_code'], dic['flight_date'],dic['dep_airp_code'],dic['arri_airp_code']]
            self.cur.execute(sql,res)
            change_lines = self.cur.rowcount
            self.connect.commit()
            if(change_lines >0):
                return 1
            return 2
        except Exception as e:
            print(e)
        return 0

    #查找
    def search_flight_detail(self,dic:dict):
        sql = "select * from flightdetail where %s"
        ret = {}
        if ('flight_date' in dic.keys()):
            t = dic['flight_date']
            ttime = time.strptime(t, "%Y%m%d")
            dic['flight_date'] = time.strftime('%Y-%m-%d', ttime)

        sql_str = ''
        for key,value in dic.items():
            sql_str += key +'='
            if isinstance(value,str):
                sql_str += value.__repr__() +' and '
            else:
                sql_str += str(value) + ' and '
        try:
            sql = sql%sql_str[:-4]
            self.cur.execute(sql)
            ret['value'] = list(self.cur.fetchall())
            ret['status'] = 1
            return ret
        except Exception as e:
            print(e)
        ret['status'] = 0
        return ret

    #
# register(userID="yanhuia", pwd="12345", email="1129720379@qq.com")
# login("yanhui6","12345")
# createTable(cur)
# activate("yanhui","yanhuiGn5mCbpHuB")
# connect.commit()
# unfocus('12345',"yanhui","a123","2019-08-12 ")

pass
#db = DataBase()
#print(db.getList("yanhui",'1234'))
# db.activate("yan","p3lwgjXmys")
# db.login(userID="yan", pwd="2344")
# print(db.login_mana('xiaohong','111'))
# db.updateMessage("yan","99999")
# db.register('yan','2344','1419471045@qq.com')
# print(db.isLogedIn('yan','e1bUCTgpol'))
# db.updateMessage('e1bUCTgpol','yan','1234567')
# db.logout('xiaohong','UlVpQD46gr')
# db.focus('yan','as12345','2019-08-12 ','1111111111')
# db.unfocus('yan','ac99','2019-08-12 ')
# db.email_for_pwd('yan')
# db.send_warning_email()
# db.is_modifiable('yan','AIhf5wMdXO')
# db.send_test_email('yan','as123','2019-08-12')
# print(db.getList('yan'))
#db.add_flight('bbbbb','as1111','20190506','1234','1234','beijing','1344','1345','shanghai','yanhou')
# print(db.searchFlight('as1234','20190506'))
# db.modify_flight('bbb','as1234','20190506','1245','1245','beijing','1344','1345','shanghai','anhou')
#db.delete_flight('as1234','20190506')