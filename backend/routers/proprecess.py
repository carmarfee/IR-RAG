from fastapi import APIRouter
from backend.utils.checkfile import check_file
from backend.services.preprocess_service import run_proprecess,get_config

router = APIRouter(
    prefix="/proprecess",
    tags=['proprecess']
)

@router.get('/check_proprecess_file')
async def check_proprecess_file():
    target_file = 'data/raw_data/crawler_data.db'
    return check_file(file_path=target_file)

@router.get('/get_proprecess_config')
async def get_proprecess_config():
    return get_config()

@router.get('/start_proprecess')
async def strat_proprecess(config):
    return run_proprecess(config=config)