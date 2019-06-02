# -*- coding: utf-8 -*-
def n2o(ori, fun_type:int):
    if not ori:
        return ori
    if fun_type == 1:
        res = []
        base_url = 'http://www.variflight.com/schedule/%s-%s-%s.html?AE71649A58c77&fdate=%s'
        for item in ori:
            res.append({
                'flight_detailed_info_url' : base_url%(item["dep_airp_code"],item["arri_airp_code"],item["flight_code"],item["flight_date"]) ,
                'corp_name' : item["corp_name"] ,
                'flight_code' : item["flight_code"] ,
                'shared_fligt' : "实际承运为 %s"%item["shared_flight"] if item["shared_flight"] != "--" else "--",
                'dep_time_plan' : item["dep_time_plan"] ,
                'dep_time_act' : item["dep_time_act"] ,
                'local_dep_date_plan' : item["local_arri_date_plan"] ,
                'local_dep_date_act' : item["local_arri_date_act"] ,
                'dep_airp' : item["dep_airp_name"] ,
                'dep_airp_code' : item["dep_airp_code"] ,
                'arri_time_plan' : item["arri_time_plan"] ,
                'arri_time_act' : item["arri_time_act"] ,
                'local_arri_date_plan' : item["local_arri_date_plan"] ,
                'local_arri_date_act' : item["local_arri_date_act"] ,
                'arri_airp' : item["arri_airp_name"] ,
                'arri_airp_code' : item["arri_airp_code"] ,
                'ontime_rate' : "%.2f%%"%(item["ontime_rate"]*100) if item["ontime_rate"]!="--" else "--" ,
                'flight_status' : item["flight_status"]
              })
        return res
    else:
        airp_datas = {}
        # 出发机场
        if ori["dep_time_pred"] != "--":
            dep_1st_item_name = "预计起飞"
            dep_1st_item_key = "dep_time_pred"
        else:
            dep_1st_item_name = "实际起飞"
            dep_1st_item_key = "dep_time_act"
        airp_datas[ori["dep_airp_name"]] = {
            dep_1st_item_name : ori[dep_1st_item_key] ,
            '值机柜台' : ori["checkin_counter"],
            '登机口' : ori["dep_gate"],
            'weather' :[
                ori["dep_airp_weather"],
                "pm2.5: %d"%ori["dep_airp_pm25"] if ori["dep_airp_pm25"] != "--" else "--",
                ori["dep_airp_flow"] 
            ]
        }

        # 中转机场
        if ori["mid_airp_name"] != "--":
            if ori["mid_airp_arri_time_pred"] != "--":
                mid_1st_item_name = "预计到达"
                mid_1st_item_key = "mid_airp_arri_time_pred"
            else:
                mid_1st_item_name = "实际到达"
                mid_1st_item_key = "mid_airp_arri_time_act"

            if ori["mid_airp_dep_time_pred"] != "--":
                mid_4th_item_name = "预计起飞"
                mid_4th_item_key = "mid_airp_dep_time_pred"
            else:
                mid_4th_item_name = "实际起飞"
                mid_4th_item_key = "mid_airp_dep_time_act"


            airp_datas["经停 "+ori["mid_airp_name"]] = {
                mid_1st_item_name : ori[mid_1st_item_key] ,
                '行李转盘' : ori["mid_airp_lug_turn"] ,
                '到达口' : ori["mid_airp_arri_gate"] ,
                mid_4th_item_name : ori[mid_4th_item_key] ,
                '值机柜台' : ori["mid_airp_checkin_counter"] ,
                '登机口' : ori["mid_airp_dep_gate"],
                'weather' :
                [
                  ori["mid_airp_weather"] ,
                  "pm2.5: %d"%ori["mid_airp_pm25"]  if ori["mid_airp_pm25"] != "--" else "--",
                  ori["mid_airp_flow"]
                ]
              }

        # 到达机场
        if ori["arri_time_pred"] != "--":
            arri_1st_item_name = "预计到达"
            arri_1st_item_key = "arri_time_pred"
        else:
            arri_1st_item_name = "实际到达"
            arri_1st_item_key = "arri_time_act"

        airp_datas[ori["arri_airp_name"]] = {
            arri_1st_item_name: ori[arri_1st_item_key],
            '行李转盘': ori["lug_turn"] ,
            '到达口': ori["arri_gate"] ,
            'weather': [
                ori["arri_airp_weather"],
                "pm2.5: %d"%ori["arri_airp_pm25"] if ori["arri_airp_pm25"] != "--" else "--",
                ori["arri_airp_flow"]
            ]
        }

        return {
        'corp_name_and_flight_code' : '%s %s'%(ori["corp_name"],ori["flight_code"]) ,
        'corp_name' : ori["corp_name"] ,
        'flight_code' : ori["flight_code"] ,
        'flight_status' : ori["flight_status"] ,
        'dep_city' : ori["dep_city"] ,
        'arri_city' : ori["arri_city"] ,
        'flight_distance' : '全程 %d 公里'%ori["flight_distance"] if ori["flight_distance"]!="--" else "--" ,
        'flight_dur_time' : ori["flight_dur_time"] ,
        'plane_type' : ori["plane_type"] ,
        'plane_age' : '%.1f年'%ori["plane_age"] if ori["plane_age"] != "--" else "--" ,
        'ave_ontime_rate' : "%.2f%%"%(ori["ave_ontime_rate"]*100) if ori["ave_ontime_rate"] != "--" else "--" ,
        'delay_time_tip' : ori["delay_time_tip"] ,
        'pre_fligt' : ori["pre_flight"],
        'airp_datas' :airp_datas
        }
if __name__ == '__main__':
    pass

