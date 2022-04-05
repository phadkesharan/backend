from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import pytz
from tzlocal import get_localzone
from app.db.database import db
#from datetime import datetime, timedelta
local_tz = get_localzone() 
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 5,
    'misfire_grace_time':None
}
scheduler = BackgroundScheduler( executors=executors, job_defaults=job_defaults, timezone=local_tz)
def my_listener(event):
    if event.exception:
        print('The job crashed :(')
    else:
        print('The job worked :)')
scheduler.add_jobstore(MongoDBJobStore(client=db))

scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
def test(text1,text2):
    print("working  job prev")
    print(text1)
    print(text2)
# alarm_time = datetime.now() + timedelta(seconds=10)
# print(alarm_time)
# scheduler.add_job(test,'date',run_date=alarm_time,args=["test1","test2"])
scheduler.start()


# scheduler.add_job(myfunc, 'interval', minutes=2, id='my_job_id')
# scheduler.remove_job('my_job_id')