# =============== description ===============
# 这里是历史记录的接口
# ===========================================
from fastapi import APIRouter
from backend.services.history_service import save_history,get_all_history,delete_history,delete_all_history

router = APIRouter(
    prefix="/history",
    tags=['history']
)

@router.get("/record_history")
async def record_history(search_query:str,time:str,num:int):
    result = save_history(search_query=search_query,time=time,num=num)
    return result

@router.get("/get_history")
async def get_history():
    results = get_all_history()
    return results

@router.get("/remove_history")
async def remove_history(id:int):
    result = delete_history(id=id)
    return result

@router.get("/remove_all_history")
async def remove_all_history():
    result = delete_all_history()
    return result