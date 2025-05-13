import os
import pickle
import numpy as np
import pandas as pd
import logging
import time
import json
from collections import defaultdict

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """递归地将NumPy类型转换为Python原生类型，解决JSON序列化问题"""
    if isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, tuple):
        return tuple(convert_numpy_types(item) for item in obj)
    elif isinstance(obj, dict):
        return {convert_numpy_types(key): convert_numpy_types(value) for key, value in obj.items()}
    else:
        return obj

class InvertedIndexBuilder:
    """
    倒排索引构建器 - 基于预处理后的TF-IDF矩阵构建高效搜索索引
    """
    
    def __init__(self, preprocessed_data_dir, output_dir=None):
        """
        初始化倒排索引构建器
        
        参数:
            preprocessed_data_dir (str): 预处理数据目录路径，应包含处理后的文档和TF-IDF矩阵
            output_dir (str, optional): 输出目录，默认为preprocessed_data_dir下的inverted_index子目录
        """
        self.preprocessed_data_dir = preprocessed_data_dir
        self.output_dir = output_dir if output_dir else os.path.join(preprocessed_data_dir, "inverted_index")
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 存储索引相关数据
        self.processed_data = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.inverted_index = None
        self.doc_lengths = None
        self.feature_names = None
        self.metadata = None
        self.doc_id_mapping = None  # 添加文档ID映射
        
    def load_preprocessed_data(self):
        """加载预处理后的数据"""
        try:
            # 加载处理后的文档数据
            processed_data_path = os.path.join(self.preprocessed_data_dir, "processed_documents.csv")
            self.processed_data = pd.read_csv(processed_data_path, encoding='utf-8')
            logger.info(f"成功加载处理后的文档数据，共{len(self.processed_data)}条记录")
            
            # 加载TF-IDF向量化器
            vectorizer_path = os.path.join(self.preprocessed_data_dir, "tfidf_vectorizer.pkl")
            with open(vectorizer_path, 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
            
            # 获取特征名称（词汇表）
            self.feature_names = self.tfidf_vectorizer.get_feature_names_out()
            logger.info(f"成功加载TF-IDF向量化器，词汇表大小: {len(self.feature_names)}")
            
            # 加载TF-IDF矩阵
            matrix_path = os.path.join(self.preprocessed_data_dir, "tfidf_matrix.pkl")
            with open(matrix_path, 'rb') as f:
                self.tfidf_matrix = pickle.load(f)
            logger.info(f"成功加载TF-IDF矩阵，维度: {self.tfidf_matrix.shape}")
            
            # 尝试加载文档ID映射
            doc_id_mapping_path = os.path.join(self.preprocessed_data_dir, "doc_id_mapping.pkl")
            if os.path.exists(doc_id_mapping_path):
                with open(doc_id_mapping_path, 'rb') as f:
                    self.doc_id_mapping = pickle.load(f)
                logger.info(f"成功加载文档ID映射，共{len(self.doc_id_mapping)}个映射")
            else:
                # 如果没有专门的映射文件，检查处理后的数据是否包含doc_id
                if 'doc_id' in self.processed_data.columns:
                    self.doc_id_mapping = self.processed_data['doc_id'].tolist()
                    logger.info(f"从处理后的数据中提取文档ID映射，共{len(self.doc_id_mapping)}个文档")
                else:
                    logger.warning("未找到文档ID映射，将使用行索引作为文档ID")
                    self.doc_id_mapping = None
            
            return True
        except Exception as e:
            logger.error(f"加载预处理数据失败: {e}")
            return False
    
    def compute_document_lengths(self):
        """计算文档向量的长度（用于余弦相似度计算）"""
        start_time = time.time()
        logger.info("计算文档向量长度...")
        
        # 计算每个文档向量的L2范数（欧几里得长度）
        self.doc_lengths = np.sqrt(np.array(self.tfidf_matrix.power(2).sum(axis=1)).flatten())
        
        logger.info(f"文档向量长度计算完成，耗时: {time.time() - start_time:.2f}秒")
        
    def build_inverted_index(self):
        """构建倒排索引"""
        if self.tfidf_matrix is None or self.feature_names is None:
            logger.error("TF-IDF矩阵或特征名称未加载，无法构建倒排索引")
            return False
        
        start_time = time.time()
        logger.info("开始构建倒排索引...")
        
        # 初始化倒排索引字典
        self.inverted_index = defaultdict(list)
        
        # 获取TF-IDF矩阵的非零元素
        cx = self.tfidf_matrix.tocoo()
        
        # 遍历所有非零元素
        for i, j, v in zip(cx.row, cx.col, cx.data):
            # i: 矩阵行索引, j: 特征(词)的索引, v: TF-IDF值
            if v > 0:  # 只记录TF-IDF值大于0的条目
                term = self.feature_names[j]
                
                # 使用原始文档ID而不是矩阵行索引
                if self.doc_id_mapping is not None:
                    doc_id = int(self.doc_id_mapping[i])  # 获取原始文档ID
                else:
                    doc_id = int(i)  # 如果没有映射，则使用矩阵行索引
                
                weight = float(v)  # 确保是Python原生float类型
                
                # 将(文档ID, 权重)对添加到该词的倒排列表中
                self.inverted_index[term].append((doc_id, weight))
        
        # 统计索引大小
        total_entries = sum(len(postings) for postings in self.inverted_index.values())
        logger.info(f"倒排索引构建完成，包含{len(self.inverted_index)}个词条，{total_entries}个索引条目")
        logger.info(f"构建耗时: {time.time() - start_time:.2f}秒")
        
        # 创建索引元数据
        self.metadata = {
            "index_created_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_documents": int(len(self.processed_data)),  # 确保是原生int类型
            "vocabulary_size": int(len(self.feature_names)),
            "total_index_entries": int(total_entries),
            "average_postings_per_term": float(total_entries / max(1, len(self.inverted_index))),
            "uses_original_doc_ids": self.doc_id_mapping is not None  # 记录是否使用了原始文档ID
        }
        
        return True
    
    def optimize_index(self, min_tfidf=0.01):
        """
        优化倒排索引，去除低权重条目
        
        参数:
            min_tfidf (float): 最小TF-IDF阈值，低于此值的条目会被移除
        """
        if self.inverted_index is None:
            logger.error("倒排索引尚未构建，无法优化")
            return
        
        start_time = time.time()
        logger.info(f"开始优化倒排索引(最小TF-IDF阈值: {min_tfidf})...")
        
        # 记录优化前的统计信息
        original_terms = len(self.inverted_index)
        original_entries = sum(len(postings) for postings in self.inverted_index.values())
        
        # 优化索引
        optimized_index = defaultdict(list)
        
        for term, postings in self.inverted_index.items():
            # 保留权重大于阈值的条目
            filtered_postings = [(int(doc_id), float(weight)) for doc_id, weight in postings if weight >= min_tfidf]
            
            # 如果该词仍有文档与之关联，则保留在索引中
            if filtered_postings:
                optimized_index[term] = filtered_postings
        
        # 更新索引
        self.inverted_index = optimized_index
        
        # 更新统计信息 (确保使用原生Python类型)
        remaining_terms = len(self.inverted_index)
        remaining_entries = sum(len(postings) for postings in self.inverted_index.values())
        reduction_terms = original_terms - remaining_terms
        reduction_entries = original_entries - remaining_entries
        
        logger.info(f"索引优化完成，耗时: {time.time() - start_time:.2f}秒")
        logger.info(f"优化前: {original_terms}个词条，{original_entries}个索引条目")
        logger.info(f"优化后: {remaining_terms}个词条，{remaining_entries}个索引条目")
        logger.info(f"减少了: {reduction_terms}个词条({reduction_terms/max(1,original_terms)*100:.2f}%)，"
                   f"{reduction_entries}个索引条目({reduction_entries/max(1,original_entries)*100:.2f}%)")
        
        # 更新元数据
        self.metadata["optimized"] = True
        self.metadata["optimization_threshold"] = float(min_tfidf)
        self.metadata["original_terms"] = int(original_terms)
        self.metadata["original_entries"] = int(original_entries)
        self.metadata["optimized_terms"] = int(remaining_terms)
        self.metadata["optimized_entries"] = int(remaining_entries)
        self.metadata["reduction_percentage"] = {
            "terms": float(reduction_terms/max(1,original_terms)*100),
            "entries": float(reduction_entries/max(1,original_entries)*100)
        }
    
    def save_inverted_index(self):
        """保存倒排索引和相关数据"""
        if self.inverted_index is None:
            logger.error("倒排索引尚未构建，无法保存")
            return False
        
        try:
            start_time = time.time()
            logger.info("开始保存倒排索引...")
            
            # 转换defaultdict为普通dict以便序列化，并转换NumPy类型
            index_dict = convert_numpy_types(dict(self.inverted_index))
            
            # 保存倒排索引
            index_file = os.path.join(self.output_dir, "inverted_index.json")
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_dict, f, ensure_ascii=False)
            
            # 保存文档长度数组
            if self.doc_lengths is not None:
                doc_lengths_file = os.path.join(self.output_dir, "doc_lengths.npy")
                np.save(doc_lengths_file, self.doc_lengths)
            
            # 保存文档元数据（用于结果展示）
            doc_meta_file = os.path.join(self.output_dir, "document_metadata.csv")
            if self.processed_data is not None:
                # 确保包含doc_id列
                meta_columns = ['doc_id', 'title', 'source', 'publish_time']
                meta_columns = [col for col in meta_columns if col in self.processed_data.columns]
                
                # 添加内容预览列
                if 'content' in self.processed_data.columns:
                    # 创建一个内容预览列，提取前50个字符
                    self.processed_data['content_preview'] = self.processed_data['content'].apply(
                        lambda x: str(x)[:50] + '...' if isinstance(x, str) and len(str(x)) > 50 else str(x)[:50]
                    )
                    meta_columns.append('content_preview')
                
                # 保存文档元数据，使用doc_id作为索引
                if 'doc_id' in self.processed_data.columns:
                    # 使用doc_id作为索引列
                    doc_meta = self.processed_data[meta_columns].copy()
                    doc_meta.set_index('doc_id', inplace=True)
                    doc_meta.to_csv(doc_meta_file, encoding='utf-8')
                else:
                    # 如果没有doc_id列，则使用默认索引
                    self.processed_data[meta_columns].to_csv(doc_meta_file, index=True, encoding='utf-8')
            
            # 如果存在文档ID映射，保存它
            if self.doc_id_mapping is not None:
                doc_id_map_file = os.path.join(self.output_dir, "doc_id_mapping.json")
                with open(doc_id_map_file, 'w', encoding='utf-8') as f:
                    json.dump(convert_numpy_types(self.doc_id_mapping), f, ensure_ascii=False)
            
            # 保存元数据 (处理NumPy类型)
            meta_file = os.path.join(self.output_dir, "index_metadata.json")
            with open(meta_file, 'w', encoding='utf-8') as f:
                converted_metadata = convert_numpy_types(self.metadata)
                json.dump(converted_metadata, f, ensure_ascii=False, indent=2)
            
            # 保存词汇表（特征名称）
            vocab_file = os.path.join(self.output_dir, "vocabulary.txt")
            with open(vocab_file, 'w', encoding='utf-8') as f:
                for term in self.feature_names:
                    f.write(f"{term}\n")
            
            logger.info(f"倒排索引及相关数据保存完成，耗时: {time.time() - start_time:.2f}秒")
            logger.info(f"数据已保存到: {self.output_dir}")
            
            return True
        except Exception as e:
            logger.error(f"保存倒排索引失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def run_pipeline(self, optimize=True, min_tfidf=0.01):
        """
        运行完整的倒排索引构建流程
        
        参数:
            optimize (bool): 是否优化索引
            min_tfidf (float): 优化时使用的最小TF-IDF阈值
        """
        logger.info("开始倒排索引构建流程...")
        start_time = time.time()
        
        # 1. 加载预处理数据
        if not self.load_preprocessed_data():
            logger.error("加载预处理数据失败，流程终止")
            return False
        
        # 2. 计算文档向量长度
        self.compute_document_lengths()
        
        # 3. 构建倒排索引
        if not self.build_inverted_index():
            logger.error("构建倒排索引失败，流程终止")
            return False
        
        # 4. 优化索引（可选）
        if optimize:
            self.optimize_index(min_tfidf=min_tfidf)
        
        # 5. 保存索引
        if not self.save_inverted_index():
            logger.error("保存倒排索引失败")
            return False
        
        total_time = time.time() - start_time
        logger.info(f"倒排索引构建流程完成，总耗时: {total_time:.2f}秒")
        
        return True


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='构建倒排索引')
    parser.add_argument('--data_dir', type=str, required=True, help='预处理数据目录')
    parser.add_argument('--output_dir', type=str, help='输出目录(可选)')
    parser.add_argument('--optimize', action='store_true', help='是否优化索引')
    parser.add_argument('--min_tfidf', type=float, default=0.01, help='最小TF-IDF阈值')
    
    args = parser.parse_args()
    
    # 构建索引
    builder = InvertedIndexBuilder(
        preprocessed_data_dir=args.data_dir,
        output_dir=args.output_dir
    )
    
    result = builder.run_pipeline(
        optimize=args.optimize,
        min_tfidf=args.min_tfidf
    )
    
    return 0 if result else 1


if __name__ == "__main__":
    main()