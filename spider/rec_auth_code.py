# -*- coding: utf-8 -*-
# @Author: 毅梅傲雪
# @Date:   2019-04-22 13:07:56
# @Last Modified by:   毅梅傲雪
# @Last Modified time: 2019-04-22 14:16:58
from . import fateadm_api


class Rec_auth_code(object):
    def __init__(self, logger):
        pd_id = "111381"     # 用户中心页可以查询到pd信息
        pd_key = "xLHZpDYFiAHmaF3bhpUfbo51kFNc9BjN"
        app_id = "311381"     # 开发者分成用的账号，在开发者中心可以查询到
        app_key = "rOmbrN3a6gfLC5Vjva0RhEI+9TlMjhEq"
        self.ocr = fateadm_api.FateadmApi(app_id, app_key, pd_id, pd_key)
        self.logger = logger

    def rec(self, img_path):
        bal = self.get_balc()
        if bal < 10:
            self.logger.critical("打码账户积分小于 10，无法识别验证码！")
            return None
        elif bal < 100:
            self.logger.warning("打码账户积分小于 100，请及时充值")
        res = self.ocr.PredictFromFile("30400", img_path)
        return {"result": res.pred_rsp.value, "request_id": res.request_id}

    def get_balc(self):
        # 查询账户余额
        return self.ocr.QueryBalcExtend()

    def refund(self, request_id):
        return self.ocr.JusticeExtend(request_id)


if __name__ == "__main__":
    r = Rec_auth_code(None)
    print(r.get_balc())
    result = r.rec(r".\auth_code_imgs\auth_code_2019-04-21 15-31-46.647262.png")
    print(result)
    # print(r.refund(result.request_id))
