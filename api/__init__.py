
# import asyncio

#from bson.json_util import ObjectId
from datetime import date, datetime,timedelta
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)
# loop = asyncio.get_event_loop()

# app.config["JWT_SECRET_KEY"] = "something"  # change this!
# #app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 10  # 10 minutes
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
# app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 30  # 30 days
# app.config["JWT_COOKIE_SECURE"] = True
# app.config["JWT_TOKEN_LOCATION"] = ["headers"]
# class MyEncoder(json.JSONEncoder):

#     def default(self, obj):
#         if isinstance(obj, ObjectId):
#             return str(obj)
#         if isinstance(obj, (datetime, date)):
#             return obj.isoformat()
#         return super(MyEncoder, self).default(obj)

# app.json_encoder = MyEncoder
