<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import {
    VideoPlay,
    VideoPause,
    CircleClose,
    Setting,
    Loading,
    Document,
    Delete,
    Download
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { StartCrawler, StopCrawler, ContinueCrawler } from '@/api/crawler';

// 爬虫状态
const crawlerStatus = ref('stopped'); // 'stopped', 'running', 'paused'
const pagesCompleted = ref(0);
const totalPages = ref(0);
const successCount = ref(0);
const failureCount = ref(0);
const pendingCount = ref(0);
const crawlSpeed = ref(0);
const currentUrl = ref('');
const currentTitle = ref('');
const startTime = ref('');
const progressPercentage = ref(0);

const router = useRouter();

// SSE相关
let eventSource = null;
let crawlStartTime = null;

// 爬虫日志
const logs = ref([]);

//-------------------------------方法和计算属性--------------------------------

// 计算属性
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
    if (progressPercentage.value >= 100) return 'success';
    return '';
});

// 计算爬取速度
const calculateCrawlSpeed = () => {
    if (!crawlStartTime || pagesCompleted.value === 0) {
        crawlSpeed.value = 0;
        return;
    }

    const now = Date.now();
    const elapsedMinutes = (now - crawlStartTime) / 60000;

    if (elapsedMinutes > 0) {
        crawlSpeed.value = Math.round(pagesCompleted.value / elapsedMinutes);
    } else {
        crawlSpeed.value = 0;
    }
};

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

// 连接到进度更新
const connectToProgress = () => {
    // 关闭旧的连接
    if (eventSource) {
        eventSource.close();
    }

    // 创建新的SSE连接
    eventSource = new EventSource(`http://localhost:8000/crawler/get_progress`);

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);

            // 处理心跳
            if (data.type === 'heartbeat') {
                return;
            }

            // 根据消息类型更新状态
            switch (data.type) {
                case 'crawl_started':
                    // 爬虫开始，初始化状态
                    crawlerStatus.value = 'running';
                    totalPages.value = data.data.max_pages;
                    pagesCompleted.value = data.data.current_pages;
                    pendingCount.value = data.data.pending_urls;
                    crawlStartTime = Date.parse(data.timestamp);
                    startTime.value = new Date(data.timestamp).toLocaleString();

                    // 重置计数器
                    successCount.value = 0;
                    failureCount.value = 0;
                    crawlSpeed.value = 0;
                    progressPercentage.value = 0;

                    addLog('info', `爬虫已启动 - 最大页面数: ${data.data.max_pages}, 待处理URL: ${data.data.pending_urls}`);
                    break;

                case 'progress_update':
                    // 页面处理进度更新
                    pagesCompleted.value = data.data.current_pages;
                    totalPages.value = data.data.max_pages;
                    progressPercentage.value = data.data.progress_percentage;
                    successCount.value = data.data.current_pages; // 假设完成的都是成功的
                    currentUrl.value = data.data.url;
                    currentTitle.value = data.data.title || '无标题';

                    // 计算爬取速度
                    calculateCrawlSpeed();

                    addLog('success', `[${progressPercentage.value.toFixed(1)}%] 处理页面: ${data.data.title || data.data.url}`);
                    break;

                case 'iteration_update':
                    // 迭代更新
                    pagesCompleted.value = data.data.current_pages;
                    totalPages.value = data.data.max_pages;
                    pendingCount.value = data.data.pending_urls;
                    progressPercentage.value = data.data.progress_percentage;

                    // 更新爬虫状态
                    if (data.data.status === 'near_complete') {
                        addLog('info', `迭代 ${data.data.iteration}/${data.data.total_iterations} - 接近完成，剩余URL: ${data.data.pending_urls}`);
                    } else {
                        addLog('info', `迭代 ${data.data.iteration}/${data.data.total_iterations} - 进度: ${progressPercentage.value.toFixed(1)}%, 待处理: ${data.data.pending_urls}`);
                    }

                    calculateCrawlSpeed();
                    break;

                case 'crawl_completed':
                    // 爬取完成
                    crawlerStatus.value = 'stopped';
                    pagesCompleted.value = data.data.total_pages;
                    totalPages.value = data.data.max_pages;
                    successCount.value = data.data.total_pages;
                    pendingCount.value = 0;
                    progressPercentage.value = 100;

                    const duration = data.data.duration_seconds;
                    const minutes = Math.floor(duration / 60);
                    const seconds = Math.floor(duration % 60);
                    const timeStr = minutes > 0 ? `${minutes}分${seconds}秒` : `${seconds}秒`;

                    // 计算平均速度
                    const avgSpeed = duration > 0 ? (data.data.total_pages / (duration / 60)).toFixed(1) : 0;

                    addLog('success', `爬取完成！总页面: ${data.data.total_pages}, 耗时: ${timeStr}, 平均速度: ${avgSpeed} 页/分钟`);

                    // 显示完成通知
                    ElMessage.success({
                        message: `爬取完成！共爬取 ${data.data.total_pages} 个页面`,
                        duration: 5000
                    });

                    // 关闭SSE连接
                    if (eventSource) {
                        eventSource.close();
                        eventSource = null;
                    }
                    break;

                case 'error':
                    // 处理错误消息
                    addLog('error', `错误: ${data.message}`);
                    ElMessage.error(data.message);
                    break;

                case 'waiting':
                    // 等待状态
                    addLog('info', data.message);
                    break;

                default:
                    console.log('未知消息类型:', data.type, data);
                    addLog('warning', `收到未知消息类型: ${data.type}`);
            }

        } catch (error) {
            console.error('解析消息失败:', error);
            addLog('error', '解析进度消息失败: ' + error.message);
        }
    };

    eventSource.onerror = (error) => {
        console.error('SSE连接错误:', error);

        // 只有在爬虫运行中才显示连接错误
        if (crawlerStatus.value === 'running') {
            addLog('error', 'SSE连接断开，3秒后尝试重连...');

            // 关闭当前连接
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }

            // 3秒后重连
            setTimeout(() => {
                if (crawlerStatus.value === 'running') {
                    addLog('info', '尝试重新连接SSE...');
                    connectToProgress();
                }
            }, 3000);
        }
    };

    eventSource.onopen = () => {
        addLog('info', 'SSE连接已建立');
    };
};

// 启动爬虫
const startCrawler = async () => {
    try {
        // 重置所有状态
        pagesCompleted.value = 0;
        totalPages.value = 0;
        successCount.value = 0;
        failureCount.value = 0;
        pendingCount.value = 0;
        crawlSpeed.value = 0;
        progressPercentage.value = 0;
        currentUrl.value = '';
        currentTitle.value = '';
        logs.value = [];

        // 调用后端API启动爬虫
        const response = await StartCrawler();

        if (response.success || response.info) {
            const message = response.success || response.info;
            addLog('info', message);
            // 连接到SSE进度更新
            connectToProgress();
        } else if (response.error) {
            throw new Error(response.error);
        }

    } catch (error) {
        ElMessage.error('启动爬虫失败: ' + error.message);
        addLog('error', '启动爬虫失败: ' + error.message);
        crawlerStatus.value = 'stopped';
    }
};

// 暂停爬虫（实际调用后端API）
const pauseCrawler = async () => {
    try {
        if (!StopCrawler) {
            // 如果没有停止API，使用模拟暂停
            crawlerStatus.value = 'paused';
            addLog('warning', '注意：爬虫暂停功能未实现');
            return;
        }

        const response = await StopCrawler();

        if (response.success) {
            crawlerStatus.value = 'paused';
            addLog('info', response.success);
        } else if (response.error) {
            throw new Error(response.error);
        }
    } catch (error) {
        ElMessage.error('暂停爬虫失败: ' + error.message);
        addLog('error', '暂停爬虫失败: ' + error.message);
    }
};

// 恢复爬虫
const resumeCrawler = async () => {
    try {
        if (!ContinueCrawler) {
            // 如果没有恢复API，使用模拟恢复
            crawlerStatus.value = 'running';
            addLog('warning', '注意：爬虫恢复功能未实现');
            return;
        }

        const response = await ContinueCrawler();

        if (response.success) {
            crawlerStatus.value = 'running';
            addLog('info', response.success);
            // 重新连接进度
            connectToProgress();
        } else if (response.error) {
            throw new Error(response.error);
        }
    } catch (error) {
        ElMessage.error('恢复爬虫失败: ' + error.message);
        addLog('error', '恢复爬虫失败: ' + error.message);
    }
};

// 停止爬虫
const stopCrawler = async () => {
    try {
        if (!StopCrawler) {
            // 如果没有停止API，直接停止
            crawlerStatus.value = 'stopped';
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            addLog('warning', '爬虫已停止（本地）');
            return;
        }

        const response = await StopCrawler();

        if (response.success) {
            crawlerStatus.value = 'stopped';
            addLog('info', response.success);
        } else if (response.error) {
            throw new Error(response.error);
        }

    } catch (error) {
        ElMessage.error('停止爬虫失败: ' + error.message);
        addLog('error', '停止爬虫失败: ' + error.message);
    } finally {
        // 关闭SSE连接
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    }
};

// 处理配置跳转
const handleLink = () => {
    router.push({
        path: '/DocCrawler/CrawlerConfig'
    });
};

// 添加日志
const addLog = (type, message) => {
    const timestamp = new Date().toLocaleString();
    logs.value.push({ timestamp, type, message });

    // 限制日志数量，保持性能
    if (logs.value.length > 200) {
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

// 清除日志
const clearLog = () => {
    logs.value = [];
    addLog('info', '日志已清除');
};

// 导出日志
const exportLog = () => {
    const content = logs.value.map(log =>
        `${log.timestamp} [${log.type.toUpperCase()}] ${log.message}`
    ).join('\n');

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crawler_logs_${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);

    addLog('info', '日志已导出');
    ElMessage.success('日志已导出');
};

// 组件挂载时
onMounted(() => {
    // 添加初始日志
    setTimeout(() => {
        addLog('info', '爬虫控制面板已就绪');
        addLog('info', '请确保后端服务已启动 (http://localhost:8000)');
        addLog('info', '准备开始爬取，请点击"开始爬取"按钮');
    }, 500);
});

// 组件卸载时清理
onUnmounted(() => {
    if (eventSource) {
        eventSource.close();
    }
});
</script>

<template>
    <div class="doc-crawler" style="height: 100%;">
        <el-row style="height: 100%;">
            <el-col :span="24" style="display: flex;flex-direction: column;">
                <el-card style="margin-top: 10px;height: 95%;">
                    <!-- 爬虫控制和状态区域 -->
                    <div class="crawler-header">
                        <div class="crawler-status">
                            <el-tag :type="statusTagType" size="large">{{ crawlerStatusText }}</el-tag>
                            <span v-if="startTime" class="crawler-time">开始时间: {{ startTime }}</span>
                        </div>
                        <div class="crawler-controls">
                            <el-button type="primary" v-if="crawlerStatus === 'stopped'" @click="startCrawler"
                                :icon="VideoPlay">
                                开始爬取
                            </el-button>
                            <el-button type="warning" v-if="crawlerStatus === 'running'" @click="pauseCrawler"
                                :icon="VideoPause">
                                暂停
                            </el-button>
                            <el-button type="primary" v-if="crawlerStatus === 'paused'" @click="resumeCrawler"
                                :icon="VideoPlay">
                                恢复
                            </el-button>
                            <el-button type="danger" v-if="crawlerStatus === 'running' || crawlerStatus === 'paused'"
                                @click="stopCrawler" :icon="CircleClose">
                                停止
                            </el-button>
                            <el-button type="info" @click="handleLink" :icon="Setting">
                                配置
                            </el-button>
                        </div>
                    </div>

                    <!-- 爬虫进度区域 -->
                    <el-card class="progress-card" shadow="never">
                        <template #header>
                            <div class="progress-header">
                                <span>
                                    <el-icon>
                                        <Loading />
                                    </el-icon> 爬虫进度
                                </span>
                                <span>{{ pagesCompleted }} / {{ totalPages }} 页面</span>
                            </div>
                        </template>

                        <el-progress :percentage="progressPercentage" :status="progressStatus" :stroke-width="15"
                            :format="(p) => p.toFixed(1) + '%'" />

                        <div class="current-url">
                            <span class="url-label">当前URL:</span>
                            <el-tag size="small" effect="plain">
                                {{ currentUrl || '尚未开始' }}
                            </el-tag>
                        </div>

                        <div class="current-title" v-if="currentTitle">
                            <span class="title-label">页面标题:</span>
                            <span class="title-text">{{ currentTitle }}</span>
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

                    <!-- 爬虫日志区域 -->
                    <el-card class="log-card" shadow="never">
                        <template #header>
                            <div class="log-header">
                                <span>
                                    <el-icon>
                                        <Document />
                                    </el-icon> 爬虫日志
                                </span>
                                <div>
                                    <el-button size="small" @click="clearLog" :icon="Delete">
                                        清除
                                    </el-button>
                                    <el-button size="small" @click="exportLog" :icon="Download">
                                        导出
                                    </el-button>
                                </div>
                            </div>
                        </template>

                        <div class="log-container">
                            <div v-for="(log, index) in logs" :key="index" class="log-entry" :class="'log-' + log.type" style="text-align: left;font-size: small;">
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
    padding-bottom: 20px;
    border-bottom: 1px solid #EBEEF5;
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

.current-url .el-tag {
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.current-title {
    margin-top: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.title-label {
    font-size: 14px;
    color: #606266;
    min-width: 60px;
}

.title-text {
    font-size: 14px;
    color: #303133;
}

.stats-row {
    margin-top: 20px;
}

.stat-card {
    text-align: center;
    padding: 10px;
    transition: transform 0.3s;
}

.stat-card:hover {
    transform: translateY(-2px);
}

.stat-value {
    font-size: 28px;
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
    padding: 5px 8px;
    border-radius: 2px;
    display: flex;
    align-items: center;
    gap: 10px;
    color: #e0e0e0;
    transition: background-color 0.2s;
}

.log-entry:hover {
    background-color: rgba(255, 255, 255, 0.05);
}

.log-timestamp {
    color: #909399;
    font-size: 12px;
    min-width: 140px;
}

.log-tag {
    min-width: 60px;
    text-align: center;
}

.log-message {
    flex: 1;
    word-wrap: break-word;
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

/* 滚动条样式 */
.log-container::-webkit-scrollbar {
    width: 8px;
}

.log-container::-webkit-scrollbar-track {
    background: #2d2d2d;
    border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb {
    background: #555;
    border-radius: 4px;
}

.log-container::-webkit-scrollbar-thumb:hover {
    background: #777;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .crawler-header {
        flex-direction: column;
        gap: 15px;
        align-items: flex-start;
    }

    .crawler-controls {
        flex-wrap: wrap;
    }

    .stats-row .el-col {
        margin-bottom: 10px;
    }
}
</style>