"""
Database Migrator
处理数据库模式变更和数据迁移。
"""

import os
from typing import List, Dict, Any
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class DBMigrator:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # 解析数据库URL
        # 假设格式为: postgresql://user:password@host:port/database
        parts = self.db_url.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_port_db = parts[1].split("/")
        host_port = host_port_db[0].split(":")
        
        self.connection_params = {
            "user": user_pass[0],
            "password": user_pass[1],
            "host": host_port[0],
            "port": host_port[1],
            "database": host_port_db[1]
        }
    
    def connect(self):
        """建立数据库连接"""
        return psycopg2.connect(**self.connection_params)
    
    def create_table(self, table_name: str, columns: Dict[str, str]):
        """
        创建新表。
        
        Args:
            table_name: 表名。
            columns: 列定义的字典，键为列名，值为SQL类型定义。
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                column_defs = ", ".join([f"{name} {type_def}" for name, type_def in columns.items()])
                query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                    sql.Identifier(table_name),
                    sql.SQL(column_defs)
                )
                cur.execute(query)
                conn.commit()
    
    def add_column(self, table_name: str, column_name: str, column_type: str):
        """
        向现有表添加新列。
        
        Args:
            table_name: 表名。
            column_name: 新列名。
            column_type: SQL类型定义。
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                query = sql.SQL("ALTER TABLE {} ADD COLUMN IF NOT EXISTS {} {}").format(
                    sql.Identifier(table_name),
                    sql.Identifier(column_name),
                    sql.SQL(column_type)
                )
                cur.execute(query)
                conn.commit()
    
    def run_migration(self, migration_sql: str):
        """
        执行自定义的迁移SQL脚本。
        
        Args:
            migration_sql: 要执行的SQL脚本。
        """
        with self.connect() as conn:
            with conn.cursor() as cur:
                cur.execute(migration_sql)
                conn.commit()

# 用于测试的主函数
if __name__ == "__main__":
    migrator = DBMigrator()
    
    # 创建示例表
    # migrator.create_table("conversations", {
    #     "id": "SERIAL PRIMARY KEY",
    #     "user_id": "VARCHAR(255) NOT NULL",
    #     "question": "TEXT NOT NULL",
    #     "answer": "TEXT NOT NULL",
    #     "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
    # })
    # 
    # # 添加新列
    # migrator.add_column("conversations", "model_used", "VARCHAR(255)")