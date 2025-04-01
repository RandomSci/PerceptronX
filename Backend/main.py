from connections.database import *
from connections.functions import *
from connections.routes import *
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware


MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "PerceptronX"
COLLECTION_NAME = "annotations"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]
app = FastAPI(title="PerceptronX API", version="1.0")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)


#@app.get("/")
#def home():
#    return {"message": "Hello, PerceptronX!"}

@app.get("/register")
def register():
    pass

@app.get("/login")
def login():
    pass

def serialize_document(doc):
    """Convert MongoDB document to a JSON-serializable format"""
    return {
        "id": str(doc["_id"]),
        "user_id": doc["user_id"],
        "image": doc["image"],
        "annotations": doc["annotations"],
        "size": doc["size"],
        "save_location": doc["save_location"],
        "model_used": doc["model_used"],
        "timestamp": doc["timestamp"].isoformat(),
        "status": doc["status"],
        "confidence_threshold": doc["confidence_threshold"],
        "processing_time": doc["processing_time"],
        "device": doc["device"]
    }

@app.get("/")
def annotation():
    """Fetch all annotations from MongoDB and return as JSON"""
    res = collection.find()
    annotations = [serialize_document(doc) for doc in res]

    if not annotations:
        return {"message": "No annotations found"}

    return {"annotations": annotations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
