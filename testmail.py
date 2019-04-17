import smtplib
from email.mime.text import MIMEText
 
# 第三方 SMTP 服务
mail_host = "smtp.163.com"  # SMTP服务器
mail_user = "buaamyflight@163.com"  # 用户名
mail_pass = "2019flight"  # 密码
 
sender = 'buaamyflight@163.com'  # 发件人邮箱
receivers = ['786311041@qq.com']  # 接收人邮箱
 
 
content = 'Python Send Mail !'
title = 'Python SMTP Mail '  # 邮件主题
message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
message['From'] = "{}".format(sender)
message['To'] = ",".join(receivers)
message['Subject'] = title
 
try:
    smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
    smtpObj.login(mail_user, mail_pass)  # 登录验证
    smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
    print("mail has been send successfully.")
except smtplib.SMTPException as e:
    print(e)