from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.db import DBManager
from contextlib import asynccontextmanager
from backend.database.init_database import init_db
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(str(root_dir)) 


# 定义lifespan上下文管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 数据库注册
    docs_db_path = "data/raw_data/crawler_data.db"
    app_db_path = "backend/database/app.db"
    
    db_manager = DBManager()
    docs_db = db_manager.register_db("docs", docs_db_path)
    app_db = db_manager.register_db("app", app_db_path)

    init_db()
    yield  # 应用运行期间
    db_manager.close_all()



app = FastAPI(title="IR搜索系统", description="文档搜索与管理API",lifespan=lifespan)

from backend.routers import search
from backend.routers import crawler
from backend.routers import history
# 路由聚合
app.include_router(search.router)
app.include_router(crawler.router)
app.include_router(history.router)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message":root_dir}

@app.get("/test")
async def db():
    docs_db = DBManager().get_db("docs")
    return docs_db.fetch_one("SELECT * FROM pages WHERE id = ?", (1,))


