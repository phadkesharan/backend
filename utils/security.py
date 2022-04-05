import email
import json
from random import random
import sys
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union
from app.db.models import User
from fastapi import security
from jose import JWTError, jwt
from passlib.context import CryptContext

# from core import crud
from app.db.config import settings
from .error import MyGraphQLError
import bcrypt
ALGORITHM = "HS256"


# temperory user 
# temp_pass = "qwerty1234"
# temp_name = "name1234"
# temp_email = "qwerty1234@something.com"

backToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjU1MzY3OTIzMjQuMDUyNzg1LCJzdWIiOiJ7J25hbWUnOiAnU3RldmVuIEdpanNtYW4nLCAnZW1haWwnOiAnaW5mb0BhbXBpcmUuY28nLCAnaWQnOiAnNjFlYjU3ZTNiMjY1NDRkZDY4ZDc4MWEwJ30iLCJpYXQiOjE2NDg3OTIzMjR9.fgLRMBfMsNpwU2R4dLEncb45vGA2WRdGczC7sp_zKBw';

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt(12))

def check_password(plain_text_password, hashed_password):
    print("checking")
    print(plain_text_password)
    print(hashed_password)
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(plain_text_password, hashed_password)
def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS
        )
    to_encode = {
        "exp": expire.timestamp(),
        "sub": str(subject),
        "iat": datetime.utcnow(),
    }
    gen = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    print("generated token : " + gen)

    print("generated") 
    print(gen)
    return gen


def decode_access_token(token):
    try: 
        print(f"token : {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM],)
    except JWTError as e:
        #traceback.print_exception(*sys.exc_info())
        raise MyGraphQLError(code=404, message="Invalid Token format")

    date_time_obj = datetime.fromtimestamp(payload["exp"])
    if date_time_obj < datetime.utcnow():
        raise MyGraphQLError(code=404, message="Token expired")

    return payload["sub"].replace("\'", "\"")


async def get_current_user_by_info(info) -> Optional[Dict]:
    print("context : ")
    print(info.context)
    auth_header = [
        blog[1]
        for blog in info.context["request"]["headers"]
        if blog[0] == b"authorization"
    ]
    if not auth_header:
        raise MyGraphQLError(code=404, message="Could not find Authorization header")
    #print(auth_header[0].decode())
    return await get_current_user_by_auth_header(auth_header[0].decode())


async def get_current_user_by_auth_header(auth_header) -> Optional[Dict]:
    _, token = security.utils.get_authorization_scheme_param(auth_header)
    # token = backToken
    print("auth header")
    print(token)
    token = backToken

    print(token,"hi")
    user_id = json.loads(decode_access_token(token))["id"]
    user = User.objects(id=user_id)[0]

    # created temp dummy User
    # tempUser = User(name=temp_name, email=temp_email, password=temp_pass, id=user_id)
    # tempUser.save()

    # tempUser = User.objects.filter(name=temp_name)
    # print("user id : " + user_id)
    # return tempUser
    return user
