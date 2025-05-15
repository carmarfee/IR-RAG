from fastapi import APIRouter,Depends,HTTPException
from backend.services.crawler_service import get_config,save_config,run_crawler,quit_crawler,resume_crawler,event_generator
from fastapi.responses import StreamingResponse

router = APIRouter(
    prefix='/crawler',
    tags=['crawler']
)


@router.get('/get_crawler_config')
async def get_crawler_config():
    config = get_config()
    return config

@router.post('/save_crawler_config')
async def save_crawler_config(config:dict):
    result = save_config(config)
    return result

@router.get('/start_crawler')
async def start_crawler():
    await run_crawler()
    return {'success': '爬虫已完成'}

@router.get('/stop_crawler')
async def stop_crawler():
    await quit_crawler()
    return {'success': '爬虫已停止'}

@router.get('/continue_crawler')
async def continue_crawler():
    await resume_crawler()
    return {'success': '爬虫已恢复'}

@router.get('/get_progress')
async def crawler_progress():
    return StreamingResponse(
        event_generator(),
        media_type='text/event-stream'
    )
    