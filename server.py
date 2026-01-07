from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
import shutil
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from google_oauth import router as google_router

app = FastAPI()

# Include Google OAuth authentication routes
app.include_router(google_router)

FILES_DIR = os.path.join(os.path.dirname(__file__), "files")

os.makedirs(FILES_DIR, exist_ok=True)


@app.get("/guidelines")
def get_guidelines():
    return {
        "description": "BMK Community Guidelines",
        "legal": "Follow all national laws, privacy regulations, and employment rules. Do not use the app for illegal activities.",
        "ethical": "Promote honesty, respect, non-discrimination, and fair treatment. Treat all users with dignity and fairness.",
        "community": "Reflect the values and expectations of users and local society. No hate speech, harassment, or abuse.",
        "moderation": {
            "user_reporting": "Users can report inappropriate behavior or posts directly from the app.",
            "admin_tools": "Admins can review reports, issue warnings, suspend, or ban users who violate guidelines.",
            "automated_filtering": "Offensive language, spam, or prohibited content may be blocked automatically.",
            "activity_monitoring": "User actions are tracked and repeated violations are flagged for review.",
            "documentation": "All reports, actions, and updates are documented for transparency and compliance."
        },
        "endpoints": [
            {"path": "/login", "methods": ["POST"], "desc": "Authenticate user."},
            {"path": "/login/google", "methods": ["GET"], "desc": "Start Google OAuth flow."},
            {"path": "/auth/google/callback", "methods": ["GET"], "desc": "Handle Google OAuth callback."},
            {"path": "/municipalities", "methods": ["GET", "POST"], "desc": "List/add municipalities (with internal coordinates)."},
            {"path": "/chat", "methods": ["GET", "POST", "DELETE"], "desc": "Retrieve/add/delete chat messages."},
            {"path": "/download_app", "methods": ["GET"], "desc": "Download the BMK app (APK)."},
            {"path": "/stats", "methods": ["GET"], "desc": "Get app statistics."},
            {"path": "/users", "methods": ["GET", "POST", "DELETE"], "desc": "Manage users."},
            {"path": "/tasks", "methods": ["GET", "POST"], "desc": "Manage tasks."},
            {"path": "/ban/{user_id}", "methods": ["POST"], "desc": "Ban a user."},
            {"path": "/upload", "methods": ["POST"], "desc": "Upload a file."},
            {"path": "/files/{filename}", "methods": ["GET"], "desc": "Download a file."},
            {"path": "/guidelines", "methods": ["GET"], "desc": "API and community guidelines."}
        ],
        "auth": "Use Google OAuth (/login/google) or register and login to get a JWT token. Pass the token as 'Authorization: Bearer <token>' for protected endpoints.",
        "notes": "Some endpoints may require admin privileges. See OpenAPI docs at /docs for full details."
    }

# APK download endpoint (supports GET and HEAD for browser installs)
@app.api_route("/download_app", methods=["GET", "HEAD"])
def download_app():
    # Redirect to GitHub Release for APK download
    github_release_url = "https://github.com/sushantkhatri01/BMK-Server/releases/download/v1.0.0/bmk.apk"
    return RedirectResponse(url=github_release_url, status_code=302)

# Enable CORS for your Flutter app (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "BMK server is running!"}

@app.get("/debug/files")
def debug_files():
    """Debug endpoint to check file system"""
    try:
        files_exist = os.path.exists(FILES_DIR)
        files_list = os.listdir(FILES_DIR) if files_exist else []
        apk_path = os.path.join(FILES_DIR, "bmk.apk")
        apk_exists = os.path.isfile(apk_path)
        apk_size = os.path.getsize(apk_path) if apk_exists else 0
        
        return {
            "files_dir": FILES_DIR,
            "files_dir_exists": files_exist,
            "files_in_dir": files_list,
            "apk_path": apk_path,
            "apk_exists": apk_exists,
            "apk_size_mb": round(apk_size / 1024 / 1024, 2) if apk_exists else 0,
            "current_dir": os.getcwd(),
            "dir_contents": os.listdir(os.getcwd())
        }
    except Exception as e:
        return {"error": str(e)}

# Secure config loading example

# Use environment variable for DB path, default to SQLite file
SQLITE_DB_PATH = os.environ.get("BMK_SQLITE_PATH", "bmk.db")
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Sample User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, index=True)
    password_hash = Column(String)
    banned = Column(Integer, default=0)  # 0 = not banned, 1 = banned


# Sample Municipality model
class Municipality(Base):
    __tablename__ = "municipalities"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    province = Column(String, index=True)
    district = Column(String, index=True)
    ward = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

# Task model
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, index=True)
    user_id = Column(Integer, index=True)

class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    name = Column(String, index=True)
    phone = Column(String)
    skills = Column(String)  # JSON string of skills
    location = Column(String)
    about = Column(String)
    isAvailable = Column(Integer, default=1)
    rating = Column(Float, default=0.0)

# ChatMessage model
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    content = Column(String)
    timestamp = Column(String)

# Optional Pro subscription table: keeps basic users, adds Pro tier
class ProSubscription(Base):
    __tablename__ = "pro_subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, unique=True)
    plan = Column(String, default="free")  # free | pro
    expires_at = Column(DateTime, nullable=True)  # UTC expiry for pro

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint to get all municipalities with full location details
@app.get("/municipalities")
def get_municipalities(db: Session = Depends(get_db)):
    municipalities = db.query(Municipality).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "province": m.province,
            "district": m.district,
            "ward": m.ward,
            "latitude": m.latitude,
            "longitude": m.longitude
        }
        for m in municipalities
    ]

# Endpoint to add a new municipality
from pydantic import BaseModel

# Pydantic model for creating a municipality
class MunicipalityCreate(BaseModel):
    name: str
    province: str
    district: str
    ward: str
    latitude: float
    longitude: float



# Pydantic model for creating a user
class UserCreate(BaseModel):
    name: str
    email: str | None = None
    role: str | None = None
    password: str | None = None
    phone: str | None = None
    location: str | None = None

# Pydantic model for login
class UserLogin(BaseModel):
    email: str
    password: str

# Pydantic model for creating a task
# Pydantic model for creating a task
class TaskCreate(BaseModel):
    title: str
    description: str
    status: str | None = None
    user_id: int | None = None

class SubscriptionUpdate(BaseModel):
    plan: str | None = None  # "pro" or "free"
    days: int | None = None  # number of days to extend pro

# Pydantic model for creating a chat message
class ChatMessageCreate(BaseModel):
    user_id: int
    content: str
    timestamp: str

@app.post("/municipalities")
def create_municipality(muni: MunicipalityCreate, db: Session = Depends(get_db)):
    new_muni = Municipality(
        name=muni.name,
        province=muni.province,
        district=muni.district,
        ward=muni.ward,
        latitude=muni.latitude,
        longitude=muni.longitude
    )
    db.add(new_muni)
    db.commit()
    db.refresh(new_muni)
    return {
        "id": new_muni.id,
        "name": new_muni.name,
        "province": new_muni.province,
        "district": new_muni.district,
        "ward": new_muni.ward,
        "latitude": new_muni.latitude,
        "longitude": new_muni.longitude
    }

# Endpoint to get all users
@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role
        }
        for u in users
    ]

# Endpoint to add a new user
# Endpoint to add a new user

# Password hashing and JWT setup
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = os.environ.get("BMK_SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Feature flag: enable Pro plan enforcement (default: off)
# Set BMK_ENABLE_PRO=1 to enforce Pro-specific limits.
ENABLE_PRO = os.environ.get("BMK_ENABLE_PRO", "0") == "1"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Register endpoint
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        return {"error": "Email already registered"}
    hashed_pw = get_password_hash(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        role=user.role,
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }

# Login endpoint
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        return {"error": "Invalid credentials"}
    access_token = create_access_token({"sub": db_user.email, "user_id": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint to add a new user (admin only, no password)
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # If email not provided, use name as fallback
    email = user.email or f"{user.name.lower().replace(' ', '.')}@bmk.local"
    
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return {"error": "Email already registered"}
    
    # Use provided password or a short default (must be <=72 bytes for bcrypt)
    password = user.password or "bmk123"
    role = user.role or "worker"
    
    hashed_pw = get_password_hash(password)
    new_user = User(
        name=user.name,
        email=email,
        role=role,
        password_hash=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
        "role": new_user.role
    }


# Endpoint to get all tasks
@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    result = []
    for t in tasks:
        # Get user info if available
        user = db.query(User).filter(User.id == t.user_id).first()
        result.append({
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "user_id": t.user_id,
            "posterId": str(t.user_id),
            "posterName": user.name if user else "Unknown User",
            "posterPhone": "",
            "category": "General",
            "location": "Unknown Location",
            "municipality": "",
            "type": "Task",
            "salary": "",
            "budget": "Negotiable",
            "duration": "Flexible",
            "requirements": [],
            "postedDate": "2025-01-01T00:00:00",
            "applyUrl": "",
            "matchScore": 0,
            "isUrgent": False
        })
    return result

# Endpoint to add a new task
@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    user_id = task.user_id or 1

    # Optional free-plan limit (only when ENABLE_PRO=1)
    if ENABLE_PRO:
        sub = db.query(ProSubscription).filter(ProSubscription.user_id == user_id).first()
        now_utc = datetime.now(timezone.utc)
        has_pro = bool(sub and sub.plan == "pro" and (sub.expires_at is None or sub.expires_at >= now_utc))

        if not has_pro:
            open_count = (
                db.query(Task)
                .filter(Task.user_id == user_id)
                .filter((Task.status == None) | (Task.status != "closed"))
                .count()
            )
            if open_count >= 3:
                raise HTTPException(status_code=403, detail="Free plan limit reached: upgrade to Pro to post more than 3 open tasks.")

    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status or "open",  # Default to "open" if not provided
        user_id=user_id  # Default to user 1 if not provided
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "status": new_task.status,
        "user_id": new_task.user_id
    }

# Endpoint to get task by ID
@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "user_id": task.user_id
    }

# Endpoint to update task status
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = task_update.title
    task.description = task_update.description
    task.status = task_update.status
    db.commit()
    db.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "user_id": task.user_id
    }

# Endpoint to delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted"}

# ================= SUBSCRIPTIONS =================

def _now_utc():
    return datetime.now(timezone.utc)

def _is_pro(sub: 'ProSubscription | None') -> bool:
    if not sub:
        return False
    if sub.plan != "pro":
        return False
    if sub.expires_at is None:
        return True
    return sub.expires_at >= _now_utc()

@app.get("/users/{user_id}/subscription")
def get_subscription(user_id: int, db: Session = Depends(get_db)):
    sub = db.query(ProSubscription).filter(ProSubscription.user_id == user_id).first()
    return {
        "user_id": user_id,
        "plan": sub.plan if sub else "free",
        "expires_at": sub.expires_at.isoformat() if (sub and sub.expires_at) else None,
        "is_pro": _is_pro(sub),
    }

@app.post("/users/{user_id}/upgrade")
def upgrade_user(user_id: int, data: SubscriptionUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    sub = db.query(ProSubscription).filter(ProSubscription.user_id == user_id).first()
    if not sub:
        sub = ProSubscription(user_id=user_id, plan="free", expires_at=None)
        db.add(sub)
        db.flush()

    days = data.days or 30
    base_time = sub.expires_at if (sub.expires_at and sub.expires_at >= _now_utc()) else _now_utc()
    sub.plan = "pro"
    sub.expires_at = base_time + timedelta(days=days)
    db.commit()
    db.refresh(sub)
    return {"detail": "Upgraded to Pro", "expires_at": sub.expires_at.isoformat()}

@app.post("/users/{user_id}/downgrade")
def downgrade_user(user_id: int, db: Session = Depends(get_db)):
    sub = db.query(ProSubscription).filter(ProSubscription.user_id == user_id).first()
    if not sub:
        return {"detail": "Already on free"}
    sub.plan = "free"
    sub.expires_at = None
    db.commit()
    return {"detail": "Downgraded to Free"}

# ============== WORKERS ==============

# Endpoint to get all workers
@app.get("/workers")
def get_workers(db: Session = Depends(get_db)):
    workers = db.query(Worker).filter(Worker.isAvailable == 1).all()
    return [
        {
            "id": w.id,
            "user_id": w.user_id,
            "name": w.name,
            "phone": w.phone,
            "skills": w.skills,
            "location": w.location,
            "about": w.about,
            "isAvailable": w.isAvailable,
            "rating": w.rating
        }
        for w in workers
    ]

# Endpoint to create/update worker profile
@app.post("/workers")
def create_worker(data: dict, db: Session = Depends(get_db)):
    user_id = data.get('user_id', 1)
    # Check if worker already exists
    worker = db.query(Worker).filter(Worker.user_id == user_id).first()
    if worker:
        # Update existing
        worker.name = data.get('name', worker.name)
        worker.phone = data.get('phone', worker.phone)
        worker.skills = data.get('skills', worker.skills)
        worker.location = data.get('location', worker.location)
        worker.about = data.get('about', worker.about)
        worker.isAvailable = data.get('isAvailable', 1)
    else:
        # Create new
        worker = Worker(
            user_id=user_id,
            name=data.get('name', 'Unknown'),
            phone=data.get('phone', ''),
            skills=data.get('skills', ''),
            location=data.get('location', ''),
            about=data.get('about', ''),
            isAvailable=data.get('isAvailable', 1),
            rating=0.0
        )
        db.add(worker)
    db.commit()
    db.refresh(worker)
    return {
        "id": worker.id,
        "user_id": worker.user_id,
        "name": worker.name,
        "phone": worker.phone,
        "skills": worker.skills,
        "location": worker.location,
        "about": worker.about,
        "isAvailable": worker.isAvailable,
        "rating": worker.rating
    }

# Endpoint to get worker by ID
@app.get("/workers/{worker_id}")
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return {
        "id": worker.id,
        "user_id": worker.user_id,
        "name": worker.name,
        "phone": worker.phone,
        "skills": worker.skills,
        "location": worker.location,
        "about": worker.about,
        "isAvailable": worker.isAvailable,
        "rating": worker.rating
    }

# Endpoint to get all chat messages
@app.get("/chat")
def get_chat_messages(db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).all()
    return [
        {
            "id": m.id,
            "user_id": m.user_id,
            "content": m.content,
            "timestamp": m.timestamp
        }
        for m in messages
    ]

# Endpoint to add a new chat message
@app.post("/chat")
def create_chat_message(msg: ChatMessageCreate, db: Session = Depends(get_db)):
    new_msg = ChatMessage(
        user_id=msg.user_id,
        content=msg.content,
        timestamp=msg.timestamp
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return {
        "id": new_msg.id,
        "user_id": new_msg.user_id,
        "content": new_msg.content,
        "timestamp": new_msg.timestamp
    }

# File upload endpoint
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(FILES_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

# File download endpoint
# File download endpoint
@app.get("/files/{filename}")
def get_file(filename: str):
    file_path = os.path.join(FILES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

# Moderation: Delete user
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

# Moderation: Delete chat message
@app.delete("/chat/{message_id}")
def delete_chat_message(message_id: int, db: Session = Depends(get_db)):
    msg = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"detail": "Message deleted"}

# Moderation: Ban user
@app.post("/ban/{user_id}")
def ban_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.banned = 1
    db.commit()
    return {"detail": f"User {user_id} banned"}

# App statistics endpoint
@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    user_count = db.query(User).count()
    task_count = db.query(Task).count()
    chat_count = db.query(ChatMessage).count()
    return {
        "users": user_count,
        "tasks": task_count,
        "chat_messages": chat_count
    }

# App version check endpoint
@app.get("/app/version")
def check_app_version():
    # Get the request host to dynamically determine the download URL
    # This allows it to work on both Render and local environments
    base_url = os.environ.get("APP_BASE_URL", "https://bmk-server.onrender.com")
    
    return {
        "latest_version": "1.0.2",
        "current_version": "1.0.1",
        "min_required_version": "1.0.0",
        "download_url": f"{base_url}/download_app",
        "force_update": False,  # Set True to force all users to update
        "update_message": "New features and improvements available!",
        "changelog": [
            "Added in-app update system",
            "Added remote feature flags",
            "Performance improvements",
            "Bug fixes"
        ]
    }

# Feature flags endpoint for remote control
@app.get("/app/features")
def get_feature_flags():
    return {
        "google_maps_enabled": True,
        "chat_enabled": True,
        "task_posting_enabled": True,
        "worker_registration_enabled": True,
        "google_oauth_enabled": True,
        "whatsapp_sharing_enabled": False,  # Coming soon
        "admin_reports_enabled": True,
        "guidelines_enabled": True,
        "search_enabled": True,
        "max_tasks_per_user": 50,
        "maintenance_mode": False,  # Set True to show maintenance screen
        "maintenance_message": "Server maintenance in progress. Please try again later."
    }