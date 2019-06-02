from .myPrint import myPrint
def create_notice(ty:str,dic:dict):
    """
    生成通知内容
    :param ty: 通知条件/航班当前状态，在本程序最下边有全部实例
    除了"起飞前一天"、"起飞前三小时"和"即将降落"三个需要手动控制通知时间外，
    其他都是航班状态，值与航班状态的值相同，可以直接在航班状态改变时把最新航班状态作为参数传进来
    :param dic: 航班最新的详细信息，调用spider的get_detailed_info时的 return_type 值设为 1，此时返回的结果可以直接当做参数传进来
    :return: 字典，键是关注人的身份，值是一个元组，元组第一个元素是通知标题，第二个元素是通知内容。
    根据通知条件不同，字典里可能没用某些身份的通知内容，表示不给这些身份的人发通知
    """
    if not dic:
        print("航班详细信息为空！")
        return {}
    month = dic["flight_date"][4:6]
    day = dic["flight_date"][6:]
    if ty == "起飞前一天":
        noti_1 = "您将在明天乘坐%s月%s日 %s 航班（%s-%s），预计将于 %s 起飞，"%(
            month,day,dic["flight_code"],dic["dep_city"],dic["arri_city"],dic["dep_time_plan"])
        noti_2 = "您关注的%s月%s日 %s 航班（%s-%s），预计将于 %s 起飞，"%(
            month,day,dic["flight_code"],dic["dep_city"],dic["arri_city"],dic["dep_time_plan"])
        noti_3 = "您关注的%s月%s日 %s 航班（%s-%s），预计将于 %s 到达，"%(
            month,day,dic["flight_code"],dic["dep_city"],dic["arri_city"],dic["arri_time_plan"])
        if "--" not in dic["dep_airp_weather"]:
            noti_1 += "%s 机场明日天气: %s，"%(dic["dep_airp_name"],dic["dep_airp_weather"])
            noti_2 += "%s 机场明日天气: %s，"%(dic["dep_airp_name"],dic["dep_airp_weather"])
        if "--" not in dic["arri_airp_weather"]:
            noti_1 += "%s 机场明日天气: %s，"%(dic["arri_airp_name"],dic["arri_airp_weather"])
            noti_3 += "%s 机场明日天气: %s，"%(dic["arri_airp_name"],dic["arri_airp_weather"])
        noti_1 += "请您提前做好准备，安排好行程。"
        noti_1 += "请您提前做好准备，安排好行程。"
        noti_1 += "请您提前做好准备，安排好行程。"
        return {
            "乘机人":("乘机提醒",noti_1),
            "送机人":("送机提醒",noti_2),
            "接机人":("接机提醒",noti_3)
        }
    elif ty == "起飞前三小时":
        tm = dic["dep_time_pred"] if dic["dep_time_pred"] != "--" else dic["dep_time_plan"]
        noti_1 = "您乘坐的 %s 航班（%s-%s）预计将于今日 %s 起飞，"%(
            dic["flight_code"],dic["dep_airp_name"],dic["arri_airp_name"],tm)
        noti_2 = "您关注的 %s 航班（%s-%s）预计将于今日 %s 起飞，"%(
            dic["flight_code"],dic["dep_airp_name"],dic["arri_airp_name"],tm)
        if dic["checkin_counter"] != "--":
            noti_1 += "值机柜台为 %s，"%dic["checkin_counter"]
        if dic["dep_gate"] != "--":
            noti_1 += "登机口为 %s，"%dic["dep_gate"]
        if "--" not in dic["dep_airp_weather"]:
            noti_1 += "%s 机场今日天气: %s，"%(dic["dep_airp_name"],dic["dep_airp_weather"])
            noti_2 += "%s 机场今日天气: %s，"%(dic["dep_airp_name"],dic["dep_airp_weather"])
        noti_1 += "请您提前做好准备，安排好行程。"
        noti_2 += "请您提前做好准备，安排好行程。"
        return {
            "乘机人":("乘机提醒",noti_1),
            "送机人":("送机提醒",noti_2)
        }
    elif ty == "正在登机":
        if dic["dep_gate"] != "--":
            return {"乘机人":("登机提醒","您乘坐的 %s 航班已经正在登机，请前往 %s 登机口登机"%(dic["flight_code"],dic["dep_gate"]))}
        else:
            return {"乘机人":("登机提醒","您乘坐的 %s 航班已经正在登机，请根据机场提醒，前往相应登机口登机"%(dic["flight_code"]))}
    elif ty == "催促登机":
        if dic["dep_gate"] != "--":
            return {"乘机人":("登机提醒","您乘坐的 %s 航班登机口即将关闭，请尽快前往 %s 登机口登机"%(dic["flight_code"],dic["dep_gate"]))}
        else:
            return {"乘机人":("登机提醒","您乘坐的 %s 航班登机口即将关闭，请根据机场提醒，尽快前往相应登机口登机"%(dic["flight_code"]))}
    elif ty == "登机结束":
        return {"乘机人":("登机结束","您乘坐的 %s 航班登机口已经关闭，飞机即将起飞，请您做好准备，航班助手祝您旅途愉快！"%(dic["flight_code"]))}
    elif ty == "起飞":
        noti_1 = "您乘坐的 %s 航班"%dic["flight_code"]
        noti_2 = "您关注的 %s 航班"%dic["flight_code"]
        noti_3 = "您关注的 %s 航班"%dic["flight_code"]
        if dic["dep_time_act"] != "--":
            noti_1 += "已于 %s 从 %s 起飞，"%(dic["dep_time_act"],dic["dep_airp_name"])
            noti_2 += "已于 %s 从 %s 起飞，"%(dic["dep_time_act"],dic["dep_airp_name"])
            noti_3 += "已于 %s 从 %s 起飞，"%(dic["dep_time_act"],dic["dep_airp_name"])
        else:
            noti_1 += "已经从 %s 起飞，"%(dic["dep_airp_name"])
            noti_2 += "已经从 %s 起飞，"%(dic["dep_airp_name"])
            noti_3 += "已经从 %s 起飞，"%(dic["dep_airp_name"])
        if dic["delay_time_tip"] != "--":
            noti_1 += dic["delay_time_tip"]
            noti_2 += dic["delay_time_tip"]
            noti_3 += dic["delay_time_tip"]
        tm = dic["arri_time_pred"] if dic["arri_time_pred"] != "--" else dic["arri_time_plan"]
        arri_gate = "%s 口"%dic["arri_gate"] if dic["arri_gate"] != "--" else ""
        noti_1 += "，预计 %s 到达 %s %s"%(tm,dic["arri_airp_name"],arri_gate)
        noti_2 += "，预计 %s 到达 %s"%(tm,dic["arri_airp_name"])
        noti_3 += "，预计 %s 到达 %s %s，请提前做好接机准备"%(tm,dic["arri_airp_name"],arri_gate)
        return {
            "乘机人":("起飞提醒",noti_1),
            "送机人":("起飞提醒",noti_2)
        }
    elif ty == "即将降落":
        tm = dic["arri_time_pred"] if dic["arri_time_pred"] != "--" else dic["arri_time_plan"]
        noti_1 = "您乘坐的 %s 航班即将降落，预计 %s 到达 %s 机场"%(dic["flight_code"],tm,dic["arri_airp_name"])
        noti_2 = "您关注的 %s 航班即将降落，预计 %s 到达 %s 机场"%(dic["flight_code"],tm,dic["arri_airp_name"])
        return {
            "乘机人":("即将降落",noti_1),
            "送机人":("即将降落",noti_2)
        }
    elif ty == "到达":
        if dic["arri_time_act"] != "--":
            noti_1 = "您乘坐的 %s 航班已经于 %s 到达 %s 机场，"%(dic["flight_code"],dic["arri_time_act"],dic["arri_airp_name"])
            noti_2 = "您乘坐的 %s 航班已经于 %s 到达 %s 机场，"%(dic["flight_code"],dic["arri_time_act"],dic["arri_airp_name"])
            noti_3 = "您乘坐的 %s 航班已经于 %s 到达 %s 机场，"%(dic["flight_code"],dic["arri_time_act"],dic["arri_airp_name"])
        else:
            noti_1 = "您乘坐的 %s 航班已经到达 %s 机场，"%(dic["flight_code"],dic["arri_airp_name"])
            noti_2 = "您乘坐的 %s 航班已经到达 %s 机场，"%(dic["flight_code"],dic["arri_airp_name"])
            noti_3 = "您乘坐的 %s 航班已经到达 %s 机场，"%(dic["flight_code"],dic["arri_airp_name"])
        if dic["delay_time_tip"] != "--":
            noti_1 += dic["delay_time_tip"]
            noti_2 += dic["delay_time_tip"]
            noti_3 += dic["delay_time_tip"]
        if dic["arri_gate"] != "--":
            noti_1 += "到达口为 %s，"%dic["arri_gate"]
            noti_3 += "到达口为 %s，"%dic["arri_gate"]
        if dic["lug_turn"] != "--":
            noti_1 += "行李转盘为 %s，"%dic["lug_turn"]
        noti_1 += "本次出行提醒服务结束，航班助手祝您生活愉快，工作顺利！"
        noti_2 += "航班助手祝您生活愉快，工作顺利！"
        noti_3 += "请您做好接机准备，航班助手祝您生活愉快，工作顺利！"
        return {
            "乘机人":("到达提醒",noti_1),
            "送机人":("到达提醒",noti_2),
            "接机人":("到达提醒",noti_3)
        }
    elif ty == "取消":
        return  {
            "乘机人":("航班取消提醒","很遗憾地通知您，您关注的%s月%s日的 %s 航班已被取消，详情请您联系机场 %s 航空公司，也请您密切关注机场方面的通知"%(
                month,day,dic["flight_code"],dic["corp_name"])),
            "送机人":("航班取消提醒","很遗憾地通知您，您关注的%s月%s日的 %s 航班已被取消，请您关注相关情况，合理安排行程"%(
                month,day,dic["flight_code"])),
            "接机人":("航班取消提醒","很遗憾地通知您，您关注的%s月%s日的 %s 航班已被取消，请您关注相关情况，合理安排行程"%(
                month,day,dic["flight_code"]))
        }
    elif ty == "提前取消":
        return  {
            "乘机人":("航班提前取消提醒","很遗憾地通知您，您关注的%s月%s日的 %s 航班已被提前取消，详情请您联系机场 %s 航空公司，也请您密切关注机场方面的通知"%(
                month,day,dic["flight_code"],dic["corp_name"])),
            "送机人":("航班提前取消提醒","很遗憾地通知您，您关注的%s月%s日的 %s 航班已被提前取消，请您关注相关情况，合理安排行程"%(
                month,day,dic["flight_code"])),
            "接机人":("航班提前取消提醒","很遗憾地通知您，您关注的%s月%s日的 %s 航班已被提前取消，请您关注相关情况，合理安排行程"%(
                month,day,dic["flight_code"]))
        }
    elif ty == "延误预警":
        flow_info = ""
        if dic["dep_airp_flow"] != "--":
            flow_info += "%s 机场实时流量情况：%s，"%(dic["dep_airp_name"],dic["dep_airp_flow"])
        if dic["arri_airp_flow"] != "--":
            flow_info += "%s 机场实时流量情况：%s，"%(dic["arri_airp_name"],dic["arri_airp_flow"])
        noti_1 = "航班助手提醒您，您关注的%s月%s日的 %s 航班有延误风险，%s详情请您联系机场 %s 航空公司，也请您密切关注机场方面的通知"%(
                month,day,dic["flight_code"],flow_info,dic["corp_name"])
        return  {
            "乘机人":("航班延误预警",noti_1),
            "送机人":("航班延误预警","航班助手提醒您，您关注的%s月%s日的 %s 航班有延误风险，请您关注相关情况，合理安排行程"%(
                month,day,dic["flight_code"])),
            "接机人":("航班延误预警","航班助手提醒您，您关注的%s月%s日的 %s 航班有延误风险，请您关注相关情况，合理安排行程"%(
                month,day,dic["flight_code"]))
        }
    elif ty == "延误":
        if dic["dep_time_pred"] != "--":
            noti_1 = "您关注的 %s 航班已延误，预计 %s 起飞，此消息仅供参考，请您密切注意机场方面的通知，合理安排出行。"%(dic["flight_code"],dic["dep_time_pred"])
            noti_2 = "您关注的 %s 航班已延误，预计 %s 起飞，此消息仅供参考，请您合理安排出行。"%(dic["flight_code"],dic["dep_time_pred"])
            noti_3 = "您关注的 %s 航班已延误，预计 %s 起飞，此消息仅供参考，请您合理安排出行。"%(dic["flight_code"],dic["dep_time_pred"])

        else:
            noti_1 = "您关注的 %s 航班已延误，预计起飞时间：暂无，此消息仅供参考，请您密切注意机场方面的通知，合理安排出行。"%dic["flight_code"]
            noti_2 = "您关注的 %s 航班已延误，预计起飞时间：暂无，此消息仅供参考，请您合理安排出行。"%dic["flight_code"]
            noti_3 = "您关注的 %s 航班已延误，预计起飞时间：暂无，此消息仅供参考，请您合理安排出行。"%dic["flight_code"]
        return {
            "乘机人":("航班延误",noti_1),
            "送机人":("航班延误",noti_2),
            "接机人":("航班延误",noti_3)
        }
    else:
        print("通知类型有误！")
        return {}
if __name__ == '__main__':
    test_dic = {
      'flight_code' : 'CZ3147' ,
      'flight_date' : '20190525' ,
      'dep_airp_code' : 'BHY' ,
      'arri_airp_code' : 'PEK' ,
      'corp_name' : '南方航空' ,
      'shared_flight' : '--' ,
      'dep_city' : '北海' ,
      'arri_city' : '北京' ,
      'flight_status' : '计划' ,
      'flight_distance' : 2488 ,
      'flight_dur_time' : '时长4小时0分' ,
      'plane_type' : '空客321' ,
      'plane_age' : 12.2 ,
      'ave_ontime_rate' : 0.4839 ,
      'delay_time_tip' : '--' ,
      'pre_flight' : '暂无前序航班' ,
      'dep_airp_name' : '北海福成' ,
      'arri_airp_name' : '北京首都T2' ,
      'mid_airp_name' : '长沙黄花' ,
      'dep_time_pred' : '14:50' ,
      'local_dep_date_plan' : '--' ,
      'checkin_counter' : '3-6' ,
      'dep_gate' : '--' ,
      'dep_airp_weather' : '27°/33°C 多云' ,
      'dep_airp_pm25' : '--' ,
      'dep_airp_flow' : '--' ,
      'dep_time_plan' : '14:50' ,
      'dep_time_act' : '--' ,
      'local_dep_date_act' : '--' ,
      'mid_airp_arri_time_pred' : '16:30' ,
      'local_mid_airp_arri_date_plan' : '--' ,
      'mid_airp_lug_turn' : '--' ,
      'mid_airp_arri_gate' : '--' ,
      'mid_airp_dep_time_pred' : '17:30' ,
      'local_mid_airp_dep_date_plan' : '--' ,
      'mid_airp_checkin_counter' : 'A1-A12' ,
      'mid_airp_dep_gate' : '--' ,
      'mid_airp_weather' : '23°/30°C 中雨' ,
      'mid_airp_pm25' : '--' ,
      'mid_airp_flow' : '--' ,
      'mid_airp_dep_time_plan' : '--' ,
      'mid_airp_arri_time_plan' : '--' ,
      'mid_airp_dep_time_act' : '--' ,
      'local_mid_airp_dep_date_act' : '--' ,
      'mid_airp_arri_time_act' : '--' ,
      'local_mid_airp_arri_date_act' : '--' ,
      'arri_time_pred' : '19:50' ,
      'local_arri_date_plan' : '--' ,
      'lug_turn' : '--' ,
      'arri_gate' : '--' ,
      'arri_airp_weather' : '22°/36°C多云' ,
      'arri_airp_pm25' : '--' ,
      'arri_airp_flow' : '--' ,
      'arri_time_plan' : '19:50' ,
      'arri_time_act' : '--' ,
      'local_arri_date_act' : '--'
    }
    for item in ("起飞前一天","起飞前三小时","正在登机","催促登机","登机结束","起飞","即将降落","到达","取消","提前取消","延误","延误预警"):
        print("-------------------------- %s ----------------------------"%item)
        myPrint(create_notice(item,test_dic))
        print("--------------------------------------------------------\n\n\n")


