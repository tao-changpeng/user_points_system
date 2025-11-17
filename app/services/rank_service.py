from typing import List, Optional
from app.database.redis_db import redis_client
from app.database.mysql_db import mysql_db
from app.models.point_models import RankUser
from app.services.user_service import UserService


class RankService:
    @staticmethod
    def get_top_ranks(limit: int = 10) -> List[RankUser]:
        """获取排行榜前N名用户"""
        try:
            top_users_data = redis_client.get_top_users(limit)
            ranked_users = []

            for rank, (member, points) in enumerate(top_users_data, 1):
                user_id_str, username = member.split(':', 1)
                user_id = int(user_id_str)

                # 从MySQL获取用户详细信息
                connection = mysql_db.get_connection()
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT level FROM users WHERE id = %s", (user_id,))
                user_data = cursor.fetchone()
                cursor.close()

                if user_data:
                    ranked_users.append(RankUser(
                        user_id=user_id,
                        username=username,
                        points=int(points),
                        level=user_data['level'],
                        rank=rank
                    ))

            return ranked_users

        except Exception as e:
            print(f"获取排行榜错误: {e}")
            return []

    @staticmethod
    def get_user_rank(user_id: int) -> Optional[RankUser]:
        """获取指定用户的排名信息"""
        try:
            user = UserService.get_user_by_id(user_id)
            if not user:
                return None

            rank = redis_client.get_user_rank(user_id, user.username)
            if rank is None:
                return None

            return RankUser(
                user_id=user_id,
                username=user.username,
                points=user.total_points,
                level=user.level,
                rank=rank
            )

        except Exception as e:
            print(f"获取用户排名错误: {e}")
            return None

    @staticmethod
    def refresh_rankings():
        """刷新排行榜（从MySQL同步数据到Redis）"""
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                           SELECT id, username, total_points
                           FROM users
                           WHERE is_active = TRUE
                           ORDER BY total_points DESC
                           """)

            users = cursor.fetchall()
            cursor.close()

            # 清空现有排行榜
            redis_client.client.delete("user_points_rank")

            # 重新添加所有用户
            for user in users:
                redis_client.update_rank(user['id'], user['username'], user['total_points'])

            print("排行榜刷新完成")

        except Exception as e:
            print(f"刷新排行榜错误: {e}")