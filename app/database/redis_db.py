import redis
import json
from config import settings

class RedisClient:
    def __init__(self):
        self.client = None
        self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            # 测试连接
            self.client.ping()
            print("Redis连接成功")
        except redis.ConnectionError as e:
            print(f"Redis连接错误: {e}")

    def set_user_points(self, user_id: int, points: int):
        key = f"user:{user_id}:points"
        self.client.set(key, points, ex=3600)  # 缓存1小时

    def get_user_points(self, user_id: int) -> int:
        key = f"user:{user_id}:points"
        points = self.client.get(key)
        return int(points) if points else None

    def update_rank(self, user_id: int, username: str, points: int):
        # 更新积分排行榜
        self.client.zadd("user_points_rank", {f"{user_id}:{username}": points})

    def get_top_users(self, count: int = 10):
        # 获取前N名用户
        return self.client.zrevrange("user_points_rank", 0, count-1, withscores=True)

    def get_user_rank(self, user_id: int, username: str):
        # 获取用户排名
        member = f"{user_id}:{username}"
        rank = self.client.zrevrank("user_points_rank", member)
        return rank + 1 if rank is not None else None  # 从1开始排名

    def clear_cache(self, user_id: int):
        # 清除用户缓存
        keys = [
            f"user:{user_id}:points",
            f"user:{user_id}:level"
        ]
        for key in keys:
            self.client.delete(key)

redis_client = RedisClient()