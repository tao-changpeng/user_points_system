import mysql.connector
from mysql.connector import Error
from config import settings


class MySQLDatabase:
    def __init__(self):
        self.connection = None
        self.connect()
        self.init_tables()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_USER,
                password=settings.MYSQL_PASSWORD,
                database=settings.MYSQL_DATABASE
            )
            print("MySQL数据库连接成功")
        except Error as e:
            print(f"MySQL连接错误: {e}")

    def init_tables(self):
        try:
            cursor = self.connection.cursor()

            # 用户表
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS users
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               username
                               VARCHAR
                           (
                               50
                           ) UNIQUE NOT NULL,
                               email VARCHAR
                           (
                               100
                           ) UNIQUE NOT NULL,
                               hashed_password VARCHAR
                           (
                               255
                           ) NOT NULL,
                               level INT DEFAULT 1,
                               total_points INT DEFAULT 0,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                               is_active BOOLEAN DEFAULT TRUE
                               )
                           """)

            # 积分记录表
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS point_records
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               user_id
                               INT
                               NOT
                               NULL,
                               points_change
                               INT
                               NOT
                               NULL,
                               change_type
                               ENUM
                           (
                               'earn',
                               'consume',
                               'system'
                           ) NOT NULL,
                               description VARCHAR
                           (
                               255
                           ),
                               related_id VARCHAR
                           (
                               100
                           ),
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                               FOREIGN KEY
                           (
                               user_id
                           ) REFERENCES users
                           (
                               id
                           ) ON DELETE CASCADE
                               )
                           """)

            # 等级历史表
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS level_history
                           (
                               id
                               INT
                               AUTO_INCREMENT
                               PRIMARY
                               KEY,
                               user_id
                               INT
                               NOT
                               NULL,
                               old_level
                               INT
                               NOT
                               NULL,
                               new_level
                               INT
                               NOT
                               NULL,
                               changed_at
                               TIMESTAMP
                               DEFAULT
                               CURRENT_TIMESTAMP,
                               FOREIGN
                               KEY
                           (
                               user_id
                           ) REFERENCES users
                           (
                               id
                           ) ON DELETE CASCADE
                               )
                           """)

            self.connection.commit()
            cursor.close()
            print("数据库表初始化完成")

        except Error as e:
            print(f"初始化表错误: {e}")

    def get_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connect()
        return self.connection


mysql_db = MySQLDatabase()