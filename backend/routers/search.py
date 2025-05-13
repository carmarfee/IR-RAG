from fastapi import APIRouter,Depends,HTTPException
from backend.services.search_service import search_engine,get_snapshot

router = APIRouter(
    prefix="/search",
    tags=["search"],
)


# =============== description ===============
# 最重要的搜索引擎接口
# ===========================================
@router.get("/search_engine")
async def search(query: str):
    results = search_engine(query)
    return results
    
    
@router.get("/get_snapshot")
async def snapshot(doc_id:int):
    raw_html = get_snapshot(doc_id)
    return raw_html