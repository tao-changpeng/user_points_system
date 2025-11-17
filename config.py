import os
from typing import Dict, Any


class Settings:
    # MySQL配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "1234"
    MYSQL_DATABASE: str = "points_system"

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str = None

    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 积分等级配置
    LEVEL_CONFIG: Dict[int, int] = {
        1: 100,  # 等级1需要100积分
        2: 300,  # 等级2需要300积分
        3: 600,  # 等级3需要600积分
        4: 1000,  # 等级4需要1000积分
        5: 1500,  # 等级5需要1500积分
        6: 2100,  # 等级6需要2100积分
        7: 2800,  # 等级7需要2800积分
        8: 3600,  # 等级8需要3600积分
        9: 4500,  # 等级9需要4500积分
        10: 5500  # 等级10需要5500积分
    }


settings = Settings()