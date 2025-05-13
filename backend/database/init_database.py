from backend.core.db import DBManager

def init_app_db():
    db_manager = DBManager()
    app_db = db_manager.get_db('app')
    app_db.connect()
    app_db.execute('''
        CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_query TEXT NOT NULL,
        time TEXT NOT NULL,
        num INTEGER NOT NULL,
        UNIQUE(search_query, time)
        )
    ''')
    app_db.close()
    print("app数据库初始化成功")
    
def init_db():
    init_app_db()
    print("已完成数据库全部初始化")
    