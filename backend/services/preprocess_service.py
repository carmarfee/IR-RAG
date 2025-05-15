from preprocess import ChineseDocumentPreprocessor
import json
import threading

def get_config():
    try:
        config_path = "preprocess/config.json"
        with open(config_path,'r',encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError:
        return {'error': '配置文件格式错误'}
    except FileNotFoundError:
        return {'error': '配置文件未找到'}
    
def save_config(config: dict):
    try:
        config_path = "preprocess/config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return {'success': '配置文件保存成功'}
    except Exception as e:
        return {'error': f"保存配置文件时出错: {e}"}
    
def run_proprecess(config:dict):
    save_config(config=config)
    config_path = "preprocess/config.json"
    def proprecess_task():
        processor = ChineseDocumentPreprocessor(config_path=config_path)
        processor.run_full_pipeline()
    thread = threading.Thread(target=proprecess_task,daemon=True)
    thread.start()
    return {'success': '预处理进行中'}
    
    
    
    
