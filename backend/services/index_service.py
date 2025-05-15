from index import InvertedIndexBuilder
import json
import threading
    
def run_inverted_index(optimize,min_tfidf):
    preprocess_data_dir = "data/preprocessed_data"
    def invertedindex_task():
        builder = InvertedIndexBuilder(preprocessed_data_dir=preprocess_data_dir)
        result = builder.run_pipeline(
            optimize=optimize,
            min_tfidf=min_tfidf
        )
    thread = threading.Thread(target=invertedindex_task,daemon=True)
    thread.start()
    return {'success': '索引构建进行中'}
    
    
    
