from retrieval import SearchEngine
from backend.core.db import DBManager


def search_engine(
    query: str, 
    config: dict = None
):
    index_dir = "data/preprocessed_data/inverted_index"
    search_engine = SearchEngine(index_dir=index_dir)
    if not search_engine.load_index():
        return {"加载索引失败"}
    
    # 执行搜索
    if query:
        results = search_engine.search(query, top_k=50,score_threshold=0.2)
        if results:
            return results
        else:
            return {"未找到匹配的文档。"}
    return {"请输入查询词"}
    
    
def get_snapshot(
    doc_id: int
):
    docs_db = DBManager().get_db(name='docs')
    docs_db.connect()
    raw_data = docs_db.fetch_one("SELECT html_content,url FROM pages WHERE id = ?", (doc_id,))
    docs_db.close()
    if raw_data:
        return raw_data
    return {"未找到对应的网页快照"}

def get_content(
    doc_id: int
):
    docs_db = DBManager().get_db(name='docs')
    docs_db.connect()
    raw_data = docs_db.fetch_one("SELECT content FROM pages WHERE id = ?", (doc_id,))
    docs_db.close()
    if raw_data:
        return raw_data
    return {"未找到对应的网页内容"}
    
