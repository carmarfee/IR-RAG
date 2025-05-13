from backend.core.db import DBManager

def save_history(search_query:str,time:str,num:int):
    '''
    ARGS:
        title: 文档标题
        time: 搜索时间 
        num: 搜索结果数量 
    '''
    db_manager = DBManager()
    app_db = db_manager.get_db('app')
    query = "INSERT INTO history (search_query, time, num) VALUES (?, ?, ?)"
    app_db.connect()
    rows = app_db.execute(query=query, params=(search_query, time, num))
    app_db.close()
    return {f"执行成功，受影响行数为:{rows}"}

def get_all_history():
    db_manager = DBManager()
    app_db = db_manager.get_db('app')
    query = "SELECT * FROM history"
    app_db.connect()
    results = app_db.fetch_all(query=query)
    app_db.close()
    return results

def delete_history(id:int):
    db_manager = DBManager()
    app_db = db_manager.get_db('app')
    query = "DELETE FROM history WHERE id = ?"
    app_db.connect()
    rows = app_db.execute(query=query, params=(id,))
    app_db.close()
    return {f"执行成功，受影响行数为:{rows}"}

def delete_all_history():
    db_manager = DBManager()
    app_db = db_manager.get_db('app')
    query = "DELETE FROM history"
    app_db.connect()
    rows = app_db.execute(query=query)
    app_db.close()
    return {f"执行成功，受影响行数为:{rows}"}