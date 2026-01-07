# BMK Server - Backend for connecting hirers and workers
# Deployed on Render.com

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import json
import os

app = FastAPI(title="BMK API", description="Backend for BMK - Hirer & Worker Platform for Nepal")

# Enable CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage (JSON file for persistence)
DATA_FILE = "bmk_data.json"
# Files directory for APK and downloads
FILES_DIR = os.path.join(os.path.dirname(__file__), "files")
os.makedirs(FILES_DIR, exist_ok=True)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"users": [], "tasks": [], "workers": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

# ============== MODELS ==============

class UserCreate(BaseModel):
    name: str
    phone: str
    location: str
    introduction: str = ""

class User(BaseModel):
    id: str
    name: str
    phone: str
    location: str
    introduction: str = ""
    lat: Optional[float] = None
    lng: Optional[float] = None
    created_at: str

class TaskCreate(BaseModel):
    title: str
    description: str
    category: str
    location: str
    budget: str
    duration: str
    poster_id: str
    poster_name: str
    poster_phone: str
    is_urgent: bool = False

class Task(BaseModel):
    id: str
    title: str
    description: str
    category: str
    location: str
    budget: str
    duration: str
    posted_date: str
    poster_id: str
    poster_name: str
    poster_phone: str
    status: str = "open"
    is_urgent: bool = False
    assigned_to: Optional[str] = None

class WorkerCreate(BaseModel):
    user_id: str
    name: str
    phone: str
    location: str
    skills: List[str]
    about: str
    rate: str

class Worker(BaseModel):
    id: str
    user_id: str
    name: str
    phone: str
    location: str
    skills: List[str]
    about: str
    rate: str
    is_available: bool = True
    joined_date: str
    rating: float = 0.0
    completed_tasks: int = 0

# ============== API ENDPOINTS ==============

@app.get("/")
def root():
    return {
        "message": "🤝 BMK API - Connecting Hirers & Workers in Nepal",
        "version": "1.0.0",
        "endpoints": {
            "users": "/users",
            "tasks": "/tasks",
            "workers": "/workers",
            "search": "/search",
            "stats": "/stats"
        }
    }


# Debug endpoint to inspect deployed filesystem
@app.get("/debug/files")
def debug_files():
    apk_path = os.path.join(FILES_DIR, "bmk.apk")
    files_exist = os.path.exists(FILES_DIR)
    apk_exists = os.path.isfile(apk_path)
    apk_size = os.path.getsize(apk_path) if apk_exists else 0
    return {
        "files_dir": FILES_DIR,
        "files_dir_exists": files_exist,
        "files_in_dir": os.listdir(FILES_DIR) if files_exist else [],
        "apk_path": apk_path,
        "apk_exists": apk_exists,
        "apk_size_mb": round(apk_size / 1024 / 1024, 2) if apk_exists else 0,
        "cwd": os.getcwd(),
        "cwd_files": os.listdir(os.getcwd()),
    }


# Download APK
@app.get("/download_app")
def download_app():
    apk_path = os.path.join(FILES_DIR, "bmk.apk")
    if not os.path.isfile(apk_path):
        raise HTTPException(status_code=404, detail="APK not found")
    from fastapi.responses import FileResponse  # Local import to avoid circulars at module load
    return FileResponse(apk_path, media_type="application/vnd.android.package-archive", filename="bmk.apk")


# App version metadata for in-app updater
@app.get("/app/version")
def app_version():
    base_url = os.environ.get("APP_BASE_URL", "https://bmk-server.onrender.com")
    return {
        "latest_version": "1.0.2",
        "current_version": "1.0.1",
        "min_required_version": "1.0.0",
        "download_url": f"{base_url}/download_app",
        "force_update": False,
        "update_message": "New features and improvements available!",
        "changelog": [
            "Added in-app update system",
            "Added remote feature flags",
            "Performance improvements",
            "Bug fixes",
        ],
    }

@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ============== USER ENDPOINTS ==============

@app.post("/users", response_model=User)
def create_user(user: UserCreate):
    data = load_data()
    
    # Check if phone already exists
    existing = next((u for u in data["users"] if u["phone"] == user.phone), None)
    if existing:
        return existing
    
    new_user = {
        "id": str(uuid.uuid4()),
        "name": user.name,
        "phone": user.phone,
        "location": user.location,
        "introduction": user.introduction,
        "lat": None,
        "lng": None,
        "created_at": datetime.now().isoformat()
    }
    data["users"].append(new_user)
    save_data(data)
    return new_user

@app.get("/users", response_model=List[User])
def get_users(location: Optional[str] = None):
    data = load_data()
    users = data["users"]
    if location:
        users = [u for u in users if location.lower() in u.get("location", "").lower()]
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    data = load_data()
    user = next((u for u in data["users"] if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ============== TASK ENDPOINTS ==============

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    data = load_data()
    new_task = {
        "id": str(uuid.uuid4()),
        "title": task.title,
        "description": task.description,
        "category": task.category,
        "location": task.location,
        "budget": task.budget,
        "duration": task.duration,
        "posted_date": datetime.now().isoformat(),
        "poster_id": task.poster_id,
        "poster_name": task.poster_name,
        "poster_phone": task.poster_phone,
        "status": "open",
        "is_urgent": task.is_urgent,
        "assigned_to": None
    }
    data["tasks"].append(new_task)
    save_data(data)
    return new_task

@app.get("/tasks", response_model=List[Task])
def get_tasks(
    category: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    urgent_only: bool = False
):
    data = load_data()
    tasks = data["tasks"]
    
    if category:
        tasks = [t for t in tasks if t["category"].lower() == category.lower()]
    if location:
        tasks = [t for t in tasks if location.lower() in t["location"].lower()]
    if status:
        tasks = [t for t in tasks if t["status"] == status]
    if urgent_only:
        tasks = [t for t in tasks if t.get("is_urgent", False)]
    
    # Sort by date (newest first)
    tasks.sort(key=lambda x: x["posted_date"], reverse=True)
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    data = load_data()
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}/status")
def update_task_status(task_id: str, status: str, assigned_to: Optional[str] = None):
    data = load_data()
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task["status"] = status
    if assigned_to:
        task["assigned_to"] = assigned_to
    save_data(data)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    data = load_data()
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    save_data(data)
    return {"message": "Task deleted"}

# ============== WORKER ENDPOINTS ==============

@app.post("/workers", response_model=Worker)
def register_worker(worker: WorkerCreate):
    data = load_data()
    
    # Check if already registered
    existing = next((w for w in data["workers"] if w["user_id"] == worker.user_id), None)
    if existing:
        # Update existing
        existing.update({
            "name": worker.name,
            "phone": worker.phone,
            "location": worker.location,
            "skills": worker.skills,
            "about": worker.about,
            "rate": worker.rate,
        })
        save_data(data)
        return existing
    
    new_worker = {
        "id": str(uuid.uuid4()),
        "user_id": worker.user_id,
        "name": worker.name,
        "phone": worker.phone,
        "location": worker.location,
        "skills": worker.skills,
        "about": worker.about,
        "rate": worker.rate,
        "is_available": True,
        "joined_date": datetime.now().isoformat(),
        "rating": 0.0,
        "completed_tasks": 0
    }
    data["workers"].append(new_worker)
    save_data(data)
    return new_worker

@app.get("/workers", response_model=List[Worker])
def get_workers(
    skill: Optional[str] = None,
    location: Optional[str] = None,
    available_only: bool = True
):
    data = load_data()
    workers = data["workers"]
    
    if skill:
        workers = [w for w in workers if any(skill.lower() in s.lower() for s in w["skills"])]
    if location:
        workers = [w for w in workers if location.lower() in w["location"].lower()]
    if available_only:
        workers = [w for w in workers if w.get("is_available", True)]
    
    # Sort by rating
    workers.sort(key=lambda x: x.get("rating", 0), reverse=True)
    return workers

@app.get("/workers/{worker_id}", response_model=Worker)
def get_worker(worker_id: str):
    data = load_data()
    worker = next((w for w in data["workers"] if w["id"] == worker_id or w["user_id"] == worker_id), None)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

@app.put("/workers/{worker_id}/availability")
def update_availability(worker_id: str, is_available: bool):
    data = load_data()
    worker = next((w for w in data["workers"] if w["id"] == worker_id or w["user_id"] == worker_id), None)
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    worker["is_available"] = is_available
    save_data(data)
    return worker

# ============== SEARCH ==============

@app.get("/search")
def search(q: str, type: Optional[str] = None):
    """Search tasks and workers by keyword"""
    data = load_data()
    results = {"tasks": [], "workers": []}
    q_lower = q.lower()
    
    if type != "workers":
        results["tasks"] = [
            t for t in data["tasks"]
            if q_lower in t["title"].lower() or
               q_lower in t["description"].lower() or
               q_lower in t["category"].lower() or
               q_lower in t["location"].lower()
        ]
    
    if type != "tasks":
        results["workers"] = [
            w for w in data["workers"]
            if q_lower in w["name"].lower() or
               q_lower in w["about"].lower() or
               q_lower in w["location"].lower() or
               any(q_lower in s.lower() for s in w["skills"])
        ]
    
    return results

# ============== STATS ==============

@app.get("/stats")
def get_stats():
    data = load_data()
    return {
        "total_users": len(data["users"]),
        "total_tasks": len(data["tasks"]),
        "open_tasks": len([t for t in data["tasks"] if t["status"] == "open"]),
        "total_workers": len(data["workers"]),
        "available_workers": len([w for w in data["workers"] if w.get("is_available", True)]),
        "categories": list(set(t["category"] for t in data["tasks"])),
        "locations": list(set(t["location"] for t in data["tasks"]) | set(w["location"] for w in data["workers"]))
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
