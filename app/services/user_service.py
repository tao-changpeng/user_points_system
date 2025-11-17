from mysql.connector import Error
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.database.mysql_db import mysql_db
from app.database.redis_db import redis_client
from app.models.user_models import UserCreate, UserInDB, TokenData
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_user(user: UserCreate) -> Optional[UserInDB]:
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            hashed_password = UserService.get_password_hash(user.password)

            cursor.execute("""
                           INSERT INTO users (username, email, hashed_password)
                           VALUES (%s, %s, %s)
                           """, (user.username, user.email, hashed_password))

            connection.commit()
            user_id = cursor.lastrowid

            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()

            return UserInDB(**user_data) if user_data else None

        except Error as e:
            print(f"创建用户错误: {e}")
            return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[UserInDB]:
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            cursor.close()

            return UserInDB(**user_data) if user_data else None

        except Error as e:
            print(f"查询用户错误: {e}")
            return None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[UserInDB]:
        try:
            connection = mysql_db.get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()

            return UserInDB(**user_data) if user_data else None

        except Error as e:
            print(f"查询用户错误: {e}")
            return None

    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
        user = UserService.get_user_by_username(username)
        if not user:
            return None
        if not UserService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt