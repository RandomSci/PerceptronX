from connections.database import *
from connections.functions import *
from connections.routes import *

app = FastAPI(title="PerceptronX API", version="1.0")

app.include_router(router)

@app.get("/")
def home():
    return {"message": "Hello, PerceptronX!"}

