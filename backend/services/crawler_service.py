from crawler import *
import json
import asyncio
import aiofiles
import os
import threading

class CrawlerManager:
    """爬虫管理器，负责爬虫实例的创建和生命周期管理"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """单例模式获取管理器实例"""
        if cls._instance is None:
            cls._instance = CrawlerManager()
        return cls._instance
    
    def __init__(self):
        self.crawler = None
        self.config_file = "crawler/config.json"
        self.output_dir = "data/test_data"
        self.is_running = False
    
    def initialize_crawler(self):
        """初始化爬虫实例"""
        if self.crawler is None:
            from crawler import WebCrawler
            # 确保目录存在
            import os
            os.makedirs(self.output_dir, exist_ok=True)
            
            self.crawler = WebCrawler(
                config_file=self.config_file,
                output_dir=self.output_dir
            )
            return {'success': '爬虫已初始化'}
        return {'info': '爬虫已经初始化'}
    
    def run_crawler(self):
        """运行爬虫"""
        try:
            if self.crawler is None:
                self.initialize_crawler()
            
            if not self.is_running:
                self.is_running = True
                def crawl_task():
                    try:
                        self.crawler.crawl()
                    finally:
                        self.is_running = False
                        
                thread = threading.Thread(target=crawl_task,daemon=True)
                thread.start()
                return {'success': '爬取已开始运行'}
            else:
                return {'error': '爬虫已在运行中'}
        except Exception as e:
            self.is_running = False
            return {'error': f"爬取过程中出错: {e}"}
    
    def stop_crawler(self):
        """停止爬虫"""
        try:
            if self.crawler and self.is_running:
                self.crawler.stop()
                self.is_running = False
                return {'success': '爬虫已停止'}
            return {'info': '爬虫未在运行中'}
        except Exception as e:
            return {'error': f"停止爬虫时出错: {e}"}
    
    def resume_crawler(self):
        """恢复爬虫"""
        try:
            if self.crawler is None:
                self.initialize_crawler()
            
            if not self.is_running:
                self.is_running = True
                def resume_task():
                    try:
                        self.crawler.resume()
                    finally:
                        self.is_running = False
                        
                thread = threading.Thread(target=resume_task,daemon=True)
                thread.start()
                return {'success': '爬虫已恢复运行'}
            else:
                return {'error': '爬虫已在运行中'}
        except Exception as e:
            self.is_running = False
            return {'error': f"恢复爬虫时出错: {e}"}


def get_config():
    try:
        config_path = "crawler/config.json"
        with open(config_path,'r',encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        return {'error': '配置文件格式错误'}
    except FileNotFoundError:
        return {'error': '配置文件未找到'}
        
        
def save_config(config: dict):
    try:
        config_path = "crawler/config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return {'success': '配置文件保存成功'}
    except Exception as e:
        return {'error': f"保存配置文件时出错: {e}"}

async def run_crawler():
    manager = CrawlerManager.get_instance()
    return manager.run_crawler()

async def quit_crawler():
    manager = CrawlerManager.get_instance()
    return manager.stop_crawler()

async def resume_crawler():
    manager = CrawlerManager.get_instance()
    return manager.resume_crawler()
    
async def event_generator():
    """生成SSE事件流"""
    progress_file = f"crawler/progress.jsonl"
    
    # 获取文件的初始大小，从文件末尾开始监控
    try:
        if os.path.exists(progress_file):
            last_position = os.path.getsize(progress_file)
        else:
            last_position = 0
    except Exception:
        last_position = 0
    
    try:
        while True:
            try:
                # 检查文件是否存在
                if not os.path.exists(progress_file):
                    yield f"data: {json.dumps({'type': 'waiting', 'message': '等待进度文件创建'})}\n\n"
                    await asyncio.sleep(1)
                    continue
                
                async with aiofiles.open(progress_file, 'r', encoding='utf-8') as f:
                    # 获取当前文件大小
                    await f.seek(0, 2)  # 移到文件末尾
                    file_size = await f.tell()
                    
                    # 如果文件没有新内容，发送心跳
                    if file_size <= last_position:
                        yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                        await asyncio.sleep(0.5)
                        continue
                    
                    # 移到上次读取的位置
                    await f.seek(last_position)
                    
                    # 读取新增的内容
                    new_content = await f.read(file_size - last_position)
                    last_position = file_size
                    
                    # 处理新增的行
                    new_lines = new_content.strip().split('\n')
                    for line in new_lines:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                yield f"data: {json.dumps(data)}\n\n"
                                
                                # 如果是完成消息，结束监控
                                if data.get('type') == 'crawl_completed':
                                    return
                            except json.JSONDecodeError:
                                continue
                
                await asyncio.sleep(0.5)
                
            except FileNotFoundError:
                yield f"data: {json.dumps({'type': 'waiting', 'message': '等待进度文件创建'})}\n\n"
                await asyncio.sleep(1)
                
    except asyncio.CancelledError:
        pass
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    