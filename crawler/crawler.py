import json
import os
import re
import time
import requests
import sqlite3
import hashlib
import logging
import random
import threading
import chardet
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor
import networkx as nx


class DatabaseManager:
    """数据库管理类，负责所有数据库操作，线程安全"""
    
    _local = threading.local()  # 线程本地存储
    
    def __init__(self, db_path):
        """初始化数据库管理器"""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库结构"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA journal_mode=WAL')  # 使用WAL模式提高性能
        conn.execute('PRAGMA synchronous=NORMAL')  # 降低同步级别提高性能
        
        cursor = conn.cursor()
        
        # 创建页面表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            content TEXT,
            html_content TEXT,
            content_hash TEXT,
            publish_time TEXT,
            source TEXT,
            crawl_time TEXT,
            encoding TEXT,
            pagerank REAL DEFAULT 0
        )
        ''')
        
        # 创建链接表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_url TEXT,
            to_url TEXT,
            anchor_text TEXT,
            crawl_time TEXT,
            UNIQUE(from_url, to_url)
        )
        ''')
        
        # 创建下载链接表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            filename TEXT,
            title TEXT,
            file_type TEXT,
            crawl_time TEXT
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_from ON links(from_url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_links_to ON links(to_url)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_downloads_url ON downloads(url)')
        
        conn.commit()
        conn.close()
    
    def get_conn(self):
        """获取当前线程的数据库连接"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.execute('PRAGMA journal_mode=WAL')
            self._local.conn.execute('PRAGMA synchronous=NORMAL')
            self._local.conn.text_factory = str
        return self._local.conn
    
    def execute(self, sql, params=None):
        """执行SQL语句"""
        conn = self.get_conn()
        cursor = conn.cursor()
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        conn.commit()
        return cursor
    
    def execute_many(self, sql, params_list):
        """执行批量SQL语句"""
        conn = self.get_conn()
        cursor = conn.cursor()
        cursor.executemany(sql, params_list)
        conn.commit()
        return cursor
    
    def close_all(self):
        """关闭所有线程的连接"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn
    
    def save_page(self, page_info):
        """保存页面信息到数据库"""
        try:
            # 计算内容哈希值
            content_hash = hashlib.md5(page_info['html_content'].encode('utf-8')).hexdigest()
            
            return self.execute('''
            INSERT OR REPLACE INTO pages 
            (url, title, content, html_content, content_hash, encoding, publish_time, source, crawl_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                page_info['url'], 
                page_info['title'], 
                page_info['content'], 
                page_info['html_content'], 
                content_hash,
                page_info['encoding'],
                page_info.get('publish_time', ''),
                page_info.get('source', ''),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        except Exception as e:
            logging.error(f"数据库保存页面错误: {e}")
            return None
    
    def save_link(self, from_url, to_url, anchor_text):
        """保存链接关系到数据库"""
        try:
            return self.execute('''
            INSERT OR IGNORE INTO links (from_url, to_url, anchor_text, crawl_time)
            VALUES (?, ?, ?, ?)
            ''', (from_url, to_url, anchor_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except Exception as e:
            logging.error(f"数据库保存链接错误: {e}")
            return None
    
    def save_download(self, download_info):
        """保存下载链接信息到数据库"""
        try:
            cursor = self.execute('''
            INSERT OR IGNORE INTO downloads 
            (url, filename, title, file_type, crawl_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                download_info['url'],
                download_info['filename'],
                download_info['title'],
                download_info['file_type'],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            return cursor.lastrowid
        except Exception as e:
            logging.error(f"数据库保存下载链接错误: {e}")
            return None
    
    def update_pagerank(self, url, score):
        """更新页面的PageRank值"""
        try:
            self.execute('UPDATE pages SET pagerank = ? WHERE url = ?', (score, url))
            return True
        except Exception as e:
            logging.error(f"更新PageRank错误 {url}: {e}")
            return False


class PageRankCalculator:
    """PageRank计算类"""
    
    def __init__(self, damping_factor=0.85):
        """初始化PageRank计算器"""
        self.graph = nx.DiGraph()
        self.damping_factor = damping_factor
    
    def add_link(self, from_url, to_url):
        """添加链接到图中"""
        self.graph.add_edge(from_url, to_url)
    
    def calculate(self, max_iterations=100, min_delta=1e-5):
        """计算PageRank值"""
        return nx.pagerank(
            self.graph, 
            alpha=self.damping_factor, 
            max_iter=max_iterations, 
            tol=min_delta
        )
    
    def get_top_pages(self, pagerank_scores, n=10):
        """获取PageRank值最高的n个页面"""
        return sorted(pagerank_scores.items(), key=lambda x: x[1], reverse=True)[:n]


class ContentExtractor:
    """内容提取类"""
    
    def __init__(self, selectors=None):
        """初始化内容提取器"""
        print("初始化内容提取器", selectors)
        self.selectors = selectors or {
            'title_selectors': [],
            'content_selectors': [],
            'time_selectors': [],
            'source_selectors': [],
            'remove_selectors': []
        }
    
    def extract_from_soup(self, soup, url):
        """从BeautifulSoup对象中提取内容"""
        # 移除不需要的元素
        if self.selectors.get('remove_selectors'):
            for selector in self.selectors['remove_selectors']:
                for element in soup.select(selector):
                    element.decompose()

        # 提取标题
        title = "无标题"
        if self.selectors.get('title_selectors'):
            for selector in self.selectors['title_selectors']:
                title_element = soup.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    break
        
        # 如果没有找到标题，使用<title>标签
        if title == "无标题" and soup.title:
            title = soup.title.get_text(strip=True)

        # 提取内容
        content = ""
        if self.selectors.get('content_selectors'):
            for selector in self.selectors['content_selectors']:
                content_element = soup.select_one(selector)
                if content_element:
                    content = content_element.get_text('\n', strip=True)
                    break
        
        # 如果没有找到内容，使用备用方法提取
        # if not content:
        #     content = self._extract_content_fallback(soup)

        # 提取发布时间
        publish_time = ""
        if self.selectors.get('time_selectors'):
            for selector in self.selectors['time_selectors']:
                time_element = soup.select_one(selector)
                if time_element:
                    publish_time = time_element.get_text(strip=True)
                    break
        
        # 提取来源
        source = ""
        if self.selectors.get('source_selectors'):
            for selector in self.selectors['source_selectors']:
                source_element = soup.select_one(selector)
                if source_element:
                    source = source_element.get_text(strip=True)
                    break
        
        # 清理内容
        content = re.sub(r'\s+', ' ', content).strip()
        
        return {
            'title': title,
            'content': content,
            'publish_time': publish_time,
            'source': source
        }
    
    def _extract_content_fallback(self, soup):
        """备用的内容提取方法"""
        content = ""
        for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
            if element.parent.name not in ['script', 'style']:
                text = element.get_text(strip=True)
                if text:
                    content += text + "\n"
        return content
    
    def extract_links(self, soup, url, base_url=None, exclude_patterns=None, download_types=None):
        """从页面中提取链接"""
        links = []
        downloads = []
        exclude_patterns = exclude_patterns or []
        download_types = download_types or []
        
        # 使用集合去重
        seen_urls = set()
        
        for a_tag in soup.find_all('a', href=True):
            try:
                href = a_tag.get('href', '')
                
                # 跳过空链接和锚点
                if not href or href == '#':
                    continue
                
                # 处理相对URL
                full_url = self._normalize_url(href, url, base_url, exclude_patterns)
                if not full_url or full_url in seen_urls:
                    continue
                
                seen_urls.add(full_url)
                
                # 获取锚文本
                anchor_text = a_tag.get_text(strip=True) or "无文本"
                
                # 检查是否是下载链接
                file_ext = os.path.splitext(full_url)[1].lower().lstrip('.')
                if file_ext in download_types:
                    # 处理下载链接
                    downloads.append({
                        'url': full_url,
                        'title': anchor_text,
                        'filename': os.path.basename(full_url),
                        'file_type': file_ext
                    })
                else:
                    # 普通链接
                    links.append({
                        'url': full_url, 
                        'anchor_text': anchor_text
                    })
            except Exception as e:
                logging.error(f"提取链接错误: {e}")
                continue
        
        return links, downloads
    
    def _normalize_url(self, href, current_url, base_url=None, exclude_patterns=None):
        """处理并规范化URL"""
        exclude_patterns = exclude_patterns or []
        
        # 处理相对URL
        if not href.startswith(('http://', 'https://')):
            href = urljoin(current_url, href)
        
        # 基本过滤
        if '#' in href:
            href = href.split('#')[0]
        
        # 过滤排除模式
        for pattern in exclude_patterns:
            if pattern in href:
                return None
        
        if len(href) < 2:
            return None
        
        # 域名过滤
        if base_url:
            base_domain = urlparse(base_url).netloc
            url_domain = urlparse(href).netloc
            if not url_domain.endswith(base_domain) and not base_domain.endswith(url_domain):
                return None
        
        return href


class EncodingHandler:
    """编码处理类"""
    
    def __init__(self, settings=None, domain_specific_encodings=None):
        """初始化编码处理器"""
        self.settings = settings or {
            'default_encoding': 'utf-8',
            'fallback_encodings': ['gb18030', 'gbk', 'gb2312', 'big5'],
            'detect_encoding': True,
            'force_encoding': None,
            'store_encoding': 'utf-8',
            'use_meta_charset': True
        }
        self.domain_specific_encodings = domain_specific_encodings or {}
        self.domain_encoding_cache = {}
    
    def detect_encoding(self, response):
        """检测网页编码"""
        # 强制编码
        if self.settings.get('force_encoding'):
            return self.settings['force_encoding']
        
        # 从HTTP头获取编码
        content_type = response.headers.get('Content-Type', '').lower()
        if 'charset=' in content_type:
            charset = content_type.split('charset=')[-1].strip().split(';')[0]
            return self._normalize_encoding(charset)
        
        # 从meta标签获取编码
        if self.settings.get('use_meta_charset', True):
            try:
                meta_match = re.search(r'<meta[^>]*charset=["\']?([^"\'>]+)', 
                                      response.content.decode('ascii', errors='ignore'), 
                                      re.IGNORECASE)
                if meta_match:
                    return self._normalize_encoding(meta_match.group(1))
                
                content_type_match = re.search(
                    r'<meta[^>]*http-equiv=["\']?content-type["\']?[^>]*content=["\']?[^;]+;\s*charset=([^"\'>]+)', 
                    response.content.decode('ascii', errors='ignore'), 
                    re.IGNORECASE
                )
                if content_type_match:
                    return self._normalize_encoding(content_type_match.group(1))
            except Exception:
                pass
        
        # 使用chardet检测
        if self.settings.get('detect_encoding', True):
            # 先分析一部分提高速度
            detection = chardet.detect(response.content[:4096])
            if detection['confidence'] > 0.7:
                return self._normalize_encoding(detection['encoding'])
            
            # 全文分析
            detection = chardet.detect(response.content)
            if detection['confidence'] > 0.5:
                return self._normalize_encoding(detection['encoding'])
        
        # 使用requests的apparent_encoding
        return self._normalize_encoding(response.apparent_encoding)
    
    def get_domain_encoding(self, url):
        """获取域名的编码设置"""
        domain = urlparse(url).netloc
        
        # 检查缓存
        if domain in self.domain_encoding_cache:
            return self.domain_encoding_cache[domain]
        
        # 检查是否有特定网站编码设置
        for site, encoding in self.domain_specific_encodings.items():
            if domain.endswith(site):
                self.domain_encoding_cache[domain] = encoding
                return encoding
        
        # 返回默认编码
        default_encoding = self.settings.get('default_encoding', 'utf-8')
        self.domain_encoding_cache[domain] = default_encoding
        return default_encoding
    
    def _normalize_encoding(self, encoding):
        """规范化编码名称"""
        if not encoding:
            return self.settings.get('default_encoding', 'utf-8')
        
        encoding = encoding.lower().replace('-', '').replace('_', '')
        
        # 编码映射表
        encoding_map = {
            'gb2312': 'gb18030',  # gb18030 是 gb2312 的超集
            'gbk': 'gb18030',     # gb18030 是 gbk 的超集
            'chinese': 'gb18030',
            'csgb2312': 'gb18030',
            'csgb231280': 'gb18030',
            'gb_2312': 'gb18030',
            'gb_2312_80': 'gb18030',
            'iso88591': 'iso-8859-1',
            'latin1': 'iso-8859-1',
            'cp1252': 'windows-1252',
            'windows1252': 'windows-1252',
            'utf8': 'utf-8',
            'utf16': 'utf-16',
            'utf16le': 'utf-16-le',
            'utf16be': 'utf-16-be',
            'unicodelittle': 'utf-16-le',
            'unicodebig': 'utf-16-be',
            'eucjp': 'euc-jp',
            'shiftjis': 'shift_jis',
            'sjis': 'shift_jis',
            'euckr': 'euc-kr',
            'big5hkscs': 'big5',
        }
        
        return encoding_map.get(encoding, encoding)
    
    def has_encoding_issues(self, text, sample_size=1000, threshold=0.1):
        """检测文本是否可能包含乱码"""
        if not text:
            return False
        
        # 获取文本样本
        sample = text[:sample_size]
        
        # 检查非ASCII字符比例
        non_ascii_count = sum(1 for c in sample if ord(c) > 127)
        non_ascii_ratio = non_ascii_count / len(sample) if sample else 0
        
        # 检查常见乱码特征字符
        messy_chars = ['�', '□', '■', '▯', '▒', '◯', '○', '⃝']
        messy_count = sum(sample.count(c) for c in messy_chars)
        messy_ratio = messy_count / len(sample) if sample else 0
        
        # 拉丁字符与中日韩字符混合的情况下，检测乱码特征
        has_cjk = any(0x4E00 <= ord(c) <= 0x9FFF for c in sample)  # 中文字符范围
        has_latin = any(0x0041 <= ord(c) <= 0x007A for c in sample)  # 英文字母范围
        
        if has_cjk and has_latin:
            cjk_count = sum(1 for c in sample if 0x4E00 <= ord(c) <= 0x9FFF)
            if cjk_count < 10 and non_ascii_ratio > 0:
                return True
        
        # 返回是否可能有乱码
        return (messy_ratio > threshold) or (non_ascii_ratio > 0.5 and messy_count > 0)


class WebCrawler:
    """网络爬虫主类"""
    
    def __init__(self,config_file=None, output_dir=None,start_urls=None, base_url=None, max_pages=100, iterations=10, timeout=10):
        """初始化爬虫"""
        
        # 基本配置
        self.output_dir = output_dir
        self.base_url = base_url
        self.max_pages = max_pages
        self.iterations = iterations
        self.timeout = timeout
        self.urls_taken = set()
        self.page_count = 0
        
        # 设置日志
        self._setup_logging()
        
        # 下载文件类型
        self.download_types = ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "zip", "rar"]
        
        # 排除模式
        self.exclude_patterns = ['/login', '/logout', '/search', 'javascript:', 'mailto:']
        
        # HTTP请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # 用户代理列表
        self.user_agent_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
        ]
        
        # 爬虫设置
        self.crawl_settings = {
            'delay_between_requests': 2.0,
            'max_concurrent_requests': 5,
            'follow_redirects': True,
            'max_depth': 8,
            'random_delay': True,
            'delay_variance': 0.5
        }
        
        # 初始化起始URL
        self.start_urls = start_urls
        
        # 初始化数据库
        self.db_path = os.path.join(self.output_dir, 'crawler_data.db')
        self.db = DatabaseManager(self.db_path)
        
        # 初始化PageRank计算器
        self.pagerank = PageRankCalculator()
        
        # 初始化内容提取器
        self.content_extractor = ContentExtractor()
        
        # 初始化编码处理器
        self.encoding_handler = EncodingHandler()
        
        # 加载配置文件
        self.load_config(config_file)
    
    def _setup_logging(self):
        """配置日志"""
        log_filename = os.path.join(self.output_dir, "crawler.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_filename, mode="w", encoding="utf-8")
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_file):
        """从配置文件加载起始URL和其他配置"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 基本配置
                self.start_urls = config.get('start_urls', [])
                self.base_url = config.get('base_url', self.base_url)
                self.max_pages = config.get('max_pages', self.max_pages)
                self.iterations = config.get('iterations', self.iterations)
                self.timeout = config.get('timeout', self.timeout)
                
                # 编码设置
                if 'encoding_settings' in config:
                    self.encoding_handler = EncodingHandler(
                        config.get('encoding_settings'),
                        config.get('domain_specific_encodings', {})
                    )
                
                # 请求头配置
                if 'headers' in config:
                    self.headers = config.get('headers', {})
                
                # 排除模式
                if 'exclude_patterns' in config:
                    self.exclude_patterns = config.get('exclude_patterns', self.exclude_patterns)
                
                # 下载类型
                if 'download_types' in config:
                    self.download_types = config.get('download_types', self.download_types)
                
                # 内容选择器
                if 'content_extraction' in config:
                    self.content_extractor = ContentExtractor(config.get('content_extraction'))
                
                # 爬虫设置
                if 'crawl_settings' in config:
                    self.crawl_settings = config.get('crawl_settings', self.crawl_settings)
                
                # 用户代理设置
                if 'user_agent_list' in config:
                    self.user_agent_list = config.get('user_agent_list', self.user_agent_list)
            
            self.logger.info(f"已加载配置文件: {config_file}")
            self.logger.info(f"起始URL: {self.start_urls}")
            
        except Exception as e:
            self.logger.error(f"加载配置文件错误: {e}")
            raise
    
    def get_html(self, url):
        """获取页面HTML内容"""
        self.logger.info(f"正在获取: {url}")
        
        # 随机选择用户代理
        if self.user_agent_list:
            self.headers['User-Agent'] = random.choice(self.user_agent_list)
        
        try:
            # 请求页面
            response = requests.get(
                url, 
                timeout=self.timeout, 
                headers=self.headers, 
                allow_redirects=self.crawl_settings.get('follow_redirects', True)
            )
            
            if response.status_code != 200:
                self.logger.warning(f"获取页面失败 {url}, 状态码: {response.status_code}")
                return None, None
            
            # 检测编码
            encoding = self.encoding_handler.detect_encoding(response)
            
            # 设置响应编码并获取内容
            response.encoding = encoding
            html_content = response.text
            
            # 验证内容
            if not html_content or len(html_content.strip()) < 10:
                self.logger.warning(f"页面内容为空或过短: {url}")
                return None, None
            
            # 检查内容是否有乱码
            if self.encoding_handler.has_encoding_issues(html_content):
                self.logger.warning(f"页面内容可能存在编码问题，尝试备用方法: {url}")
                # 尝试直接用chardet全面分析
                detection = chardet.detect(response.content)
                if detection['encoding'] and detection['confidence'] > 0.6:
                    fallback_encoding = self.encoding_handler._normalize_encoding(detection['encoding'])
                    try:
                        html_content = response.content.decode(fallback_encoding, errors='replace')
                        encoding = fallback_encoding
                    except Exception as e:
                        self.logger.warning(f"备用编码解码失败: {e}")
            
            return html_content, encoding
            
        except requests.RequestException as e:
            self.logger.error(f"请求错误 {url}: {e}")
            return None, None
        except Exception as e:
            self.logger.error(f"未预期错误 {url}: {e}")
            return None, None
    
    def process_page(self, url):
        """处理单个页面"""
        # 检查URL是否已处理
        if url in self.urls_taken:
            return []
        
        # 标记为已处理
        self.urls_taken.add(url)
        
        # 获取页面内容
        result = self.get_html(url)
        if not result or not result[0]:
            return []
        
        html_content, encoding = result
        
        # 解析页面
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取内容
        extracted_content = self.content_extractor.extract_from_soup(soup, url)
        
        # 提取链接和下载链接
        links, downloads = self.content_extractor.extract_links(
            soup, url, self.base_url, self.exclude_patterns, self.download_types
        )
        
        # 检查内容和标题是否为空
        if (not extracted_content['content'] or not extracted_content['title'] or 
            extracted_content['title'] == "无标题"):
            self.logger.warning(f"页面内容或标题为空，跳过保存: {url} - {extracted_content['title']}")
        # 检查是否是错误页面
        elif '404' not in extracted_content['title'] and '301' not in extracted_content['title'] and '302' not in extracted_content['title']:
            # 创建页面信息对象
            page_info = {
                "url": url,
                "title": extracted_content['title'],
                "content": extracted_content['content'],
                "html_content": html_content,
                "encoding": encoding,
                "publish_time": extracted_content['publish_time'],
                "source": extracted_content['source']
            }
            
            # 保存页面
            success = self.db.save_page(page_info)
            if success:
                self.page_count += 1
                self.logger.info(f"已保存页面: {url} - {extracted_content['title']}")
                
                # 保存原始HTML以便调试
                if self.page_count % 50 == 0:  # 每50页保存一次样本
                    sample_path = os.path.join(self.output_dir, f"sample_page_{self.page_count}.html")
                    with open(sample_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
        
        # 保存链接关系
        for link in links:
            self.db.save_link(url, link['url'], link['anchor_text'])
            # 添加到PageRank计算
            self.pagerank.add_link(url, link['url'])
        
        # 保存下载链接
        for download in downloads:
            download_id = self.db.save_download(download)
            if download_id:
                # 保存下载信息到JSON文件
                download_path = os.path.join(self.output_dir, f"download_{download_id}.json")
                with open(download_path, 'w', encoding='utf-8') as f:
                    json.dump(download, f, ensure_ascii=False, indent=4)
        
        # 返回新链接（过滤已处理的）
        return [link['url'] for link in links if link['url'] not in self.urls_taken]
    
    def crawl_batch(self, urls):
        """批量处理页面"""
        new_urls = []
        with ThreadPoolExecutor(max_workers=self.crawl_settings.get('max_concurrent_requests', 5)) as executor:
            # 使用并行执行
            results = list(executor.map(self.process_page, urls))
            
            # 合并结果
            for result in results:
                if result:  # 确保结果不是None或空列表
                    new_urls.extend(result)
            
            # 去重
            new_urls = list(set(new_urls) - self.urls_taken)
        
        return new_urls
    
    def crawl(self):
        """开始爬取过程"""
        self.logger.info(f"开始爬取，起始URL数量: {len(self.start_urls)}")
        self.logger.info(f"最大页面数: {self.max_pages}, 迭代次数: {self.iterations}")
        
        current_urls = self.start_urls.copy()
        
        # 迭代爬取
        for i in range(self.iterations):
            if not current_urls or self.page_count >= self.max_pages:
                break
            
            self.logger.info(f"迭代 {i+1}/{self.iterations}, 待处理URL数量: {len(current_urls)}")
            
            # 添加随机延迟
            if self.crawl_settings.get('random_delay', True):
                delay = self.crawl_settings.get('delay_between_requests', 2.0)
                variance = self.crawl_settings.get('delay_variance', 0.5)
                time.sleep(delay * (1 + random.uniform(-variance, variance)))
            
            new_urls = self.crawl_batch(current_urls)
            
            self.logger.info(f"迭代 {i+1} 完成。总页面数: {self.page_count}, 新URL数量: {len(new_urls)}")
            
            # 准备下一轮迭代
            current_urls = new_urls[:self.max_pages - self.page_count]
        
        # 计算并更新PageRank
        self.update_pagerank()
        
        self.logger.info(f"爬取完成。总页面数: {self.page_count}")
        
        # 导出统计数据
        self.export_stats()
    
    def update_pagerank(self):
        """计算并更新PageRank值"""
        self.logger.info("计算PageRank...")
        
        # 计算PageRank值
        pagerank_scores = self.pagerank.calculate()
        
        # 更新数据库
        for url, score in pagerank_scores.items():
            self.db.update_pagerank(url, score)
        
        # 保存计算结果
        pagerank_path = os.path.join(self.output_dir, "pagerank.json")
        with open(pagerank_path, 'w', encoding='utf-8') as f:
            json.dump(pagerank_scores, f, ensure_ascii=False, indent=4)
        
        # 获取排名前10的页面
        top_pages = self.pagerank.get_top_pages(pagerank_scores, 10)
        self.logger.info("PageRank排名前10的页面:")
        for url, score in top_pages:
            self.logger.info(f"{url}: {score:.6f}")
    
    def export_stats(self):
        """导出爬虫统计数据"""
        # 获取页面数量
        cursor = self.db.execute("SELECT COUNT(*) FROM pages")
        page_count = cursor.fetchone()[0]
        
        # 获取链接数量
        cursor = self.db.execute("SELECT COUNT(*) FROM links")
        link_count = cursor.fetchone()[0]
        
        # 获取下载链接数量
        cursor = self.db.execute("SELECT COUNT(*) FROM downloads")
        download_count = cursor.fetchone()[0]
        
        # 统计各种文件类型的数量
        cursor = self.db.execute("SELECT file_type, COUNT(*) FROM downloads GROUP BY file_type")
        file_type_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 获取编码分布
        cursor = self.db.execute("""
        SELECT encoding, COUNT(*) as count 
        FROM pages 
        WHERE encoding IS NOT NULL 
        GROUP BY encoding 
        ORDER BY count DESC
        """)
        encoding_stats = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 获取域名分布
        domain_stats = self._get_top_domains(10)
        
        # 导出统计数据
        stats = {
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_pages": page_count,
            "total_links": link_count,
            "total_downloads": download_count,
            "file_type_stats": file_type_stats,
            "encoding_stats": encoding_stats,
            "top_domains": domain_stats,
        }
        
        stats_path = os.path.join(self.output_dir, "crawl_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=4)
        
        self.logger.info(f"统计数据已导出到 {stats_path}")
        
        # 打印摘要
        self.logger.info(f"爬取摘要:")
        self.logger.info(f"总页面数: {page_count}")
        self.logger.info(f"总链接数: {link_count}")
        self.logger.info(f"总下载链接数: {download_count}")
    
    def _get_top_domains(self, limit=10):
        """获取出现频率最高的域名"""
        domains = {}
        
        # 从链接中提取域名
        cursor = self.db.execute("SELECT to_url FROM links")
        for row in cursor.fetchall():
            url = row[0]
            try:
                domain = urlparse(url).netloc
                if domain:
                    domains[domain] = domains.get(domain, 0) + 1
            except:
                continue
        
        # 排序并返回前N个
        top_domains = sorted(domains.items(), key=lambda x: x[1], reverse=True)[:limit]
        return {domain: count for domain, count in top_domains}
    
    def fix_encoding_issues(self, limit=None):
        """尝试修复数据库中的编码问题"""
        # 获取所有页面
        query = "SELECT id, url, html_content, encoding FROM pages"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = self.db.execute(query)
        pages = cursor.fetchall()
        
        fixed_count = 0
        for page_id, url, html_content, current_encoding in pages:
            # 尝试更好的编码检测
            try:
                # 如果内容是字符串，先转换为字节
                if isinstance(html_content, str):
                    content_bytes = html_content.encode('utf-8', errors='replace')
                else:
                    content_bytes = html_content
                
                # 检测编码
                detection = chardet.detect(content_bytes)
                detected_encoding = detection['encoding']
                
                if detected_encoding and detected_encoding.lower() != (current_encoding or '').lower():
                    # 使用检测到的编码重新解码内容
                    if isinstance(html_content, bytes):
                        decoded_content = html_content.decode(detected_encoding, errors='replace')
                    else:
                        # 如果已经是字符串，重新编码然后解码
                        decoded_content = html_content.encode('utf-8', errors='replace').decode(detected_encoding, errors='replace')
                    
                    # 解析并重新提取文本内容
                    soup = BeautifulSoup(decoded_content, 'html.parser')
                    
                    # 提取标题
                    title = soup.title.text.strip() if soup.title else "无标题"
                    
                    # 提取文本内容
                    content = ""
                    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
                        if element.parent.name not in ['script', 'style']:
                            text = element.get_text(strip=True)
                            if text:
                                content += text + "\n"
                    
                    # 更新数据库
                    self.db.execute("""
                    UPDATE pages SET title = ?, content = ?, encoding = ? WHERE id = ?
                    """, (title, content, detected_encoding, page_id))
                    
                    fixed_count += 1
                    self.logger.info(f"已修复页面 {page_id} 的编码: {current_encoding} -> {detected_encoding}")
            
            except Exception as e:
                self.logger.error(f"修复页面 {page_id} 编码时出错: {e}")
        
        self.logger.info(f"已修复 {fixed_count} 个页面的编码问题")
        return fixed_count
    
    def close(self):
        """关闭数据库连接"""
        self.db.close_all()
        self.logger.info("数据库连接已关闭")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Web Crawler with Chinese encoding support')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--workers', type=int, default=5, help='并发工作线程数')
    parser.add_argument('--output-dir', type=str, help='自定义输出目录名(默认:时间戳)')
    parser.add_argument('--force-encoding', type=str, help='强制使用指定编码(如 gb18030)')
    parser.add_argument('--fix-encoding', action='store_true', help='尝试修复数据库中的编码问题')
    
    args = parser.parse_args()
    
    if not args.config:
        print("错误: 必须提供 --config")
        parser.print_help()
        return

    if not args.output_dir:
        print("错误: 必须提供 --output-dir")
        parser.print_help()
        return
    
    try:
        # 创建爬虫实例
        crawler = WebCrawler(
            config_file=args.config,
            output_dir=args.output_dir,
        )
        
        # 设置并发工作线程数
        if args.workers:
            crawler.crawl_settings['max_concurrent_requests'] = args.workers
        
        # 设置强制编码
        if args.force_encoding:
            crawler.encoding_handler.settings['force_encoding'] = args.force_encoding
            print(f"强制使用编码: {args.force_encoding}")
        
        # 修复编码问题
        if args.fix_encoding:
            fixed_count = crawler.fix_encoding_issues()
            print(f"已修复 {fixed_count} 个页面的编码问题")
            return
        
        # 开始爬取
        crawler.crawl()
        
    except KeyboardInterrupt:
        print("\n爬取被用户中断")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'crawler' in locals():
            crawler.close()


if __name__ == "__main__":
    main()