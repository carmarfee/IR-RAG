import sqlite3
import re
import jieba
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ChineseDocumentPreprocessor:
    def __init__(self, db_path, stopwords_path):
        """
        初始化预处理器
        
        参数:
            db_path (str): SQLite数据库路径
            stopwords_path (str): 停用词表路径
        """
        self.db_path = db_path
        self.stopwords_path = stopwords_path
        self.stopwords = self._load_stopwords()
        self.processed_data = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.output_dir = "../data/preprocessed_data"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _load_stopwords(self):
        """加载停用词表"""
        try:
            with open(self.stopwords_path, 'r', encoding='utf-8') as f:
                stopwords = set([line.strip() for line in f.readlines()])
            logger.info(f"成功加载停用词表，共{len(stopwords)}个停用词")
            return stopwords
        except Exception as e:
            logger.error(f"加载停用词表失败: {e}")
            return set()
    
    def load_data(self):
        """从SQLite数据库加载文档数据，包括文档ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            # 修改查询，添加id字段
            query = "SELECT id, title, content, publish_time, source FROM pages"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            # 将id列重命名为doc_id，以便更清晰地表示它是文档的ID
            df.rename(columns={'id': 'doc_id'}, inplace=True)
            
            logger.info(f"成功从数据库加载数据，共{len(df)}条记录")
            return df
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return pd.DataFrame()
    
    def clean_text(self, text):
        """
        清洗文本数据
        
        参数:
            text (str): 原始文本
            
        返回:
            str: 清洗后的文本
        """
        if not isinstance(text, str) or pd.isna(text):
            return ""
        
        # 1. 去除HTML标签
        text = re.sub(r'<.*?>', '', text)
        
        # 2. 去除URL
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # 3. 去除特殊字符和标点符号（保留中文标点）
        text = re.sub(r'[^\u4e00-\u9fa5\u3000-\u303f\uff00-\uffef\s]', '', text)
        
        # 4. 去除多余空白字符
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 5. 去除空行
        text = re.sub(r'\n+', '\n', text).strip()
        
        return text
    
    def segment_text(self, text):
        """
        对文本进行分词并去除停用词
        
        参数:
            text (str): 清洗后的文本
            
        返回:
            str: 分词后的文本，词语间用空格分隔
        """
        if not isinstance(text, str) or pd.isna(text) or text == "":
            return ""
        
        # 使用jieba分词
        words = jieba.cut(text)
        
        # 去除停用词
        filtered_words = [word for word in words if word.strip() and word not in self.stopwords]
        
        return ' '.join(filtered_words)
    
    def remove_duplicates(self, df):
        """
        移除内容重复的文档，只保留一个副本
        
        参数:
            df (DataFrame): 包含文档数据的DataFrame
            
        返回:
            DataFrame: 去重后的DataFrame
        """
        initial_count = len(df)
        
        # 对文档内容进行去重，保留第一次出现的记录
        df_no_duplicates = df.drop_duplicates(subset=['clean_content'], keep='first')
        
        duplicate_count = initial_count - len(df_no_duplicates)
        logger.info(f"移除了{duplicate_count}个重复内容的文档，剩余{len(df_no_duplicates)}个文档")
        
        return df_no_duplicates
    
    def process_data(self):
        """处理数据：清洗、分词和去重"""
        df = self.load_data()
        if df.empty:
            logger.error("没有数据可处理")
            return
        
        # 创建处理后的数据副本
        processed_df = df.copy()
        
        # 清洗标题和内容
        logger.info("开始清洗文本...")
        processed_df['clean_title'] = processed_df['title'].apply(self.clean_text)
        processed_df['clean_content'] = processed_df['content'].apply(self.clean_text)
        
        # 去除重复内容的文档
        logger.info("开始去除重复内容的文档...")
        processed_df = self.remove_duplicates(processed_df)
        
        # 分词
        logger.info("开始分词...")
        processed_df['segmented_title'] = processed_df['clean_title'].apply(self.segment_text)
        processed_df['segmented_content'] = processed_df['clean_content'].apply(self.segment_text)
        
        # 合并标题和内容用于向量化
        processed_df['combined_text'] = processed_df['segmented_title'] + ' ' + processed_df['segmented_content']
        
        self.processed_data = processed_df
        logger.info("数据预处理完成")
        
        # 保存处理后的数据
        processed_df.to_csv(f"{self.output_dir}/processed_documents.csv", index=False, encoding='utf-8')
        logger.info(f"已保存处理后的数据至 {self.output_dir}/processed_documents.csv")
        
        return processed_df
    
    def vectorize_documents(self, min_df=2, max_df=0.95):
        """
        使用TF-IDF对文档进行向量化
        
        参数:
            min_df: 词语最小文档频率
            max_df: 词语最大文档频率
        """
        if self.processed_data is None or len(self.processed_data) == 0:
            logger.error("没有处理过的数据可用于向量化")
            return
        
        logger.info("开始TF-IDF向量化...")
        
        # 初始化TF-IDF向量化器
        self.tfidf_vectorizer = TfidfVectorizer(
            min_df=min_df,  # 词语至少出现在min_df个文档中
            max_df=max_df,  # 词语最多出现在max_df比例的文档中
            use_idf=True,   # 使用IDF
            norm='l2',      # 使用L2正则化
            smooth_idf=True # 平滑IDF权重
        )
        
        # 对文档进行向量化
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.processed_data['combined_text'])
        
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        logger.info(f"向量化完成，特征词汇量: {len(feature_names)}")
        
        # 保存向量化结果
        with open(f"{self.output_dir}/tfidf_vectorizer.pkl", 'wb') as f:
            pickle.dump(self.tfidf_vectorizer, f)
        
        with open(f"{self.output_dir}/tfidf_matrix.pkl", 'wb') as f:
            pickle.dump(self.tfidf_matrix, f)
        
        # 保存文档ID与TF-IDF矩阵行索引的映射关系
        doc_ids = self.processed_data['doc_id'].tolist()
        with open(f"{self.output_dir}/doc_id_mapping.pkl", 'wb') as f:
            pickle.dump(doc_ids, f)
        
        logger.info(f"已保存TF-IDF向量化结果及文档ID映射至 {self.output_dir}/")
        
        # 生成并保存特征词汇表
        vocab_df = pd.DataFrame({
            'word': feature_names,
            'idf': self.tfidf_vectorizer.idf_
        }).sort_values('idf', ascending=False)
        
        vocab_df.to_csv(f"{self.output_dir}/feature_vocabulary.csv", index=False, encoding='utf-8')
        logger.info(f"已保存特征词汇表至 {self.output_dir}/feature_vocabulary.csv")
        
        return self.tfidf_matrix, self.tfidf_vectorizer
    
    def generate_document_vectors_sample(self, sample_size=5):
        """
        生成并展示文档向量样例
        
        参数:
            sample_size: 样例文档数量
        """
        if self.tfidf_matrix is None or self.tfidf_vectorizer is None:
            logger.error("尚未完成向量化，无法生成文档向量样例")
            return
        
        # 获取样本文档
        sample_indices = np.random.choice(len(self.processed_data), min(sample_size, len(self.processed_data)), replace=False)
        sample_docs = self.processed_data.iloc[sample_indices]
        sample_vectors = self.tfidf_matrix[sample_indices]
        
        # 获取特征名称
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # 生成每个样本文档的前10个高权重词语
        logger.info("\n文档向量样例 (前10个高权重词语):")
        
        results = []
        for i, (idx, doc) in enumerate(zip(sample_indices, sample_docs.itertuples())):
            # 获取非零元素的索引和值
            nonzero_indices = sample_vectors[i].nonzero()[1]
            weights = sample_vectors[i].data
            
            # 按权重排序
            sorted_indices = nonzero_indices[np.argsort(weights)[::-1]]
            sorted_weights = np.sort(weights)[::-1]
            
            # 获取前10个高权重词语
            top_words = [(feature_names[idx], weight) for idx, weight in zip(sorted_indices[:10], sorted_weights[:10])]
            
            result = {
                'document_id': doc.doc_id,  # 使用原始doc_id而不是DataFrame索引
                'title': doc.title,
                'source': doc.source,
                'top_words': top_words
            }
            results.append(result)
            
            # 打印结果
            logger.info(f"文档 {doc.doc_id} - {doc.title} (来源: {doc.source})")
            for word, weight in top_words:
                logger.info(f"  {word}: {weight:.4f}")
            logger.info("-" * 50)
        
        # 保存样例结果
        with open(f"{self.output_dir}/document_vectors_sample.txt", 'w', encoding='utf-8') as f:
            for result in results:
                f.write(f"文档 {result['document_id']} - {result['title']} ({result['source']})\n")
                for word, weight in result['top_words']:
                    f.write(f"  {word}: {weight:.4f}\n")
                f.write("-" * 50 + "\n")
        
        logger.info(f"已保存文档向量样例至 {self.output_dir}/document_vectors_sample.txt")
    
    def run_full_pipeline(self):
        """运行完整的预处理流程"""
        logger.info("开始运行文档预处理流程...")
        start_time = datetime.now()
        
        # 1. 数据清洗和分词
        self.process_data()
        
        # 2. TF-IDF向量化
        self.vectorize_documents()
        
        # 3. 生成文档向量样例
        self.generate_document_vectors_sample()
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"预处理流程完成，总耗时: {processing_time:.2f}秒")
        
        # 生成处理报告
        self.generate_report(processing_time)
    
    def generate_report(self, processing_time):
        """生成预处理报告"""
        if self.processed_data is None:
            logger.error("没有处理数据，无法生成报告")
            return
        
        report = {
            "总文档数": len(self.processed_data),
            "处理耗时(秒)": processing_time,
            "特征词汇量": len(self.tfidf_vectorizer.get_feature_names_out()) if self.tfidf_vectorizer else 0,
            "TF-IDF矩阵维度": self.tfidf_matrix.shape if self.tfidf_matrix is not None else (0, 0),
            "TF-IDF矩阵稀疏度": (1.0 - self.tfidf_matrix.nnz / (self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1])) if self.tfidf_matrix is not None else 0,
            "文档来源统计": self.processed_data['source'].value_counts().to_dict(),
            "标题平均长度(字符)": self.processed_data['clean_title'].str.len().mean(),
            "内容平均长度(字符)": self.processed_data['clean_content'].str.len().mean(),
            "标题平均分词数": self.processed_data['segmented_title'].str.split().str.len().mean(),
            "内容平均分词数": self.processed_data['segmented_content'].str.split().str.len().mean()
        }
        
        # 保存报告
        with open(f"{self.output_dir}/preprocessing_report.txt", 'w', encoding='utf-8') as f:
            f.write("中文文档预处理报告\n")
            f.write("=" * 50 + "\n\n")
            
            for key, value in report.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for k, v in value.items():
                        f.write(f"  {k}: {v}\n")
                else:
                    f.write(f"{key}: {value}\n")
            
            # 添加去重信息到报告
            f.write("\n去重信息:\n")
            try:
                original_count = self.load_data().shape[0]
                duplicates_removed = original_count - len(self.processed_data)
                duplicate_percentage = (duplicates_removed / original_count) * 100 if original_count > 0 else 0
                f.write(f"  原始文档数: {original_count}\n")
                f.write(f"  移除重复文档数: {duplicates_removed}\n")
                f.write(f"  重复率: {duplicate_percentage:.2f}%\n")
            except Exception as e:
                f.write(f"  无法计算去重信息: {e}\n")
            
            # 添加时间戳
            f.write(f"\n报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        logger.info(f"已生成预处理报告至 {self.output_dir}/preprocessing_report.txt")


if __name__ == "__main__":
    # 设置路径
    db_path = "../data/raw_data/crawler_data.db"
    stopwords_path = "../cn_stopwords.txt"
    
    # 创建预处理器并运行
    processor = ChineseDocumentPreprocessor(db_path, stopwords_path)
    processor.run_full_pipeline()