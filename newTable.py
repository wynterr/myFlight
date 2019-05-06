
#创建各个表的初始函数
def createTable(cur):
    #用户信息表
    sql1 = "create table userMessage(\
	userID varchar(50) primary key,\
	pwd varchar(50) not null,\
	email varchar(50) not null,\
    activateCode varchar(50) not null,\
    modifyCode varchar(50) default '110',\
    activate bit not null\
)"
    #用户关注表
    sql3 = "create table map(\
	userID varchar(50) ,\
	flightID varchar(50) ,\
    date datetime,\
    f_status varchar(50),\
	primary key(userID, flightID,date),\
	foreign key(userID) references userMessage(userID)\
 )"
    #状态码表
    sql4 = "create table state(\
	userID varchar(50) not null,\
	s_code varchar(50) not null\
)"
    #管理员信息表
    sql5 = "create table manager(\
	userID varchar(50) primary key,\
	pwd varchar(50) not null\
)"
    #用户关注记录表
    sql6 = "create table focus_record(\
	userID varchar(50) ,\
	flightID varchar(50),\
	date datetime,\
	primary key(userID, flightID,date)\
)"

    '''''#机场表
    sql4= "create table airports(\
	airportCode varchar(50) primary key,\
	airportName varchar(50) not null,\
	countryName	varchar(50) not null,\
	airportPy	varchar(50) not null,\
	airportPyShort	varchar(50) not null,\
	airportEnName	varchar(50) not null,\
	more varchar(50)\
)"
    #航班信息表
    sql2 = "create table flight(\
    flightCode varchar(50) ,\
    cityFrom varchar(50) not NULL,\
    cityTo varchar(50) not null,\
    date datetime,\
    primary key(flightCode,date)\
)"'''
    try:
        cur.execute(sql1)
        print("success to create user table")
        cur.execute(sql3)
        print("success to create map table")
        cur.execute(sql4)
        print("success to create state table")
        cur.execute(sql5)
        cur.execute(sql6)
        '''''
        cur.execute(sql2)
        print("success to create flight table")
        cur.execute(sql4)
        print("success to create airport table")
        '''
    except Exception as e:
        print(e)
