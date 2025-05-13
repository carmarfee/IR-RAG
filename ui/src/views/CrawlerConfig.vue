<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import {
    Setting,
    Close,
    RefreshRight,
    Check
} from '@element-plus/icons-vue';
import { useRouter } from 'vue-router';
import { GetCrawlerConfig, SaveCrawlerConfig } from '../api/crawler';

// 默认爬虫配置 - 必须在使用前先定义
const defaultConfig = {
    baseUrl: 'https://news.whu.edu.cn/',
    maxPages: 100,
    iterations: 10,
    maxDepth: 8,
    delay: 2.0,
    concurrency: 5,
    timeout: 20,
    randomDelay: true,
    respectRobotsTxt: true,
    allowSubdomains: true,
    saveRawHtml: true,
    encoding: 'utf-8',
    fallbackEncodings: ['gb18030', 'gbk', 'gb2312', 'big5'],
    detectEncoding: true,
    useMetaCharset: true,
    verifyContent: true,
    fixBrokenHtml: true,
    startUrls: [
        'https://news.whu.edu.cn/',
        'https://news.whu.edu.cn/wdzx/wdyw.htm',
        'https://news.whu.edu.cn/wdzx/zhxw.htm'
    ],
    excludePatterns: [
        '/login',
        '/logout',
        '/search'
    ],
    domainSpecificEncodings: {
        'www.whu.edu.cn': 'utf-8'
    },
    downloadTypes: [
        'pdf',
        'doc',
        'docx',
        'ppt',
        'pptx',
        'xls',
        'xlsx',
        'txt',
        'zip',
        'rar'
    ],
    contentExtraction: {
        titleSelectors: ['div.arc-tit h1'],
        contentSelectors: ['div.arc-con'],
        timeSelectors: ['div.arc-info span:nth-of-type(1)'],
        sourceSelectors: ['div.arc-info span:nth-of-type(2)'],
        removeSelectors: [
            'div.share',
            'div.pageBtn',
            'div.bot_tools',
            'div.print',
            'div.function',
            'div.tools',
            'script',
            'style'
        ]
    },
    headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.whu.edu.cn/'
    },
    crawlSettings: {
        maxRedirects: 3,
        retryTimes: 3,
        retryDelay: 5,
        delayVariance: 0.5
    },
    userAgentList: [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15'
    ]
};

// 爬虫配置 - 在defaultConfig定义后再使用
const config = ref({ ...defaultConfig });

// 从服务器加载的完整配置
const fullConfig = ref(null);

// 是否正在加载配置
const isLoadingConfig = ref(false);

// 是否已修改配置
const configModified = ref(false);

// 当前选中的配置标签页
const activeTab = ref('basic');

// 日志相关状态
const totalPages = ref(100);
const pendingCount = ref(totalPages.value);

const router = useRouter();

// 临时变量用于添加新的头部或用户代理
const newHeader = reactive({ name: '', value: '' });
const newUserAgent = ref('');
const newDomainEncoding = reactive({ domain: '', encoding: 'utf-8' });
const newSelector = ref('');
const newDownloadType = ref('');

//-------------------------------分割线--------------------------------
const goBack = () => {
    router.back();
};

const loadConfig = async () => {
    isLoadingConfig.value = true;

    try {
        // 这里可以使用API获取配置，但示例中我们使用提供的配置文件
        await new Promise(resolve => setTimeout(resolve, 500));

        // 使用您提供的配置文件内容
        const serverConfig = {
            "base_url": "https://news.whu.edu.cn/",
            "start_urls": [
                "https://news.whu.edu.cn/",
                "https://news.whu.edu.cn/wdzx/wdyw.htm",
                "https://news.whu.edu.cn/wdzx/zhxw.htm",
                "https://news.whu.edu.cn/wdzx/hzjl.htm",
                "https://news.whu.edu.cn/wdzx/yxcz.htm",
                "https://news.whu.edu.cn/kydt.htm",
                "https://news.whu.edu.cn/xywh/bfxy.htm",
                "https://news.whu.edu.cn/ztbd.htm",
                "https://news.whu.edu.cn/mtwd.htm",
                "https://news.whu.edu.cn/ljrw.htm",
                "https://news.whu.edu.cn/stkj/ljyx.htm"
            ],
            "max_pages": 10,
            "iterations": 10,
            "timeout": 20,
            "encoding_settings": {
                "default_encoding": "utf-8",
                "fallback_encodings": [
                    "gb18030",
                    "gbk",
                    "gb2312",
                    "big5"
                ],
                "detect_encoding": true,
                "force_encoding": null,
                "store_encoding": "utf-8",
                "use_meta_charset": true,
                "verify_content": true,
                "fix_broken_html": true
            },
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Connection": "keep-alive",
                "Cache-Control": "max-age=0",
                "Upgrade-Insecure-Requests": "1",
                "Referer": "https://www.whu.edu.cn/"
            },
            "download_types": [
                "pdf",
                "doc",
                "docx",
                "ppt",
                "pptx",
                "xls",
                "xlsx",
                "txt",
                "zip",
                "rar"
            ],
            "exclude_patterns": [
                "/login",
                "/logout",
                "/search",
                "javascript:",
                "mailto:",
                "/comment",
                "/submit",
                "/help/",
                "javascript:void",
                "rss",
                "/404.html",
                "/old/",
                "/en/",
                "/print/",
                "/_redirect/"
            ],
            "domain_specific_encodings": {
                "www.whu.edu.cn": "utf-8"
            },
            "content_extraction": {
                "title_selectors": [
                    "div.arc-tit h1"
                ],
                "content_selectors": [
                    "div.arc-con"
                ],
                "time_selectors": [
                    "div.arc-info span:nth-of-type(1)"
                ],
                "source_selectors": [
                    "div.arc-info span:nth-of-type(2)"
                ],
                "remove_selectors": [
                    "div.share",
                    "div.pageBtn",
                    "div.bot_tools",
                    "div.print",
                    "div.function",
                    "div.tools",
                    "script",
                    "style"
                ]
            },
            "crawl_settings": {
                "delay_between_requests": 2.0,
                "max_concurrent_requests": 5,
                "follow_redirects": true,
                "max_redirects": 3,
                "retry_times": 3,
                "retry_delay": 5,
                "respect_robots_txt": true,
                "max_depth": 8,
                "allow_subdomains": true,
                "random_delay": true,
                "delay_variance": 0.5
            },
            "user_agent_list": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36 OPR/85.0.4341.75"
            ]
        };

        fullConfig.value = serverConfig;

        // 更新组件的配置对象
        config.value = {
            baseUrl: serverConfig.base_url,
            maxPages: serverConfig.max_pages,
            iterations: serverConfig.iterations,
            maxDepth: serverConfig.crawl_settings.max_depth,
            delay: serverConfig.crawl_settings.delay_between_requests,
            concurrency: serverConfig.crawl_settings.max_concurrent_requests,
            timeout: serverConfig.timeout,
            randomDelay: serverConfig.crawl_settings.random_delay,
            respectRobotsTxt: serverConfig.crawl_settings.respect_robots_txt,
            allowSubdomains: serverConfig.crawl_settings.allow_subdomains,
            saveRawHtml: true, // 假设这个值在配置中不存在
            encoding: serverConfig.encoding_settings.default_encoding,
            fallbackEncodings: serverConfig.encoding_settings.fallback_encodings,
            detectEncoding: serverConfig.encoding_settings.detect_encoding,
            useMetaCharset: serverConfig.encoding_settings.use_meta_charset,
            verifyContent: serverConfig.encoding_settings.verify_content,
            fixBrokenHtml: serverConfig.encoding_settings.fix_broken_html,
            startUrls: serverConfig.start_urls,
            excludePatterns: serverConfig.exclude_patterns,
            domainSpecificEncodings: serverConfig.domain_specific_encodings,
            downloadTypes: serverConfig.download_types,
            contentExtraction: {
                titleSelectors: serverConfig.content_extraction.title_selectors,
                contentSelectors: serverConfig.content_extraction.content_selectors,
                timeSelectors: serverConfig.content_extraction.time_selectors,
                sourceSelectors: serverConfig.content_extraction.source_selectors,
                removeSelectors: serverConfig.content_extraction.remove_selectors
            },
            headers: serverConfig.headers,
            crawlSettings: {
                maxRedirects: serverConfig.crawl_settings.max_redirects,
                retryTimes: serverConfig.crawl_settings.retry_times,
                retryDelay: serverConfig.crawl_settings.retry_delay,
                delayVariance: serverConfig.crawl_settings.delay_variance
            },
            userAgentList: serverConfig.user_agent_list
        };

        totalPages.value = config.value.maxPages;
        pendingCount.value = totalPages.value;

        console.log('success', '配置文件加载成功');
        configModified.value = false;
    } catch (error) {
        console.log('error', `配置文件加载失败: ${error.message}`);
    } finally {
        isLoadingConfig.value = false;
    }
};

const saveConfig = async () => {
    try {
        // 将前端配置转换为后端需要的格式
        const backendConfig = {
            base_url: config.value.baseUrl,
            start_urls: config.value.startUrls,
            max_pages: config.value.maxPages,
            iterations: config.value.iterations,
            timeout: config.value.timeout,
            encoding_settings: {
                default_encoding: config.value.encoding,
                fallback_encodings: config.value.fallbackEncodings,
                detect_encoding: config.value.detectEncoding,
                force_encoding: null,
                store_encoding: "utf-8",
                use_meta_charset: config.value.useMetaCharset,
                verify_content: config.value.verifyContent,
                fix_broken_html: config.value.fixBrokenHtml
            },
            headers: config.value.headers,
            download_types: config.value.downloadTypes,
            exclude_patterns: config.value.excludePatterns,
            domain_specific_encodings: config.value.domainSpecificEncodings,
            content_extraction: {
                title_selectors: config.value.contentExtraction.titleSelectors,
                content_selectors: config.value.contentExtraction.contentSelectors,
                time_selectors: config.value.contentExtraction.timeSelectors,
                source_selectors: config.value.contentExtraction.sourceSelectors,
                remove_selectors: config.value.contentExtraction.removeSelectors
            },
            crawl_settings: {
                delay_between_requests: config.value.delay,
                max_concurrent_requests: config.value.concurrency,
                follow_redirects: true,
                max_redirects: config.value.crawlSettings.maxRedirects,
                retry_times: config.value.crawlSettings.retryTimes,
                retry_delay: config.value.crawlSettings.retryDelay,
                respect_robots_txt: config.value.respectRobotsTxt,
                max_depth: config.value.maxDepth,
                allow_subdomains: config.value.allowSubdomains,
                random_delay: config.value.randomDelay,
                delay_variance: config.value.crawlSettings.delayVariance
            },
            user_agent_list: config.value.userAgentList
        };

        // 在实际应用中，这里应该调用API保存配置
        // await SaveCrawlerConfig(backendConfig);

        // 模拟保存成功
        await new Promise(resolve => setTimeout(resolve, 500));
        configModified.value = false;
    } catch (error) {
        console.log(`配置保存失败: ${error.message}`)
    }
};

const restoreDefaults = () => {
    // 恢复默认配置
    config.value = { ...defaultConfig };
    configModified.value = true;
};

const onConfigChange = () => {
    configModified.value = true;
};

// 辅助方法，添加头部
const addHeader = () => {
    if (newHeader.name && newHeader.value) {
        config.value.headers[newHeader.name] = newHeader.value;
        newHeader.name = '';
        newHeader.value = '';
        onConfigChange();
    }
};

// 删除头部
const removeHeader = (key) => {
    if (config.value.headers[key]) {
        delete config.value.headers[key];
        onConfigChange();
    }
};

// 添加用户代理
const addUserAgent = () => {
    if (newUserAgent.value) {
        config.value.userAgentList.push(newUserAgent.value);
        newUserAgent.value = '';
        onConfigChange();
    }
};

// 添加域名特定编码
const addDomainEncoding = () => {
    if (newDomainEncoding.domain) {
        config.value.domainSpecificEncodings[newDomainEncoding.domain] = newDomainEncoding.encoding;
        newDomainEncoding.domain = '';
        newDomainEncoding.encoding = 'utf-8';
        onConfigChange();
    }
};

// 添加下载类型
const addDownloadType = () => {
    if (newDownloadType.value && !config.value.downloadTypes.includes(newDownloadType.value)) {
        config.value.downloadTypes.push(newDownloadType.value);
        newDownloadType.value = '';
        onConfigChange();
    }
};

// 添加选择器
const addSelector = (selectorType) => {
    if (newSelector.value) {
        config.value.contentExtraction[selectorType].push(newSelector.value);
        newSelector.value = '';
        onConfigChange();
    }
};

// 转换对象为数组用于表格显示
const headersArray = computed(() => {
    return Object.entries(config.value.headers).map(([name, value]) => ({ name, value }));
});

const domainEncodingsArray = computed(() => {
    return Object.entries(config.value.domainSpecificEncodings).map(([domain, encoding]) => ({ domain, encoding }));
});

// 生命周期钩子
onMounted(() => {
    loadConfig();
});
</script>

<template>
    <el-card class="config-card" shadow="never">
        <template #header>
            <div class="config-header">
                <el-button size="small" type="primary" @click="goBack">
                    返回
                </el-button>
                <span><el-icon>
                        <Setting />
                    </el-icon> 爬虫配置</span>
                <div>
                    <el-button size="small" type="warning" @click="restoreDefaults">
                        <el-icon>
                            <RefreshRight />
                        </el-icon> 恢复默认
                    </el-button>
                    <el-button size="small" type="primary" @click="saveConfig" :disabled="!configModified">
                        <el-icon>
                            <Check />
                        </el-icon> 应用
                    </el-button>
                </div>
            </div>
        </template>

        <el-tabs v-model="activeTab">
            <el-tab-pane label="基本设置" name="basic">
                <el-form :model="config" label-width="120px" label-position="left" @change="onConfigChange">
                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="基础URL">
                                <el-input v-model="config.baseUrl" placeholder="输入基础URL" @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="最大页面数">
                                <el-input-number v-model="config.maxPages" :min="1" :max="100000"
                                    @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="迭代次数">
                                <el-input-number v-model="config.iterations" :min="1" :max="100"
                                    @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="爬取深度">
                                <el-input-number v-model="config.maxDepth" :min="1" :max="20"
                                    @change="onConfigChange" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="请求间隔 (秒)">
                                <el-input-number v-model="config.delay" :min="0.1" :max="10" :step="0.1"
                                    @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="并发请求数">
                                <el-input-number v-model="config.concurrency" :min="1" :max="20"
                                    @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="超时时间 (秒)">
                                <el-input-number v-model="config.timeout" :min="1" :max="60" @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="延迟方差">
                                <el-input-number v-model="config.crawlSettings.delayVariance" :min="0.1" :max="1.0"
                                    :step="0.1" @change="onConfigChange" />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-divider />

                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="随机延迟">
                                <el-switch v-model="config.randomDelay" @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="遵循robots.txt">
                                <el-switch v-model="config.respectRobotsTxt" @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="最大重定向次数">
                                <el-input-number v-model="config.crawlSettings.maxRedirects" :min="1" :max="10"
                                    @change="onConfigChange" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="允许子域名">
                                <el-switch v-model="config.allowSubdomains" @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="保存原始HTML">
                                <el-switch v-model="config.saveRawHtml" @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="重试次数">
                                <el-input-number v-model="config.crawlSettings.retryTimes" :min="0" :max="10"
                                    @change="onConfigChange" />
                            </el-form-item>
                            <el-form-item label="重试延迟 (秒)">
                                <el-input-number v-model="config.crawlSettings.retryDelay" :min="1" :max="30"
                                    @change="onConfigChange" />
                            </el-form-item>
                        </el-col>
                    </el-row>
                </el-form>
            </el-tab-pane>

            <el-tab-pane label="编码设置" name="encoding">
                <el-form :model="config" label-width="140px" label-position="left" @change="onConfigChange">
                    <el-form-item label="默认编码">
                        <el-select v-model="config.encoding" placeholder="选择编码" @change="onConfigChange">
                            <el-option label="UTF-8" value="utf-8" />
                            <el-option label="GB18030" value="gb18030" />
                            <el-option label="GBK" value="gbk" />
                            <el-option label="GB2312" value="gb2312" />
                            <el-option label="Big5" value="big5" />
                        </el-select>
                    </el-form-item>

                    <el-form-item label="检测编码">
                        <el-switch v-model="config.detectEncoding" @change="onConfigChange" />
                    </el-form-item>

                    <el-form-item label="使用Meta编码">
                        <el-switch v-model="config.useMetaCharset" @change="onConfigChange" />
                    </el-form-item>

                    <el-form-item label="验证内容">
                        <el-switch v-model="config.verifyContent" @change="onConfigChange" />
                    </el-form-item>

                    <el-form-item label="修复损坏的HTML">
                        <el-switch v-model="config.fixBrokenHtml" @change="onConfigChange" />
                    </el-form-item>

                    <el-form-item label="备用编码">
                        <el-tag v-for="(encoding, index) in config.fallbackEncodings" :key="index" closable
                            @close="config.fallbackEncodings.splice(index, 1); onConfigChange()" class="m-1">
                            {{ encoding }}
                        </el-tag>
                        <el-input class="w-50 m-2" placeholder="添加备用编码" v-model="newSelector"
                            @keyup.enter="config.fallbackEncodings.push(newSelector); newSelector = ''; onConfigChange()">
                            <template #append>
                                <el-button
                                    @click="config.fallbackEncodings.push(newSelector); newSelector = ''; onConfigChange()">
                                    添加
                                </el-button>
                            </template>
                        </el-input>
                    </el-form-item>

                    <el-divider>域名特定编码</el-divider>

                    <el-table :data="domainEncodingsArray" style="width: 100%" border>
                        <el-table-column prop="domain" label="域名" />
                        <el-table-column prop="encoding" label="编码"/>
                        <el-table-column label="操作">
                            <template #default="scope">
                                <el-button type="danger" size="small"
                                    @click="delete config.domainSpecificEncodings[scope.row.domain]; onConfigChange()">
                                    删除
                                </el-button>
                            </template>
                        </el-table-column>
                    </el-table>

                    <div class="mt-4 d-flex">
                        <el-input v-model="newDomainEncoding.domain" placeholder="域名" class="mr-2" />
                        <el-select v-model="newDomainEncoding.encoding" placeholder="编码" class="mr-2">
                            <el-option label="UTF-8" value="utf-8" />
                            <el-option label="GB18030" value="gb18030" />
                            <el-option label="GBK" value="gbk" />
                            <el-option label="GB2312" value="gb2312" />
                            <el-option label="Big5" value="big5" />
                        </el-select>
                        <el-button type="primary" @click="addDomainEncoding">添加</el-button>
                    </div>
                </el-form>
            </el-tab-pane>

            <el-tab-pane label="起始URL" name="startUrls">
                <el-alert title="起始URL是爬虫开始爬取的入口点" type="info" :closable="false" class="mb-4">
                </el-alert>

                <el-table :data="config.startUrls" style="width: 100%" height="250">
                    <el-table-column label="URL" prop="url">
                        <template #default="{ $index }">
                            <el-input v-model="config.startUrls[$index]" @change="onConfigChange" />
                        </template>
                    </el-table-column>
                    <el-table-column width="80">
                        <template #default="{ $index }">
                            <el-button type="danger" size="small"
                                @click="config.startUrls.splice($index, 1); onConfigChange()">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="mt-4">
                    <el-button type="primary" size="small"
                        @click="config.startUrls.push(''); onConfigChange()">添加URL</el-button>
                </div>
            </el-tab-pane>

            <el-tab-pane label="排除规则" name="excludePatterns">
                <el-alert title="排除规则用于过滤不需要爬取的URL" type="info" :closable="false" class="mb-4">
                </el-alert>

                <el-table :data="config.excludePatterns" style="width: 100%" height="250">
                    <el-table-column label="规则" prop="pattern">
                        <template #default="{ $index }">
                            <el-input v-model="config.excludePatterns[$index]" @change="onConfigChange" />
                        </template>
                    </el-table-column>
                    <el-table-column width="80">
                        <template #default="{ $index }">
                            <el-button type="danger" size="small"
                                @click="config.excludePatterns.splice($index, 1); onConfigChange()">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="mt-4">
                    <el-button type="primary" size="small"
                        @click="config.excludePatterns.push(''); onConfigChange()">添加规则</el-button>
                </div>
            </el-tab-pane>

            <el-tab-pane label="下载类型" name="downloadTypes">
                <el-alert title="下载类型表示爬虫会自动保存的文件类型" type="info" :closable="false" class="mb-4">
                </el-alert>

                <el-table :data="config.downloadTypes" style="width: 100%" height="250">
                    <el-table-column label="文件类型" prop="type">
                        <template #default="{ row, $index }">
                            <div class="d-flex align-items-center">
                                <el-tag>{{ row }}</el-tag>
                            </div>
                        </template>
                    </el-table-column>
                    <el-table-column width="80">
                        <template #default="{ $index }">
                            <el-button type="danger" size="small"
                                @click="config.downloadTypes.splice($index, 1); onConfigChange()">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="mt-4 d-flex">
                    <el-input v-model="newDownloadType" placeholder="添加文件类型(如 pdf, doc)" class="mr-2" />
                    <el-button type="primary" @click="addDownloadType">添加</el-button>
                </div>
            </el-tab-pane>

            <el-tab-pane label="内容提取" name="contentExtraction">
                <el-alert title="内容提取规则定义如何从HTML页面中提取标题、内容等信息" type="info" :closable="false" class="mb-4">
                </el-alert>

                <el-collapse accordion>
                    <el-collapse-item title="标题选择器" name="titleSelectors">
                        <el-table :data="config.contentExtraction.titleSelectors" style="width: 100%">
                            <el-table-column label="CSS选择器" prop="selector">
                                <template #default="{ row, $index }">
                                    <el-input v-model="config.contentExtraction.titleSelectors[$index]"
                                        @change="onConfigChange" />
                                </template>
                            </el-table-column>
                            <el-table-column width="80">
                                <template #default="{ $index }">
                                    <el-button type="danger" size="small"
                                        @click="config.contentExtraction.titleSelectors.splice($index, 1); onConfigChange()">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="mt-2">
                            <el-input v-model="newSelector" placeholder="输入CSS选择器" />
                            <el-button class="mt-2" type="primary" size="small"
                                @click="addSelector('titleSelectors')">添加选择器</el-button>
                        </div>
                    </el-collapse-item>

                    <el-collapse-item title="内容选择器" name="contentSelectors">
                        <el-table :data="config.contentExtraction.contentSelectors" style="width: 100%">
                            <el-table-column label="CSS选择器" prop="selector">
                                <template #default="{ row, $index }">
                                    <el-input v-model="config.contentExtraction.contentSelectors[$index]"
                                        @change="onConfigChange" />
                                </template>
                            </el-table-column>
                            <el-table-column width="80">
                                <template #default="{ $index }">
                                    <el-button type="danger" size="small"
                                        @click="config.contentExtraction.contentSelectors.splice($index, 1); onConfigChange()">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="mt-2">
                            <el-input v-model="newSelector" placeholder="输入CSS选择器" />
                            <el-button class="mt-2" type="primary" size="small"
                                @click="addSelector('contentSelectors')">添加选择器</el-button>
                        </div>
                    </el-collapse-item>

                    <el-collapse-item title="时间选择器" name="timeSelectors">
                        <el-table :data="config.contentExtraction.timeSelectors" style="width: 100%">
                            <el-table-column label="CSS选择器" prop="selector">
                                <template #default="{ row, $index }">
                                    <el-input v-model="config.contentExtraction.timeSelectors[$index]"
                                        @change="onConfigChange" />
                                </template>
                            </el-table-column>
                            <el-table-column width="80">
                                <template #default="{ $index }">
                                    <el-button type="danger" size="small"
                                        @click="config.contentExtraction.timeSelectors.splice($index, 1); onConfigChange()">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="mt-2">
                            <el-input v-model="newSelector" placeholder="输入CSS选择器" />
                            <el-button class="mt-2" type="primary" size="small"
                                @click="addSelector('timeSelectors')">添加选择器</el-button>
                        </div>
                    </el-collapse-item>

                    <el-collapse-item title="来源选择器" name="sourceSelectors">
                        <el-table :data="config.contentExtraction.sourceSelectors" style="width: 100%">
                            <el-table-column label="CSS选择器" prop="selector">
                                <template #default="{ row, $index }">
                                    <el-input v-model="config.contentExtraction.sourceSelectors[$index]"
                                        @change="onConfigChange" />
                                </template>
                            </el-table-column>
                            <el-table-column width="80">
                                <template #default="{ $index }">
                                    <el-button type="danger" size="small"
                                        @click="config.contentExtraction.sourceSelectors.splice($index, 1); onConfigChange()">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="mt-2">
                            <el-input v-model="newSelector" placeholder="输入CSS选择器" />
                            <el-button class="mt-2" type="primary" size="small"
                                @click="addSelector('sourceSelectors')">添加选择器</el-button>
                        </div>
                    </el-collapse-item>

                    <el-collapse-item title="移除选择器" name="removeSelectors">
                        <el-table :data="config.contentExtraction.removeSelectors" style="width: 100%">
                            <el-table-column label="CSS选择器" prop="selector">
                                <template #default="{ row, $index }">
                                    <el-input v-model="config.contentExtraction.removeSelectors[$index]"
                                        @change="onConfigChange" />
                                </template>
                            </el-table-column>
                            <el-table-column width="80">
                                <template #default="{ $index }">
                                    <el-button type="danger" size="small"
                                        @click="config.contentExtraction.removeSelectors.splice($index, 1); onConfigChange()">删除</el-button>
                                </template>
                            </el-table-column>
                        </el-table>
                        <div class="mt-2">
                            <el-input v-model="newSelector" placeholder="输入CSS选择器" />
                            <el-button class="mt-2" type="primary" size="small"
                                @click="addSelector('removeSelectors')">添加选择器</el-button>
                        </div>
                    </el-collapse-item>
                </el-collapse>
            </el-tab-pane>

            <el-tab-pane label="HTTP头" name="headers">
                <el-alert title="HTTP头用于模拟浏览器行为，避免被网站屏蔽" type="info" :closable="false" class="mb-4">
                </el-alert>

                <el-table :data="headersArray" style="width: 100%" height="250">
                    <el-table-column prop="name" label="名称" width="180" />
                    <el-table-column prop="value" label="值" />
                    <el-table-column label="操作" width="100">
                        <template #default="scope">
                            <el-button type="danger" size="small" @click="removeHeader(scope.row.name)">
                                删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="mt-4 d-flex">
                    <el-input v-model="newHeader.name" placeholder="头部名称" class="mr-2" />
                    <el-input v-model="newHeader.value" placeholder="头部值" class="mr-2" />
                    <el-button type="primary" @click="addHeader">添加</el-button>
                </div>
            </el-tab-pane>

            <el-tab-pane label="用户代理" name="userAgents">
                <el-alert title="用户代理列表用于随机选择，模拟不同浏览器" type="info" :closable="false" class="mb-4">
                </el-alert>

                <el-table :data="config.userAgentList" style="width: 100%" height="250">
                    <el-table-column label="User-Agent" prop="agent">
                        <template #default="{ row, $index }">
                            <el-input v-model="config.userAgentList[$index]" @change="onConfigChange" />
                        </template>
                    </el-table-column>
                    <el-table-column width="80">
                        <template #default="{ $index }">
                            <el-button type="danger" size="small"
                                @click="config.userAgentList.splice($index, 1); onConfigChange()">删除</el-button>
                        </template>
                    </el-table-column>
                </el-table>

                <div class="mt-4 d-flex">
                    <el-input v-model="newUserAgent" placeholder="输入User-Agent字符串" class="mr-2" />
                    <el-button type="primary" @click="addUserAgent">添加</el-button>
                </div>
            </el-tab-pane>
        </el-tabs>
    </el-card>
</template>

<style scoped>
.config-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* 添加辅助类 */
.mb-4 {
    margin-bottom: 16px;
}

.mt-4 {
    margin-top: 16px;
}

.mt-2 {
    margin-top: 8px;
}

.mr-2 {
    margin-right: 8px;
}

.w-50 {
    width: 50%;
}

.m-1 {
    margin: 4px;
}

.m-2 {
    margin: 8px;
}

.d-flex {
    display: flex;
}

.align-items-center {
    align-items: center;
}

.config-card {
    margin-bottom: 20px;
}
</style>