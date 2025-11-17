from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import users, points, ranks
from app.database.mysql_db import mysql_db
from app.database.redis_db import redis_client
from app.services.rank_service import RankService

app = FastAPI(
    title="用户积分等级系统",
    description="基于FastAPI + Redis + MySQL的复杂积分等级系统",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router)
app.include_router(points.router)
app.include_router(ranks.router)


@app.on_event("startup")
async def startup_event():
    # 启动时刷新排行榜
    RankService.refresh_rankings()


@app.get("/")
async def root():
    return {"message": "用户积分等级系统 API"}


@app.get("/health")
async def health_check():
    # 检查数据库连接状态
    mysql_healthy = mysql_db.connection and mysql_db.connection.is_connected()
    redis_healthy = redis_client.client and redis_client.client.ping()

    return {
        "status": "healthy" if mysql_healthy and redis_healthy else "unhealthy",
        "mysql": "connected" if mysql_healthy else "disconnected",
        "redis": "connected" if redis_healthy else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)