from bson.objectid import ObjectId
from job_scheduler.scheduler import scheduler
from db.models import Prospect, UserSequence,SequenceMessages, SequenceConnections
from linkedin_scraper import Person, actions
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from datetime import datetime, timedelta

MESSAGE_READ_WAIT="1 mm"
def get_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('--no-sandbox')
    return webdriver.Chrome(options=chrome_options)
def seq_scheduler(prospect_id,token):
    pipeline = [
        { "$match": { "sequences.prospects.id": ObjectId(prospect_id)} },
        { "$project": {
    "sequences": {
      "$filter": {
        "input": {
          "$map": {
            "input": "$sequences",
            "as": "sequences",
            "in": {
              "id": "$$sequences.id",
              "instructions":"$$sequences.instructions",
              "prospects": {
                "$filter": {
                  "input": "$$sequences.prospects",
                  "as": "prospect",
                  "cond": { '$eq': ["$$prospect.id", ObjectId(prospect_id) ] }
                }
              }
            }
          }
        },
        "as": "sequences",
        "cond": { "$ne": [ "$$sequences.prospects", [] ]}
      }
    }
  }}
   ]
    print("starting job")
    #UserSequence.objects(prospects__id=prospect_id).update_one(set__prospects.currentStep0)
    #return
    #userSeq=UserSequence.objects().aggregate(pipeline).next()
    #print(userSeq)
    userSeq=UserSequence.objects.filter(prospects__id=prospect_id).fields(name=1,userId=1,instructions=1,prospects={'$elemMatch': {'id':ObjectId(prospect_id)}})[0]

    
    
   
    prospect=userSeq.prospects[0]
    current_instruction=userSeq.instructions[prospect.currentStep]
    addedJob=False
    exit=False
    #messageId=None
    if current_instruction.instructionType=="ACTION":
        if current_instruction.instruction=="SEND_CONNECTION":
            
            print("in send connect")
            driver=get_driver()
            person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,linkedin_url=prospect["url"],sendResponseFlag=False)
            status=person.send_Connect(close_on_complete=False)
            if status==False:
                connect_status=person.send_Connect_Status()
                if connect_status:
                    connection=SequenceConnections(to=prospect["url"],text="")
                    UserSequence.objects(prospects__id=prospect_id).update_one(push__sequenceConnections=connection)
                    userSeq.prospects[0].lastConnectionId=connection.id
                    job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime("1 mm"))
                    print(job.id)
                    print(job.next_run_time)
                    userSeq.prospects[0].currentStep=prospect.currentStep+1
                    userSeq.prospects[0].jobId=job.id
                    userSeq.prospects[0].nextRunTime=job.next_run_time
                    userSeq.prospects[0].remarks.append("Connection already accepted ")
                    print("connect already accpted")
                    addedJob=True
                else:
                    
                    userSeq.prospects[0].remarks.append("Connection already sent and not Accepted")
                    connection=SequenceConnections(to=prospect["url"],text="")
                    userSeq.prospects[0].lastConnectionId=connection.id
                    UserSequence.objects(prospects__id=prospect_id).update_one(push__sequenceConnections=connection)
                
            else:
                print("sent connection")
                connection=SequenceConnections(to=prospect["url"],text="")
                userSeq.prospects[0].lastConnectionId=connection.id
                UserSequence.objects(prospects__id=prospect_id).update_one(push__sequenceConnections=connection)
                
                userSeq.prospects[0].remarks.append("connect sent")
                driver.close()

        if current_instruction.instruction=="SEND_MESSAGE":
            driver=get_driver()
            textString=current_instruction.text.format(name=userSeq.prospects[0]["name"],role=userSeq.prospects[0]["role"])
            
            person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,linkedin_url=prospect["url"],messageText=textString,sendResponseFlag=False)
            person.send_Message()
            userSeq.prospects[0].remarks.append("message sent ")
            message=SequenceMessages(to=prospect["url"],text=textString)
            
            UserSequence.objects(prospects__id=prospect_id).update_one(push__sequenceMessages=message)
            userSeq.prospects[0].lastMessageId=message.id
            job=scheduler.add_job(checkMessageStatus,'date',args=[message.id,token],run_date=getTime(MESSAGE_READ_WAIT))
            print("message sent")
        
        if current_instruction.instruction=="FOLLOW":
            driver=get_driver()
            
            person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,link=prospect["url"],sendResponseFlag=False)
            person.sendFollow()
            userSeq.prospects[0].remarks.append("follow sent ")
        if current_instruction.instruction=="VIEW":
            driver=get_driver()
            
            person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,link=prospect["url"],sendResponseFlag=False)
            res=person.viewProfile()
            userSeq.prospects[0].remarks.append("profile viewed ")
            if res["company"] is not None:
                userSeq.prospects[0].company=res["company"]
            if res["position"] is not None:
                 userSeq.prospects[0].position=res["position"]
            if res["company"] is not None and res["position"] is not None:
                userSeq.prospects[0].role=res["position"] +" at "+res["company"]
            if res["email"] is not None:
                userSeq.prospects[0].email=res["email"]
        if current_instruction.instruction=="LIKE_POST":
            driver=get_driver()
            
            person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,link=prospect["url"],sendResponseFlag=False)
            status=person.likeLastPost()
            if status==1:
                userSeq.prospects[0].remarks.append("liked last post ")
            else:
                userSeq.prospects[0].remarks.append("no post to like")
            

           
        if current_instruction.end:
            print("completed")
            userSeq.prospects[0].remarks.append("done")

            #userSeq.completedProspect.append(userSeq.prospects[0])
            UserSequence.objects(id=userSeq.id).update_one(push__completedProspects=userSeq.prospects[0])
            #userSeq.prospects[0].delete()
            exit=True
            #return
        elif addedJob==False:
            job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime(current_instruction["wait"]))
            print(job.id)
            print(job.next_run_time)
            userSeq.prospects[0].currentStep=prospect.currentStep+1
            userSeq.prospects[0].jobId=job.id
            userSeq.prospects[0].nextRunTime=job.next_run_time
            #userSeq.prospects[0].remarks.append("done ")
            
            
           
            
    else:
        if current_instruction.instruction=="ACCEPT_CONNECTION":
             driver=get_driver()
             person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,linkedin_url=prospect["url"],sendResponseFlag=False)
             status=person.send_Connect_Status()
             print("accept connection")
             if status:
                userSeq_connection=UserSequence.objects.filter(sequenceConnections__to=prospect["url"]).fields(name=1,userId=1,sequenceConnections={'$elemMatch': {'to':prospect["url"]}})[0]
                userSeq_connection.sequenceConnections[0].status=True
                userSeq_connection.sequenceConnections[0].acceptedOn=datetime.now()
                UserSequence.objects(sequenceConnections__to=prospect["url"]).update_one(
    set__sequenceConnections__S=userSeq_connection.sequenceConnections[0]
    )
                print("connection accepted")
                if current_instruction["end"]:
                    print("completed")
                    userSeq.prospects[0].remarks.append("done")
                    UserSequence.objects(id=userSeq.id).update_one(push__completedProspects=userSeq.prospects[0])

                    #userSeq.completedProspects.append(userSeq.prospects[0])
                    exit=True
                    #return
                else:
                    wait=current_instruction["wait"]
                    job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime(wait))
                    userSeq.prospects[0].currentStep=prospect.currentStep+1
                    userSeq.prospects[0].jobId=job.id
                    userSeq.prospects[0].nextRunTime=job.next_run_time
                    userSeq.prospects[0].remarks.append("connection accepted moving forward ")
                    
                
             else:
                 print("connection not accepted")
                 person.withdraw_Connect()
                 if current_instruction["end"] or "jump" not in current_instruction:
                    userSeq.prospects[0].remarks.append("done")

                    #userSeq.completedProspect.append(userSeq.prospects[0])
                    UserSequence.objects(id=userSeq.id).update_one(push__completedProspects=userSeq.prospects[0])
                    exit=True
                 
                 else:
                    wait=current_instruction["wait"]
                    job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime(wait))
                    userSeq.prospects[0].currentStep=current_instruction["jump"]
                    
                    userSeq.prospects[0].jobId=job.id
                    userSeq.prospects[0].nextRunTime=job.next_run_time
                    userSeq.prospects[0].remarks.append("connection not accepted connection withdrawn moving forward ")
        if current_instruction.instruction=="REPLIED_MESSAGE":
             driver=get_driver()
             person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,linkedin_url=prospect["url"],sendResponseFlag=False)
             status=person.messageStatus()
             print("accept connection")
             userSeq_message=UserSequence.objects.filter(sequenceMessages__id=userSeq.prospects[0].lastMessageId).fields(name=1,userId=1,sequenceMessages={'$elemMatch': {'id':userSeq.prospects[0].lastMessageId}})[0]
    
             if status==1:
                userSeq_message.sequenceMessages[0].read=True
                userSeq_message.sequenceMessages[0].replied=True
                userSeq_message.sequenceMessages[0].repliedOn=datetime.now()
                userSeq_message.sequenceMessages[0].readOn=datetime.now()
                UserSequence.objects(sequenceMessages__id=userSeq.prospects[0].lastMessageId).update_one(
    set__sequenceMessages__S=userSeq_message.sequenceMessages[0])
                userSeq.prospects[0].remarks.append("replied")
                print("connection accepted")
                if current_instruction["end"]:
                    print("completed")
                    userSeq.prospects[0].remarks.append("done")
                    UserSequence.objects(id=userSeq.id).update_one(push__completedProspects=userSeq.prospects[0])

                    #userSeq.completedProspects.append(userSeq.prospects[0])
                    exit=True
                    #return
            
                else:
                    wait=current_instruction["wait"]
                    job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime(wait))
                    userSeq.prospects[0].currentStep=prospect.currentStep+1
                    userSeq.prospects[0].jobId=job.id
                    userSeq.prospects[0].nextRunTime=job.next_run_time
                    userSeq.prospects[0].remarks.append("message replied ")
             elif status==2:
                userSeq_message.sequenceMessages[0].read=True
                print("read")
       
                userSeq_message.sequenceMessages[0].readOn=datetime.now()
                userSeq.prospects[0].remarks.append("message seen but not replied")
                UserSequence.objects(sequenceMessages__id=userSeq.prospects[0].lastMessageId).update_one(
    set__sequenceMessages__S=userSeq_message.sequenceMessages[0])
                if current_instruction["end"] or "jump" not in current_instruction:
                    userSeq.prospects[0].remarks.append("done")

                    #userSeq.completedProspect.append(userSeq.prospects[0])
                    UserSequence.objects(id=userSeq.id).update_one(push__completedProspects=userSeq.prospects[0])
                    exit=True
                else:
                    wait=current_instruction["wait"]
                    job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime(wait))
                    userSeq.prospects[0].currentStep=current_instruction["jump"]
                    
                    userSeq.prospects[0].jobId=job.id
                    userSeq.prospects[0].nextRunTime=job.next_run_time
                #userSeq.prospects[0].remarks.append("connection not accepted connection withdrawn moving forward ")
                
             else:
                 print("message not opened")
                 
                 if current_instruction["end"] or "jump" not in current_instruction:
                    userSeq.prospects[0].remarks.append("done")

                    #userSeq.completedProspect.append(userSeq.prospects[0])
                    UserSequence.objects(id=userSeq.id).update_one(push__completedProspects=userSeq.prospects[0])
                    exit=True
                 
                 else:
                    wait=current_instruction["wait"]
                    job=scheduler.add_job(seq_scheduler,'date',args=[prospect_id,token],run_date=getTime(wait))
                    userSeq.prospects[0].currentStep=current_instruction["jump"]
                    
                    userSeq.prospects[0].jobId=job.id
                    userSeq.prospects[0].nextRunTime=job.next_run_time
                    userSeq.prospects[0].remarks.append("message not opened ")
    if exit:
        print("exit true")
        UserSequence.objects(id=userSeq.id).update_one(pull__prospects__id=prospect_id)
        return
    print("saving...")
    UserSequence.objects(prospects__id=prospect_id).update_one(
    set__prospects__S=userSeq.prospects[0]
    
    )
    print("saved")

        

def checkMessageStatus(id,token):
    print("in check status")
    userSeq_message=UserSequence.objects.filter(sequenceMessages__id=id).fields(name=1,userId=1,sequenceMessages={'$elemMatch': {'id':ObjectId(id)}})[0]
    driver=get_driver()
    person = Person( driver=driver,close_on_complete=True,scrape=False,get=False,cookie=token,linkedin_url=userSeq_message.sequenceMessages[0].to,sendResponseFlag=False)
    status=person.messageStatus()
    if (status==1):
        print("replied")
        userSeq_message.sequenceMessages[0].read=True
        userSeq_message.sequenceMessages[0].replied=True
        userSeq_message.sequenceMessages[0].repliedOn=datetime.now()
        userSeq_message.sequenceMessages[0].readOn=datetime.now()
    elif(status==2):
        userSeq_message.sequenceMessages[0].read=True
        print("read")
       
        userSeq_message.sequenceMessages[0].readOn=datetime.now()
    else:
        print("nothing")
        return
    UserSequence.objects(sequenceMessages__id=id).update_one(
    set__sequenceMessages__S=userSeq_message.sequenceMessages[0])
        
        
def getTime(wait):
    arr=wait.split()
    if len(arr)==1:
         return datetime.now() + timedelta(minutes=int(arr[0]))
    if arr[1]=='mm':
        return datetime.now() + timedelta(minutes=int(arr[0]))
    if arr[1]=='ss':
        return datetime.now() + timedelta(seconds=int(arr[0]))
    if arr[1]=='hh':
        return datetime.now() + timedelta(hours=int(arr[0]))
    if arr[1]=='dd':
        return datetime.now() + timedelta(days=int(arr[0]))
    if arr[1]=='ww':
        return datetime.now() + timedelta(weeks=int(arr[0]))
    
