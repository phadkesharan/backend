
   
#from decouple import config
from pydantic import BaseSettings

# Key = config("SECRET_KEY")
# queue = config("QUEUE")


class Settings((BaseSettings)):
    SECRET_KEY = "anfgei5nkjsngkj4"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 1080000
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@db/fastql"
    # SQLALCHEMY_DATABASE_SSL = False
    # SQLALCHEMY_DATABASE_MIN_POOL = 1
    # SQLALCHEMY_DATABASE_MAX_POOL = 20


settings = Settings()