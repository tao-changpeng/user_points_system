from mysql.connector import Error
from typing import List, Optional, Tuple

from app.database.mysql_db import mysql_db
from app.database.redis_db import redis_client
from app.models.point_models import PointRecordCreate, PointRecordResponse, LevelUpResponse
from app.services.user_service import UserService
from config import settings


class PointService:
    @staticmethod
    def calculate_level(points: int) -> int:
        """根据积分计算等级"""
        level = 1
        for lvl, required_points in sorted(settings.LEVEL_CONFIG.items()):
            if points >= required_points:
                level = lvl
            else:
                break
        return level

    @staticmethod
    def add_points(user_id: int, points_data: PointRecordCreate) -> Tuple[bool, Optional[LevelUpResponse]]:
        """添加积分并检查是否升级"""
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            # 开始事务
            connection.start_transaction()

            # 获取用户当前信息
            cursor.execute("SELECT level, total_points FROM users WHERE id = %s FOR UPDATE", (user_id,))
            user_data = cursor.fetchone()

            if not user_data:
                cursor.close()
                return False, None

            old_level = user_data['level']
            new_total_points = user_data['total_points'] + points_data.points_change

            # 计算新等级
            new_level = PointService.calculate_level(new_total_points)

            # 更新用户积分和等级
            cursor.execute("""
                           UPDATE users
                           SET total_points = %s,
                               level        = %s
                           WHERE id = %s
                           """, (new_total_points, new_level, user_id))

            # 记录积分变更
            cursor.execute("""
                           INSERT INTO point_records (user_id, points_change, change_type, description, related_id)
                           VALUES (%s, %s, %s, %s, %s)
                           """, (user_id, points_data.points_change, points_data.change_type,
                                 points_data.description, points_data.related_id))

            level_up_response = None
            if new_level > old_level:
                # 记录等级变更历史
                cursor.execute("""
                               INSERT INTO level_history (user_id, old_level, new_level)
                               VALUES (%s, %s, %s)
                               """, (user_id, old_level, new_level))

                level_up_response = LevelUpResponse(
                    user_id=user_id,
                    old_level=old_level,
                    new_level=new_level,
                    current_points=new_total_points,
                    message=f"恭喜升级！从等级 {old_level} 升级到等级 {new_level}"
                )

            # 提交事务
            connection.commit()
            cursor.close()

            # 更新Redis缓存
            redis_client.set_user_points(user_id, new_total_points)

            # 更新排行榜
            user = UserService.get_user_by_id(user_id)
            if user:
                redis_client.update_rank(user_id, user.username, new_total_points)

            # 清除相关缓存
            redis_client.clear_cache(user_id)

            return True, level_up_response

        except Error as e:
            connection.rollback()
            print(f"添加积分错误: {e}")
            return False, None

    @staticmethod
    def get_user_points_history(user_id: int, limit: int = 50) -> List[PointRecordResponse]:
        """获取用户积分历史"""
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                           SELECT *
                           FROM point_records
                           WHERE user_id = %s
                           ORDER BY created_at DESC
                               LIMIT %s
                           """, (user_id, limit))

            records = cursor.fetchall()
            cursor.close()

            return [PointRecordResponse(**record) for record in records]

        except Error as e:
            print(f"获取积分历史错误: {e}")
            return []

    @staticmethod
    def get_user_level_history(user_id: int) -> List[dict]:
        """获取用户等级变更历史"""
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                           SELECT *
                           FROM level_history
                           WHERE user_id = %s
                           ORDER BY changed_at DESC
                           """, (user_id,))

            records = cursor.fetchall()
            cursor.close()

            return records

        except Error as e:
            print(f"获取等级历史错误: {e}")
            return []