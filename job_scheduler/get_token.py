from job_scheduler.scheduler import scheduler
import asyncio
from db.models import Prospect, UserSequence,SequenceMessages, SequenceConnections
from linkedin_scraper.actions import  login
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime, timedelta

def sendResponseBack(data,queue):
    asyncio.run(queue.put(data))
    
  
    return
def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')
    return webdriver.Chrome(options=chrome_options)

def fetchandSaveToken(email,password,current_user,queue,sendResponse):
    
    driver=get_driver()
    cookie=login(driver=driver,email=email,password=password)
    if cookie==-1 and sendResponse:
        data={}
        data["exitCode"]=500
        sendResponseBack(data,queue)
    
    if cookie!=-1 and sendResponse:
        data={}
        data["exitCode"]=200
        sendResponseBack(data,queue)
    if cookie!=-1:    
        print(cookie["value"])
        current_user.linkedInToken=cookie["value"]
        current_user.save()
    return


    
             


