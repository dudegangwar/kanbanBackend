from application.workers import celery
from datetime import datetime
from celery.schedules import crontab
from application.sendemail import mail_run, monthly_run
import os

@celery.on_after_finalize.connect
def setup_10sec_periodic_tasks(sender,**kwargs):
    sender.add_periodic_task(10.0,delete_files.s(),name="run every 60 seconds")


@celery.on_after_finalize.connect
def setup_daily_periodic_tasks(sender,**kwargs):
    sender.add_periodic_task(crontab(minute=0, hour='18'),daily_task.s(),name="run every day 6 pm")

@celery.on_after_finalize.connect
def setup_monthly_periodic_tasks(sender,**kwargs):
    sender.add_periodic_task(crontab(0, 0, day_of_month='1'),monthly_task.s(),name="run every 1st day of month")


@celery.task
def daily_task():
    print("Running daily")
    mail_run()
    return "daily task running"

@celery.task()
def monthly_task():
    print("running monthly")
    monthly_run()
    return "monthly"

@celery.task()
def delete_files():
    folder = './exceldownload/'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                print(file_path)
                # os.unlink(file_path)
        except Exception as e:
            print(e)
    return 'All files in {} have been deleted.'.format(folder)