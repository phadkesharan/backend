
from asyncio.tasks import Task
from os import error
from ariadne import SubscriptionType
import asyncio
from .job_scheduler.get_token import fetchandSaveToken
from .utils import security
from ariadne.asgi import GraphQL
from graphql.error.graphql_error import GraphQLError
from .linkedin_scraper import Person, actions
from selenium import webdriver
from .utils.error import MyGraphQLError
#from db.store import queue
import threading
from selenium.webdriver.chrome.options import Options
from .db.models import UserSequence
from .utils.validator import updateUserValidate

subscription = SubscriptionType()

linkedInToken = 'AQEDASS2FXADl0_iAAABfF_F9mMAAAF_RNbRtU4AOv8RuYzNrncA_RjRpDIJKbsLoamJIK5WkGZou_c2s6H-5jvbf2Qqd-g8oeWjyiuyJV7fL7RCAGIpE9G2BrC1PFDQzLo4PTuNPd-EZzCU3EDH2N_E'
token2 = "AQEDATkEMFICFBZFAAABfumBbGwAAAF_DY3wbE0AV4qE9ubODaDsCTU296cwaMhWWNysjQwlm1poi08gtyQdPpi2QfyH0Ji6mkir-qZDGt9i0YBL3wvjzBwlFS1PtT4sH_LCqjAqfaFbPMaL86np-Mxx"


def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')

    if webdriver.Chrome() == None:
        print("driver error")
    
    
    return webdriver.Chrome(options=chrome_options)
@subscription.source("sendMessage")
async def sendMessage(obj, info, messageText,profileLink,token):
    try:
        
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        #sendResponse(queue=queue)
        # t = threading.Thread(target=sendResponse,name="send respons")
        # t.daemon = True
        # t.start()
        queue = asyncio.Queue()
        
        
       
        driver = get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,messageText=messageText,linkedin_url=profileLink)
        t = threading.Thread(target=person.send_Message ,name="send respons")
        t.daemon = True
        await queue.put("calling thread for sending message")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Message sent successfully","status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
        # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("sendMessage")
async def send_message_resolver(obj, info, messageText,profileLink,token):
    return obj
@subscription.source("getMessages")
async def getMessages(obj, info,limit, token):
    try:
        
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        #sendResponse(queue=queue)
        # t = threading.Thread(target=sendResponse,name="send respons")
        # t.daemon = True
        # t.start()
        queue = asyncio.Queue()
        
        driver=get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,messagesLimit=limit)
        print("logged in")
        t = threading.Thread(target=person.get_Messages ,name="get messages")
        t.daemon = True
        #await queue.put("calling thread for getting messages")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            #print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
        # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("getMessages")
async def getMessages_resolver(obj, info,limit, token):
    return obj



@subscription.source("sendConnect")
async def sendConnect(obj, info, profileLink,token):
    try:
        
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        #sendResponse(queue=queue)
        # t = threading.Thread(target=sendResponse,name="send respons")
        # t.daemon = True
        # t.start()
        queue = asyncio.Queue()
        
        
        driver=get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,linkedin_url=profileLink)
        t = threading.Thread(target=person.send_Connect ,name="send connect")
        t.daemon = True
        await queue.put("calling thread for sending message")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Message sent successfully","status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
        # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendConnectPerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("sendConnect")
async def send_connect_resolver(obj, info,profileLink,token):
    return obj





@subscription.source("searchResults")
async def searchResults(obj, info,searchLink,resultsToScrap, token,hideAlready,sequenceId,keywords,companies,hideImage,hideCompany,hideKeywords):
    try:
        print(resultsToScrap,hideAlready,sequenceId,hideImage,hideKeywords,hideCompany)
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        alreadyUrls=[]
        if hideAlready:
            urls=UserSequence.objects( userId=current_user.id,id=sequenceId).only('prospects.url')
            for prospect in urls[0]["prospects"]:
                alreadyUrls.append(prospect['url'])
            print(alreadyUrls)
        #sendResponse(queue=queue)
        # t = threading.Thread(target=sendResponse,name="send respons")
        # t.daemon = True
        # t.start()
        queue = asyncio.Queue()
        
        driver=get_driver()
        # print("linkedIn Token : " + current_user.linkedIntoken)
        current_user.linkedInToken = token2
        # current_user.linkedInToken = linkedInToken
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,searchLink=searchLink,resultsToScrap=resultsToScrap,prospectsUrl=alreadyUrls,hideAlready=hideAlready,hideCompany=hideCompany,hideImage=hideImage,hideKeywords=hideKeywords,keywords=keywords,companies=companies)
        t = threading.Thread(target=person.search_Results ,name="get search")
        t.daemon = True
        #await queue.put("calling thread for getting messages")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            #print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message["data"],"withoutImage":message["withoutImage"],"containingKeywords":message["containingKeywords"],"containingCompanies":message["containingCompanies"],"alreadyinSeq":message["alreadyinSeq"],"status":"continue"}
        # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("searchResults")
async def searchResultsessages_resolver(obj, info,searchLink,resultsToScrap, token,hideAlready,sequenceId,keywords,companies,hideImage,hideCompany,hideKeywords):
    return obj





@subscription.source("sendConnect")
async def sendConnect(obj, info, profileLink,token):
    try:
        
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        #sendResponse(queue=queue)
        # t = threading.Thread(target=sendResponse,name="send respons")
        # t.daemon = True
        # t.start()
        queue = asyncio.Queue()
        
        
        driver=get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,linkedin_url=profileLink)
        t = threading.Thread(target=person.send_Connect ,name="send connect")
        t.daemon = True
        await queue.put("calling thread for sending message")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Message sent successfully","status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
        # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendConnectPerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("sendConnect")
async def send_connect_resolver(obj, info,profileLink,token):
    return obj





@subscription.source("viewProfile")
async def viewProfile(obj, info,token,link):
    try:
        print(link)
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        queue = asyncio.Queue()
        
        driver=get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,link=link)
        t = threading.Thread(target=person.viewProfile ,name="view ptofile")
        t.daemon = True
        #await queue.put("calling thread for getting messages")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            #print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Message sent successfully","status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
            # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("viewProfile")
async def viewProfileMessages_resolver(obj, info,token,link):
    return obj
@subscription.source("sendFollow")
async def sendFollow(obj, info,token,link):
    try:
        print(link)
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        queue = asyncio.Queue()
        
        driver=get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,link=link)
        t = threading.Thread(target=person.sendFollow ,name="send follow")
        t.daemon = True
        #await queue.put("calling thread for getting messages")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            #print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Message sent successfully","status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
            # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("sendFollow")
async def sendFollowMessages_resolver(obj, info,token,link):
    return obj
@subscription.source("likePost")
async def likePost(obj, info,token,link):
    try:
        print(link)
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        queue = asyncio.Queue()
        
        driver=get_driver()
        person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken,queue=queue,link=link)
        t = threading.Thread(target=person.likeLastPost ,name="send like")
        t.daemon = True
        #await queue.put("calling thread for getting messages")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            #print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Message sent successfully","status":"completed"}
                else:
                    errors={}
                    errors["msg"]="Failed to send message"
                    raise MyGraphQLError(errors,500)
                break
            yield {"data":message,"status":"continue"}
            # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("likePost")
async def likePostMessages_resolver(obj, info,token,link):
    return obj

@subscription.source("addTokenWithCred")
async def addTokenWithCred(obj, info,email,password,token):
    try:
       
        current_user = await security.get_current_user_by_auth_header(token)
        
        if not current_user:
            raise MyGraphQLError(code=401, message="User not authenticated")
        
        queue = asyncio.Queue()
        
        
        t = threading.Thread(target=fetchandSaveToken ,name="send like",args=(email,password,current_user,queue,True))
        t.daemon = True
        #await queue.put("calling thread for getting messages")
        t.start()
        while t.is_alive():
            print('listen')
            message = await queue.get()
            #print(message)
            queue.task_done()
            if "exitCode" in message:
                print("here")
                #yield {"data":"came to end","status":"continue"}
                if message["exitCode"]==200:
                    print("here")
                    yield {"data":"Saved Token","status":"200"}
                else:
                    errors={}
                    errors["msg"]="Invalid Credentials"
                    raise MyGraphQLError(errors,400)
                break
            yield {"data":message,"status":"continue"}
            # driver = webdriver.Chrome()
        # person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=current_user.linkedInToken)
        # await queue.put("starting sending message")
        # yield "doing"
        # loop = asyncio.get_running_loop()
        # #await asyncio.gather(sendMessagePerson(person=person,loop=loop,messageText=messageText,profileLink=profileLink,queue=queue),sendResponse(queue=queue))
        # person.send_Message(message=messageText,link=profileLink)   
        
        return 
        # while True:
        #     print('listen')
        #     yield "hi there "+current_user.email
        #     await asyncio.sleep(3)
        #     yield "hi there closing"
        #     return
    except asyncio.CancelledError:
        raise MyGraphQLError(code=400, message={"errors":"User not authenticated"})

@subscription.field("addTokenWithCred")
async def addTokenWithCredMessages_resolver(obj, info,email,password,token):
    return obj
