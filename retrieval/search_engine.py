import os
import numpy as np
import pandas as pd
import logging
import time
import json
from collections import defaultdict
import heapq

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class SearchEngine:
    """
    基于倒排索引的搜索引擎
    """
    
    def __init__(self, index_dir):
        """
        初始化搜索引擎
        
        参数:
            index_dir (str): 倒排索引目录路径
        """
        self.index_dir = index_dir
        self.inverted_index = None
        self.doc_lengths = None
        self.document_metadata = None
        self.vocabulary = None
        self.metadata = None
        
    def load_index(self):
        """加载倒排索引及相关数据"""
        try:
            # 加载倒排索引
            index_file = os.path.join(self.index_dir, "inverted_index.json")
            with open(index_file, 'r', encoding='utf-8') as f:
                self.inverted_index = json.load(f)
            
            # 加载文档长度（可选）
            doc_lengths_file = os.path.join(self.index_dir, "doc_lengths.npy")
            if os.path.exists(doc_lengths_file):
                self.doc_lengths = np.load(doc_lengths_file)
            
            # 加载文档元数据（可选）
            doc_meta_file = os.path.join(self.index_dir, "document_metadata.csv")
            if os.path.exists(doc_meta_file):
                try:
                    self.document_metadata = pd.read_csv(doc_meta_file, encoding='utf-8', index_col=0)
                except Exception as e:
                    logger.warning(f"加载文档元数据失败: {e}，将使用简化结果展示")
            
            # 加载元数据（可选）
            meta_file = os.path.join(self.index_dir, "index_metadata.json")
            if os.path.exists(meta_file):
                with open(meta_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            
            # 加载词汇表（可选）
            vocab_file = os.path.join(self.index_dir, "vocabulary.txt")
            if os.path.exists(vocab_file):
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    self.vocabulary = [line.strip() for line in f.readlines()]
            
            logger.info(f"成功加载倒排索引，包含{len(self.inverted_index)}个词条")
            if self.metadata:
                logger.info(f"文档数量: {self.metadata.get('total_documents', '未知')}")
            
            return True
        except Exception as e:
            logger.error(f"加载倒排索引失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def search(self, query, top_k=10):
        """
        搜索查询
        
        参数:
            query (str): 查询字符串
            top_k (int): 返回的最大结果数
        
        返回:
            list: 搜索结果列表，每个结果是一个字典
        """
        if self.inverted_index is None:
            logger.error("倒排索引尚未加载，请先调用load_index()")
            return []
        
        start_time = time.time()
        logger.info(f"执行查询: '{query}'...")
        
        # 1. 查询预处理：分词
        try:
            import jieba
            words = jieba.cut(query)
            query_terms = [w for w in words if w.strip()]
        except ImportError:
            # 如果没有jieba，简单按空格分词
            query_terms = query.split()
        
        logger.info(f"查询分词结果: {', '.join(query_terms)}")
        
        # 2. 计算每个文档的得分
        doc_scores = defaultdict(float)
        matched_terms = []
        
        for term in query_terms:
            if term in self.inverted_index:
                matched_terms.append(term)
                
                # 为每个包含该词的文档增加得分
                for doc_id_str, weight in self.inverted_index[term]:
                    # 注意：JSON中的键都是字符串，需要转换为整数
                    doc_id = int(doc_id_str) if isinstance(doc_id_str, str) else doc_id_str
                    doc_scores[doc_id] += weight
        
        if not doc_scores:
            logger.info(f"未找到匹配的文档，查询耗时: {time.time() - start_time:.2f}秒")
            return []
        
        # 3. 使用最小堆找出得分最高的top_k个文档
        top_docs = []
        for doc_id, score in doc_scores.items():
            if len(top_docs) < top_k:
                heapq.heappush(top_docs, (score, doc_id))
            else:
                if score > top_docs[0][0]:
                    heapq.heappushpop(top_docs, (score, doc_id))
        
        # 4. 按得分降序排列结果
        results = []
        for score, doc_id in sorted(top_docs, reverse=True):
            result = {
                'doc_id': doc_id,
                'score': score,
                'matched_terms': matched_terms
            }
            
            # 添加文档元数据
            if self.document_metadata is not None:
                try:
                    if doc_id < len(self.document_metadata):
                        if 'title' in self.document_metadata.columns:
                            result['title'] = self.document_metadata.iloc[doc_id]['title']
                        if 'source' in self.document_metadata.columns:
                            result['source'] = self.document_metadata.iloc[doc_id]['source']
                        if 'publish_time' in self.document_metadata.columns:
                            result['publish_time'] = self.document_metadata.iloc[doc_id]['publish_time']
                except Exception as e:
                    logger.warning(f"获取文档{doc_id}元数据失败: {e}")
            
            results.append(result)
        
        logger.info(f"找到{len(doc_scores)}个匹配文档，返回得分最高的{len(results)}个")
        logger.info(f"匹配的查询词: {', '.join(matched_terms)}")
        logger.info(f"搜索耗时: {time.time() - start_time:.2f}秒")
        
        return results
    
    def get_term_stats(self):
        """获取索引词汇的统计信息"""
        if not self.inverted_index:
            return None
        
        # 计算每个词的文档频率
        term_stats = []
        for term, postings in self.inverted_index.items():
            doc_freq = len(postings)  # 包含该词的文档数
            max_weight = max(weight for _, weight in postings)  # 最大TF-IDF权重
            avg_weight = sum(weight for _, weight in postings) / doc_freq  # 平均TF-IDF权重
            
            term_stats.append({
                'term': term,
                'document_frequency': doc_freq,
                'max_tfidf': max_weight,
                'avg_tfidf': avg_weight
            })
        
        # 按文档频率降序排序
        term_stats.sort(key=lambda x: x['document_frequency'], reverse=True)
        
        return term_stats
    
    def interactive_search(self):
        """交互式搜索界面"""
        print("\n======= 倒排索引搜索引擎 =======")
        print("输入'quit'或'exit'退出")
        
        while True:
            query = input("\n请输入搜索词: ").strip()
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            # 执行搜索
            top_k = 10
            results = self.search(query, top_k=top_k)
            
            # 显示搜索结果
            print(f"\n找到 {len(results)} 个匹配文档:")
            
            if results:
                for i, result in enumerate(results):
                    doc_id = result['doc_id']
                    title = result.get('title', '文档'+str(doc_id))
                    print(f"{i+1}. [{result['score']:.4f}] {title}")
                    print(f"   来源: {result.get('source', '未知')}")
                    if 'publish_time' in result:
                        print(f"   发布时间: {result['publish_time']}")
                    print(f"   匹配词: {', '.join(result.get('matched_terms', []))}")
                    print("-" * 60)
            else:
                print("未找到匹配的文档，请尝试其他关键词。")
                
            # 询问是否需要查看文档详情
            if results:
                detail_choice = input("\n输入文档编号查看详情，或按Enter继续: ").strip()
                if detail_choice.isdigit() and 1 <= int(detail_choice) <= len(results):
                    doc_id = results[int(detail_choice)-1]['doc_id']
                    self.show_document_detail(doc_id)
    
    def show_document_detail(self, doc_id):
        """显示文档详细信息"""
        if self.document_metadata is None:
            print(f"无法获取文档{doc_id}的详细信息，元数据不可用")
            return
            
        try:    
            if doc_id >= len(self.document_metadata):
                print(f"无法获取文档{doc_id}的详细信息，文档ID超出范围")
                return
            
            doc = self.document_metadata.iloc[doc_id]
            print("\n" + "="*60)
            print(f"文档详情 (ID: {doc_id})")
            print("="*60)
            
            # 显示文档元数据
            for col in self.document_metadata.columns:
                print(f"{col}: {doc[col]}")
            
            print("="*60)
        except Exception as e:
            print(f"获取文档详情时发生错误: {e}")
        
        input("\n按Enter返回搜索...")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='搜索倒排索引')
    parser.add_argument('--index_dir', type=str, required=True, help='倒排索引目录')
    parser.add_argument('--query', type=str, help='搜索查询')
    parser.add_argument('--top_k', type=int, default=10, help='返回结果数量')
    parser.add_argument('--interactive', action='store_true', help='启动交互式搜索界面')
    
    args = parser.parse_args()
    
    # 创建搜索引擎
    search_engine = SearchEngine(args.index_dir)
    
    # 加载索引
    if not search_engine.load_index():
        logger.error("加载索引失败，程序退出")
        return 1
    
    # 执行搜索
    if args.interactive:
        search_engine.interactive_search()
    elif args.query:
        results = search_engine.search(args.query, top_k=args.top_k)
        print(f"\n搜索: '{args.query}'")
        if results:
            for i, result in enumerate(results):
                doc_id = result['doc_id']
                title = result.get('title', '文档'+str(doc_id))
                print(f"{i+1}. [{result['score']:.4f}] {title}")
                print(f"   来源: {result.get('source', '未知')}")
                if 'publish_time' in result:
                    print(f"   发布时间: {result['publish_time']}")
                print(f"   匹配词: {', '.join(result.get('matched_terms', []))}")
                print("-" * 50)
        else:
            print("未找到匹配的文档。")
    else:
        # 如果没有提供查询参数，进入交互式模式
        search_engine.interactive_search()
    
    return 0


if __name__ == "__main__":
    main()