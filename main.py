# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager  # 추가
from routers import posts, comments, token_transfer, external  # 추가
from database.connection import conn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작할 때 실행됨
    conn()
    yield
    # 종료할 때 실행됨
    # 필요한 정리 작업이 있다면 여기에 추가

app = FastAPI(lifespan=lifespan)

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
app.include_router(external.router, tags=["External Data"])
