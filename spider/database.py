import pymysql as sql
from aipport_data import CitiesinbyAZ
from spider.spider import *


class Database(object):
    _db_name = 'flights_data'
    _tb1_name = "flights_tb"
    _tb2_name = "flys_tb"
    def __init__(self):
        self.db = sql.connect('localhost', 'root', '594127', autocommit = True)
        self.cursor = self.db.cursor()
        self.cursor.execute('USE flights_data;')
        
    def create_tb(self):
        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s(
                flight_code VARCHAR(8) NOT NULL,
                flight_date DATE NOT NULL,
                dep_airp_code CHAR(3) NOT NULL,
                arri_airp_code CHAR(3) NOT NULL,
                corp_name VARCHAR(50),
                shared_flight VARCHAR(8),
                dep_city VARCHAR(20),
                dep_airp_name VARCHAR(40) NOT NULL,
                dep_time_plan TIME NOT NULL,
                dep_time_pred TIME,
                dep_time_act TIME,
                local_dep_date_plan VARCHAR(20),
                local_dep_date_act VARCHAR(20),
                checkin_counter VARCHAR(30),
                dep_gate VARCHAR(10),
                dep_airp_weather VARCHAR(50),
                dep_airp_pm25 INT,
                dep_airp_flow VARCHAR(20),
                arri_city VARCHAR(20),
                arri_airp_name VARCHAR(40) NOT NULL,
                arri_time_plan TIME NOT NULL,
                arri_time_pred TIME,
                arri_time_act TIME,
                local_arri_date_plan VARCHAR(20),
                local_arri_date_act VARCHAR(20),
                lug_turn VARCHAR(10),
                arri_gate VARCHAR(10),
                arri_airp_weather VARCHAR(50),
                arri_airp_pm25 INT,
                arri_airp_flow VARCHAR(20),
                flight_status VARCHAR(10) NOT NULL,
                ontime_rate FLOAT,
                ave_ontime_rate FLOAT,
                pre_flight VARCHAR(50),
                delay_time_tip VARCHAR(60),
                flight_distance INT,
                flight_dur_time VARCHAR(30),
                plane_type VARCHAR(50),
                plane_age FLOAT,
                mid_airp_name VARCHAR(15),
                mid_airp_arri_time_plan TIME,
                mid_airp_arri_time_pred TIME,
                mid_airp_arri_time_act TIME,
                local_mid_airp_arri_date_plan VARCHAR(20),
                local_mid_airp_arri_date_act VARCHAR(20),
                mid_airp_lug_turn VARCHAR(10),
                mid_airp_arri_gate VARCHAR(10),
                mid_airp_dep_time_plan TIME,
                mid_airp_dep_time_pred TIME,
                mid_airp_dep_time_act TIME,
                local_mid_airp_dep_date_plan VARCHAR(20),
                local_mid_airp_dep_date_act VARCHAR(20),
                mid_airp_checkin_counter VARCHAR(30),
                mid_airp_dep_gate VARCHAR(10),
                mid_airp_weather VARCHAR(50),
                mid_airp_pm25 INT,
                mid_airp_flow VARCHAR(20),
                PRIMARY KEY(flight_code,flight_date,dep_airp_code,arri_airp_code)
                );
                ''' % self._tb1_name)
            print("已创建表格：%s" % self._tb1_name)
        except Exception as e:
            if e.args[0] != 1050:
                print('在创建表格 %s 时发生以下错误：' % self._tb1_name)
                print(e)

        try:
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS %s(
                flight_code VARCHAR(8) NOT NULL,
                flight_date DATE NOT NULL,
                dep_airp_code CHAR(3) NOT NULL,
                arri_airp_code CHAR(3) NOT NULL
                );
                ''' % self._tb2_name)
            print("已创建表格：%s" % self._tb2_name)
        except Exception as e:
            if e.args[0] != 1050:
                print('在创建表格 %s 时发生以下错误：' % self._tb2_name)
                print(e)

    def desc_table(self,tb):
        tb_name = self._tb1_name if tb==1 else self._tb2_name
        print(self.in_execute('DESC TABLE %s' % tb_name))

    def in_execute(self, sql_line):
        to_return = {"code":0,"message":"ok","data":None}
        try:
            # print("执行命令： %s\n" % sql_line)
            self.cursor.execute(sql_line)
        except Exception as e:
            to_return["code"] = e.args[0]
            to_return["message"] = e.args[1]
            return to_return
        to_return["data"] = self.cursor.fetchall()
        return to_return

    def _add_one(self,tb:int, dic):
        # 添加一条数据
        tb_name = self._tb1_name if tb == 1 else self._tb2_name
        col = ''
        values = ''
        for key, value in dic.items():
            if value != "--":
                col += key+','
                if value in ("--",None):
                    values += "NULL,"
                elif isinstance(value, str):
                    values += value.__repr__()+','
                elif isinstance(value, (float,int)):
                    values += str(value)+','
                else:
                    raise Exception('[E]in_add,value type is', type(value))
        p = self.in_execute("INSERT INTO %s (%s) VALUES (%s)" % (tb_name, col[:-1], values[:-1]))
        if p["code"] != 0 and p["code"] == 1062:
            condition = {
                "flight_code":dic["flight_code"],
                "flight_date":dic["flight_date"],
                "dep_airp_code":dic["dep_airp_code"],
                "arri_airp_code":dic["arri_airp_code"]
            }
            print("该条目已存在，操作改为更新该条目！")
            return self.update(tb,dic,condition)
        else:
            return p

    def add(self,tb:int, data: dict or list):
        # 若data 为字典，则认为是插入单条数据
        # 若data 为列表，则认为是插入多条数据，此时列表元素应为字典
        if isinstance(data, dict):
            return self._add_one(tb,data)
        else:
            res = []
            for dic in data:
                res.append(self._add_one(tb,dic))
            return res

    def update(self,tb:int, data_dic, condition: dict):
        tb_name = self._tb1_name if tb == 1 else self._tb2_name
        update_content = ''
        for key, value in data_dic.items():
            if value != "--":
                if value in ("--",None):
                    update_content += "%s=%s," % (key, "NULL")
                elif isinstance(value, str):
                    update_content += "%s=%s," % (key, value.__repr__())
                elif isinstance(value, (float,int)):
                    update_content += "%s=%s," % (key, value)
                else:
                    raise Exception('[E]in_add,value type is', type(value))
        update_content = update_content[:-1]
        condition_sql = ''
        for key, value in condition.items():
            if isinstance(value, str):
                condition_sql += "%s='%s' AND " % (key, value)
            elif isinstance(value, (float,int)):
                condition_sql += "%s=%s AND " % (key, value)
        condition_sql = condition_sql[:-4]
        return self.in_execute("UPDATE %s SET %s WHERE %s;" % (tb_name, update_content, condition_sql))

    def delete(self,tb:int, condition: dict):
        tb_name = self._tb1_name if tb == 1 else self._tb2_name
        condition_sql = ''
        for key, value in condition.items():
            if isinstance(value, str):
                condition_sql += "%s='%s' AND " % (key, value)
            elif isinstance(value, int):
                condition_sql += "%s=%s AND " % (key, value)
            else:
                raise Exception('[E]in_add,value type is', type(value))
        condition_sql = condition_sql[:-4]
        return self.in_execute("DELETE FROM %s WHERE %s" % (tb_name, condition_sql))

    def _delete_all(self,tb:int):
        tb_name = self._tb1_name if tb == 1 else self._tb2_name
        # 删除整张表的数据，慎用！
        return self.in_execute("DELETE FROM %s" % tb_name)

    def query_data(self,tb:int, query_item_names: iter, query_condition: dict):
        tb_name = self._tb1_name if tb == 1 else self._tb2_name
        
        query_item_sql = ''
        for item in query_item_names:
            query_item_sql += '%s,' % item
        query_item_sql = query_item_sql[:-1]

        query_condition_sql = ''
        for key, value in query_condition.items():
            query_condition_sql += "%s='%s' AND " % (key, value)
        query_condition_sql = query_condition_sql[:-4]+';'
        return self.in_execute("SELECT %s FROM %s WHERE %s" % (query_item_sql, tb_name, query_condition_sql))

    def table_headers(self,tb:int):
        tb_name = self._tb1_name if tb == 1 else self._tb2_name
        return [x[0] for x in self.in_execute("SHOW COLUMNS FROM %s"%tb_name)]


if __name__ == '__main__':
    t = Database()
    print(t.table_headers(1))
