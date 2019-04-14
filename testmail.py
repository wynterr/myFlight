import smtplib
import email.mime.multipart
import email.mime.text
 
msg = email.mime.multipart.MIMEMultipart()
'''
最后终于还是找到解决办法了：邮件主题为‘test’的时候就会出现错误，换成其他词就好了。。我也不知道这是什么奇葩的原因
'''
msg['Subject'] = 'duanx'
msg['From'] = 'buaamyflight@163.com'
msg['To'] = '786311041@qq.com'
content = '''''
    你好，xiaoming
            这是一封自动发送的邮件。
        www.ustchacker.com
'''
txt = email.mime.text.MIMEText(content)
msg.attach(txt)
 
#smtp = smtplib
smtp = smtplib.SMTP()
smtp.connect('smtp.163.com', '25')
smtp.login('buaamyflight@163.com', '2019flight')
smtp.sendmail('buaamyflight@163.com', '786311041@qq.com', msg.as_string())
smtp.quit()
print('邮件发送成功email has send out !')