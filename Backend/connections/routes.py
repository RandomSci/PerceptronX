from connections.functions import *
from connections.mysql_database import *
from connections.redis_database import *
from connections.mongo_db import *
from contextlib import asynccontextmanager
import traceback


def find_best_matching_image(therapist_id, requested_filename, static_dir):
    """
    Find the best matching image for a therapist, even if the filename doesn't exactly match.
    This handles cases where database references don't match actual files.
    
    Args:
        therapist_id: The ID of the therapist
        requested_filename: The filename from the database
        static_dir: The static directory path
        
    Returns:
        The best matching filename or a default avatar
    """
    import os
    
    user_images_dir = os.path.join(static_dir, "assets/images/user")
    
    if requested_filename and os.path.exists(os.path.join(user_images_dir, requested_filename)):
        return requested_filename
    
    if therapist_id:
        prefix = f"therapist_{therapist_id}_"
        
        if os.path.exists(user_images_dir) and os.path.isdir(user_images_dir):
            try:
                all_files = os.listdir(user_images_dir)
                
                matching_files = [f for f in all_files if f.startswith(prefix)]
                
                if matching_files:
                    print(f"Found matching image for therapist {therapist_id}: {matching_files[0]}")
                    return matching_files[0]
            except Exception as e:
                print(f"Error searching for matching images: {e}")
    
    avatar_id = (therapist_id % 10) if therapist_id else 1
    default_image = f"avatar-{avatar_id}.jpg"
    
    if os.path.exists(os.path.join(user_images_dir, default_image)):
        return default_image
    else:
        return "avatar-1.jpg"

def getIP():
    try:
        hostname = socket.gethostname()
        
        ip = socket.gethostbyname(hostname)
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        
        full_ip = f"http://{ip}:8000"
        print(f"Using IP: {ip}")
        print(f"Base URL: {full_ip}")
        return full_ip
    except Exception as e:
        print(f"Error detecting IP: {e}")
        print("Defaulting to localhost")
        return "http://127.0.0.1:8000"

def safely_parse_json_field(field_value, default=None):
    """
    Safely parse a JSON field from the database.
    Returns the parsed JSON or the default value if parsing fails.
    """
    if field_value is None:
        return default if default is not None else []
    
    if isinstance(field_value, (list, dict)):
        return field_value
        
    if isinstance(field_value, bytes):
        field_value = field_value.decode('utf-8')
        
    if not isinstance(field_value, str):
        return default if default is not None else []
        
    try:
        return json.loads(field_value)
    except (json.JSONDecodeError, TypeError):
        if isinstance(field_value, str) and ',' in field_value:
            return [item.strip() for item in field_value.split(',')]
        return default if default is not None else []

def ensure_bytes(data):
    """
    Ensure data is in bytes format, converting from string if necessary.
    Use this before writing data to binary mode files or sending to functions expecting bytes.
    """
    if data is None:
        return b''
    if isinstance(data, bytes):
        return data
    if isinstance(data, str):
        return data.encode('utf-8')
    return str(data).encode('utf-8')

def ensure_str(data):
    """
    Ensure data is in string format, converting from bytes if necessary.
    Use this before inserting data into database fields expecting strings.
    """
    if data is None:
        return None
    if isinstance(data, str):
        return data
    if isinstance(data, bytes):
        return data.decode('utf-8')
    return str(data)

async def test_redis_connection():
    pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    if not hasattr(app.state, 'base_url') or not app.state.base_url:
        app.state.base_url = getIP()

    await test_redis_connection()
    yield

def configure_static_files(app):
    static_dir = os.environ.get("STATIC_DIR", None)
    
    if not static_dir:
        current_file = FilePath(__file__).resolve()
        project_root = current_file.parent.parent.parent
        static_dir = str(project_root / "Frontend_Web" / "static")
    
    if not os.path.exists(static_dir):
        os.makedirs(static_dir, exist_ok=True)
        print(f"Created static directory: {static_dir}")
    
    if not hasattr(app.state, 'base_url') or not app.state.base_url:
        base_url = os.environ.get("BASE_URL", None)
        if base_url:
            app.state.base_url = base_url
        else:
            app.state.base_url = getIP()
    
    if not any(route.path == "/static" for route in app.routes):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
        print(f"Static directory mounted: {static_dir}")
    
    print(f"Base URL configured as: {app.state.base_url}")
    
    templates_dir = os.path.join(os.path.dirname(static_dir), "templates")
    if os.path.exists(templates_dir) and not any(route.path == "/dist" for route in app.routes):
        app.mount("/dist", StaticFiles(directory=templates_dir), name="templates")
        print(f"Templates directory mounted: {templates_dir}")
    
    return Jinja2Templates(directory=templates_dir) if os.path.exists(templates_dir) else None

app = FastAPI(title="PerceptronX API", version="1.0", lifespan=lifespan)

templates = configure_static_files(app)

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

@app.on_event("startup")
async def startup_event():
    await test_redis_connection()

router = APIRouter()
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

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
                user_data = await get_redis_session(session_id)
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
            session_data = await get_redis_session(session_id)
            print(f"Session data retrieved: {session_data}")
            if not session_data:
                print("Session data is None")
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)
            try:
 
                cursor.execute(
                    "SELECT first_name, last_name FROM Therapists WHERE id = %s", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()
                print(f"Therapist data: {therapist}")
                if not therapist:
                    print(f"No therapist found for ID: {session_data['user_id']}")
                    return RedirectResponse(url="/Therapist_Login")

 
                cursor.execute(
                    """SELECT m.message_id, m.subject, m.content, m.created_at, 
                            t.first_name, t.last_name, COALESCE(t.profile_image, 'avatar-1.jpg') as profile_image
                        FROM Messages m
                        JOIN Therapists t ON m.sender_id = t.id
                        WHERE m.recipient_id = %s AND m.is_read = FALSE
                        ORDER BY m.created_at DESC
                        LIMIT 4""",
                    (session_data["user_id"],)
                )
                messages_result = cursor.fetchall()

 
                recent_messages = []
                for message in messages_result:
                    message_with_time = message.copy()

 
                    timestamp = message['created_at']
                    now = datetime.datetime.now()
                    if isinstance(timestamp, datetime.datetime):
                        diff = now - timestamp
                        if timestamp.date() == now.date():
                            message_with_time['time_display'] = timestamp.strftime('%I:%M %p')

                            minutes_ago = diff.seconds // 60
                            if minutes_ago < 60:
                                message_with_time['time_ago'] = f"{minutes_ago} min ago"
                            else:
                                hours_ago = minutes_ago // 60
                                message_with_time['time_ago'] = f"{hours_ago} hours ago"

                        elif timestamp.date() == (now - timedelta(days=1)).date():
                            message_with_time['time_display'] = "Yesterday"
                            message_with_time['time_ago'] = timestamp.strftime('%I:%M %p')
                        else:
                            message_with_time['time_display'] = timestamp.strftime('%d %b')
                            message_with_time['time_ago'] = timestamp.strftime('%Y')

                    recent_messages.append(message_with_time)

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Appointments WHERE therapist_id = %s", 
                    (session_data["user_id"],)
                )
                appointments_result = cursor.fetchone()
                appointments_count = appointments_result['count'] if appointments_result else 0

 
                last_month = datetime.datetime.now() - timedelta(days=30)
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Appointments WHERE therapist_id = %s AND created_at < %s", 
                    (session_data["user_id"], last_month)
                )
                last_month_appointments = cursor.fetchone()
                last_month_count = last_month_appointments['count'] if last_month_appointments else 0

 
                appointments_monthly_diff = appointments_count - last_month_count
                appointments_growth = round((appointments_monthly_diff / max(last_month_count, 1)) * 100, 1)

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Patients WHERE therapist_id = %s AND status = 'Active'", 
                    (session_data["user_id"],)
                )
                active_patients_result = cursor.fetchone()
                active_patients_count = active_patients_result['count'] if active_patients_result else 0

 
                this_month_start = datetime.datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Patients WHERE therapist_id = %s AND created_at >= %s", 
                    (session_data["user_id"], this_month_start)
                )
                new_patients_result = cursor.fetchone()
                new_patients_monthly = new_patients_result['count'] if new_patients_result else 0

 
                last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Patients WHERE therapist_id = %s AND created_at BETWEEN %s AND %s", 
                    (session_data["user_id"], last_month_start, this_month_start)
                )
                last_month_new_patients = cursor.fetchone()
                last_month_new_count = last_month_new_patients['count'] if last_month_new_patients else 1
                patient_growth = round((new_patients_monthly / max(last_month_new_count, 1)) * 100, 1)

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM TreatmentPlans WHERE therapist_id = %s", 
                    (session_data["user_id"],)
                )
                treatment_plans_result = cursor.fetchone()
                treatment_plans_count = treatment_plans_result['count'] if treatment_plans_result else 0

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM TreatmentPlans WHERE therapist_id = %s AND created_at >= %s", 
                    (session_data["user_id"], this_month_start)
                )
                new_plans_result = cursor.fetchone()
                new_plans_monthly = new_plans_result['count'] if new_plans_result else 0

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM TreatmentPlans WHERE therapist_id = %s AND created_at BETWEEN %s AND %s", 
                    (session_data["user_id"], last_month_start, this_month_start)
                )
                last_month_plans = cursor.fetchone()
                last_month_plans_count = last_month_plans['count'] if last_month_plans else 1
                plans_growth = round((new_plans_monthly / max(last_month_plans_count, 1)) * 100, 1)

 
                cursor.execute(
                    "SELECT AVG(adherence_rate) as avg_rate FROM PatientMetrics WHERE therapist_id = %s", 
                    (session_data["user_id"],)
                )
                adherence_result = cursor.fetchone()
                average_adherence_rate = round(adherence_result['avg_rate'], 1) if adherence_result and adherence_result['avg_rate'] is not None else 0

 
                cursor.execute(
                    """SELECT AVG(adherence_rate) as avg_rate 
                    FROM PatientMetrics 
                    WHERE therapist_id = %s AND measurement_date BETWEEN %s AND %s""", 
                    (session_data["user_id"], last_month_start, this_month_start)
                )
                last_month_adherence = cursor.fetchone()
                last_month_adherence_rate = last_month_adherence['avg_rate'] if last_month_adherence and last_month_adherence['avg_rate'] is not None else 0

 
                adherence_monthly_diff = round(average_adherence_rate - last_month_adherence_rate, 1)
                adherence_change = abs(adherence_monthly_diff)

                if adherence_monthly_diff >= 0:
                    adherence_trend_direction = "up"
                    adherence_trend_color = "success"
                    adherence_direction = "Up by"
                else:
                    adherence_trend_direction = "down"
                    adherence_trend_color = "warning"
                    adherence_direction = "Down"

                week_ago = datetime.datetime.now() - timedelta(days=7)
                cursor.execute(
                    """SELECT AVG(
                        CASE 
                            WHEN repetitions IS NOT NULL THEN (repetitions_completed / repetitions) * 100
                            ELSE (sets_completed / sets) * 100
                        END
                    ) as completion_rate
                    FROM PatientExerciseProgress pep
                    JOIN TreatmentPlanExercises tpe ON pep.plan_exercise_id = tpe.plan_exercise_id
                    WHERE pep.completion_date >= %s""", 
                    (week_ago,)
                )
                completion_result = cursor.fetchone()
                weekly_completion_rate = round(completion_result['completion_rate'], 0) if completion_result and completion_result['completion_rate'] is not None else 0

 
                cursor.execute(
                    """SELECT p.patient_id, p.first_name, p.last_name, p.diagnosis, p.status,
                        COALESCE(AVG(pm.adherence_rate), 0) as adherence_rate
                    FROM Patients p
                    LEFT JOIN PatientMetrics pm ON p.patient_id = pm.patient_id
                    WHERE p.therapist_id = %s
                    GROUP BY p.patient_id
                    ORDER BY p.created_at DESC
                    LIMIT 5""", 
                    (session_data["user_id"],)
                )
                recent_patients_result = cursor.fetchall()

 
                recent_patients = []
                for patient in recent_patients_result:
                    status_color = "success"
                    if patient['status'] == "Inactive":
                        status_color = "danger"
                    elif patient['status'] == "At Risk":
                        status_color = "warning"

                    patient_with_color = patient.copy()
                    patient_with_color['status_color'] = status_color
                    patient_with_color['adherence_rate'] = round(patient['adherence_rate'], 0)
                    recent_patients.append(patient_with_color)

 
                cursor.execute(
                    "SELECT AVG(recovery_progress) as avg_recovery FROM PatientMetrics WHERE therapist_id = %s", 
                    (session_data["user_id"],)
                )
                recovery_result = cursor.fetchone()
                avg_recovery_rate = round(recovery_result['avg_recovery'], 1) if recovery_result and recovery_result['avg_recovery'] is not None else 0

 
                cursor.execute(
                    """SELECT AVG(
                        CASE 
                            WHEN repetitions IS NOT NULL THEN (repetitions_completed / repetitions) * 100
                            ELSE (sets_completed / sets) * 100
                        END
                    ) as completion_rate
                    FROM PatientExerciseProgress pep
                    JOIN TreatmentPlanExercises tpe ON pep.plan_exercise_id = tpe.plan_exercise_id"""
                )
                overall_completion = cursor.fetchone()
                exercise_completion_rate = round(overall_completion['completion_rate'], 1) if overall_completion and overall_completion['completion_rate'] is not None else 0

 
                cursor.execute(
                    "SELECT AVG(rating) as avg_rating FROM feedback"
                )
                satisfaction_result = cursor.fetchone()
                avg_satisfaction = satisfaction_result['avg_rating'] if satisfaction_result and satisfaction_result['avg_rating'] is not None else 0

                if avg_satisfaction >= 4:
                    patient_satisfaction = "High"
                elif avg_satisfaction >= 3:
                    patient_satisfaction = "Medium"
                else:
                    patient_satisfaction = "Low"

 
                cursor.execute(
                    "SELECT AVG(functionality_score) as avg_score FROM PatientMetrics WHERE therapist_id = %s", 
                    (session_data["user_id"],)
                )
                progress_result = cursor.fetchone()
                progress_metric_value = progress_result['avg_score'] if progress_result and progress_result['avg_score'] is not None else 0

 
                cursor.execute(
                    """(SELECT 'video' as type, 'New Exercise Uploaded' as title, e.name as primary_detail, 
                        CONCAT(e.duration, ' min') as secondary_detail, e.created_at as timestamp,
                        CONCAT('/exercises/', e.exercise_id) as link
                    FROM Exercises e
                    WHERE e.therapist_id = %s
                    ORDER BY e.created_at DESC
                    LIMIT 3)
                    UNION
                    (SELECT 'user-plus' as type, 'New Patient Added' as title, 
                        CONCAT(p.first_name, ' ', p.last_name) as primary_detail, 
                        p.diagnosis as secondary_detail, p.created_at as timestamp,
                        CONCAT('/patients/', p.patient_id) as link
                    FROM Patients p
                    WHERE p.therapist_id = %s
                    ORDER BY p.created_at DESC
                    LIMIT 3)
                    UNION
                    (SELECT 'report-medical' as type, 'Progress Report Updated' as title, 
                        CONCAT(p.first_name, ' ', p.last_name) as primary_detail, 
                        CONCAT('+', pm.recovery_progress, '% improvement') as secondary_detail, 
                        pm.created_at as timestamp,
                        CONCAT('/patients/', p.patient_id) as link
                    FROM PatientMetrics pm
                    JOIN Patients p ON pm.patient_id = p.patient_id
                    WHERE pm.therapist_id = %s
                    ORDER BY pm.created_at DESC
                    LIMIT 3)
                    ORDER BY timestamp DESC
                    LIMIT 3""", 
                    (session_data["user_id"], session_data["user_id"], session_data["user_id"])
                )
                activities_result = cursor.fetchall()

 
                recent_activities = []
                for activity in activities_result:
                    activity_with_color = activity.copy()

 
                    if activity['type'] == 'video':
                        activity_with_color['color'] = 'success'
                        activity_with_color['icon'] = 'video'
                    elif activity['type'] == 'user-plus':
                        activity_with_color['color'] = 'primary'
                        activity_with_color['icon'] = 'user-plus'
                    else:
                        activity_with_color['color'] = 'warning'
                        activity_with_color['icon'] = 'report-medical'

 
                    timestamp = activity['timestamp']
                    now = datetime.datetime.now()
                    if isinstance(timestamp, datetime.datetime):
                        if timestamp.date() == now.date():
                            activity_with_color['timestamp'] = f"Today, {timestamp.strftime('%I:%M %p')}"
                        elif timestamp.date() == (now - timedelta(days=1)).date():
                            activity_with_color['timestamp'] = f"Yesterday, {timestamp.strftime('%I:%M %p')}"
                        else:
                            activity_with_color['timestamp'] = f"{(now - timestamp).days} days ago"

                    recent_activities.append(activity_with_color)

 
                cursor.execute(
                    """SELECT 
                        DATE_FORMAT(completion_date, '%a') as day, 
                        COUNT(*) as count
                    FROM PatientExerciseProgress
                    WHERE completion_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    GROUP BY DATE_FORMAT(completion_date, '%a')
                    ORDER BY FIELD(day, 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')"""
                )
                weekly_activity = cursor.fetchall()

 
                days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                activity_data = {day: 0 for day in days_of_week}

                for record in weekly_activity:
                    if record['day'] in activity_data:
                        activity_data[record['day']] = record['count']

                chart_data = [{'day': day, 'count': count} for day, count in activity_data.items()]

                cursor.execute(
                    """SELECT 
                        DATE_FORMAT(completion_date, '%d') as date, 
                        COUNT(*) as count
                    FROM PatientExerciseProgress
                    WHERE completion_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE_FORMAT(completion_date, '%d')
                    ORDER BY date"""
                )
                monthly_activity = cursor.fetchall()
                monthly_chart_data = [{'date': record['date'], 'count': record['count']} for record in monthly_activity]

                cursor.execute(
                    """SELECT 
                        DATE_FORMAT(measurement_date, '%d %b') as date,
                        AVG(functionality_score) as score 
                    FROM PatientMetrics 
                    WHERE measurement_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    AND therapist_id = %s
                    GROUP BY DATE_FORMAT(measurement_date, '%d %b')
                    ORDER BY measurement_date""", 
                    (session_data["user_id"],)
                )
                progress_chart_data = cursor.fetchall()
                progress_data = [{'date': record['date'], 'score': float(record['score']) if record['score'] is not None else 0} for record in progress_chart_data]

 
                cursor.execute(
                    """SELECT 
                        CASE 
                            WHEN (
                                CASE 
                                    WHEN repetitions IS NOT NULL THEN (repetitions_completed / repetitions) * 100
                                    ELSE (sets_completed / sets) * 100
                                END
                            ) >= 90 THEN 'Completed'
                            WHEN (
                                CASE 
                                    WHEN repetitions IS NOT NULL THEN (repetitions_completed / repetitions) * 100
                                    ELSE (sets_completed / sets) * 100
                                END
                            ) >= 50 THEN 'Partial'
                            ELSE 'Missed'
                        END as status,
                        COUNT(*) as count
                    FROM PatientExerciseProgress pep
                    JOIN TreatmentPlanExercises tpe ON pep.plan_exercise_id = tpe.plan_exercise_id
                    WHERE completion_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                    GROUP BY status"""
                )
                completion_breakdown = cursor.fetchall()
                donut_data = {'Completed': 0, 'Partial': 0, 'Missed': 0}
                for record in completion_breakdown:
                    if record['status'] in donut_data:
                        donut_data[record['status']] = record['count']

 
                print("Rendering dashboard template with dynamic data")
                return templates.TemplateResponse(
                    "dist/dashboard/index.html", 
                    {
                        "request": request,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"],
                        "appointments_count": appointments_count,
                        "appointments_growth": appointments_growth,
                        "appointments_monthly_diff": appointments_monthly_diff,
                        "active_patients_count": active_patients_count,
                        "patient_growth": patient_growth,
                        "new_patients_monthly": new_patients_monthly,
                        "treatment_plans_count": treatment_plans_count,
                        "plans_growth": plans_growth,
                        "new_plans_monthly": new_plans_monthly,
                        "average_adherence_rate": average_adherence_rate,
                        "adherence_trend_color": adherence_trend_color,
                        "adherence_trend_direction": adherence_trend_direction,
                        "adherence_change": adherence_change,
                        "adherence_direction": adherence_direction,
                        "adherence_monthly_diff": adherence_monthly_diff,
                        "weekly_completion_rate": weekly_completion_rate,
                        "recent_patients": recent_patients,
                        "avg_recovery_rate": avg_recovery_rate,
                        "exercise_completion_rate": exercise_completion_rate,
                        "patient_satisfaction": patient_satisfaction,
                        "progress_metric_value": progress_metric_value,
                        "recent_activities": recent_activities,
                        "chart_data": chart_data,
                        "monthly_chart_data": monthly_chart_data,
                        "progress_data": progress_data,
                        "donut_data": donut_data,
                        "recent_messages": recent_messages,
                        "unread_messages_count": unread_messages_count
                    }
                )
            except Exception as e:
                print(f"Database error in front-page route: {e}")
                return RedirectResponse(url="/Therapist_Login")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in front-page route: {e}")
            return RedirectResponse(url="/Therapist_Login")
        
    @app.get("/messages")
    async def messages_page(request: Request, search: str = None):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    "SELECT first_name, last_name FROM Therapists WHERE id = %s", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()
                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")

 
                search_condition = ""
                search_params = []
                if search:
                    search_condition = """
                        AND (
                            t.first_name LIKE %s OR 
                            t.last_name LIKE %s OR 
                            m.subject LIKE %s OR 
                            m.content LIKE %s
                        )
                    """
                    search_term = f"%{search}%"
                    search_params = [search_term, search_term, search_term, search_term]

 
                inbox_query = f"""
                    SELECT 
                        m.message_id, m.subject, m.content, m.created_at, m.is_read,
                        CASE 
                            WHEN m.sender_type = 'therapist' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Therapists WHERE id = m.sender_id)
                            WHEN m.sender_type = 'patient' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Patients WHERE patient_id = m.sender_id)
                            ELSE 
                                (SELECT username FROM users WHERE user_id = m.sender_id)
                        END as sender_name,
                        CASE 
                            WHEN m.sender_type = 'therapist' THEN 
                                COALESCE((SELECT profile_image FROM Therapists WHERE id = m.sender_id), 'avatar-1.jpg')
                            WHEN m.sender_type = 'patient' THEN 
                                'patient-avatar.jpg'
                            ELSE 
                                COALESCE((SELECT profile_pic FROM users WHERE user_id = m.sender_id), 'user-avatar.jpg')
                        END as profile_image,
                        m.sender_type,
                        m.sender_id
                    FROM Messages m
                    WHERE m.recipient_id = %s 
                    AND m.recipient_type = 'therapist'
                    {search_condition}
                    ORDER BY m.created_at DESC
                """

                inbox_params = [session_data["user_id"]] + search_params if search else [session_data["user_id"]]
                cursor.execute(inbox_query, inbox_params)
                inbox_messages = cursor.fetchall()

 
                sent_query = f"""
                    SELECT 
                        m.message_id, m.subject, m.content, m.created_at, m.is_read,
                        CASE 
                            WHEN m.recipient_type = 'therapist' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Therapists WHERE id = m.recipient_id)
                            WHEN m.recipient_type = 'patient' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Patients WHERE patient_id = m.recipient_id)
                            ELSE 
                                (SELECT username FROM users WHERE user_id = m.recipient_id)
                        END as recipient_name,
                        CASE 
                            WHEN m.recipient_type = 'therapist' THEN 
                                COALESCE((SELECT profile_image FROM Therapists WHERE id = m.recipient_id), 'avatar-1.jpg')
                            WHEN m.recipient_type = 'patient' THEN 
                                'patient-avatar.jpg'
                            ELSE 
                                COALESCE((SELECT profile_pic FROM users WHERE user_id = m.recipient_id), 'user-avatar.jpg')
                        END as profile_image,
                        m.recipient_type,
                        m.recipient_id
                    FROM Messages m
                    WHERE m.sender_id = %s 
                    AND m.sender_type = 'therapist'
                    {search_condition}
                    ORDER BY m.created_at DESC
                """

                sent_params = [session_data["user_id"]] + search_params if search else [session_data["user_id"]]
                cursor.execute(sent_query, sent_params)
                sent_messages = cursor.fetchall()

 
                for messages_list in [inbox_messages, sent_messages]:
                    for message in messages_list:
 
                        timestamp = message['created_at']
                        now = datetime.datetime.now()
                        if isinstance(timestamp, datetime.datetime):
                            diff = now - timestamp

                            if timestamp.date() == now.date():
                                message['formatted_date'] = timestamp.strftime('%I:%M %p')

                                minutes_ago = diff.seconds // 60
                                if minutes_ago < 60:
                                    message['time_ago'] = f"{minutes_ago} min ago"
                                else:
                                    hours_ago = minutes_ago // 60
                                    message['time_ago'] = f"{hours_ago} hours ago"

                            elif timestamp.date() == (now - timedelta(days=1)).date():
                                message['formatted_date'] = "Yesterday"
                                message['time_ago'] = timestamp.strftime('%I:%M %p')
                            else:
                                message['formatted_date'] = timestamp.strftime('%d %b')
                                message['time_ago'] = timestamp.strftime('%Y')

 
                        if message['content'] and len(message['content']) > 100:
                            message['short_content'] = message['content'][:100] + '...'
                        else:
                            message['short_content'] = message['content']

 
                cursor.execute(
                    "SELECT id, first_name, last_name FROM Therapists WHERE id != %s",
                    (session_data["user_id"],)
                )
                therapists = cursor.fetchall()

 
                cursor.execute(
                    "SELECT patient_id, first_name, last_name FROM Patients"
                )
                patients = cursor.fetchall()

 
                cursor.execute(
                    "SELECT user_id, username FROM users"
                )
                users = cursor.fetchall()

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

                return templates.TemplateResponse(
                    "dist/messages/index.html", 
                    {
                        "request": request,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"],
                        "inbox_messages": inbox_messages,
                        "sent_messages": sent_messages,
                        "therapists": therapists,
                        "patients": patients,
                        "users": users,
                        "unread_messages_count": unread_messages_count,
                        "search_term": search
                    }
                )

            except Exception as e:
                print(f"Database error in messages page: {e}")
                return RedirectResponse(url="/front-page")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in messages page: {e}")
            return RedirectResponse(url="/Therapist_Login")
        
    
    @app.get("/messages/{message_id}")
    async def view_message(request: Request, message_id: int):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    "SELECT first_name, last_name FROM Therapists WHERE id = %s", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()
                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")

 
                cursor.execute(
                    """SELECT 
                        m.message_id, m.subject, m.content, m.created_at, m.is_read,
                        m.sender_id, m.recipient_id, m.sender_type, m.recipient_type,
                        CASE 
                            WHEN m.sender_type = 'therapist' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Therapists WHERE id = m.sender_id)
                            WHEN m.sender_type = 'patient' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Patients WHERE patient_id = m.sender_id)
                            ELSE 
                                (SELECT username FROM users WHERE user_id = m.sender_id)
                        END as sender_name,
                        CASE 
                            WHEN m.recipient_type = 'therapist' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Therapists WHERE id = m.recipient_id)
                            WHEN m.recipient_type = 'patient' THEN 
                                (SELECT CONCAT(first_name, ' ', last_name) FROM Patients WHERE patient_id = m.recipient_id)
                            ELSE 
                                (SELECT username FROM users WHERE user_id = m.recipient_id)
                        END as recipient_name,
                        CASE 
                            WHEN m.sender_type = 'therapist' THEN 
                                COALESCE((SELECT profile_image FROM Therapists WHERE id = m.sender_id), 'avatar-1.jpg')
                            WHEN m.sender_type = 'patient' THEN 
                                'patient-avatar.jpg'
                            ELSE 
                                COALESCE((SELECT profile_pic FROM users WHERE user_id = m.sender_id), 'user-avatar.jpg')
                        END as sender_profile_image
                    FROM Messages m
                    WHERE m.message_id = %s
                    AND ((m.sender_id = %s AND m.sender_type = 'therapist') 
                         OR (m.recipient_id = %s AND m.recipient_type = 'therapist'))""", 
                    (message_id, session_data["user_id"], session_data["user_id"])
                )
                message = cursor.fetchone()

                if not message:
 
                    return RedirectResponse(url="/messages")

 
                if message['recipient_id'] == int(session_data["user_id"]) and message['recipient_type'] == 'therapist' and not message['is_read']:
                    cursor.execute(
                        "UPDATE Messages SET is_read = TRUE WHERE message_id = %s",
                        (message_id,)
                    )
                    db.commit()

 
                timestamp = message['created_at']
                if isinstance(timestamp, datetime.datetime):
                    now = datetime.datetime.now()
                    if timestamp.date() == now.date():
                        message['formatted_date'] = f"Today at {timestamp.strftime('%I:%M %p')}"
                    elif timestamp.date() == (now - timedelta(days=1)).date():
                        message['formatted_date'] = f"Yesterday at {timestamp.strftime('%I:%M %p')}"
                    else:
                        message['formatted_date'] = timestamp.strftime('%b %d, %Y at %I:%M %p')

 
                message['direction'] = 'received' if message['recipient_id'] == int(session_data["user_id"]) and message['recipient_type'] == 'therapist' else 'sent'

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

                return templates.TemplateResponse(
                    "dist/messages/view.html",
                    {
                        "request": request,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"],
                        "message": message,
                        "unread_messages_count": unread_messages_count
                    }
                )

            except Exception as e:
                print(f"Database error in view message: {e}")
                return RedirectResponse(url="/messages")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in view message: {e}")
            return RedirectResponse(url="/Therapist_Login")

    @app.post("/messages/send")
    async def send_message(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return {"success": False, "message": "Not authenticated"}

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return {"success": False, "message": "Not authenticated"}

            form_data = await request.form()
            recipient_type = form_data.get("recipient_type")
            recipient_id = form_data.get("recipient_id")
            subject = form_data.get("subject")
            content = form_data.get("content")

 
            if not recipient_type or not recipient_id or not content:
                return {"success": False, "message": "Recipient and message content are required"}

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                recipient_exists = False

                if recipient_type == "therapist":
                    cursor.execute(
                        "SELECT id FROM Therapists WHERE id = %s",
                        (recipient_id,)
                    )
                    recipient = cursor.fetchone()
                    recipient_exists = recipient is not None
                elif recipient_type == "patient":
                    cursor.execute(
                        "SELECT patient_id FROM Patients WHERE patient_id = %s",
                        (recipient_id,)
                    )
                    recipient = cursor.fetchone()
                    recipient_exists = recipient is not None
                elif recipient_type == "user":
                    cursor.execute(
                        "SELECT user_id FROM users WHERE user_id = %s",
                        (recipient_id,)
                    )
                    recipient = cursor.fetchone()
                    recipient_exists = recipient is not None

                if not recipient_exists:
                    return {"success": False, "message": "Recipient not found"}

 
                cursor.execute(
                    """INSERT INTO Messages 
                        (sender_id, sender_type, recipient_id, recipient_type, subject, content) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                    (session_data["user_id"], "therapist", recipient_id, recipient_type, subject, content)
                )
                db.commit()

 
                new_message_id = cursor.lastrowid

                return {"success": True, "message_id": new_message_id}

            except Exception as e:
                print(f"Database error sending message: {e}")
                return {"success": False, "message": "Error sending message"}
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error sending message: {e}")
            return {"success": False, "message": "Error processing request"}

    @app.post("/messages/reply/{message_id}")
    async def reply_to_message(request: Request, message_id: int):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return {"success": False, "message": "Not authenticated"}

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return {"success": False, "message": "Not authenticated"}

            form_data = await request.form()
            content = form_data.get("content")

 
            if not content:
                return {"success": False, "message": "Message content is required"}

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT sender_id, recipient_id, subject, sender_type, recipient_type
                        FROM Messages 
                        WHERE message_id = %s 
                        AND ((sender_id = %s AND sender_type = 'therapist') 
                             OR (recipient_id = %s AND recipient_type = 'therapist'))""",
                    (message_id, session_data["user_id"], session_data["user_id"])
                )
                original_message = cursor.fetchone()

                if not original_message:
                    return {"success": False, "message": "Original message not found"}

 
                if int(original_message['recipient_id']) == int(session_data["user_id"]) and original_message['recipient_type'] == 'therapist':
                    reply_to_id = original_message['sender_id']
                    reply_to_type = original_message['sender_type']
                else:
                    reply_to_id = original_message['recipient_id']
                    reply_to_type = original_message['recipient_type']

 
                subject = original_message['subject']
                if not subject.startswith("Re:"):
                    subject = f"Re: {subject}"

 
                cursor.execute(
                    """INSERT INTO Messages 
                        (sender_id, sender_type, recipient_id, recipient_type, subject, content) 
                        VALUES (%s, %s, %s, %s, %s, %s)""",
                    (session_data["user_id"], "therapist", reply_to_id, reply_to_type, subject, content)
                )
                db.commit()

 
                new_message_id = cursor.lastrowid

                return {"success": True, "message_id": new_message_id}

            except Exception as e:
                print(f"Database error sending reply: {e}")
                return {"success": False, "message": "Error sending reply"}
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error sending reply: {e}")
            return {"success": False, "message": "Error processing request"}

    @app.delete("/messages/{message_id}")
    async def delete_message(request: Request, message_id: int):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return {"success": False, "message": "Not authenticated"}

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return {"success": False, "message": "Not authenticated"}

            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    """SELECT message_id 
                       FROM Messages 
                       WHERE message_id = %s 
                       AND ((sender_id = %s AND sender_type = 'therapist') 
                            OR (recipient_id = %s AND recipient_type = 'therapist'))""",
                    (message_id, session_data["user_id"], session_data["user_id"])
                )

                message = cursor.fetchone()
                if not message:
                    return {"success": False, "message": "Message not found or you don't have permission to delete it"}

 
                cursor.execute(
                    "DELETE FROM Messages WHERE message_id = %s",
                    (message_id,)
                )
                db.commit()

                return {"success": True}

            except Exception as e:
                print(f"Database error deleting message: {e}")
                return {"success": False, "message": "Error deleting message"}
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error deleting message: {e}")
            return {"success": False, "message": "Error processing request"}
        
    @app.get("/api/messages/unread-count")
    async def get_unread_count(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return {"count": 0}

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return {"count": 0}

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                result = cursor.fetchone()
                return {"count": result['count'] if result else 0}

            except Exception as e:
                print(f"Error fetching unread count: {e}")
                return {"count": 0}
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in unread count API: {e}")
            return {"count": 0}
        
    @app.get("/profile")
    async def view_profile(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    """SELECT id, first_name, last_name, company_email, profile_image, 
                            bio, experience_years, specialties, education, languages, 
                            address, rating, review_count, 
                            is_accepting_new_patients, average_session_length
                    FROM Therapists 
                    WHERE id = %s""", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()

                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")

                for field in ['specialties', 'education', 'languages']:
                    therapist[field] = safely_parse_json_field(therapist[field])

                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

                cursor.execute(
                    """SELECT patient_id, first_name, last_name, diagnosis, status 
                    FROM Patients 
                    WHERE therapist_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT 5""",
                    (session_data["user_id"],)
                )
                recent_patients = cursor.fetchall()
                
                for patient in recent_patients:
                    for key in patient:
                        if isinstance(patient[key], bytes):
                            patient[key] = patient[key].decode('utf-8')

                cursor.execute(
                    "SELECT COUNT(*) as count FROM Patients WHERE therapist_id = %s",
                    (session_data["user_id"],)
                )
                total_patients_result = cursor.fetchone()
                total_patients = total_patients_result['count'] if total_patients_result else 0

                cursor.execute(
                    """SELECT AVG(rating) as average_rating, COUNT(*) as review_count 
                    FROM Reviews 
                    WHERE therapist_id = %s""",
                    (session_data["user_id"],)
                )
                reviews_summary = cursor.fetchone()
                if reviews_summary and reviews_summary['average_rating']:
                    average_rating = round(reviews_summary['average_rating'], 1)
                    review_count = reviews_summary['review_count']
                else:
                    average_rating = 0
                    review_count = 0

                cursor.execute(
                    """SELECT r.review_id, r.rating, r.comment, r.created_at, 
                            p.first_name, p.last_name
                    FROM Reviews r
                    JOIN Patients p ON r.patient_id = p.patient_id
                    WHERE r.therapist_id = %s
                    ORDER BY r.created_at DESC
                    LIMIT 3""",
                    (session_data["user_id"],)
                )
                recent_reviews = cursor.fetchall()
                
                for review in recent_reviews:
                    for key in review:
                        if isinstance(review[key], bytes):
                            review[key] = review[key].decode('utf-8')

                return templates.TemplateResponse(
                    "dist/dashboard/therapist_profile.html",
                    {
                        "request": request,
                        "therapist": therapist,
                        "first_name": ensure_str(therapist["first_name"]),
                        "last_name": ensure_str(therapist["last_name"]),
                        "unread_messages_count": unread_messages_count,
                        "recent_patients": recent_patients,
                        "total_patients": total_patients,
                        "average_rating": average_rating,
                        "review_count": review_count,
                        "recent_reviews": recent_reviews,
                    }
                )

            except Exception as e:
                print(f"Database error in profile view: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return RedirectResponse(url="/front-page")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in profile view: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return RedirectResponse(url="/Therapist_Login")
    @app.get("/api/therapist/{therapist_id}")
    async def get_therapist_api(therapist_id: int):
        """API endpoint to get therapist information"""
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT id, first_name, last_name, profile_image, 
                        bio, experience_years, specialties, education, languages, 
                        address, rating, review_count, 
                        is_accepting_new_patients, average_session_length
                FROM Therapists 
                WHERE id = %s""", 
                (therapist_id,)
            )
            therapist = cursor.fetchone()

            if not therapist:
                return JSONResponse(
                    status_code=404,
                    content={"error": "Therapist not found"}
                )

 
            for field in ['specialties', 'education', 'languages']:
                if therapist[field] and isinstance(therapist[field], str):
                    try:
                        therapist[field] = json.loads(therapist[field])
                    except:
                        therapist[field] = []
                elif therapist[field] is None:
                    therapist[field] = []

 
            response_data = {
                "id": therapist["id"],
                "name": f"{therapist['first_name']} {therapist['last_name']}",
                "photoUrl": f"/static/assets/images/user/{therapist['profile_image']}",
                "specialties": therapist["specialties"],
                "bio": therapist["bio"] or "",
                "experienceYears": therapist["experience_years"] or 0,
                "education": therapist["education"],
                "languages": therapist["languages"],
                "address": therapist["address"] or "",
                "rating": therapist["rating"] or 0,
                "reviewCount": therapist["review_count"] or 0,
                "isAcceptingNewPatients": bool(therapist["is_accepting_new_patients"]),
                "averageSessionLength": therapist["average_session_length"] or 60
            }

            return response_data

        except Exception as e:
            print(f"Database error in get therapist API: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Internal server error: {str(e)}"}
            )
        finally:
            cursor.close()
            db.close()
        
    @app.get("`/profile`/edit")
    async def edit_profile_form(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")
        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute(
                    """SELECT id, first_name, last_name, company_email, profile_image, 
                            bio, experience_years, specialties, education, languages, 
                            address, rating, review_count, 
                            is_accepting_new_patients, average_session_length
                    FROM Therapists 
                    WHERE id = %s""", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()
                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")
                for field in ['specialties', 'education', 'languages']:
                    therapist[field] = safely_parse_json_field(therapist[field])
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0
                all_specialties = get_all_specialties()
                existing_specialties = therapist["specialties"]
                
                return templates.TemplateResponse(
                    "dist/dashboard/therapist_edit_profile.html",
                    {
                        "request": request,
                        "therapist": therapist,
                        "first_name": ensure_str(therapist["first_name"]),
                        "last_name": ensure_str(therapist["last_name"]),
                        "unread_messages_count": unread_messages_count,
                        "all_specialties": all_specialties,
                        "existing_specialties": existing_specialties
                    }
                )
            except Exception as e:
                print(f"Database error in edit profile form: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return RedirectResponse(url="/front-page")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in edit profile form: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return RedirectResponse(url="/Therapist_Login")
        
    @app.get("/profile/edit")
    async def edit_profile_form(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")
        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)
            try:
                cursor.execute(
                    """SELECT id, first_name, last_name, company_email, profile_image, 
                            bio, experience_years, specialties, education, languages, 
                            address, rating, review_count, 
                            is_accepting_new_patients, average_session_length
                    FROM Therapists 
                    WHERE id = %s""", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()
                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")
                for field in ['specialties', 'education', 'languages']:
                    therapist[field] = safely_parse_json_field(therapist[field])
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0
                all_specialties = get_all_specialties()
                existing_specialties = therapist["specialties"]
                
                return templates.TemplateResponse(
                    "dist/dashboard/therapist_edit_profile.html",
                    {
                        "request": request,
                        "therapist": therapist,
                        "first_name": ensure_str(therapist["first_name"]),
                        "last_name": ensure_str(therapist["last_name"]),
                        "unread_messages_count": unread_messages_count,
                        "all_specialties": all_specialties,
                        "existing_specialties": existing_specialties
                    }
                )
            except Exception as e:
                print(f"Database error in edit profile form: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return RedirectResponse(url="/front-page")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in edit profile form: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return RedirectResponse(url="/Therapist_Login")
    
    @app.post("/profile/update2")
    async def update_profile_v2(request: Request):
        """
        A completely new implementation of profile update using only the Request object.
        This approach eliminates any potential conflict with FastAPI's Form dependencies.
        """
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login", status_code=303)

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login", status_code=303)
            form_data = await request.form()
            profile_data = {
                "first_name": ensure_str(form_data.get("first_name", "")),
                "last_name": ensure_str(form_data.get("last_name", "")),
                "company_email": ensure_str(form_data.get("company_email", "")),
                "bio": ensure_str(form_data.get("bio", "")),
                "address": ensure_str(form_data.get("address", ""))
            }
            try:
                profile_data["experience_years"] = int(form_data.get("experience_years", "0"))
            except ValueError:
                profile_data["experience_years"] = 0
                
            try:
                profile_data["rating"] = float(form_data.get("rating", "0"))
            except ValueError:
                profile_data["rating"] = 0
                
            try:
                profile_data["review_count"] = int(form_data.get("review_count", "0"))
            except ValueError:
                profile_data["review_count"] = 0
                
            try:
                profile_data["average_session_length"] = int(form_data.get("average_session_length", "60"))
            except ValueError:
                profile_data["average_session_length"] = 60
            profile_data["is_accepting_new_patients"] = form_data.get("is_accepting_new_patients") == "1"
            specialties = form_data.getlist("specialties")
            profile_data["specialties"] = json.dumps(specialties)
                
            education = form_data.getlist("education")
            profile_data["education"] = json.dumps(education)
                
            languages = form_data.getlist("languages")
            profile_data["languages"] = json.dumps(languages)
            profile_image_filename = None
            profile_image = form_data.get("profile_image")
            if profile_image and hasattr(profile_image, "filename") and profile_image.filename:
                try:
                    contents = await profile_image.read()
                    if contents and len(contents) > 0:
                        contents = ensure_bytes(contents)
                        file_extension = profile_image.filename.split(".")[-1].lower()
                        allowed_extensions = ["jpg", "jpeg", "png", "gif"]
                        
                        if file_extension in allowed_extensions:
                            profile_image_filename = f"therapist_{session_data['user_id']}_{int(time.time())}.{file_extension}"
                            current_file = FilePath(__file__).resolve()
                            project_root = current_file.parent.parent.parent
                            uploads_dir = project_root / "Frontend_Web" / "static" / "assets" / "images" / "user"
                            uploads_dir.mkdir(parents=True, exist_ok=True)
                            file_path = uploads_dir / profile_image_filename
                            with open(file_path, "wb") as f:
                                f.write(contents)
                            
                            print(f"Profile image saved: {profile_image_filename}")
                            print(f"File path: {file_path}")
                        else:
                            print(f"Invalid file extension: {file_extension}")
                    else:
                        print("Empty file content")
                except Exception as img_error:
                    print(f"Error processing image: {img_error}")
                    print(f"Traceback: {traceback.format_exc()}")
            db = get_Mysql_db()
            cursor = None
            try:
                cursor = db.cursor()
                update_fields = []
                params = []
                for field in profile_data:
                    update_fields.append(f"{field} = %s")
                    params.append(profile_data[field])
                if profile_image_filename:
                    update_fields.append("profile_image = %s")
                    params.append(profile_image_filename)
                params.append(session_data["user_id"])
                query = f"UPDATE Therapists SET {', '.join(update_fields)} WHERE id = %s"
                cursor.execute(query, params)
                db.commit()
                print("Profile updated successfully")
                return RedirectResponse(url="/profile", status_code=303)
            except Exception as db_error:
                print(f"Database error: {db_error}")
                print(f"Traceback: {traceback.format_exc()}")
                if db:
                    db.rollback()
                return RedirectResponse(url="/profile/edit", status_code=303)
            finally:
                if cursor:
                    cursor.close()
                if db:
                    db.close()
                    
        except Exception as e:
            print(f"Unexpected error in profile update: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return RedirectResponse(url="/Therapist_Login", status_code=303)

 

    async def get_therapist_data(db, user_id):
        """Retrieve therapist data from database"""
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                """SELECT id, first_name, last_name, company_email, profile_image, 
                        bio, experience_years, specialties, education, languages, 
                        address, rating, review_count, 
                        is_accepting_new_patients, average_session_length
                FROM Therapists 
                WHERE id = %s""", 
                (user_id,)
            )
            therapist = cursor.fetchone()
            
 
            for field in ['specialties', 'education', 'languages']:
                if therapist[field] and isinstance(therapist[field], str):
                    try:
                        therapist[field] = json.loads(therapist[field])
                    except:
                        therapist[field] = []
                elif therapist[field] is None:
                    therapist[field] = []
                    
            return therapist
        except Exception as e:
            print(f"Error retrieving therapist data: {e}")
            return {
                "first_name": "",
                "last_name": "",
                "company_email": "",
                "profile_image": "avatar-1.jpg",
                "specialties": [],
                "education": [],
                "languages": []
            }
        finally:
            if cursor:
                cursor.close()

    async def get_unread_messages_count(db, user_id):
        """Get count of unread messages"""
        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute(
                "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                (user_id,)
            )
            result = cursor.fetchone()
            return result['count'] if result else 0
        except Exception as e:
            print(f"Error counting unread messages: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()

    def get_all_specialties():
        """Return list of all specialties"""
        return [
            "Orthopedic Physical Therapy",
            "Neurological Physical Therapy",
            "Cardiovascular & Pulmonary Physical Therapy",
            "Pediatric Physical Therapy",
            "Geriatric Physical Therapy",
            "Sports Physical Therapy",
            "Women's Health Physical Therapy",
            "Manual Therapy",
            "Vestibular Rehabilitation",
            "Post-Surgical Rehabilitation",
            "Pain Management"
        ]
        
    @app.get("/api/therapist/{therapist_id}")
    async def get_therapist_api(therapist_id: int):
            """API endpoint to get therapist information"""
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    """SELECT id, first_name, last_name, profile_image, 
                            bio, experience_years, specialties, education, languages, 
                            address, latitude, longitude, rating, review_count, 
                            is_accepting_new_patients, average_session_length
                    FROM Therapists 
                    WHERE id = %s""", 
                    (therapist_id,)
                )
                therapist = cursor.fetchone()

                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Therapist not found"}
                    )

 
                for field in ['specialties', 'education', 'languages']:
                    if therapist[field] and isinstance(therapist[field], str):
                        try:
                            therapist[field] = json.loads(therapist[field])
                        except:
                            therapist[field] = []
                    elif therapist[field] is None:
                        therapist[field] = []

 
                response_data = {
                    "id": therapist["id"],
                    "name": f"{therapist['first_name']} {therapist['last_name']}",
                    "photoUrl": f"/static/assets/images/user/{therapist['profile_image']}",
                    "specialties": therapist["specialties"],
                    "bio": therapist["bio"] or "",
                    "experienceYears": therapist["experience_years"] or 0,
                    "education": therapist["education"],
                    "languages": therapist["languages"],
                    "address": therapist["address"] or "",
                    "latitude": therapist["latitude"] or 0,
                    "longitude": therapist["longitude"] or 0,
                    "rating": therapist["rating"] or 0,
                    "reviewCount": therapist["review_count"] or 0,
                    "isAcceptingNewPatients": bool(therapist["is_accepting_new_patients"]),
                    "averageSessionLength": therapist["average_session_length"] or 60
                }

                return response_data

            except Exception as e:
                print(f"Database error in get therapist API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()


    @app.get("/api/therapist/{therapist_id}/reviews")
    async def get_therapist_reviews(therapist_id: int, limit: int = 10, offset: int = 0):
        """API endpoint to get therapist reviews"""
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
 
            cursor.execute(
                """SELECT r.review_id, r.rating, r.comment, r.created_at, 
                         p.patient_id, p.first_name, p.last_name
                   FROM Reviews r
                   JOIN Patients p ON r.patient_id = p.patient_id
                   WHERE r.therapist_id = %s
                   ORDER BY r.created_at DESC
                   LIMIT %s OFFSET %s""", 
                (therapist_id, limit, offset)
            )
            reviews = cursor.fetchall()

 
            cursor.execute(
                """SELECT COUNT(*) as total, AVG(rating) as average_rating
                   FROM Reviews
                   WHERE therapist_id = %s""", 
                (therapist_id,)
            )
            stats = cursor.fetchone()

 
            formatted_reviews = []
            for review in reviews:
                formatted_reviews.append({
                    "id": review["review_id"],
                    "rating": review["rating"],
                    "comment": review["comment"],
                    "createdAt": review["created_at"].isoformat(),
                    "patient": {
                        "id": review["patient_id"],
                        "name": f"{review['first_name']} {review['last_name']}"
                    }
                })

            return {
                "reviews": formatted_reviews,
                "totalReviews": stats["total"] or 0,
                "averageRating": float(stats["average_rating"]) if stats["average_rating"] else 0,
                "limit": limit,
                "offset": offset
            }

        except Exception as e:
            print(f"Database error in get therapist reviews API: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Internal server error: {str(e)}"}
            )
        finally:
            cursor.close()
            db.close()


    @app.post("/api/therapist/reviews")
    async def create_therapist_review(
        request: Request,
        therapist_id: int = Form(...),
        patient_id: int = Form(...),
        rating: float = Form(...),
        comment: str = Form(None)
    ):
        """API endpoint to create a review for a therapist"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"error": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Not authenticated"}
                )

 
 

            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    """SELECT review_id FROM Reviews 
                       WHERE therapist_id = %s AND patient_id = %s""", 
                    (therapist_id, patient_id)
                )
                existing_review = cursor.fetchone()

                if existing_review:
 
                    cursor.execute(
                        """UPDATE Reviews 
                           SET rating = %s, comment = %s, updated_at = NOW() 
                           WHERE therapist_id = %s AND patient_id = %s""", 
                        (rating, comment, therapist_id, patient_id)
                    )
                    db.commit()

                    return {"message": "Review updated successfully", "review_id": existing_review[0]}
                else:
 
                    cursor.execute(
                        """INSERT INTO Reviews (therapist_id, patient_id, rating, comment)
                           VALUES (%s, %s, %s, %s)""", 
                        (therapist_id, patient_id, rating, comment)
                    )
                    db.commit()

                    return {"message": "Review created successfully", "review_id": cursor.lastrowid}

            except Exception as e:
                db.rollback()
                print(f"Database error in create review: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Error submitting review: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in create review: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Error processing request: {str(e)}"}
            )

    @app.get("/profile/reviews")
    async def therapist_reviews(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT id, first_name, last_name, company_email, profile_image, 
                            rating, review_count
                       FROM Therapists 
                       WHERE id = %s""", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()

                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")

 
                cursor.execute(
                    """SELECT r.review_id, r.rating, r.comment, r.created_at, 
                             p.patient_id, p.first_name, p.last_name
                       FROM Reviews r
                       JOIN Patients p ON r.patient_id = p.patient_id
                       WHERE r.therapist_id = %s
                       ORDER BY r.created_at DESC""",
                    (session_data["user_id"],)
                )
                reviews = cursor.fetchall()

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

 
                for review in reviews:
                    if isinstance(review['created_at'], datetime.datetime):
                        review['formatted_date'] = review['created_at'].strftime('%B %d, %Y')

 
                rating_distribution = {
                    5: 0,
                    4: 0,
                    3: 0,
                    2: 0,
                    1: 0
                }

                for review in reviews:
                    rating = int(review['rating'])
                    if rating < 1:
                        rating = 1
                    elif rating > 5:
                        rating = 5
                    rating_distribution[rating] += 1

 
                total_reviews = len(reviews)
                rating_percentages = {}
                for rating, count in rating_distribution.items():
                    if total_reviews > 0:
                        rating_percentages[rating] = (count / total_reviews) * 100
                    else:
                        rating_percentages[rating] = 0

                return templates.TemplateResponse(
                    "dist/dashboard/Therapist_reviews.html",
                    {
                        "request": request,
                        "therapist": therapist,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"],
                        "unread_messages_count": unread_messages_count,
                        "reviews": reviews,
                        "rating_distribution": rating_distribution,
                        "rating_percentages": rating_percentages,
                        "total_reviews": total_reviews
                    }
                )

            except Exception as e:
                print(f"Database error in therapist reviews: {e}")
                return RedirectResponse(url="/profile")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in therapist reviews: {e}")
            return RedirectResponse(url="/Therapist_Login")

    @app.post("/api/reviews/{review_id}/reply")
    async def reply_to_review(
        request: Request,
        review_id: int,
        reply: str = Form(...)
    ):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(status_code=401, content={"success": False, "message": "Not authenticated"})

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(status_code=401, content={"success": False, "message": "Not authenticated"})

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT review_id 
                       FROM Reviews 
                       WHERE review_id = %s AND therapist_id = %s""",
                    (review_id, session_data["user_id"])
                )
                review = cursor.fetchone()

                if not review:
                    return JSONResponse(status_code=404, content={"success": False, "message": "Review not found"})

 
                cursor.execute(
                    """UPDATE Reviews 
                       SET therapist_reply = %s, 
                           therapist_reply_date = CURRENT_TIMESTAMP
                       WHERE review_id = %s""",
                    (reply, review_id)
                )
                db.commit()

                return JSONResponse(content={"success": True})

            except Exception as e:
                print(f"Database error in reply to review: {e}")
                return JSONResponse(status_code=500, content={"success": False, "message": "Error replying to review"})
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in reply to review: {e}")
            return JSONResponse(status_code=500, content={"success": False, "message": "Server error"})

    @app.get("/dashboard")
    async def dashboard(user = Depends(get_current_user)):
        return {"message": f"Welcome, {user['username']}!", "user_id": user["user_id"]}

    @app.post("/registerUser")
    async def registerUser(result: Register): 
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
                )

                response.set_cookie(
                    key="session_id", 
                    value=session_id, 
                    httponly=True,
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
            
    @app.get("/getUserInfo") 
    async def get_user_info(request: Request):
        session_id = request.cookies.get("session_id")

        if not session_id:
            raise HTTPException(status_code=401, detail="Session not found") 

        session_data = await get_session_data(session_id)

        if not session_data:
            raise HTTPException(status_code=401, detail="Invalid session")

        user_id = session_data.user_id  

        db = get_Mysql_db()
        cursor = db.cursor()

        try:
            cursor.execute("SELECT username, email, created_at FROM users WHERE user_id = %s", (user_id,))
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="User not found")

            username, email, created_at = row
            return {
                "username": username,
                "email": email,
                "joined": str(created_at)
            }

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
                session_data = {
                    "user_id": str(therapist["id"]),
                    "email": therapist["company_email"]
                }

                session_id = await create_redis_session(
                    data=session_data,
                )

                print(f"Session created: {session_id}")
                print(f"User ID: {therapist['id']}")

                response = RedirectResponse(url="/front-page", status_code=303)

                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    httponly=True,
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
            
    @app.get("/reports/patients")
    async def patient_reports(request: Request):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT id, first_name, last_name, profile_image
                    FROM Therapists 
                    WHERE id = %s""", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()

                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")

 
                cursor.execute(
                    """SELECT patient_id, first_name, last_name, diagnosis, status
                    FROM Patients 
                    WHERE therapist_id = %s
                    ORDER BY last_name, first_name""",
                    (session_data["user_id"],)
                )
                patients = cursor.fetchall()

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

                return templates.TemplateResponse(
                    "dist/reports/patient_reports.html",
                    {
                        "request": request,
                        "therapist": therapist,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"],
                        "unread_messages_count": unread_messages_count,
                        "patients": patients
                    }
                )

            except Exception as e:
                print(f"Database error in patient reports: {e}")
                return RedirectResponse(url="/front-page")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in patient reports: {e}")
            return RedirectResponse(url="/Therapist_Login")


    @app.get("/reports/patients/{patient_id}")
    async def patient_detailed_report(request: Request, patient_id: int):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return RedirectResponse(url="/Therapist_Login")

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return RedirectResponse(url="/Therapist_Login")

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT id, first_name, last_name, profile_image
                    FROM Therapists 
                    WHERE id = %s""", 
                    (session_data["user_id"],)
                )
                therapist = cursor.fetchone()

                if not therapist:
                    return RedirectResponse(url="/Therapist_Login")

 
                cursor.execute(
                    """SELECT * FROM Patients 
                    WHERE patient_id = %s AND therapist_id = %s""",
                    (patient_id, session_data["user_id"])
                )
                patient = cursor.fetchone()

                if not patient:
                    return RedirectResponse(url="/reports/patients")

 
                cursor.execute(
                    """SELECT pep.*, tpe.sets, tpe.repetitions,
                            e.name as exercise_name, e.video_url, e.difficulty
                    FROM PatientExerciseProgress pep
                    JOIN TreatmentPlanExercises tpe ON pep.plan_exercise_id = tpe.plan_exercise_id
                    JOIN Exercises e ON tpe.exercise_id = e.exercise_id
                    JOIN TreatmentPlans tp ON tpe.plan_id = tp.plan_id
                    WHERE tp.patient_id = %s
                    ORDER BY pep.completion_date DESC, pep.modified_at DESC""",
                    (patient_id,)
                )
                exercise_history = cursor.fetchall()

 
                cursor.execute(
                    """SELECT * FROM TreatmentPlans
                    WHERE patient_id = %s
                    ORDER BY created_at DESC""",
                    (patient_id,)
                )
                treatment_plans = cursor.fetchall()

 
                cursor.execute(
                    """SELECT * FROM PatientMetrics
                    WHERE patient_id = %s
                    ORDER BY measurement_date DESC""",
                    (patient_id,)
                )
                patient_metrics = cursor.fetchall()

 
                cursor.execute(
                    """SELECT * FROM feedback
                    WHERE patient_id = %s
                    ORDER BY created_at DESC""",
                    (patient_id,)
                )
                patient_feedback = cursor.fetchall()

 
                cursor.execute(
                    "SELECT COUNT(*) as count FROM Messages WHERE recipient_id = %s AND recipient_type = 'therapist' AND is_read = FALSE",
                    (session_data["user_id"],)
                )
                unread_count_result = cursor.fetchone()
                unread_messages_count = unread_count_result['count'] if unread_count_result else 0

                return templates.TemplateResponse(
                    "dist/reports/patient_detailed_report.html",
                    {
                        "request": request,
                        "therapist": therapist,
                        "first_name": therapist["first_name"],
                        "last_name": therapist["last_name"],
                        "unread_messages_count": unread_messages_count,
                        "patient": patient,
                        "exercise_history": exercise_history,
                        "treatment_plans": treatment_plans,
                        "patient_metrics": patient_metrics,
                        "patient_feedback": patient_feedback
                    }
                )

            except Exception as e:
                print(f"Database error in patient detailed report: {e}")
                return RedirectResponse(url="/reports/patients")
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in patient detailed report: {e}")
            return RedirectResponse(url="/Therapist_Login")


    @app.post("/api/exercises/rate")
    async def rate_exercise(
        request: Request,
        exercise_progress_id: int = Form(...),
        rating: int = Form(...),
        feedback: str = Form(None)
    ):
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(status_code=401, content={"success": False, "message": "Not authenticated"})

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(status_code=401, content={"success": False, "message": "Not authenticated"})

 
            if rating < 1 or rating > 5:
                return JSONResponse(status_code=400, content={"success": False, "message": "Rating must be between 1 and 5"})

            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT pep.progress_id 
                    FROM PatientExerciseProgress pep
                    JOIN TreatmentPlanExercises tpe ON pep.plan_exercise_id = tpe.plan_exercise_id
                    JOIN TreatmentPlans tp ON tpe.plan_id = tp.plan_id
                    JOIN Patients p ON tp.patient_id = p.patient_id
                    WHERE pep.progress_id = %s AND p.therapist_id = %s""",
                    (exercise_progress_id, session_data["user_id"])
                )
                progress = cursor.fetchone()

                if not progress:
                    return JSONResponse(status_code=404, content={"success": False, "message": "Exercise progress not found"})

 
                cursor.execute(
                    """UPDATE PatientExerciseProgress 
                    SET therapist_rating = %s, therapist_feedback = %s
                    WHERE progress_id = %s""",
                    (rating, feedback, exercise_progress_id)
                )
                db.commit()

                return JSONResponse(content={"success": True})

            except Exception as e:
                print(f"Database error in rate exercise: {e}")
                return JSONResponse(status_code=500, content={"success": False, "message": "Error updating rating"})
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in rate exercise: {e}")
            return JSONResponse(status_code=500, content={"success": False, "message": "Server error"})

            
    @app.get("/patients")
    async def get_patients_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM Patients WHERE therapist_id = %s ORDER BY last_name", 
                (user["user_id"],)
            )
            patients = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/dashboard/patient_directory.html", 
                {
                    "request": request,
                    "patients": patients,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.get("/patients/add")
    async def add_patient_page(request: Request, user=Depends(get_current_user)):
        therapist_data = await get_therapist_data(user["user_id"])

        return templates.TemplateResponse(
            "dist/dashboard/add_patient.html", 
            {
                "request": request,
                "first_name": therapist_data["first_name"],
                "last_name": therapist_data["last_name"]
            }
        )

    @app.post("/patients/add")
    async def add_patient(
        request: Request,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: str = Form(None),
        phone: str = Form(None),
        date_of_birth: str = Form(None),
        address: str = Form(None),
        diagnosis: str = Form(None),
        notes: str = Form(None),
        user=Depends(get_current_user)
    ):
        db = get_Mysql_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                """INSERT INTO Patients 
                (therapist_id, first_name, last_name, email, phone, date_of_birth, 
                address, diagnosis, notes) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (user["user_id"], first_name, last_name, email, phone, 
                date_of_birth, address, diagnosis, notes)
            )
            db.commit()
            return RedirectResponse(url="/patients", status_code=303)
        except Exception as e:
            print(f"Error adding patient: {e}")
            therapist_data = await get_therapist_data(user["user_id"])
            return templates.TemplateResponse(
                "dist/dashboard/add_patient.html", 
                {
                    "request": request,
                    "error": f"Error adding patient: {str(e)}",
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"],
                    "today": datetime.datetime.now()
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.get("/patients/{patient_id}")
    async def patient_detail(request: Request, patient_id: int, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT * FROM Patients WHERE patient_id = %s AND therapist_id = %s", 
                (patient_id, user["user_id"])
            )
            patient = cursor.fetchone()

            if not patient:
                return RedirectResponse(url="/patients")

            cursor.execute(
                "SELECT * FROM TreatmentPlans WHERE patient_id = %s ORDER BY created_at DESC", 
                (patient_id,)
            )
            treatment_plans = cursor.fetchall()

            cursor.execute(
                """SELECT * FROM Appointments 
                WHERE patient_id = %s 
                ORDER BY appointment_date DESC, appointment_time DESC 
                LIMIT 5""", 
                (patient_id,)
            )
            appointments = cursor.fetchall()

            cursor.execute(
                """SELECT * FROM PatientMetrics 
                WHERE patient_id = %s 
                ORDER BY measurement_date DESC 
                LIMIT 10""", 
                (patient_id,)
            )
            metrics = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/dashboard/patient_details.html", 
                {
                    "request": request,
                    "patient": patient,
                    "treatment_plans": treatment_plans,
                    "appointments": appointments,
                    "metrics": metrics,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.get("/appointments")
    async def appointments_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT a.*, p.first_name as patient_first_name, p.last_name as patient_last_name 
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.patient_id
                WHERE a.therapist_id = %s AND a.appointment_date >= CURDATE()
                ORDER BY a.appointment_date, a.appointment_time""", 
                (user["user_id"],)
            )
            upcoming_appointments = cursor.fetchall()

            cursor.execute(
                """SELECT a.*, p.first_name as patient_first_name, p.last_name as patient_last_name 
                FROM Appointments a
                JOIN Patients p ON a.patient_id = p.patient_id
                WHERE a.therapist_id = %s AND a.appointment_date < CURDATE()
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
                LIMIT 10""", 
                (user["user_id"],)
            )
            past_appointments = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/appointments/appointment_list.html", 
                {
                    "request": request,
                    "upcoming_appointments": upcoming_appointments,
                    "past_appointments": past_appointments,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.get("/appointments/new")
    async def new_appointment_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT patient_id, first_name, last_name FROM Patients WHERE therapist_id = %s", 
                (user["user_id"],)
            )
            patients = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/appointments/new_appointment.html", 
                {
                    "request": request,
                    "patients": patients,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.post("/appointments/new")
    async def create_appointment(
        request: Request,
        patient_id: int = Form(...),
        appointment_date: str = Form(...),
        appointment_time: str = Form(...),
        duration: int = Form(60),
        notes: str = Form(None),
        user=Depends(get_current_user)
    ):
        db = get_Mysql_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                """INSERT INTO Appointments 
                (patient_id, therapist_id, appointment_date, appointment_time, duration, notes) 
                VALUES (%s, %s, %s, %s, %s, %s)""",
                (patient_id, user["user_id"], appointment_date, appointment_time, duration, notes)
            )
            db.commit()
            return RedirectResponse(url="/appointments", status_code=303)
        except Exception as e:
            print(f"Error creating appointment: {e}")
            return RedirectResponse(url="/appointments/new", status_code=303)
        finally:
            cursor.close()
            db.close()

    @app.get("/exercises")
    async def exercises_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT e.*, c.name as category_name 
                FROM Exercises e
                LEFT JOIN ExerciseCategories c ON e.category_id = c.category_id
                WHERE e.therapist_id = %s
                ORDER BY e.name""", 
                (user["user_id"],)
            )
            exercises = cursor.fetchall()

            cursor.execute("SELECT * FROM ExerciseCategories")
            categories = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/exercises/exercise_list.html", 
                {
                    "request": request,
                    "exercises": exercises,
                    "categories": categories,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.get("/exercises/add")
    async def add_exercise_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM ExerciseCategories")
            categories = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/exercises/add_exercise.html", 
                {
                    "request": request,
                    "categories": categories,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.post("/exercises/add")
    async def add_exercise(
        request: Request,
        name: str = Form(...),
        category_id: int = Form(...),
        description: str = Form(None),
        video_url: str = Form(None),
        duration: int = Form(None),
        difficulty: str = Form(None),
        instructions: str = Form(None),
        user=Depends(get_current_user)
    ):
        db = get_Mysql_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                """INSERT INTO Exercises 
                (therapist_id, category_id, name, description, video_url, duration, difficulty, instructions) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (user["user_id"], category_id, name, description, video_url, duration, difficulty, instructions)
            )
            db.commit()
            return RedirectResponse(url="/exercises", status_code=303)
        except Exception as e:
            print(f"Error adding exercise: {e}")
            return RedirectResponse(url="/exercises/add", status_code=303)
        finally:
            cursor.close()
            db.close()

    @app.get("/treatment-plans")
    async def treatment_plans_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                """SELECT tp.*, p.first_name, p.last_name 
                FROM TreatmentPlans tp
                JOIN Patients p ON tp.patient_id = p.patient_id
                WHERE tp.therapist_id = %s
                ORDER BY tp.created_at DESC""", 
                (user["user_id"],)
            )
            treatment_plans = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/treatment_plans/plan_list.html", 
                {
                    "request": request,
                    "treatment_plans": treatment_plans,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    @app.get("/treatment-plans/new")
    async def new_treatment_plan_page(request: Request, user=Depends(get_current_user)):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT patient_id, first_name, last_name FROM Patients WHERE therapist_id = %s", 
                (user["user_id"],)
            )
            patients = cursor.fetchall()

            cursor.execute(
                "SELECT * FROM Exercises WHERE therapist_id = %s", 
                (user["user_id"],)
            )
            exercises = cursor.fetchall()

            therapist_data = await get_therapist_data(user["user_id"])

            return templates.TemplateResponse(
                "dist/treatment_plans/new_plan.html", 
                {
                    "request": request,
                    "patients": patients,
                    "exercises": exercises,
                    "first_name": therapist_data["first_name"],
                    "last_name": therapist_data["last_name"]
                }
            )
        finally:
            cursor.close()
            db.close()

    async def get_therapist_data(therapist_id):
        db = get_Mysql_db()
        cursor = db.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT first_name, last_name FROM Therapists WHERE id = %s", 
                (therapist_id,)
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            db.close()
            
 
    @app.get("/therapists")
    async def get_therapists():
        """API endpoint to get a list of all therapists for the mobile app"""
        try:
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    """SELECT id, first_name, last_name, profile_image, 
                            specialties, address, rating, review_count, 
                            is_accepting_new_patients
                    FROM Therapists 
                    WHERE is_accepting_new_patients = TRUE
                    ORDER BY rating DESC, review_count DESC"""
                )
                therapists = cursor.fetchall()

                base_url = app.state.base_url
                static_dir = getattr(app.state, 'static_directory', "/PERCEPTRONX/Frontend_Web/static")
                
                print(f"Using base URL: {base_url}")
                
                formatted_therapists = []
                for therapist in therapists:
                    specialties = safely_parse_json_field(therapist['specialties'], [])
                    
                    profile_image = therapist['profile_image']
                    matched_image = find_best_matching_image(
                        therapist["id"], 
                        profile_image, 
                        static_dir
                    )
                    
                    photoUrl = f"/static/assets/images/user/{matched_image}"
                    
                    print(f"Therapist ID: {therapist['id']}, Original Image: {profile_image}, Matched: {matched_image}, URL: {photoUrl}")

                    formatted_therapists.append({
                        "id": therapist["id"],
                        "name": f"{therapist['first_name']} {therapist['last_name']}",
                        "photoUrl": photoUrl,
                        "specialties": specialties,
                        "location": therapist["address"] or "Location not provided",
                        "rating": float(therapist["rating"] or 0),
                        "reviewCount": therapist["review_count"] or 0,
                        "distance": 0.0, 
                        "nextAvailable": "Today" 
                    })

                return formatted_therapists

            except Exception as e:
                print(f"Database error in get therapists API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get therapists API: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Server error: {str(e)}"}
            )
            
    @app.get("/therapists/{id}")
    async def get_therapist_details(id: int):
        """API endpoint to get detailed information about a specific therapist"""
        try:
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
                cursor.execute(
                    """SELECT id, first_name, last_name, profile_image, 
                            bio, experience_years, specialties, education, languages, 
                            address, rating, review_count, 
                            is_accepting_new_patients, average_session_length
                    FROM Therapists 
                    WHERE id = %s""", 
                    (id,)
                )
                therapist = cursor.fetchone()

                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Therapist not found"}
                    )
                
                for field in ['specialties', 'education', 'languages']:
                    therapist[field] = safely_parse_json_field(therapist[field], [])
                        
                static_dir = getattr(app.state, 'static_directory', "/PERCEPTRONX/Frontend_Web/static")
                
                profile_image = therapist['profile_image']
                matched_image = find_best_matching_image(id, profile_image, static_dir)
                
                photoUrl = f"/static/assets/images/user/{matched_image}"
                
                print(f"Therapist detail ID: {id}, Original Image: {profile_image}, Matched: {matched_image}, URL: {photoUrl}")

                formatted_therapist = {
                    "id": therapist["id"],
                    "name": f"{therapist['first_name']} {therapist['last_name']}",
                    "photoUrl": photoUrl,
                    "specialties": therapist["specialties"],
                    "bio": therapist["bio"] or "",
                    "experienceYears": therapist["experience_years"] or 0,
                    "education": therapist["education"],
                    "languages": therapist["languages"],
                    "address": therapist["address"] or "",
                    "rating": float(therapist["rating"] or 0),
                    "reviewCount": therapist["review_count"] or 0,
                    "isAcceptingNewPatients": bool(therapist["is_accepting_new_patients"]),
                    "averageSessionLength": therapist["average_session_length"] or 60
                }

                return formatted_therapist
                
            except Exception as e:
                print(f"Database error in get therapist details API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get therapist details API: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Server error: {str(e)}"}
            )

    @app.get("/therapists/{id}/availability")
    async def get_therapist_availability(id: int, date: str = None):
        """API endpoint to get available time slots for a therapist"""
        try:
 
            if not date:
                date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    "SELECT id, average_session_length FROM Therapists WHERE id = %s",
                    (id,)
                )
                therapist = cursor.fetchone()
                
                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Therapist not found"}
                    )
                
 
                cursor.execute(
                    """SELECT appointment_time, duration 
                    FROM Appointments 
                    WHERE therapist_id = %s AND appointment_date = %s 
                    AND status != 'Cancelled'""",
                    (id, date)
                )
                booked_slots = cursor.fetchall()
                
 
                start_hour = 9
                end_hour = 17
                
 
                slot_duration = therapist['average_session_length'] or 60
                
 
                available_slots = []
                current_time = datetime.time(start_hour, 0)
                end_time = datetime.time(end_hour, 0)
                
                slot_id = 1
                while current_time < end_time:
                    slot_end = (datetime.datetime.combine(datetime.date.today(), current_time) + 
                            datetime.timedelta(minutes=slot_duration)).time()
                    
 
                    is_available = True
                    for booked in booked_slots:
                        booked_start = booked['appointment_time']
                        booked_end_dt = (datetime.datetime.combine(datetime.date.today(), booked_start) + 
                                    datetime.timedelta(minutes=booked['duration']))
                        booked_end = booked_end_dt.time()
                        
 
                        if (current_time < booked_end and slot_end > booked_start):
                            is_available = False
                            break
                    
 
                    formatted_time = current_time.strftime("%I:%M %p")
                    
                    available_slots.append({
                        "id": slot_id,
                        "date": date,
                        "time": formatted_time,
                        "isAvailable": is_available
                    })
                    
                    slot_id += 1
                    
 
                    current_time_dt = datetime.datetime.combine(datetime.date.today(), current_time)
                    current_time_dt += datetime.timedelta(minutes=30)
                    current_time = current_time_dt.time()
                
                return available_slots

            except Exception as e:
                print(f"Database error in get therapist availability API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get therapist availability API: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Server error: {str(e)}"}
            )
    
    @app.post("/appointments/request")
    async def request_appointment(request: Request, appointment_request: AppointmentRequest):
        """API endpoint to request an appointment with a therapist"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"status": "invalid", "detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"status": "invalid", "detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    "SELECT id FROM Therapists WHERE id = %s",
                    (appointment_request.therapist_id,)
                )
                therapist = cursor.fetchone()
                
                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"status": "invalid", "detail": "Therapist not found"}
                    )
                
 
                cursor.execute(
                    "SELECT patient_id FROM Patients WHERE user_id = %s",
                    (user_id,)
                )
                patient_record = cursor.fetchone()
                
                patient_id = None
                if patient_record:
                    patient_id = patient_record[0]
                else:
 
                    cursor.execute(
                        "SELECT username, email FROM users WHERE user_id = %s",
                        (user_id,)
                    )
                    user_info = cursor.fetchone()
                    
                    if not user_info:
                        return JSONResponse(
                            status_code=404,
                            content={"status": "invalid", "detail": "User not found"}
                        )
                    
 
                    cursor.execute(
                        """INSERT INTO Patients 
                        (therapist_id, user_id, first_name, last_name, email) 
                        VALUES (%s, %s, %s, %s, %s)""",
                        (appointment_request.therapist_id, user_id, user_info[0], "", user_info[1])
                    )
                    db.commit()
                    patient_id = cursor.lastrowid
                
 
                time_parts = appointment_request.time.split()
                time_str = time_parts[0] 
                am_pm = time_parts[1] if len(time_parts) > 1 else "AM" 
                
                time_obj = datetime.datetime.strptime(f"{time_str} {am_pm}", "%I:%M %p").time()
                
 
                duration = 60
                
 
                full_notes = f"Type: {appointment_request.type}\n"
                if appointment_request.notes:
                    full_notes += f"Notes: {appointment_request.notes}\n"
                if appointment_request.insuranceProvider:
                    full_notes += f"Insurance: {appointment_request.insuranceProvider}\n"
                if appointment_request.insuranceMemberId:
                    full_notes += f"Member ID: {appointment_request.insuranceMemberId}"
                
 
                cursor.execute(
                    """INSERT INTO Appointments 
                    (patient_id, therapist_id, appointment_date, appointment_time, duration, notes, status) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (patient_id, appointment_request.therapist_id, appointment_request.date, 
                    time_obj, duration, full_notes, "Scheduled")
                )
                db.commit()
                
 
                cursor.execute(
                    """INSERT INTO Messages
                    (sender_id, sender_type, recipient_id, recipient_type, subject, content)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (user_id, "user", appointment_request.therapist_id, "therapist", 
                    "New Appointment Request", 
                    f"A new appointment has been requested for {appointment_request.date} at {appointment_request.time}.")
                )
                db.commit()
                
                return {"status": "valid", "message": "Appointment requested successfully"}

            except Exception as e:
                db.rollback()
                print(f"Database error in request appointment API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error requesting appointment: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in request appointment API: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )

    @app.post("/messages/send")
    async def send_message(request: Request, message_request: MessageRequest):
        """API endpoint to send a message to a therapist"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"status": "invalid", "detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"status": "invalid", "detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    "SELECT id FROM Therapists WHERE id = %s",
                    (message_request.recipient_id,)
                )
                therapist = cursor.fetchone()
                
                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"status": "invalid", "detail": "Recipient not found"}
                    )
                
 
                cursor.execute(
                    """INSERT INTO Messages 
                    (sender_id, sender_type, recipient_id, recipient_type, subject, content) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (user_id, "user", message_request.recipient_id, "therapist", 
                    message_request.subject, message_request.content)
                )
                db.commit()
                
                return {"status": "valid", "message": "Message sent successfully"}

            except Exception as e:
                db.rollback()
                print(f"Database error in send message API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error sending message: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in send message API: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )

    @app.post("/therapists/{id}/add_patient")
    async def add_patient_to_therapist(request: Request, id: int, patient: dict):
        """API endpoint to add a user as a patient to a therapist"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"status": "invalid", "detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"status": "invalid", "detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    "SELECT id FROM Therapists WHERE id = %s",
                    (id,)
                )
                therapist = cursor.fetchone()
                
                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"status": "invalid", "detail": "Therapist not found"}
                    )
                
 
                cursor.execute(
                    "SELECT patient_id FROM Patients WHERE user_id = %s",
                    (user_id,)
                )
                existing_patient = cursor.fetchone()
                
                if existing_patient:
 
                    cursor.execute(
                        """UPDATE Patients 
                        SET therapist_id = %s,
                            first_name = %s,
                            last_name = %s,
                            phone = %s,
                            diagnosis = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = %s""",
                        (id, patient.get('first_name', ''), patient.get('last_name', ''), 
                        patient.get('phone', ''), patient.get('diagnosis', ''), user_id)
                    )
                else:
 
                    cursor.execute(
                        "SELECT email FROM users WHERE user_id = %s",
                        (user_id,)
                    )
                    user_email = cursor.fetchone()
                    email = user_email[0] if user_email else ''
                    
 
                    cursor.execute(
                        """INSERT INTO Patients 
                        (therapist_id, user_id, first_name, last_name, email, phone, diagnosis) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                        (id, user_id, patient.get('first_name', ''), patient.get('last_name', ''), 
                        email, patient.get('phone', ''), patient.get('diagnosis', ''))
                    )
                
                db.commit()
                
                return {"status": "valid", "message": "Patient added successfully"}

            except Exception as e:
                db.rollback()
                print(f"Database error in add patient API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error adding patient: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in add patient API: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )

    @app.get("/user/appointments")
    async def get_user_appointments(request: Request):
        """API endpoint to get all appointments for the current user"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    "SELECT patient_id FROM Patients WHERE user_id = %s",
                    (user_id,)
                )
                patient_record = cursor.fetchone()
                
                if not patient_record:
 
                    return []
                
                patient_id = patient_record['patient_id']
                
 
                cursor.execute(
                    """SELECT a.appointment_id, a.appointment_date, a.appointment_time, a.duration, a.status, a.notes,
                            t.id as therapist_id, t.first_name, t.last_name, t.profile_image
                    FROM Appointments a
                    JOIN Therapists t ON a.therapist_id = t.id
                    WHERE a.patient_id = %s
                    ORDER BY 
                        CASE WHEN a.status = 'Scheduled' THEN 0
                            WHEN a.status = 'Completed' THEN 1
                            ELSE 2 END,
                        a.appointment_date DESC, 
                        a.appointment_time DESC""",
                    (patient_id,)
                )
                appointments = cursor.fetchall()
                
 
                formatted_appointments = []
                for appointment in appointments:
 
                    time_obj = appointment['appointment_time']
                    formatted_time = time_obj.strftime("%I:%M %p") if time_obj else "N/A"
                    
 
                    date_obj = appointment['appointment_date']
                    formatted_date = date_obj.strftime("%Y-%m-%d") if date_obj else "N/A"
                    
                    formatted_appointments.append({
                        "id": appointment['appointment_id'],
                        "date": formatted_date,
                        "time": formatted_time,
                        "duration": appointment['duration'],
                        "status": appointment['status'],
                        "notes": appointment['notes'],
                        "therapist": {
                            "id": appointment['therapist_id'],
                            "name": f"{appointment['first_name']} {appointment['last_name']}",
                            "photoUrl": f"/static/assets/images/user/{appointment['profile_image']}" if appointment['profile_image'] else "/static/assets/images/user/avatar-1.jpg"
                        }
                    })
                
                return formatted_appointments

            except Exception as e:
                print(f"Database error in get user appointments API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get user appointments API: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Server error: {str(e)}"}
            )

    @app.get("/user/therapist")
    async def get_current_therapist(request: Request):
        """API endpoint to get the current therapist for the logged-in user"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT p.therapist_id, t.first_name, t.last_name, t.profile_image, 
                            t.bio, t.experience_years, t.specialties, t.education, t.languages, 
                            t.address, t.rating, t.review_count, 
                            t.is_accepting_new_patients, t.average_session_length
                    FROM Patients p
                    JOIN Therapists t ON p.therapist_id = t.id
                    WHERE p.user_id = %s""",
                    (user_id,)
                )
                result = cursor.fetchone()
                
                if not result:
 
                    return None
                
 
                for field in ['specialties', 'education', 'languages']:
                    if result[field] and isinstance(result[field], str):
                        try:
                            result[field] = json.loads(result[field])
                        except:
                            result[field] = []
                    elif result[field] is None:
                        result[field] = []
                
 
                therapist = {
                    "id": result["therapist_id"],
                    "name": f"{result['first_name']} {result['last_name']}",
                    "photoUrl": f"/static/assets/images/user/{result['profile_image']}" if result['profile_image'] else "/static/assets/images/user/avatar-1.jpg",
                    "specialties": result["specialties"],
                    "bio": result["bio"] or "",
                    "experienceYears": result["experience_years"] or 0,
                    "education": result["education"],
                    "languages": result["languages"],
                    "address": result["address"] or "",
                    "rating": float(result["rating"] or 0),
                    "reviewCount": result["review_count"] or 0,
                    "isAcceptingNewPatients": bool(result["is_accepting_new_patients"]),
                    "averageSessionLength": result["average_session_length"] or 60
                }
                
                return therapist

            except Exception as e:
                print(f"Database error in get current therapist API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get current therapist API: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Server error: {str(e)}"}
            )

    @app.post("/therapists/{id}/rate")
    async def rate_therapist(request: Request, id: int, rating: dict):
        """API endpoint to rate a therapist"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"status": "invalid", "detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"status": "invalid", "detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    "SELECT id FROM Therapists WHERE id = %s",
                    (id,)
                )
                therapist = cursor.fetchone()
                
                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"status": "invalid", "detail": "Therapist not found"}
                    )
                
 
                cursor.execute(
                    "SELECT patient_id FROM Patients WHERE user_id = %s",
                    (user_id,)
                )
                patient_record = cursor.fetchone()
                
                if not patient_record:
                    return JSONResponse(
                        status_code=400,
                        content={"status": "invalid", "detail": "You must be a patient to leave a review"}
                    )
                
                patient_id = patient_record[0]
                
 
                cursor.execute(
                    "SELECT review_id FROM Reviews WHERE therapist_id = %s AND patient_id = %s",
                    (id, patient_id)
                )
                existing_review = cursor.fetchone()
                
                rating_value = float(rating.get('rating', 5))
                comment = rating.get('comment', '')
                
                if existing_review:
 
                    cursor.execute(
                        """UPDATE Reviews 
                        SET rating = %s, comment = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE review_id = %s""",
                        (rating_value, comment, existing_review[0])
                    )
                else:
 
                    cursor.execute(
                        """INSERT INTO Reviews 
                        (therapist_id, patient_id, rating, comment) 
                        VALUES (%s, %s, %s, %s)""",
                        (id, patient_id, rating_value, comment)
                    )
                
                db.commit()
                
 
                cursor.execute(
                    """UPDATE Therapists t
                    SET rating = (
                        SELECT AVG(r.rating) FROM Reviews r WHERE r.therapist_id = %s
                    ),
                    review_count = (
                        SELECT COUNT(*) FROM Reviews r WHERE r.therapist_id = %s
                    )
                    WHERE t.id = %s""",
                    (id, id, id)
                )
                db.commit()
                
                return {"status": "valid", "message": "Review submitted successfully"}

            except Exception as e:
                db.rollback()
                print(f"Database error in rate therapist API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error submitting review: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in rate therapist API: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )

    @app.post("/reset-password")
    async def reset_password(email: dict):
        """API endpoint to initiate password reset"""
        try:
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
                email_address = email.get("email")
                if not email_address:
                    return JSONResponse(
                        status_code=400,
                        content={"status": "invalid", "detail": "Email is required"}
                    )
                
 
                cursor.execute(
                    "SELECT user_id FROM users WHERE email = %s",
                    (email_address,)
                )
                user = cursor.fetchone()
                
                if not user:
 
                    cursor.execute(
                        "SELECT id FROM Therapists WHERE company_email = %s",
                        (email_address,)
                    )
                    therapist = cursor.fetchone()
                    
                    if not therapist:
 
                        return {"status": "valid", "message": "If this email is registered, you will receive reset instructions"}
                
 
                expiry = datetime.datetime.now() + datetime.timedelta(hours=24)
                
 
                reset_token = secrets.token_hex(32)

 
                await r.set(f"reset:{reset_token}", email_address, ex=86400)
 
 
                print(f"Password reset requested for {email_address}. Token: {reset_token}")
                
                return {"status": "valid", "message": "If this email is registered, you will receive reset instructions"}

            except Exception as e:
                print(f"Database error in reset password API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error processing request: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in reset password API: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )

    @app.get("/therapists/{id}/reviews")
    async def get_therapist_reviews(id: int, limit: int = 10, offset: int = 0):
        """API endpoint to get reviews for a specific therapist"""
        try:
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    "SELECT id FROM Therapists WHERE id = %s",
                    (id,)
                )
                therapist = cursor.fetchone()
                
                if not therapist:
                    return JSONResponse(
                        status_code=404,
                        content={"error": "Therapist not found"}
                    )
                
 
                cursor.execute(
                    """SELECT r.review_id, r.rating, r.comment, r.created_at,
                            p.first_name, p.last_name
                    FROM Reviews r
                    JOIN Patients p ON r.patient_id = p.patient_id
                    WHERE r.therapist_id = %s
                    ORDER BY r.created_at DESC
                    LIMIT %s OFFSET %s""",
                    (id, limit, offset)
                )
                reviews = cursor.fetchall()
                
 
                formatted_reviews = []
                for review in reviews:
 
                    created_date = review['created_at']
                    formatted_date = created_date.strftime("%Y-%m-%d") if created_date else "N/A"
                    
 
                    patient_name = f"{review['first_name'] or ''} {review['last_name'] or ''}".strip()
                    if not patient_name:
                        patient_name = "Anonymous Patient"
                    
                    formatted_reviews.append({
                        "id": review['review_id'],
                        "patientName": patient_name,
                        "rating": float(review['rating']),
                        "comment": review['comment'] or "",
                        "date": formatted_date
                    })
                
                return formatted_reviews

            except Exception as e:
                print(f"Database error in get therapist reviews API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get therapist reviews API: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": f"Server error: {str(e)}"}
            )

    @app.get("/user/messages")
    async def get_user_messages(request: Request):
        """API endpoint to get messages for the current user"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    """SELECT m.message_id, m.subject, m.content, m.created_at, m.is_read,
                            CASE 
                                WHEN m.sender_type = 'therapist' THEN 
                                    CONCAT(t.first_name, ' ', t.last_name)
                                ELSE 'System'
                            END as sender_name,
                            CASE 
                                WHEN m.sender_type = 'therapist' THEN 
                                    t.profile_image
                                ELSE 'system-avatar.jpg'
                            END as sender_image,
                            m.sender_id, m.sender_type
                    FROM Messages m
                    LEFT JOIN Therapists t ON m.sender_id = t.id AND m.sender_type = 'therapist'
                    WHERE (m.recipient_id = %s AND m.recipient_type = 'user')
                    OR (m.sender_id = %s AND m.sender_type = 'user')
                    ORDER BY m.created_at DESC""",
                    (user_id, user_id)
                )
                messages = cursor.fetchall()
                
 
                formatted_messages = []
                for message in messages:
 
                    created_date = message['created_at']
                    formatted_date = created_date.strftime("%Y-%m-%d %H:%M") if created_date else "N/A"
                    
                    formatted_messages.append({
                        "id": message['message_id'],
                        "subject": message['subject'] or "",
                        "content": message['content'] or "",
                        "date": formatted_date,
                        "isRead": bool(message['is_read']),
                        "sender": {
                            "id": message['sender_id'],
                            "name": message['sender_name'],
                            "photoUrl": f"/static/assets/images/user/{message['sender_image']}" if message['sender_image'] else "/static/assets/images/user/avatar-1.jpg",
                            "type": message['sender_type']
                        },
                        "direction": "incoming" if message['recipient_id'] == int(user_id) and message['recipient_type'] == 'user' else "outgoing"
                    })
                
                return formatted_messages

            except Exception as e:
                print(f"Database error in get user messages API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get user messages API: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Server error: {str(e)}"}
            )

    
    @app.post("/messages/{message_id}/read")
    async def mark_message_read(request: Request, message_id: int):
        """API endpoint to mark a message as read"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"status": "invalid", "detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"status": "invalid", "detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
 
                cursor.execute(
                    """SELECT message_id 
                    FROM Messages 
                    WHERE message_id = %s AND recipient_id = %s AND recipient_type = 'user'""",
                    (message_id, user_id)
                )
                message = cursor.fetchone()
                
                if not message:
                    return JSONResponse(
                        status_code=404,
                        content={"status": "invalid", "detail": "Message not found"}
                    )
                
 
                cursor.execute(
                    "UPDATE Messages SET is_read = TRUE WHERE message_id = %s",
                    (message_id,)
                )
                db.commit()
                
                return {"status": "valid", "message": "Message marked as read"}

            except Exception as e:
                db.rollback()
                print(f"Database error in mark message read API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error updating message: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in mark message read API: {e}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )

    @app.get("/user/profile")
    async def get_user_profile(request: Request):
        """API endpoint to get the user's profile information"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor(dictionary=True)

            try:
 
                cursor.execute(
                    "SELECT username, email, profile_pic, created_at FROM users WHERE user_id = %s",
                    (user_id,)
                )
                user = cursor.fetchone()
                
                if not user:
                    return JSONResponse(
                        status_code=404,
                        content={"detail": "User not found"}
                    )
                
 
                cursor.execute(
                    """SELECT p.*, t.first_name as therapist_first_name, t.last_name as therapist_last_name
                    FROM Patients p
                    LEFT JOIN Therapists t ON p.therapist_id = t.id
                    WHERE p.user_id = %s""",
                    (user_id,)
                )
                patient = cursor.fetchone()
                
 
                profile = {
                    "username": user['username'],
                    "email": user['email'],
                    "profilePicture": f"/static/assets/images/user/{user['profile_pic']}" if user['profile_pic'] else None,
                    "joinedDate": user['created_at'].strftime("%Y-%m-%d") if user['created_at'] else None,
                    "hasPatientProfile": patient is not None
                }
                
                if patient:
                    profile.update({
                        "patientProfile": {
                            "id": patient['patient_id'],
                            "firstName": patient['first_name'],
                            "lastName": patient['last_name'],
                            "phoneNumber": patient['phone'],
                            "dateOfBirth": patient['date_of_birth'].strftime("%Y-%m-%d") if patient['date_of_birth'] else None,
                            "address": patient['address'],
                            "diagnosis": patient['diagnosis'],
                            "status": patient['status'],
                            "therapist": {
                                "id": patient['therapist_id'],
                                "name": f"{patient['therapist_first_name']} {patient['therapist_last_name']}".strip() if patient['therapist_first_name'] else None
                            }
                        }
                    })
                
                return profile

            except Exception as e:
                print(f"Database error in get user profile API: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Internal server error: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in get user profile API: {e}")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Server error: {str(e)}"}
            )

    @app.put("/user/profile")
    async def update_user_profile(request: Request, profile_data: dict):
        """API endpoint to update user profile information"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"status": "invalid", "detail": "Not authenticated"}
            )

        try:
            session_data = await get_redis_session(session_id)
            if not session_data:
                return JSONResponse(
                    status_code=401,
                    content={"status": "invalid", "detail": "Not authenticated"}
                )

            user_id = session_data["user_id"]
            
            db = get_Mysql_db()
            cursor = db.cursor()

            try:
                if 'username' in profile_data or 'email' in profile_data:
                    update_fields = []
                    params = []
                    
                    if 'username' in profile_data:
                        update_fields.append("username = %s")
                        params.append(ensure_str(profile_data['username']))
                    
                    if 'email' in profile_data:
                        update_fields.append("email = %s")
                        params.append(ensure_str(profile_data['email']))
                    
                    params.append(user_id)
                    
                    cursor.execute(
                        f"UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE user_id = %s",
                        params
                    )
                patient_data = profile_data.get('patientProfile', {})
                if patient_data:
                    cursor.execute(
                        "SELECT patient_id FROM Patients WHERE user_id = %s",
                        (user_id,)
                    )
                    patient = cursor.fetchone()
                    
                    if patient:
                        patient_id = patient[0]
                        
                        update_fields = []
                        params = []
                        
                        for field, db_field in [
                            ('firstName', 'first_name'),
                            ('lastName', 'last_name'),
                            ('phoneNumber', 'phone'),
                            ('dateOfBirth', 'date_of_birth'),
                            ('address', 'address'),
                            ('diagnosis', 'diagnosis')
                        ]:
                            if field in patient_data:
                                update_fields.append(f"{db_field} = %s")
                                params.append(ensure_str(patient_data[field]))
                        
                        if update_fields:
                            params.append(patient_id)
                            cursor.execute(
                                f"UPDATE Patients SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE patient_id = %s",
                                params
                            )
                    else:
                        pass
                
                db.commit()
                
                return {"status": "valid", "message": "Profile updated successfully"}

            except Exception as e:
                db.rollback()
                print(f"Database error in update user profile API: {e}")
                print(f"Traceback: {traceback.format_exc()}")
                return JSONResponse(
                    status_code=500,
                    content={"status": "invalid", "detail": f"Error updating profile: {str(e)}"}
                )
            finally:
                cursor.close()
                db.close()
        except Exception as e:
            print(f"Error in update user profile API: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return JSONResponse(
                status_code=500,
                content={"status": "invalid", "detail": f"Server error: {str(e)}"}
            )
    

    if __name__ == "__main__":
        base_url = getIP()
        uvicorn.run(app, host="0.0.0.0", port=8000)