from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, todos, work_logs, reports, templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="工作 Todo API",
    description="工作任务管理与报告生成系统",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(work_logs.router)
app.include_router(reports.router)
app.include_router(templates.router)


@app.get("/")
async def root():
    return {"message": "工作 Todo API", "docs": "/docs"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
