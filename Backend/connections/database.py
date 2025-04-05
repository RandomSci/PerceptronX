import bcrypt
from pymongo import MongoClient
import mysql.connector

def get_Mongo_db(collection_name): #MongoDB
    MONGO_URI = "mongodb://localhost:27017"
    DB_NAME = "PerceptronX"
    COLLECTION_NAME = collection_name

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    return collection

#collection = get_Mongo_db("annotations")
#res = collection.find()

def get_Mysql_db(): #Mysql
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="perceptronx"
    )


