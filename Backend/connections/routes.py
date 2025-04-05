from connections.functions import *
from connections.database import *
from pydantic import BaseModel


router = APIRouter()

app = FastAPI()

app = FastAPI(title="PerceptronX API", version="1.0")

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

def Routes():
    @app.get("/")
    def Home(res = "invalid"):
        return {"status": res}
    
    @app.post("/registerUser")
    async def registerUser(result: Register): # Mysql 
        db = get_Mysql_db()
        cursor = db.cursor()
    
        hashed_password = bcrypt.hashpw(result.password.encode("utf-8"), bcrypt.gensalt())

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (result.username, result.email, hashed_password.decode("utf-8"))
            )
            db.commit()
            return RedirectResponse(url="/", status_code=303)
        except mysql.connector.IntegrityError:
            return {"error": "Username or email already exists."}
        finally:
            cursor.close()
            db.close()
        
    @app.post("/loginUser")
    async def loginUser(result: Login):# Mysql 
        db = get_Mysql_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "SELECT password_hash FROM users WHERE username = %s",
                (result.username,)
            )
            user = cursor.fetchone()
            if user:
                Home(res="valid")
                
            if user is None:
                raise HTTPException(status_code=401, detail="Invalid username or password")

            stored_password_hash = user[0].encode("utf-8")

            if not bcrypt.checkpw(result.password.encode("utf-8"), stored_password_hash):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            return RedirectResponse(url="/", status_code=303)

        finally:
            cursor.close()
            db.close()
    
    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)