import psutil
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import time

# 设置监控阈值
cpu_threshold = 30
memory_threshold = 70

# 设置发件人和收件人信息
sender_email = '1103412707@qq.com'
sender_password = 'toyxaqqpkrxjfjja'
receiver_email = 'htma1003@gmail.com'


# 定义邮件内容
def send_email(subject, content):
    message = MIMEText(content, 'plain', 'utf-8')
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = Header(subject, 'utf-8')
    try:
        smtpObj = smtplib.SMTP_SSL('smtp.qq.com', 465)
        smtpObj.login(sender_email, sender_password)
        smtpObj.sendmail(sender_email, receiver_email, message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件", e)


# 监控函数
while True:
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent

    if cpu_percent > cpu_threshold:
        subject = "CPU使用过高"
        content = "当前CPU使用率为{}%".format(cpu_percent)
        send_email(subject, content)

    if memory_percent > memory_threshold:
        subject = "内存使用过高"
        content = "当前内存使用率为{}%".format(memory_percent)
        send_email(subject, content)

    time.sleep(60)  # 每分钟监控一次
