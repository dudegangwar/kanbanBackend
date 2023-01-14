import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from application.database import db
from application.models import Users, Tasks, List
from sqlalchemy import extract
from datetime import datetime

#Read these from config
SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = "dudegangwar@gmail.com"
SENDER_PASSWORD = ""

def send_email(to_address, subject, message, content="text", attachment_file=None):
    msg = MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    # msg["message"] = message

    if content == "html":
        msg.attach(MIMEText(message, "html"))
    else:
        msg.attach(MIMEText(message, "plain"))

    
    # msg.attach(MIMEText(message, "html"))


    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        #email attached are sent as base64 encoded
        encoders.encode_base64(part)

    s= smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    return True

def format_message(template_file, data={}):
    with open(template_file) as file_:
            template = Template(file_.read())
            return template.render(data=data)

def send_welcome_message(data):
    message = format_message('./templates/welcome_email.html', data=data)
    send_email(
        data["email"], 
        subject="Kanban App Report", 
        message=message,
        content="html",
        # attachment_file="manual.pdf",
        )


def mail_run():
    users = db.session.query(Users).all()
    
    for user in users:
        todoList = List.query.filter_by(userid=user.id).all()
        todoTask = Tasks.query.filter_by(userID=user.id).all()
        completedTask = Tasks.query.filter_by(userID=user.id ,flag=1).count()
        inCompletedTask = Tasks.query.filter_by(userID=user.id,flag=0).count()
        if inCompletedTask > 0:
            user_data = {"name":user.name, "email":user.email, "list": todoList, "task": todoTask, "completedTask": completedTask, "inCompletedTask": inCompletedTask}
        # print(todoTask)
        # print(todoList)
            send_welcome_message(data=user_data)

def monthly_run():
    users = db.session.query(Users).all()
    currentMonth = datetime.now().month-1
    print(currentMonth)
    currentYear = datetime.now().year
    if(currentMonth==0):
        currentMonth= 12
        currentYear = currentYear-1
    for user in users:
        todoList = List.query.filter_by(userid=user.id).filter(extract('year', List.created_at)==currentYear).filter(extract('month', List.created_at)==currentMonth).all()
        todoTask = Tasks.query.filter_by(userID=user.id).filter(extract('year', Tasks.lastUpdate)==currentYear).filter(extract('month', Tasks.lastUpdate)==currentMonth).all()
        completedTask = Tasks.query.filter_by(userID=user.id ,flag=1).filter(extract('year', Tasks.lastUpdate)==currentYear).filter(extract('month', Tasks.lastUpdate)==currentMonth).count()
        inCompletedTask = Tasks.query.filter_by(userID=user.id,flag=0).filter(extract('year', Tasks.lastUpdate)==currentYear).filter(extract('month', Tasks.lastUpdate)==currentMonth).count()
        if inCompletedTask > 0:
            user_data = {"name":user.name, "email":user.email, "list": todoList, "task": todoTask, "completedTask": completedTask, "inCompletedTask": inCompletedTask}
        # print(todoTask)
        # print(todoList)
            send_welcome_message(data=user_data)