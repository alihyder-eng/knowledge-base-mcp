from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from database.database import Base, engine
from database import models
from database.models import User

from api.auth import router as auth_router
from api.documents import router as documents_router
from api.search import router as search_router

from auth.dependencies import get_current_user


app = FastAPI(
    title="Personal Knowledge Base API"
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

Base.metadata.create_all(
    bind=engine
)


# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(search_router)


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.get("/")
def home():
    return {
        "message": "Personal Knowledge Base API is running!"
    }


# ---------------------------------------------------------
# CURRENT USER
# ---------------------------------------------------------

@app.get("/me", response_model=dict)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
    }