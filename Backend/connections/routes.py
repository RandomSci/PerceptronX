from connections.functions import *
from connections.mysql_database import *
from connections.redis_database import *
from connections.mongo_db import *

router = APIRouter()

app = FastAPI(title="PerceptronX API", version="1.0")

class PlatformRoutingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.web_redirects = {
            "/": "/front-page",
            # "/mobile-page": "/web-page",
            # "/app": "/webapp",
        }

    async def dispatch(self, request: Request, call_next):
        user_agent = request.headers.get("User-Agent")
        if not user_agent:
            return await call_next(request)

        ua = user_agents.parse(user_agent)

        if ua.is_mobile:
            return await call_next(request)
        
        current_path = request.url.path
        if current_path in self.web_redirects:
            return RedirectResponse(url=self.web_redirects[current_path])

        return await call_next(request)

app.add_middleware(PlatformRoutingMiddleware)

current_file = FilePath(__file__).resolve()
project_root = current_file.parent.parent.parent

static_directory = project_root / "Frontend_Web" / "static"
templates_directory = project_root / "Frontend_Web" / "templates"

templates = Jinja2Templates(directory=templates_directory)

print(f"Static directory: {static_directory}")
print(f"Templates directory: {templates_directory}")

if static_directory.exists():
    app.mount("/static", StaticFiles(directory=str(static_directory)), name="static")
    print(f"Static directory mounted successfully")
else:
    print(f"Warning: Static directory does not exist: {static_directory}")

if templates_directory.exists():
    app.mount("/dist", StaticFiles(directory=str(templates_directory)), name="templates")
    print(f"Templates directory mounted successfully")
else:
    print(f"Warning: Templates directory does not exist: {templates_directory}")

app.include_router(router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

def Routes():
    @app.get("/")
    async def Home(request: Request):
        session_id = request.cookies.get("session_id")

        if session_id:
            try:
                user_data = await get_session(session_id)
                if user_data:
                    return {"status": "valid", "user": user_data}
            except Exception as e:
                print(f"Session validation error: {e}")

        return {"status": "valid"}
    
    @app.get("/front-page")
    async def front_page(request: Request):
        return templates.TemplateResponse("dist/dashboard/index.html", {"request": request})

    @app.get("/dashboard")
    async def dashboard(user = Depends(get_current_user)):
        return {"message": f"Welcome, {user['username']}!", "user_id": user["user_id"]}

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
            
    # TODO: Implement a user register for web
    @app.get("/Register_User_Web")
    async def Register_User_Web(request: Request):
        return templates.TemplateResponse("dist/pages/register.html", {"request": request})

    @app.post("/loginUser")
    async def loginUser(result: Login):
        db = get_Mysql_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "SELECT user_id, password_hash FROM users WHERE username = %s",
                (result.username,)
            )
            user = cursor.fetchone()

            if user is None:
                raise HTTPException(status_code=401, detail="Invalid username or password")

            user_id, stored_password_hash = user[0], user[1].encode("utf-8")

            if bcrypt.checkpw(result.password.encode("utf-8"), stored_password_hash):
                session_id = await create_session(
                    {"user_id": str(user_id), "username": result.username},
                    remember_me=result.remember_me
                )
                response = JSONResponse(content={"status": "valid"})
                response.set_cookie(key="session_id", value=session_id, httponly=True)
                print(f"response: {response}")
                return response
            else:
                raise HTTPException(status_code=401, detail="Invalid username or password")
        finally:
            cursor.close()
            db.close()
            
    @app.post("/logout")
    async def logout(request: Request):
        session_id = request.cookies.get("session_id")

        if session_id:
            await delete_session(session_id)

        response = JSONResponse(content={"message": "Logged out"})
        response.delete_cookie("session_id")
        return response
    
    @app.get("/logout_web")
    async def logout_web(request: Request):
        session_id = request.cookies.get("session_id")

        if session_id:
            await delete_session(session_id)

        response = JSONResponse(content={"message": "Logged out"})
        response.delete_cookie("session_id")
        return templates.TemplateResponse("dist/pages/login.html", {"request": request})


    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
