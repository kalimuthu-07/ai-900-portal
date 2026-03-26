from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, marks

app = FastAPI(title="AI-900 Training Portal")

# CORS - allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(marks.router, prefix="/marks", tags=["Marks"])

@app.get("/")
def root():
    return {"message": "AI-900 Training Portal API is running!"}
