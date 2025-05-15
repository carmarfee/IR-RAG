from fastapi import APIRouter
from backend.utils.checkfile import check_file
from backend.services.preprocess_service import run_preprocess,get_config

router = APIRouter(
    prefix="/preprocess",
    tags=['preprocess']
)

@router.get('/check_preprocess_file')
async def check_preprocess_file():
    target_file = 'data/raw_data/crawler_data.db'
    return check_file(file_path=target_file)

@router.get('/get_preprocess_config')
async def get_preprocess_config():
    return get_config()

@router.get('/start_preprocess')
async def strat_preprocess(min_df,max_df):
    return run_preprocess(min_df=int(min_df),max_df=float(max_df))