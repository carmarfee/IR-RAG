from index import InvertedIndexBuilder
import json
import threading
    
def run_inverted_index(optimize,min_tfidf):
    preprocess_data_dir = "data/preprocessed_data"
    builder = InvertedIndexBuilder(preprocessed_data_dir=preprocess_data_dir)
    builder.run_pipeline(
        optimize=optimize,
        min_tfidf=min_tfidf
    )
    try:
        report_path = "data/preprocessed_data/inverted_index/index_results.json"
        with open(report_path,'r',encoding='utf-8') as f:
            report = json.load(f)
        return report
    except json.JSONDecodeError:
        return {'error': '文件格式错误'}
    except FileNotFoundError:
        return {'error': '文件未找到'}
    
    
    
