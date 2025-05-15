from fastapi import APIRouter
from backend.utils.checkfile import check_multiple_files
from backend.services.index_service import run_inverted_index


router = APIRouter(
    prefix="/index",
    tags=["/index"]
)

@router.get("/check_index_file")
async def check_index_file():
    target_files = [
        "data/preprocessed_data/processed_documents.csv",
        "data/preprocessed_data/tfidf_matrix.pkl"
    ]
    return check_multiple_files(
        file_paths=target_files
    )
    
@router.get("/start_inverted_index")
async def start_inverted_index(optimize,min_tfidf):
    return run_inverted_index(
        optimize=optimize,
        min_tfidf=min_tfidf
    )