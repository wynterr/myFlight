import pymysql
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import random,string
from newTable import createTable

class DataBase:


    def __init__(self):
        self.codeSource = string.ascii_letters + string.digits  # 字母及数字，用来生成验证码
        #self.activated = 0  # 账号是否被激活，若无则为0
        self.sender = 'buaamyflight@163.com'  # 服务器邮箱
        pwd = '2019flight'  # 密码

        # 初始化邮箱连接
        #smtp = smtplib.SMTP()
        #smtp.connect('smtp.163.com', '25')
        #smtp.login(self.sender, pwd)  # username  ,pwd
        #print("邮箱连接成功")

        # 建立数据库连接
        try:
            #self.connect = pymysql.connect(host="localHost", port=3306, user="root", passwd="yh112972m", db="flight")
            self.connect = pymysql.connect(host="localHost", port=3306, user="root", passwd="se2019flight", db="flight")
            self.cur = self.connect.cursor()
        except Exception as e:
            print(e)
        else:
            print("数据库连接成功")

        #createTable(self.cur)     #创建表

    # 登记用户信息，并发送激活邮件，登记失败（如账号已存在）返回0，成功返回1
    def register(self,userID, pwd, email):
        sql1 = "select count(*) from userMessage where userID = %s"
        sql2 = "insert into userMessage values (%s,%s,%s,%s,%s)"
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
                msg['Subject'] = "queren"  # Header('确认注册', 'utf-8')
                msg['From'] = formataddr(["flight", self.sender])
                msg['To'] = formataddr(["client", email])
                #print("com")
                print(activateCode)
                #self.smtp.sendmail(self.sender, email, msg.as_string())  # 发送邮件
                #print("aa")
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
            print(int.from_bytes(count[0], byteorder="big"))
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

    # 修改个人信息
    def updateMessage(self,stateCode,*args):
        # print(args)
        sql1 = "update userMessage set userID = %s ,pwd = %s , email = %s  \
               where userID = %s and exists(\
	            select * from state\
	            where userID = %s and s_code = %s\
)"
        res = [args[0], args[1], args[2], args[0],args[0],stateCode]
        try:
            line = self.cur.execute(sql1, res)
            self. connect.commit()
        except Exception as e:
            print(e)
        if (line == 1):
            print("修改成功")
            return 1
        print("修改失败")
        return 0

    # 关注函数，成功插入返回1，失败返回0，账号未登录返回-1 时间数据如：2019-08-12 00:00:00
    def focus(self,userID, flightID, f_date):
        sql = "insert into map values(%s,%s,%s)"
        try:
            res = [userID, flightID, f_date]
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
# register(userID="yanhuia", pwd="12345", email="1129720379@qq.com")
# login("yanhui6","12345")
# createTable(cur)
# activate("yanhui","yanhuiGn5mCbpHuB")
# connect.commit()
# unfocus('12345',"yanhui","a123","2019-08-12 00:00:00")


# db = DataBase()
#print(db.getList("yanhui",'1234'))
# db.activate("yanhuib","1jLAh7IFVN")
# db.login(userID="yanhuib", pwd="12345")
# updateMessage("yanhui","123456","11239@qq.com")