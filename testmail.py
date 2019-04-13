import smtplib
from email.mime.text import MIMEText
from email.header import Header
# import init
userID = "yanhui2"
pwd1 = "123456"
email = "1129720379@qq.com"

username = 'buaamyflight@163.com'
pwd = '2019flight'
msg = MIMEText( 'abc', 'txt', 'utf-8' )
msg['Subject'] = Header( '2345', 'utf-8' )
msg['From'] = "flight<buaamyflight@163.com>"
msg['To'] = "yanhui<1129720379@qq.com>"
receive = [email,username]
smtp = smtplib.SMTP()
smtp.connect('smtp.163.com','25')
#smtp.set_debuglevel(1)
smtp.login(username,pwd)  #username  ,pwd
try:

    smtp.sendmail(username,receive,msg.as_string())
except Exception as e:
    print(e)
smtp.quit()
