
#创建各个表的初始函数
def createTable(cur):
    #用户信息表
    sql1 = "create table userMessage(\
	userID varchar(50) primary key,\
	pwd varchar(50) not null,\
	email varchar(50) not null,\
    activateCode varchar(50) not null,\
    activate bit not null\
)"
    #用户关注表
    sql3 = "create table map(\
	userID varchar(50) ,\
	flightID varchar(50) ,\
    date datetime,\
	primary key(userID, flightID,date),\
	foreign key(userID) references userMessage(userID)\
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
        '''''
        cur.execute(sql2)
        print("success to create flight table")
        cur.execute(sql4)
        print("success to create airport table")
        '''
    except Exception as e:
        print(e)