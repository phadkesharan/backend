""" database.py """

from mongoengine import connect
import os
DATABASE = "admin"
#PASSWORD = os.environ.get("")
PASSWORD = "3b14L8Y6Et07MgS9"
CA_PATH="ca-certificate.crt"


MONGO_PASS =  "ypf%2Aqvp6BHG%40una%2Aghb"
MONGO_DB = "linqerdb"
MONGO_USER = "admin"
MONGO_USER_2 = 'doadmin'
MONGO_URL = f"mongodb+srv://{MONGO_USER}:{MONGO_PASS}@cluster0.klscv.mongodb.net/{MONGO_DB}?retryWrites=true&w=majority"

# db = connect(
#     MONGO_DB,
#     host=MONGO_URL,
#     alias="default",
# )
# print(db)


#mongodb+srv://doadmin:<replace-with-your-password>@db-mongodb-nyc3-17443-8aed69d6.mongo.ondigitalocean.com/admin?authSource=admin&replicaSet=db-mongodb-nyc3-17443&tls=true&tlsCAFile=<replace-with-path-to-CA-cert>
# MONGO_STRING = f"mongodb+srv://doadmin:{PASSWORD}@db-mongodb-nyc3-17443-8aed69d6.mongo.ondigitalocean.com/admin?authSource=admin&replicaSet=db-mongodb-nyc3-17443&tls=true&tlsCAFile={CA_PATH}"

MONGO_STRING = "mongodb+srv://doadmin:3b14L8Y6Et07MgS9@db-mongodb-nyc3-17443-8aed69d6.mongo.ondigitalocean.com/admin?tls=true&authSource=admin&replicaSet=db-mongodb-nyc3-17443&tlsCAFile=ca-certificate.crt"
db = connect(
    DATABASE,
    host=MONGO_STRING,
)
print(db)
