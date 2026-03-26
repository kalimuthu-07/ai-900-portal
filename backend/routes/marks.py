from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from database import supabase
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()
SECRET_KEY = os.getenv("SECRET_KEY", "secret123")

class MarkUpload(BaseModel):
    student_id: str
    topic: str
    score: float
    date: str

def get_current_user(authorization: str):
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Upload mark (Staff only)
@router.post("/upload")
def upload_mark(mark: MarkUpload, authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user["role"] != "staff":
        raise HTTPException(status_code=403, detail="Only staff can upload marks")

    supabase.table("marks").insert({
        "student_id": mark.student_id,
        "topic": mark.topic,
        "score": mark.score,
        "date": mark.date,
        "uploaded_by": user["id"]
    }).execute()

    return {"message": "Mark uploaded successfully"}

# ✅ All marks (Staff) - with roll_number
@router.get("/all")
def get_all_marks(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user["role"] != "staff":
        raise HTTPException(status_code=403, detail="Only staff can view")

    result = supabase.table("marks") \
        .select("topic, score, date, users!marks_student_id_fkey(name, roll_number)") \
        .execute()

    return result.data

# ✅ Top performers (Staff) - with roll_number
@router.get("/top-performers")
def get_top_performers(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user["role"] != "staff":
        raise HTTPException(status_code=403, detail="Only staff can view")

    result = supabase.table("marks") \
        .select("student_id, score, users!marks_student_id_fkey(name, roll_number)") \
        .order("score", desc=True) \
        .limit(10) \
        .execute()

    return result.data

# ✅ Student own marks
@router.get("/my-marks")
def get_my_marks(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students")

    result = supabase.table("marks") \
        .select("topic, score, date") \
        .eq("student_id", user["id"]) \
        .execute()

    return result.data

# ✅ Leaderboard (Any logged in user)
@router.get("/leaderboard")
def get_leaderboard(authorization: str = Header(...)):
    get_current_user(authorization)

    result = supabase.table("marks") \
        .select("student_id, score, users!marks_student_id_fkey(name)") \
        .order("score", desc=True) \
        .limit(10) \
        .execute()

    return result.data

# ✅ Get students list - with roll_number
@router.get("/students")
def get_all_students(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user["role"] != "staff":
        raise HTTPException(status_code=403, detail="Only staff")

    result = supabase.table("users") \
        .select("id, name, roll_number") \
        .eq("role", "student") \
        .execute()

    return result.data

# ✅ Stats for tiles
@router.get("/stats")
def get_stats(authorization: str = Header(...)):
    user = get_current_user(authorization)
    if user["role"] != "staff":
        raise HTTPException(status_code=403, detail="Only staff")

    students = supabase.table("users").select("id").eq("role", "student").execute()
    marks = supabase.table("marks").select("score").execute()

    total_students = len(students.data)
    total_marks = len(marks.data)
    avg_score = round(sum(m["score"] for m in marks.data) / total_marks, 1) if total_marks > 0 else 0
    top_score = max((m["score"] for m in marks.data), default=0)

    return {
        "total_students": total_students,
        "total_marks": total_marks,
        "avg_score": avg_score,
        "top_score": top_score
    }






