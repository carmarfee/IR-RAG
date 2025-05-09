<script setup>
import { ref, computed, onMounted } from 'vue';
import {
    VideoPlay,
    VideoPause,
    CircleClose,
    Setting,
    Loading,
    Document,
    Close
} from '@element-plus/icons-vue';

// 爬虫状态
const crawlerStatus = ref('stopped'); // 'stopped', 'running', 'paused'
const pagesCompleted = ref(0);
const totalPages = ref(1000);
const successCount = ref(0);
const failureCount = ref(0);
const pendingCount = ref(0);
const crawlSpeed = ref(0);
const currentUrl = ref('');
const startTime = ref('');
const showConfig = ref(false);

// 爬虫日志
const logs = ref([
    { timestamp: '2025-05-09 10:15:22', type: 'info', message: '爬虫初始化完成' },
    { timestamp: '2025-05-09 10:15:23', type: 'info', message: '加载配置文件: config.json' }
]);

// 爬虫配置
const config = ref({
    baseUrl: 'https://news.whu.edu.cn/',
    maxPages: 10000,
    maxDepth: 8,
    delay: 2.0,
    concurrency: 5,
    timeout: 20,
    randomDelay: true,
    respectRobotsTxt: true,
    allowSubdomains: true,
    saveRawHtml: true,
    encoding: 'utf-8'
});

// 计算属性
const progressPercentage = computed(() => {
    return Math.round((pagesCompleted.value / totalPages.value) * 100);
});

const crawlerStatusText = computed(() => {
    switch (crawlerStatus.value) {
        case 'running': return '爬虫运行中';
        case 'paused': return '爬虫已暂停';
        case 'stopped': return '爬虫已停止';
        default: return '未知状态';
    }
});

const statusTagType = computed(() => {
    switch (crawlerStatus.value) {
        case 'running': return 'success';
        case 'paused': return 'warning';
        case 'stopped': return 'info';
        default: return 'info';
    }
});

const progressStatus = computed(() => {
    if (crawlerStatus.value === 'running') return 'success';
    if (crawlerStatus.value === 'paused') return 'warning';
    if (pagesCompleted.value >= totalPages.value) return 'success';
    return '';
});

// 方法
const logTagType = (type) => {
    switch (type) {
        case 'info': return 'info';
        case 'success': return 'success';
        case 'warning': return 'warning';
        case 'error': return 'danger';
        default: return 'info';
    }
};

const startCrawler = () => {
    crawlerStatus.value = 'running';
    startTime.value = new Date().toLocaleString();
    pagesCompleted.value = 0;
    successCount.value = 0;
    failureCount.value = 0;
    pendingCount.value = totalPages.value;
    crawlSpeed.value = 0;

    addLog('info', '爬虫开始运行');
    addLog('info', `基础URL: ${config.value.baseUrl}`);

    // 模拟爬虫进度更新
    simulateCrawlerProgress();
};

const pauseCrawler = () => {
    crawlerStatus.value = 'paused';
    addLog('warning', '爬虫已暂停');
};

const resumeCrawler = () => {
    crawlerStatus.value = 'running';
    addLog('info', '爬虫已恢复运行');

    // 继续模拟进度更新
    simulateCrawlerProgress();
};

const stopCrawler = () => {
    crawlerStatus.value = 'stopped';
    addLog('error', '爬虫已停止');
};

const saveConfig = () => {
    addLog('success', '配置已保存');
    showConfig.value = false;
};

const addLog = (type, message) => {
    const timestamp = new Date().toLocaleString();
    logs.value.push({ timestamp, type, message });

    // 限制日志数量，保持性能
    if (logs.value.length > 100) {
        logs.value.shift();
    }

    // 滚动到最新日志
    setTimeout(() => {
        const logContainer = document.querySelector('.log-container');
        if (logContainer) {
            logContainer.scrollTop = logContainer.scrollHeight;
        }
    }, 50);
};

const clearLog = () => {
    logs.value = [];
    addLog('info', '日志已清除');
};

const exportLog = () => {
    addLog('info', '日志导出功能已触发');
    // 这里可以实现导出日志的逻辑
};

// 模拟爬虫进度更新
const simulateCrawlerProgress = () => {
    if (crawlerStatus.value !== 'running') return;

    const randomUrls = [
        'https://news.whu.edu.cn/wdzx/wdyw/123456.htm',
        'https://news.whu.edu.cn/kydt/987654.htm',
        'https://news.whu.edu.cn/xywh/bfxy/246810.htm',
        'https://news.whu.edu.cn/ztbd/135790.htm',
        'https://news.whu.edu.cn/ljrw/112233.htm'
    ];

    // 随机更新当前URL
    currentUrl.value = randomUrls[Math.floor(Math.random() * randomUrls.length)];

    // 随机决定成功或失败
    const isSuccess = Math.random() > 0.1; // 90%成功率

    if (isSuccess) {
        successCount.value++;
        addLog('success', `成功爬取: ${currentUrl.value}`);
    } else {
        failureCount.value++;
        addLog('error', `爬取失败: ${currentUrl.value} (超时)`);
    }

    // 更新进度
    pagesCompleted.value++;
    pendingCount.value = totalPages.value - (successCount.value + failureCount.value);

    // 更新爬取速度 (随机模拟)
    crawlSpeed.value = Math.floor(Math.random() * 20) + 40; // 40-60 页/分钟

    // 如果还没有完成，继续模拟
    if (pagesCompleted.value < totalPages.value && crawlerStatus.value === 'running') {
        setTimeout(simulateCrawlerProgress, Math.random() * 1000 + 500); // 0.5-1.5秒的随机间隔
    } else if (pagesCompleted.value >= totalPages.value) {
        // 爬虫完成
        crawlerStatus.value = 'stopped';
        addLog('success', '爬虫任务完成');
    }
};

// 创建一些初始日志
onMounted(() => {
    // 模拟一些初始状态
    pendingCount.value = totalPages.value;

    // 添加一些初始日志
    setTimeout(() => {
        addLog('info', '检查网络连接...');
        addLog('info', '网络连接正常');
        addLog('info', '准备开始爬取，请点击"开始爬取"按钮');
    }, 1000);
});
</script>

<template>
    <div class="doc-crawler" style="height: 100%;">
        <el-row style="height: 100%;">
            <el-col :span="24" style="display: flex;flex-direction: column;">
                <el-card style="margin-top: 10px;height: 95%;" header="爬虫窗口">
                    <!-- 爬虫控制和状态区域 -->
                    <div class="crawler-header">
                        <div class="crawler-status">
                            <el-tag :type="statusTagType" size="large">{{ crawlerStatusText }}</el-tag>
                            <span v-if="startTime" class="crawler-time">开始时间: {{ startTime }}</span>
                        </div>
                        <div class="crawler-controls">
                            <el-button type="primary" v-if="crawlerStatus !== 'running'" @click="startCrawler">
                                <el-icon>
                                    <VideoPlay />
                                </el-icon> 开始爬取
                            </el-button>
                            <el-button type="warning" v-if="crawlerStatus === 'running'" @click="pauseCrawler">
                                <el-icon>
                                    <VideoPause />
                                </el-icon> 暂停
                            </el-button>
                            <el-button type="primary" v-if="crawlerStatus === 'paused'" @click="resumeCrawler">
                                <el-icon>
                                    <VideoPlay />
                                </el-icon> 恢复
                            </el-button>
                            <el-button type="danger" v-if="crawlerStatus === 'running' || crawlerStatus === 'paused'"
                                @click="stopCrawler">
                                <el-icon>
                                    <CircleClose />
                                </el-icon> 停止
                            </el-button>
                            <el-button type="info" @click="showConfig = !showConfig">
                                <el-icon>
                                    <Setting />
                                </el-icon> 配置
                            </el-button>
                        </div>
                    </div>

                    <!-- 爬虫进度区域 -->
                    <el-card class="progress-card" shadow="never">
                        <template #header>
                            <div class="progress-header">
                                <span><el-icon>
                                        <Loading />
                                    </el-icon> 爬虫进度</span>
                                <span>{{ pagesCompleted }} / {{ totalPages }} 页面</span>
                            </div>
                        </template>
                        <el-progress :percentage="progressPercentage" :status="progressStatus" :stroke-width="15"
                            :format="(p) => p + '%'" />

                        <div class="current-url">
                            <span class="url-label">当前URL:</span>
                            <el-tag size="small" effect="plain">{{ currentUrl || '尚未开始' }}</el-tag>
                        </div>

                        <el-row :gutter="20" class="stats-row">
                            <el-col :span="6">
                                <el-card shadow="hover" class="stat-card">
                                    <div class="stat-value success-text">{{ successCount }}</div>
                                    <div class="stat-label">成功</div>
                                </el-card>
                            </el-col>
                            <el-col :span="6">
                                <el-card shadow="hover" class="stat-card">
                                    <div class="stat-value danger-text">{{ failureCount }}</div>
                                    <div class="stat-label">失败</div>
                                </el-card>
                            </el-col>
                            <el-col :span="6">
                                <el-card shadow="hover" class="stat-card">
                                    <div class="stat-value warning-text">{{ pendingCount }}</div>
                                    <div class="stat-label">等待中</div>
                                </el-card>
                            </el-col>
                            <el-col :span="6">
                                <el-card shadow="hover" class="stat-card">
                                    <div class="stat-value info-text">{{ crawlSpeed }}</div>
                                    <div class="stat-label">页面/分钟</div>
                                </el-card>
                            </el-col>
                        </el-row>
                    </el-card>

                    <!-- 爬虫配置区域 -->
                    <el-collapse-transition>
                        <el-card v-show="showConfig" class="config-card" shadow="never">
                            <template #header>
                                <div class="config-header">
                                    <span><el-icon>
                                            <Setting />
                                        </el-icon> 爬虫配置</span>
                                    <el-button size="small" text @click="showConfig = false">
                                        <el-icon>
                                            <Close />
                                        </el-icon>
                                    </el-button>
                                </div>
                            </template>

                            <el-form :model="config" label-width="120px" label-position="left">
                                <el-row :gutter="20">
                                    <el-col :span="12">
                                        <el-form-item label="基础URL">
                                            <el-input v-model="config.baseUrl" placeholder="输入基础URL" />
                                        </el-form-item>
                                        <el-form-item label="最大页面数">
                                            <el-input-number v-model="config.maxPages" :min="1" :max="100000" />
                                        </el-form-item>
                                        <el-form-item label="爬取深度">
                                            <el-input-number v-model="config.maxDepth" :min="1" :max="20" />
                                        </el-form-item>
                                    </el-col>
                                    <el-col :span="12">
                                        <el-form-item label="请求间隔 (秒)">
                                            <el-input-number v-model="config.delay" :min="0.1" :max="10" :step="0.1" />
                                        </el-form-item>
                                        <el-form-item label="并发请求数">
                                            <el-input-number v-model="config.concurrency" :min="1" :max="20" />
                                        </el-form-item>
                                        <el-form-item label="超时时间 (秒)">
                                            <el-input-number v-model="config.timeout" :min="1" :max="60" />
                                        </el-form-item>
                                    </el-col>
                                </el-row>

                                <el-divider />

                                <el-row :gutter="20">
                                    <el-col :span="12">
                                        <el-form-item label="随机延迟">
                                            <el-switch v-model="config.randomDelay" />
                                        </el-form-item>
                                        <el-form-item label="遵循robots.txt">
                                            <el-switch v-model="config.respectRobotsTxt" />
                                        </el-form-item>
                                    </el-col>
                                    <el-col :span="12">
                                        <el-form-item label="允许子域名">
                                            <el-switch v-model="config.allowSubdomains" />
                                        </el-form-item>
                                        <el-form-item label="保存原始HTML">
                                            <el-switch v-model="config.saveRawHtml" />
                                        </el-form-item>
                                    </el-col>
                                </el-row>

                                <el-form-item label="编码设置">
                                    <el-select v-model="config.encoding" placeholder="选择编码">
                                        <el-option label="UTF-8" value="utf-8" />
                                        <el-option label="GB18030" value="gb18030" />
                                        <el-option label="GBK" value="gbk" />
                                        <el-option label="GB2312" value="gb2312" />
                                        <el-option label="Big5" value="big5" />
                                    </el-select>
                                </el-form-item>

                                <el-form-item>
                                    <el-button type="primary" @click="saveConfig">保存配置</el-button>
                                    <el-button @click="showConfig = false">取消</el-button>
                                </el-form-item>
                            </el-form>
                        </el-card>
                    </el-collapse-transition>

                    <!-- 爬虫日志区域 -->
                    <el-card class="log-card" shadow="never">
                        <template #header>
                            <div class="log-header">
                                <span><el-icon>
                                        <Document />
                                    </el-icon> 爬虫日志</span>
                                <div>
                                    <el-button size="small" @click="clearLog" icon="Delete">
                                        清除
                                    </el-button>
                                    <el-button size="small" @click="exportLog" icon="Download">
                                        导出
                                    </el-button>
                                </div>
                            </div>
                        </template>

                        <div class="log-container">
                            <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="'log-' + log.type">
                                <span class="log-timestamp">{{ log.timestamp }}</span>
                                <el-tag size="small" :type="logTagType(log.type)" effect="dark" class="log-tag">
                                    {{ log.type.toUpperCase() }}
                                </el-tag>
                                <span class="log-message">{{ log.message }}</span>
                            </div>
                        </div>
                    </el-card>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<style scoped>
.crawler-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.crawler-status {
    display: flex;
    align-items: center;
    gap: 15px;
}

.crawler-time {
    font-size: 14px;
    color: #606266;
}

.crawler-controls {
    display: flex;
    gap: 10px;
}

.progress-card,
.config-card,
.log-card {
    margin-bottom: 20px;
}

.progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.current-url {
    margin-top: 15px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.url-label {
    font-size: 14px;
    color: #606266;
}

.stats-row {
    margin-top: 20px;
}

.stat-card {
    text-align: center;
    padding: 10px;
}

.stat-value {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 5px;
}

.stat-label {
    font-size: 12px;
    color: #909399;
}

.success-text {
    color: #67c23a;
}

.danger-text {
    color: #f56c6c;
}

.warning-text {
    color: #e6a23c;
}

.info-text {
    color: #409eff;
}

.config-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.log-container {
    height: 300px;
    overflow-y: auto;
    background-color: #1e1e1e;
    border-radius: 4px;
    padding: 10px;
    font-family: 'Courier New', monospace;
}

.log-entry {
    margin-bottom: 5px;
    padding: 5px;
    border-radius: 2px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: #e0e0e0;
}

.log-entry:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

.log-timestamp {
    color: #909399;
    font-size: 12px;
}

.log-tag {
    min-width: 52px;
    text-align: center;
}

.log-message {
    flex: 1;
}

.log-info {
    border-left: 3px solid #409eff;
}

.log-success {
    border-left: 3px solid #67c23a;
}

.log-warning {
    border-left: 3px solid #e6a23c;
}

.log-error {
    border-left: 3px solid #f56c6c;
}
</style>