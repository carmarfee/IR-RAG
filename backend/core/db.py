import os
import sqlite3
from typing import Dict, List, Any, Optional, Tuple, Union

class SQLiteDB:
    """SQLite数据库操作封装类"""
    
    def __init__(self, db_path: str):
        """
        初始化数据库连接
        
        Args:
            db_path: SQLite数据库文件完整路径
        """
        # 确保目录存在
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"创建数据库目录: {db_dir}")
        
        self.db_path = db_path
        self.conn = None
        
        # 检查数据库文件是否存在
        db_exists = os.path.isfile(self.db_path)
        if db_exists:
            print(f"使用现有数据库文件: {self.db_path}")
        else:
            print(f"将创建新数据库文件: {self.db_path}")
    
    def connect(self):
        """连接到数据库，如果不存在则创建"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            # 启用外键约束
            self.conn.execute("PRAGMA foreign_keys = ON")
            # 配置连接以返回字典形式的行
            self.conn.row_factory = sqlite3.Row
            print(f"已连接到SQLite数据库: {self.db_path}")
        return self.conn
    
    def execute(self, query: str, params: Union[Tuple, Dict, None] = None) -> int:
        """
        执行不返回数据的SQL语句
        
        Args:
            query: SQL查询语句
            params: 查询参数，可以是元组、字典或None
            
        Returns:
            受影响的行数
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except sqlite3.Error as e:
            print(f"执行SQL语句时发生错误: {e}")
            return
            
    def fetch_one(self, query: str, params: Union[Tuple, Dict, None] = None) -> Optional[Dict]:
        """
        执行查询并返回单个结果
        
        Args:
            query: SQL查询语句
            params: 查询参数，可以是元组、字典或None
            
        Returns:
            查询结果字典，如果没有结果则返回None
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        row = cursor.fetchone()
        cursor.close()
        if row:
            return dict(row)
        return None
    
    def fetch_all(self, query: str, params: Union[Tuple, Dict, None] = None) -> List[Dict]:
        """
        执行查询并返回所有结果
        
        Args:
            query: SQL查询语句
            params: 查询参数，可以是元组、字典或None
            
        Returns:
            查询结果字典列表
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]
    
    def execute_many(self, query: str, params_list: List[Union[Tuple, Dict]]) -> int:
        """
        执行批量SQL语句
        
        Args:
            query: SQL查询语句
            params_list: 参数列表
            
        Returns:
            受影响的行数
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        return affected_rows
    
    def execute_script(self, sql_script: str) -> None:
        """
        执行SQL脚本
        
        Args:
            sql_script: 包含多条SQL语句的脚本
        """
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()
        cursor.close()
    
    def get_last_row_id(self) -> int:
        """
        获取最后插入行的ID
        
        Returns:
            最后插入的行ID
        """
        return self.conn.last_insert_rowid() if self.conn else 0
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            print(f"已关闭SQLite数据库连接: {self.db_path}")


class DBManager:
    """数据库管理器，管理多个数据库连接"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(DBManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化数据库管理器"""
        if getattr(self, '_initialized', False):
            return
            
        self.databases = {}
        self._initialized = True
    
    def register_db(self, name: str, db_path: str) -> SQLiteDB:
        """
        注册一个数据库连接
        
        Args:
            name: 数据库名称，用于引用
            db_path: 数据库文件路径
            
        Returns:
            注册的数据库实例
        """
        if name in self.databases:
            print(f"数据库 '{name}' 已经注册，返回现有实例")
            return self.databases[name]
            
        db = SQLiteDB(db_path)
        self.databases[name] = db
        print(f"数据库 '{name}' 注册成功: {db_path}")
        return db
    
    def get_db(self, name: str) -> Optional[SQLiteDB]:
        """
        获取指定名称的数据库实例
        
        Args:
            name: 数据库名称
            
        Returns:
            数据库实例，如果不存在则返回None
        """
        return self.databases.get(name)
    
    def connect_all(self):
        """连接所有注册的数据库"""
        for name, db in self.databases.items():
            db.connect()
            print(f"数据库 '{name}' 已连接")
    
    def close_all(self):
        """关闭所有数据库连接"""
        for name, db in self.databases.items():
            db.close()
            print(f"数据库 '{name}' 已关闭")
            
            
