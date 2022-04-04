from copy import deepcopy
from os import error, name
from ariadne import ObjectType
from operator import attrgetter
import json
from bson.objectid import ObjectId
from graphql.error.graphql_error import GraphQLError
from mongoengine.queryset.visitor import Q
from pymongo.read_preferences import Secondary
from db.models import DndFlow, Prospect, SequenceInstruction, User, UserSequence
from types import SimpleNamespace
import time
import bcrypt
import asyncio
from utils import security
from utils.error import MyGraphQLError
from utils.validator import registerInputValidate,loginInputValidate,updateUserValidate,changePasswordValidate,sendMessageValidate,sendConnectValidate
from db import config
from datetime import datetime, timedelta
from linkedin_scraper import Person, actions
from selenium import webdriver
import json
from job_scheduler.scheduler import scheduler
from job_scheduler.sequence_scheduler import seq_scheduler 
from job_scheduler.get_token import fetchandSaveToken
mutation = ObjectType("Mutation")
async def sleep():
    time.sleep(10)
class AuthenticationError(GraphQLError):
    extensions = {"code": "UNAUTHENTICATED"}
def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    print(plain_text_password)
    return bcrypt.hashpw(plain_text_password.encode('utf8'), bcrypt.gensalt(12))

def check_password(plain_text_password, hashed_password):
    print("checking")
    #print(plain_text_password)
    #print(hashed_password)
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password.encode('utf8'), hashed_password.encode('utf8'))
@mutation.field("register")
def register(obj, info, registerInput):

    #loop = asyncio.new_event_loop() dont use!!
    #loop.run_until_complete(sleep())
    #asyncio.run(sleep())
    print(registerInput)
    obj=SimpleNamespace(**registerInput)
    name,email,password,confirmPassword = attrgetter('name', 'email', 'password', 'confirmPassword')(obj)
    print("here")
    print(name)
    errors,isExit= registerInputValidate(name,email,password,confirmPassword)
    if isExit:
        #errors["code"]=422
        raise MyGraphQLError(errors,422)
    
    alreadyExists=User.objects(email=email)
    #print(alreadyExists)
    if  len(alreadyExists)==0:
        hashedPassword=get_hashed_password(password)
        user=User(name=name,email=email,password=hashedPassword)
        user.save()
        #userSequence=UserSequence(userId=user.id)
        #userSequence.save()
        access_token_expires = timedelta(
        seconds=config.settings.ACCESS_TOKEN_EXPIRE_SECONDS
    )
        #payload={"name":user.name,"email":user.email,"id":str(user.id)}
        payload={"name":user.name,"email":user.email,"id":str(user.id)}
        access_token=security.create_access_token(
        payload, expires_delta=access_token_expires
    )

        return {
            "success": True,
            "user": user,
            "token":access_token
        }
    errors["msg"]="Email already taken"
    #errors["code"]=400
    raise MyGraphQLError(errors,400)

    
@mutation.field("login")
def login(obj, info, email,password):
   

    #loop = asyncio.new_event_loop() dont use!!
    #loop.run_until_complete(sleep())
    #asyncio.run(sleep())
    print(email)
    print(password)
    errors,isExit= loginInputValidate(email,password)
    
    if isExit:
        errors["code"]=422
        raise MyGraphQLError(errors,422)
        ##errors["code"]=422
        raise MyGraphQLError(errors,422)
        # return{
        #     "success":False,
        #     "errors":[str(errors)]
        # }
    
    user=User.objects(email=email)
    print("users")
    print(user)
    print("login")
    if len(user)>0:
        user=user[0]

        
        print("here in if")
        if check_password(password,user.password):
            print(user)
            access_token_expires = timedelta(
            seconds=config.settings.ACCESS_TOKEN_EXPIRE_SECONDS)
            print(access_token_expires)
            payload={"name":user.name,"email":user.email,"id":str(user.id)}
            access_token=security.create_access_token(
            payload, expires_delta=access_token_expires
            )
            print(access_token)
            #user["id"]=user._id
            #del user.password
            return {
            "success": True,
            "user": user,
            "token":access_token
        }
    errors["msg"]="Invalid Credentials"
    #errors["code"]=401
    print("here in if")
    print("user")
    print(user)
    raise MyGraphQLError(errors,401)
    

@mutation.field("addToken")
async def addTokenResolver(obj, info, linkedInToken):
    print("in add")
    current_user=await security.get_current_user_by_info(info)
    current_user.linkedInToken=linkedInToken
    current_user.save()
    return "Success"


@mutation.field("updateUser")
async def updateUserDetails(obj, info, updateUser):
    
    current_user=await security.get_current_user_by_info(info)
    errors,isExit= updateUserValidate(updateUser)

    if isExit:
        #errors["code"]=422
        raise MyGraphQLError(errors,422)
    for key in updateUser.keys():
        current_user[key]=updateUser[key]
    current_user.save()
    return "Success"

@mutation.field("updateFlow")
async def updateFlowSeq(obj, info, updateFlow):
    
    current_user=await security.get_current_user_by_info(info)
    userSeq=UserSequence.objects(userId=current_user.id,id=updateFlow["sequenceId"]).update_one(set__instructions=updateFlow["instructions"],set__dndFlow=updateFlow["dndFlow"])
    
    return UserSequence.objects(userId=current_user.id,id=updateFlow["sequenceId"])[0]


@mutation.field("changePassword")

async def changePassword(obj, info, prevPassword,password,confirmPassword):
    current_user=await security.get_current_user_by_info(info)
    errors,isExit= changePasswordValidate(prevPassword,password,confirmPassword)
    if isExit:
        #errors["code"]=422
        raise MyGraphQLError(errors,422)
    
    if check_password(prevPassword,current_user.password):
        print(password)
        hashedPassword=get_hashed_password(password)
        print(hashedPassword)
        current_user.password=hashedPassword.decode("utf-8") 
        current_user.save()
        return "Success"
    
    errors["msg"]="Wrong current password"
    #errors["code"]=401
    raise MyGraphQLError(errors,401)
    
    
@mutation.field("addSequence")

async def addSequence(obj, info, createSequence):
        errors={}
        print("create sequence : ")
        print(createSequence)
        current_user=await security.get_current_user_by_info(info)
        
        # errors,isExit= changePasswordValidate(prevPassword,password,confirmPassword)
        # if isExit:
        #     #errors["code"]=422
        #     raise MyGraphQLError(errors,422)
        #instructions=[]
        # for ins in createSequence["sequenceInstructions"]:
        #     instructions.append(SequenceInstruction(instructionType=ins.get("instructionType"),instruction=ins.get("instruction"),wait=ins.get("wait"),jump=ins.get("jump"),text=ins.get("text"),end=ins.get("end")))
        # print(instructions)
        print("current sequence")
        print(createSequence["name"])
        userSeq=UserSequence(userId=current_user.id,name=createSequence["name"],prospects=[],completedProspects=[],instructions=createSequence["sequenceInstructions"],sequenceConnections=[],sequenceMessages=[],dndFlow=createSequence["dndFlow"])
        print(userSeq)
        #userSeq.sequences.append(seq)
        userSeq.save()
        print("done with success")
        return userSeq
        # print(e)
        # errors["msg"]="Server error"
        # #return "Error"
        # #errors["code"]=401
        # raise MyGraphQLError(errors,500)
@mutation.field("addProspects")


async def addProspects(obj, info, addProspects):
        errors={}
       
        current_user=await security.get_current_user_by_info(info)
        force=addProspects["force"]
        seqName = addProspects['sequenceId']
        tempObj = UserSequence.objects(userId=current_user.id,name=addProspects["sequenceId"])
        addProspects["sequenceId"] = tempObj[0].id

        print("seq name")
        print(seqName)

        print("seq id")
        print(addProspects['sequenceId'])
        # if len(UserSequence.objects(userId=current_user.id,id=addProspects["sequenceId"]))==0:
        if len(UserSequence.objects(userId=current_user.id,id=addProspects["sequenceId"]))==0:
            
            # print("sequence : " + tempObj.name)
            raise MyGraphQLError({"msg":"Sequence not found"},422)
        urls=[]
        inputProspects= addProspects["prospects"]
        alreadyUrl=[]
        print("length : ")
        print(len(inputProspects))
        for i in range(len(inputProspects)):
            print("i")
            print(i)
            tempUrl=inputProspects[i].get("url").split(".com/in/")[1].split("/")[0].split("?")[0]
            urls.append("https://www.linkedin.com/in/"+tempUrl)
            inputProspects[i]["url"]="https://www.linkedin.com/in/"+tempUrl
        #print(inputProspects)
        tempProspects=[]
        alreadyInSame=[]
        alreadyInDifferent=[]
        if force==False:
            print(urls)
            userSeq=UserSequence.objects( userId=current_user.id,prospects__url__in=urls)
            #pipeline=[{"$match": {'userId': current_user.id,"prospects__url__in":urls}},{"$project": {"prospects": {"$filter": {"input": "$prospects","as": "prospect","cond": {"$in:" ["$$prospect.url", urls]}}}}}]
            # pipeline=[ {"$match": {"userId": current_user.id}},{"$unwind": "$prospects"}, {"$match": {"prospects.url": {"$in":urls}}}]
            #userSeq=list(UserSequence.objects().aggregate(pipeline))
            
            print("length of seq from db")
            print(len(userSeq))
            alreadyInSameUrl=[] #case when same occurs in same seq no need to show in other first priority
            for seq in userSeq:
                print(seq["id"])
                print(addProspects["sequenceId"])
                if str(seq["id"])==str(addProspects["sequenceId"]):
                    print("here")
                    print("lenth of prospects")
                    print(len(seq["prospects"]))
                    for prospect in seq["prospects"]:
                        if prospect['url'] in urls:
                            print("in loop")
                            alreadyUrl.append(prospect["url"])
                            print(prospect["url"])
                            alreadyInSameUrl.append(prospect["url"])
                            #print(next(item for item in inputProspects if item["url"] ==prospect['url'] ))
                            alreadyInSame.append(next(item for item in inputProspects if item["url"] ==prospect['url'] ))
            for seq in userSeq:
                if seq["id"]!=addProspects["sequenceId"]:
                   
                    tempSeq=deepcopy(seq)
                    print("here in else ")
                    print(seq["prospects"])
                    tempSeq['prospects']=[]
                    
                    for prospect in seq["prospects"]:
                        print(prospect['url'])
                        if prospect['url'] in urls and  prospect['url'] not in alreadyInSameUrl:
                            
                            alreadyUrl.append(prospect["url"])
                            tempSeq['prospects'].append(prospect)
                    alreadyInDifferent.append(tempSeq)

            print(alreadyUrl)
            print(alreadyInSame)
            for prospect in inputProspects:
                if prospect["url"] not in alreadyUrl:
                    print("not in urls")
                    tempProspects.append(Prospect(name=prospect.get("name"),url=prospect.get("url").split('?')[0],summary=prospect.get("summary"),role=prospect.get("role"),location=prospect.get("location"),degree=prospect.get("degree"),mutalConnections=prospect.get("mutalConnections"),currentStep=0,remarks=[],img=prospect.get("img")))
        else:
            userSeq=UserSequence.objects( userId=current_user.id,prospects__url__in=urls,id=addProspects["sequenceId"])
            if len(userSeq)>0:
                for prospect in userSeq[0]["prospects"]:
                    if prospect['url'] in urls:
                        alreadyUrl.append(prospect["url"])
                        alreadyInSame.append(next(item for item in inputProspects if item["url"] ==prospect['url'] ))
                #return {"status":-1,"addedPrsopects":[],"addedPrsopectsLength":0,alreadyInSame:}
                for prospect in inputProspects:
                    if prospect["url"] not in alreadyUrl:
                        tempProspects.append(Prospect(name=prospect.get("name"),url=prospect.get("url").split('?')[0],summary=prospect.get("summary"),role=prospect.get("role"),location=prospect.get("location"),degree=prospect.get("degree"),mutalConnections=prospect.get("mutalConnections"),currentStep=0,remarks=[],img=prospect.get("img")))
            
            else:
                for prospect in inputProspects:
                    tempProspects.append(Prospect(name=prospect.get("name"),url=prospect.get("url").split('?')[0],summary=prospect.get("summary"),role=prospect.get("role"),location=prospect.get("location"),degree=prospect.get("degree"),mutalConnections=prospect.get("mutalConnections"),currentStep=0,remarks=[],img=prospect.get("img")))
            
        print("temp prospects")
        print(tempProspects)
        if len(tempProspects)>0:  
            UserSequence.objects(id=addProspects["sequenceId"]).update_one(push_all__prospects=tempProspects)
            # UserSequence.objects(name=addProspects["sequenceId"]).update_one(push_all__prospects=tempProspects)

            # for prospect in tempProspects:
            #     job=scheduler.add_job(seq_scheduler,'date',run_date=datetime.now() + timedelta(seconds=5),args=[prospect.id,current_user.linkedInToken])

            if len(alreadyInDifferent)>0 or len(alreadyInSame):
                respone={}
                #if len(alreadyInDifferent)>0:
                respone["alreadyInDifferent"]=alreadyInDifferent;
                #if len(alreadyInSame)>0:
                respone["alreadyInSame"]=alreadyInSame
                respone["addedPrsopects"]=tempProspects
                respone["addedPrsopectsLength"]=len(tempProspects)
                respone["statusCode"]=2 #partial added
                return respone;
            else:
                respone={}
                respone["alreadyInDifferent"]=[];
                respone["alreadyInSame"]=[]
                respone["addedPrsopects"]=tempProspects
                respone["addedPrsopectsLength"]=len(tempProspects)
                respone["statusCode"]=1 #done added all
                return respone;
        else:
            print("in else")
            print(alreadyInSame)
            respone={}
            respone["alreadyInDifferent"]=alreadyInDifferent;
            respone["alreadyInSame"]=alreadyInSame
            respone["addedPrsopects"]=alreadyInDifferent + alreadyInSame;
            respone["addedPrsopectsLength"]=len(alreadyInDifferent) + len(alreadyInSame)
            respone["statusCode"]=0 #none added
            
            return respone;



       
@mutation.field("removeSequence")

async def removeSequence(obj, info, seqIds):
    current_user=await security.get_current_user_by_info(info)
    userSeq=UserSequence.objects( userId=current_user.id,id__in=seqIds)
    if len(userSeq)==0:
        raise MyGraphQLError("failed",422)
    for seq in userSeq:
        seq.delete()
    return "Success"

@mutation.field("addTokenWithCred")

async def addTokenWithCred(obj, info, email,password):
    current_user=await security.get_current_user_by_info(info)
    job=scheduler.add_job(fetchandSaveToken,'date',run_date=datetime.now() + timedelta(seconds=1),args=[email,password,current_user])
    return "Success"
@mutation.field("removeProspect")

async def removeProspect(obj, info, prospectIds):
    current_user=await security.get_current_user_by_info(info)
    #userSeq=UserSequence.objects( userId=current_user.id).update_one(pull_all__prospects=prospectIds)
    
    for id in prospectIds:
        print(id)
        userSeq=UserSequence.objects.filter(prospects__id=id,userId=current_user.id).fields(name=1,userId=1,instructions=1,prospects={'$elemMatch': {'id':ObjectId(id)}})
        if len(userSeq)>0 and len(userSeq[0]["prospects"])==1:
            print("in deletion")
            #userSeq["prospects"][0].delete()
            #print(userSeq[0]["prospects"][0])
            # UserSequence.objects.update_one(unset__prospects__S__id=id)

            # UserSequence.objects.update_one(pull__prospects=None)
            test=UserSequence.objects( userId=current_user.id).update_one(pull__prospects=userSeq[0]["prospects"][0])
            print(test)
        else:
            userSeq=UserSequence.objects.filter(completedProspects__id=id,userId=current_user.id).fields(name=1,userId=1,instructions=1,completedProspects={'$elemMatch': {'id':ObjectId(id)}})
            if len(userSeq)>0 and len(userSeq[0]["completedProspects"])==1:
                #userSeq["completedProspects"][0].delete()
                UserSequence.objects( userId=current_user.id).update_one(pull__completedProspects=userSeq[0]["completedProspects"][0])

    return "Success"
