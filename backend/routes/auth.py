from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import supabase
from jose import jwt
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")


# ─── MODELS ────────────────────────────────────────────
class LoginRequest(BaseModel):
    identifier: str   # email OR roll_number
    password: str
    role: str         # staff / student


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

    # 🔹 Staff login → email
    if req.role == "staff":
        result = supabase.table("users") \
            .select("*") \
            .eq("email", req.identifier) \
            .eq("role", "staff") \
            .execute()

    # 🔹 Student login → roll_number
    else:
        result = supabase.table("users") \
            .select("*") \
            .eq("roll_number", req.identifier) \
            .eq("role", "student") \
            .execute()

    if not result.data:
        raise HTTPException(status_code=401, detail="Invalid credentials!")

    user = result.data[0]

    # ✅ SIMPLE PASSWORD CHECK (NO bcrypt)
    if req.password != user["password"]:
        raise HTTPException(status_code=401, detail="Invalid credentials!")

    # 🔐 TOKEN
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

    existing = supabase.table("users") \
        .select("*") \
        .eq("roll_number", req.roll_number) \
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Roll number already exists!")

    # ✅ SAVE PLAIN PASSWORD (TEMPORARY)
    supabase.table("users").insert({
        "name": req.name,
        "roll_number": req.roll_number,
        "password": req.password,
        "role": "student"
    }).execute()

    return {"message": f"Student {req.name} added successfully!"}


# ─── ADD STAFF ────────────────────────────────────────
@router.post("/add-staff")
def add_staff(req: AddStaffRequest):

    existing = supabase.table("users") \
        .select("*") \
        .eq("email", req.email) \
        .execute()

    if existing.data:
        raise HTTPException(status_code=400, detail="Email already exists!")

    # ✅ SAVE PLAIN PASSWORD
    supabase.table("users").insert({
        "name": req.name,
        "email": req.email,
        "password": req.password,
        "role": "staff"
    }).execute()

    return {"message": f"Staff {req.name} added successfully!"}