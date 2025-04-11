# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import posts, comments, token_transfer  # 추가
from database.connection import conn

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기존 라우터 등록
app.include_router(posts.router, prefix="/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
# 추가한 라우터 등록
app.include_router(token_transfer.router, prefix="/blockchain", tags=["Token Transfer"])

@app.on_event("startup")
def on_startup():
    conn()
