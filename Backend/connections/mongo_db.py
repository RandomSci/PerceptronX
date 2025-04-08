from pymongo import MongoClient

def get_Mongo_db(collection_name): #MongoDB
    MONGO_URI = "mongodb://localhost:27017"
    DB_NAME = "PerceptronX"
    COLLECTION_NAME = collection_name

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    return collection


