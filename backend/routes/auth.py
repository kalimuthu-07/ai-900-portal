from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import supabase
from passlib.context import CryptContext
from passlib.exc import UnknownHashError
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")

class LoginRequest(BaseModel):
    identifier: str
    password: str
    role: str   # "staff" or "student"

class AddStudentRequest(BaseModel):
    name: str
    roll_number: str
    password: str

class AddStaffRequest(BaseModel):
    name: str
    email: str
    password: str


# ─── LOGIN ────────────────────────────────────────────
@router.post("/login")
def login(req: LoginRequest):
    if req.role == "staff":
        result = supabase.table("users").select("*").eq("email", req.identifier).eq("role", "staff").execute()
    else:
        result = supabase.table("users").select("*").eq("roll_number", req.identifier).eq("role", "student").execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials!")

    user = result.data[0]

    try:
        # ✅ Try bcrypt verify
        if not pwd_context.verify(req.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials!")

    except UnknownHashError:
        # ⚠️ fallback (old plain password support)
        if req.password != user["password"]:
            raise HTTPException(status_code=401, detail="Invalid credentials!")

    token = jwt.encode({
        "id": user["id"],
        "role": user["role"],
        "name": user["name"]
    }, SECRET_KEY, algorithm="HS256")

    return {
        "token": token,
        "role": user["role"],
        "name": user["name"],
        "id": user["id"]
    }


# ─── ADD STUDENT ──────────────────────────────────────
@router.post("/add-student")
def add_student(req: AddStudentRequest):
    existing = supabase.table("users").select("*").eq("roll_number", req.roll_number).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Roll number already exists!")

    hashed_pw = pwd_context.hash(req.password)

    supabase.table("users").insert({
        "name": req.name,
        "roll_number": req.roll_number,
        "password": hashed_pw,
        "role": "student"
    }).execute()

    return {"message": f"Student {req.name} added successfully!"}


# ─── ADD STAFF ────────────────────────────────────────
@router.post("/add-staff")
def add_staff(req: AddStaffRequest):
    existing = supabase.table("users").select("*").eq("email", req.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already exists!")

    hashed_pw = pwd_context.hash(req.password)

    supabase.table("users").insert({
        "name": req.name,
        "email": req.email,
        "password": hashed_pw,
        "role": "staff"
    }).execute()

    return {"message": f"Staff {req.name} added successfully!"}