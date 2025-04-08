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
            "/": "/Therapist_Login",
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
        session_id = request.cookies.get("session_id")
        print(f"Session ID from cookie: {session_id}")

        if not session_id:
            print("No session ID found in cookie")
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_session_data(session_id)
            print(f"Session data retrieved: {session_data}")

            if not session_data:
                print("Session data is None")
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    "SELECT first_name, last_name FROM Therapists WHERE id = %s", 
                    (session_data.user_id,)
                )
                therapist = cursor.fetchone()
                print(f"Therapist data: {therapist}")

                if not therapist:
                    print(f"No therapist found for ID: {session_data.user_id}")
                    return RedirectResponse(url="/Therapist_Login")

                print("Rendering index.html template")
                return templates.TemplateResponse(
                    "dist/dashboard/index.html", 
                    {
                        "request": request,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"]
                    }
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in front-page route: {e}")
            return RedirectResponse(url="/Therapist_Login")

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
            
    @app.route("/Register_User_Web", methods=["GET", "POST"])
    async def Register_User_Web(request: Request):
        form = await request.form()
        first_name = form.get("first_name")
        last_name = form.get("last_name")
        company_email = form.get("company_email")
        password = form.get("password")

        if not all([first_name, last_name, company_email, password]):
            return templates.TemplateResponse("dist/pages/register.html", {
                "request": request,
                "error": "All fields are required."
            })

        db = get_Mysql_db()
        cursor = db.cursor()

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        try:
            cursor.execute(
                "INSERT INTO Therapists (first_name, last_name, company_email, password) VALUES (%s, %s, %s, %s)",
                (first_name, last_name, company_email, hashed_password.decode("utf-8"))
            )
            db.commit()
            return RedirectResponse(url="/", status_code=303)
        except mysql.connector.IntegrityError:
            return templates.TemplateResponse("dist/pages/register.html", {
                "request": request,
                "error": "Therapist with this email already exists."
            })
        finally:
            cursor.close()
            db.close()

    active_sessions: Dict[str, SessionData] = {}

    @app.post("/loginUser")
    async def loginUser(result: Login, response: Response):
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
                    user_id=user_id, 
                    email=result.username,
                    remember=result.remember_me
                )

                max_age = 30 * 24 * 60 * 60 if result.remember_me else None 
                response.set_cookie(
                    key="session_id", 
                    value=session_id, 
                    httponly=True,
                    max_age=max_age,
                    samesite="lax",
                    path="/"
                )
                print("response 152", response)

                return {"status": "valid"}
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
    
    @app.get("/logout")
    async def logout_get(request: Request):
        session_id = request.cookies.get("session_id")
        if session_id:
            await delete_session(session_id)
        response = RedirectResponse(url="/Therapist_Login")
        response.delete_cookie("session_id")
        return response

    async def create_session(user_id: int, email: str, remember: bool = False) -> str:
        session_id = secrets.token_hex(16)

        if remember:
            expires = datetime.datetime.now() + datetime.timedelta(days=30)
        else:
            expires = datetime.datetime.now() + datetime.timedelta(hours=24)

        active_sessions[session_id] = SessionData(
            user_id=user_id,
            email=email,
            expires=expires
        )

        return session_id

    async def delete_session(session_id: str) -> None:
        if session_id in active_sessions:
            del active_sessions[session_id]

    async def get_session_data(session_id: str) -> Optional[SessionData]:
        session = active_sessions.get(session_id)

        if not session:
            return None

        if session.expires < datetime.datetime.now():
            await delete_session(session_id)
            return None

        return session

    @app.get("/Therapist_Login")
    async def therapist_login_page(request: Request):
        session_id = request.cookies.get("session_id")
        if session_id:
            session = await get_session_data(session_id)
            if session:
                return RedirectResponse(url="/front-page")

        return templates.TemplateResponse("dist/pages/login.html", {"request": request})

    @app.post("/Therapist_Login")
    async def therapist_login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        remember: bool = Form(False)
    ):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT id, company_email, password, first_name, last_name FROM Therapists WHERE company_email = %s", 
                (email,)
            )
            therapist = cursor.fetchone()

            if not therapist:
                return templates.TemplateResponse(
                    "dist/pages/login.html", 
                    {"request": request, "error": "Invalid email or password"}
                )

            stored_password = therapist["password"]

            if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                session_id = await create_session(
                    user_id=therapist["id"],
                    email=therapist["company_email"],
                    remember=remember
                )

                print(f"Session created: {session_id}")
                print(f"User ID: {therapist['id']}")

                response = RedirectResponse(url="/front-page", status_code=303)

                max_age = 30 * 24 * 60 * 60 if remember else 24 * 60 * 60

                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    max_age=max_age,
                    httponly=True,
                    # secure=True,  # Commented out for testing - enable in production
                    samesite="lax"
                )

                print(f"Response created with cookie: {response.headers}")
                return response
            else:
                return templates.TemplateResponse(
                    "dist/pages/login.html", 
                    {"request": request, "error": "Invalid email or password"}
                )
        except Exception as e:
            print(f"Login error: {e}")
            return templates.TemplateResponse(
                "dist/pages/login.html", 
                {"request": request, "error": f"Server error: {str(e)}"}
            )
        finally:
            cursor.close()
            db.close()
            
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    @app.get("/qr")
    async def generate_qr_code():
        ip = get_local_ip()
        port = 8000

        server_address = f"http://{ip}:{port}/"

        print(f"[QR] Generating QR code with server address: {server_address}")

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(server_address)
        qr.make(fit=True)

        img = qr.make_image(fill="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)

        return StreamingResponse(buf, media_type="image/png")
    
    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)