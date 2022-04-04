from datetime import datetime
from mongoengine import Document, EmbeddedDocument
from mongoengine.base.fields import ObjectIdField
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    IntField,
    ListField,
    MapField,
    ReferenceField,
    StringField,
)
from bson.objectid import ObjectId
from pkg_resources import require
class User(Document):
    meta={"collection":"users"}
    name=StringField(required=True)
    email=StringField(required=True,unique=True)
    password=StringField(required=True)
    linkedInToken=StringField()
    dateCreated=DateTimeField(default=datetime.now)
    mailServer:StringField()
    mailServerUserName:StringField()
    mailServerPassword:StringField()
class SequenceInstruction(EmbeddedDocument):
    instructionType=StringField(required=True)
    instruction=StringField(required=True)
    wait=StringField(default="2 mm")
    jump=IntField()
    text=StringField()
    end=BooleanField(required=True)
class Prospect(EmbeddedDocument):
    id = ObjectIdField( required=True, default=lambda: ObjectId() )
    url=StringField(required=True)
    img=StringField()
    name= StringField(required=True)
    degree= StringField()
    position=StringField()
    role= StringField()
    company=StringField()
    location= StringField()
    summary= StringField()
    mutalConnections= StringField()
    currentStep=IntField(required=True)
    nextRunTime=DateTimeField()
    jobId=StringField()
    remarks=ListField(StringField())
    email=StringField()
    lastMessageId=ObjectIdField()
    lastConnectionId=ObjectIdField()

  
    dateCreated=DateTimeField(default=datetime.now)

# class Sequence(EmbeddedDocument):
#     id = ObjectIdField( required=True, default=lambda: ObjectId() )
    
class  SequenceMessages(EmbeddedDocument):
  id = ObjectIdField( required=True, default=lambda: ObjectId() )
  to= StringField(required=True)
  text= StringField(required=True)
  dateCreated= DateTimeField(default=datetime.now)
  read= BooleanField(default=False)
  replied= BooleanField(default=False)
  repliedOn= DateTimeField()
  readOn= DateTimeField()
class SequenceConnections(EmbeddedDocument):
  id = ObjectIdField( required=True, default=lambda: ObjectId() )
  to= StringField(required=True)
  text= StringField()
  dateCreated= DateTimeField(default=datetime.now)
  status= BooleanField(default=False)
  acceptedOn:DateTimeField()
  
class Coordinates(EmbeddedDocument):
    x=IntField()
    y=IntField()
class DndData(EmbeddedDocument):
  label=StringField()
  id=StringField()
  text=StringField()
  duration=StringField()

class DndFlow(EmbeddedDocument):
  id=StringField()
  position=EmbeddedDocumentField(Coordinates)
  type=StringField()
  data=EmbeddedDocumentField(DndData)
  source=StringField()
  sourceHandle=StringField()
  target=StringField()
  targetHandle=StringField()


class UserSequence(Document):
    meta={"collection":"User Sequences"}
    userId=ObjectIdField(required=True)
    name=StringField(required=True)
    prospects=EmbeddedDocumentListField(Prospect)
    completedProspects=EmbeddedDocumentListField(Prospect)
    dateCreated=DateTimeField(default=datetime.now)
    instructions=EmbeddedDocumentListField(SequenceInstruction)
    sequenceConnections=EmbeddedDocumentListField(SequenceConnections)
    sequenceMessages=EmbeddedDocumentListField(SequenceMessages)
    dndFlow=EmbeddedDocumentListField(DndFlow)


# class Department(Document):

#     meta = {"collection": "department"}
#     name = StringField()


# class Role(Document):

#     meta = {"collection": "role"}
#     name = StringField()


# class Task(EmbeddedDocument):

#     name = StringField()
#     deadline = DateTimeField(default=datetime.now)


# class Employee(Document):

#     meta = {"collection": "employee"}
#     name = StringField()
#     hired_on = DateTimeField(default=datetime.now)
#     department = ReferenceField(Department)
#     roles = ListField(ReferenceField(Role))
#     leader = ReferenceField("Employee")
#     tasks = EmbeddedDocumentListField(Task))