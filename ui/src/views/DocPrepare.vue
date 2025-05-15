<template>
    <div class="doc-processing-container">
        <el-card class="content-card">
            <el-tabs v-model="activeTab">
                <el-tab-pane name="preprocessing" label="文档预处理">
                    <template #label>
                        <div class="tab-label">
                            <el-icon><el-icon-filter /></el-icon>
                            文档预处理
                        </div>
                    </template>
                </el-tab-pane>
                <el-tab-pane name="indexing" label="索引构建">
                    <template #label>
                        <div class="tab-label">
                            <el-icon><el-icon-data-analysis /></el-icon>
                            索引构建
                        </div>
                    </template>
                </el-tab-pane>
            </el-tabs>

            <div class="tab-content">
                <!-- 预处理设置面板 -->
                <div v-if="activeTab === 'preprocessing'" class="preprocessing-panel">
                    <!-- 数据源配置 -->
                    <div class="data-source-panel">
                        <h2 class="section-title">
                            <el-icon><el-icon-folder-opened /></el-icon>
                            检测到已爬取数据
                        </h2>
                        <el-row :gutter="20">
                            <el-col :span="24">
                                ...
                            </el-col>
                        </el-row>
                    </div>

                    <div class="stopwords-section">
                        <h3 class="subsection-title">停用词设置</h3>
                        <el-form-item label="停用词表文件">
                            <el-input v-model="stopwordsPath" placeholder="./cn_stopwords.txt" readonly>
                            </el-input>
                        </el-form-item>
                    </div>

                    <div class="tfidf-settings">
                        <h3 class="subsection-title">TF-IDF向量化设置</h3>
                        <el-row :gutter="20">
                            <el-col :span="12">
                                <el-form-item label="最小文档频率">
                                    <el-input-number v-model="tfIdfSettings.minDf" :min="1" :max="10" />
                                </el-form-item>
                            </el-col>
                            <el-col :span="12">
                                <el-form-item label="最大文档频率">
                                    <el-slider v-model="tfIdfSettings.maxDf" :min="0.5" :max="1" :step="0.05" />
                                    <div class="slider-value">{{ tfIdfSettings.maxDf }}</div>
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </div>
                </div>

                <!-- 索引设置面板 -->
                <div v-else class="indexing-panel">
                    <!-- 数据源配置 -->
                    <div class="data-source-panel">
                        <h2 class="section-title">
                            <el-icon><el-icon-folder-opened /></el-icon>
                            检测到预处理数据
                        </h2>

                        <el-row :gutter="20">
                            <el-col :span="24">
                                ...
                            </el-col>
                        </el-row>
                    </div>

                    <div class="index-type-section">
                        <div class="form-label">索引类型</div>
                        <el-select v-model="indexSettings.indexType" class="index-type-select">
                            <el-option label="倒排索引" value="inverted" />
                        </el-select>
                    </div>

                    <div class="advanced-options">
                        <h3 class="subsection-title">索引高级选项</h3>

                        <div class="form-group">
                            <div class="form-label">索引优化</div>
                            <el-switch v-model="indexSettings.optimize" style="width: 100%;" />

                            <div v-if="indexSettings.optimize" class="sub-setting">
                                <div class="form-label">最小 TF-IDF 阈值</div>
                                <el-slider v-model="indexSettings.minTfIdf" :min="0.001" :max="0.1" :step="0.001"
                                    :format-tooltip="value => value.toFixed(3)" />
                                <div class="slider-value">{{ indexSettings.minTfIdf.toFixed(3) }}</div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="action-bar">
                    <div class="action-buttons" style="margin: 0 auto;">
                        <el-button v-if="activeTab === 'preprocessing'" type="primary"
                            :loading="processingStatus === 'processing'" @click="startPreprocessing">
                            <template v-if="processingStatus === 'idle'">
                                <el-icon class="btn-icon"><el-icon-refresh /></el-icon>
                                开始预处理
                            </template>
                            <template v-else-if="processingStatus === 'processing'">
                                处理中...
                            </template>
                            <template v-else>
                                <el-icon class="btn-icon"><el-icon-check /></el-icon>
                                预处理完成
                            </template>
                        </el-button>

                        <el-button v-else type="primary" :loading="indexingStatus === 'processing'"
                            :disabled="indexingStatus === 'processing' || !indexSettings.preprocessedDataDir"
                            @click="startIndexing">
                            <template v-if="indexingStatus === 'idle'">
                                <el-icon class="btn-icon"><el-icon-refresh /></el-icon>
                                开始构建索引
                            </template>
                            <template v-else-if="indexingStatus === 'processing'">
                                构建中...
                            </template>
                            <template v-else>
                                <el-icon class="btn-icon"><el-icon-check /></el-icon>
                                索引构建完成
                            </template>
                        </el-button>
                    </div>
                </div>

                <!-- 处理完成状态 -->
                <div v-if="processingStatus === 'completed' && activeTab === 'preprocessing'" class="result-panel">
                    <el-result icon="success" title="预处理成功" sub-title="文档预处理完成，可以进行索引构建。">
                        <template #extra>
                            <el-row :gutter="20" class="stats-grid">
                                <el-col :span="8">
                                    <el-card class="stat-card">
                                        <div class="stat-label">处理文档数</div>
                                        <div class="stat-value">{{ preprocessingStats.docCount }}</div>
                                    </el-card>
                                </el-col>
                                <el-col :span="8">
                                    <el-card class="stat-card">
                                        <div class="stat-label">特征词汇量</div>
                                        <div class="stat-value">{{ preprocessingStats.vocabSize }}</div>
                                    </el-card>
                                </el-col>
                                <el-col :span="8">
                                    <el-card class="stat-card">
                                        <div class="stat-label">去重率</div>
                                        <div class="stat-value">{{ preprocessingStats.duplicationRate }}%</div>
                                    </el-card>
                                </el-col>
                            </el-row>
                            <div class="result-actions">
                                <el-button type="primary" link @click="viewPreprocessingReport">
                                    <el-icon><el-icon-document /></el-icon>
                                    查看预处理报告
                                </el-button>
                                <el-button type="primary" @click="goToIndexing">
                                    <el-icon><el-icon-right /></el-icon>
                                    继续构建索引
                                </el-button>
                            </div>
                        </template>
                    </el-result>
                </div>

                <!-- 索引构建完成状态 -->
                <div v-if="indexingStatus === 'completed' && activeTab === 'indexing'" class="result-panel">
                    <el-result icon="success" title="索引构建成功" sub-title="索引已成功构建，现在可以进行检索。">
                        <template #extra>
                            <el-row :gutter="20" class="stats-grid">
                                <el-col :span="8">
                                    <el-card class="stat-card">
                                        <div class="stat-label">索引词条数</div>
                                        <div class="stat-value">{{ indexingStats.termCount }}</div>
                                    </el-card>
                                </el-col>
                                <el-col :span="8">
                                    <el-card class="stat-card">
                                        <div class="stat-label">索引条目数</div>
                                        <div class="stat-value">{{ indexingStats.entryCount }}</div>
                                    </el-card>
                                </el-col>
                                <el-col :span="8">
                                    <el-card class="stat-card">
                                        <div class="stat-label">索引大小</div>
                                        <div class="stat-value">{{ indexingStats.indexSize }}</div>
                                    </el-card>
                                </el-col>
                            </el-row>
                            <div class="result-actions">
                                <el-button type="primary" link @click="viewIndexMetadata">
                                    <el-icon><el-icon-document /></el-icon>
                                    查看索引元数据
                                </el-button>
                                <el-button type="primary" @click="goToSearch">
                                    <el-icon><el-icon-search /></el-icon>
                                    开始检索
                                </el-button>
                            </div>
                        </template>
                    </el-result>
                </div>
            </div>
        </el-card>

        <!-- 处理日志对话框 -->
        <el-dialog v-model="logDialogVisible" title="处理日志" width="70%">
            <div class="log-container">
                <div v-for="(log, index) in processLogs" :key="index" :class="['log-item', log.level.toLowerCase()]">
                    <span class="log-time">{{ log.time }}</span>
                    <span class="log-level">{{ log.level }}</span>
                    <span class="log-message">{{ log.message }}</span>
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="logDialogVisible = false">关闭</el-button>
                    <el-button type="primary" @click="downloadLogs">
                        <el-icon><el-icon-download /></el-icon>
                        下载日志
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 预处理报告对话框 -->
        <el-dialog v-model="reportDialogVisible" title="预处理报告" width="70%">
            <div class="report-container">
                <div v-if="preprocessingReport">
                    <h3>基本信息</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="总文档数">{{ preprocessingReport.docCount }}</el-descriptions-item>
                        <el-descriptions-item label="处理耗时">{{ preprocessingReport.processingTime
                            }}秒</el-descriptions-item>
                        <el-descriptions-item label="特征词汇量">{{ preprocessingReport.vocabSize }}</el-descriptions-item>
                        <el-descriptions-item label="TF-IDF矩阵维度">{{ preprocessingReport.matrixDimension
                            }}</el-descriptions-item>
                        <el-descriptions-item label="TF-IDF矩阵稀疏度">{{ preprocessingReport.matrixSparsity
                            }}</el-descriptions-item>
                    </el-descriptions>

                    <h3>文档统计</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="标题平均长度">{{ preprocessingReport.avgTitleLength
                            }}字符</el-descriptions-item>
                        <el-descriptions-item label="内容平均长度">{{ preprocessingReport.avgContentLength
                            }}字符</el-descriptions-item>
                        <el-descriptions-item label="标题平均分词数">{{ preprocessingReport.avgTitleTokens
                            }}</el-descriptions-item>
                        <el-descriptions-item label="内容平均分词数">{{ preprocessingReport.avgContentTokens
                            }}</el-descriptions-item>
                    </el-descriptions>

                    <h3>去重信息</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="原始文档数">{{ preprocessingReport.originalDocCount
                            }}</el-descriptions-item>
                        <el-descriptions-item label="移除重复文档数">{{ preprocessingReport.duplicatesRemoved
                            }}</el-descriptions-item>
                        <el-descriptions-item label="重复率">{{ preprocessingReport.duplicationRate
                            }}%</el-descriptions-item>
                    </el-descriptions>

                    <h3>文档来源统计</h3>
                    <el-table :data="sourceStats" style="width: 100%">
                        <el-table-column prop="source" label="来源" />
                        <el-table-column prop="count" label="文档数" />
                    </el-table>
                </div>
                <div v-else>
                    加载报告中...
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="reportDialogVisible = false">关闭</el-button>
                    <el-button type="primary" @click="downloadReport">
                        <el-icon><el-icon-download /></el-icon>
                        下载报告
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 索引元数据对话框 -->
        <el-dialog v-model="indexMetaDialogVisible" title="索引元数据" width="70%">
            <div class="meta-container">
                <div v-if="indexMetadata">
                    <h3>基本信息</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="创建时间">{{ indexMetadata.indexCreatedTime }}</el-descriptions-item>
                        <el-descriptions-item label="总文档数">{{ indexMetadata.totalDocuments }}</el-descriptions-item>
                        <el-descriptions-item label="词汇量">{{ indexMetadata.vocabularySize }}</el-descriptions-item>
                        <el-descriptions-item label="索引条目数">{{ indexMetadata.totalIndexEntries }}</el-descriptions-item>
                        <el-descriptions-item label="每个词条平均索引条目">{{ indexMetadata.averagePostingsPerTerm
                            }}</el-descriptions-item>
                    </el-descriptions>

                    <h3 v-if="indexMetadata.optimized">优化信息</h3>
                    <el-descriptions v-if="indexMetadata.optimized" :column="2" border>
                        <el-descriptions-item label="优化阈值">{{ indexMetadata.optimizationThreshold
                            }}</el-descriptions-item>
                        <el-descriptions-item label="原始词条数">{{ indexMetadata.originalTerms }}</el-descriptions-item>
                        <el-descriptions-item label="优化后词条数">{{ indexMetadata.optimizedTerms }}</el-descriptions-item>
                        <el-descriptions-item label="原始索引条目数">{{ indexMetadata.originalEntries }}</el-descriptions-item>
                        <el-descriptions-item label="优化后索引条目数">{{ indexMetadata.optimizedEntries
                            }}</el-descriptions-item>
                        <el-descriptions-item label="减少率">
                            词条: {{ indexMetadata.reductionPercentage.terms }}%，
                            条目: {{ indexMetadata.reductionPercentage.entries }}%
                        </el-descriptions-item>
                    </el-descriptions>
                </div>
                <div v-else>
                    加载元数据中...
                </div>
            </div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="indexMetaDialogVisible = false">关闭</el-button>
                    <el-button type="primary" @click="downloadIndexMetadata">
                        <el-icon><el-icon-download /></el-icon>
                        下载元数据
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import {
    ElCard, ElTabs, ElTabPane, ElRow, ElCol, ElSwitch,
    ElSelect, ElOption, ElInputNumber, ElButton, ElResult,
    ElIcon, ElDialog, ElDescriptions, ElDescriptionsItem,
    ElTable, ElTableColumn, ElFormItem, ElInput, ElSlider
} from 'element-plus';
import {
    Filter as ElIconFilter,
    DataAnalysis as ElIconDataAnalysis,
    Refresh as ElIconRefresh,
    Check as ElIconCheck,
    Document as ElIconDocument,
    Right as ElIconRight,
    Search as ElIconSearch,
    Download as ElIconDownload,
    Folder as ElIconFolder,
    FolderOpened as ElIconFolderOpened,
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

// 类型定义
interface PreprocessingSettings {
    tokenization: boolean;
    removeStopwords: boolean;
    stemming: boolean;
    lemmatization: boolean;
    caseFolding: boolean;
    removeNumbers: boolean;
    removePunctuation: boolean;
}

interface TfIdfSettings {
    minDf: number;
    maxDf: number;
}

interface IndexSettings {
    preprocessedDataDir: string;
    outputDir: string;
    indexType: string;
    compressionEnabled: boolean;
    includePositions: boolean;
    includeFrequency: boolean;
    storeOriginalText: boolean;
    optimize: boolean;
    minTfIdf: number;
}

interface ProcessingStats {
    docCount: number;
    vocabSize: number;
    duplicationRate: number;
}

interface IndexingStats {
    termCount: number;
    entryCount: number;
    indexSize: string;
}

interface LogEntry {
    time: string;
    level: string;
    message: string;
}

interface PreprocessingReport {
    docCount: number;
    processingTime: number;
    vocabSize: number;
    matrixDimension: string;
    matrixSparsity: number;
    avgTitleLength: number;
    avgContentLength: number;
    avgTitleTokens: number;
    avgContentTokens: number;
    originalDocCount: number;
    duplicatesRemoved: number;
    duplicationRate: number;
    sourceStats: {
        source: string;
        count: number;
    }[];
}

interface IndexMetadata {
    indexCreatedTime: string;
    totalDocuments: number;
    vocabularySize: number;
    totalIndexEntries: number;
    averagePostingsPerTerm: number;
    optimized: boolean;
    optimizationThreshold: number;
    originalTerms: number;
    originalEntries: number;
    optimizedTerms: number;
    optimizedEntries: number;
    reductionPercentage: {
        terms: number;
        entries: number;
    };
}


// 组件状态
const activeTab = ref('preprocessing');
const selectedFiles = ref<any[]>([]);
const dataSourceType = ref('database');
const stopwordsPath = ref('../cn_stopwords.txt');
const processingStatus = ref<'idle' | 'processing' | 'completed'>('idle');
const indexingStatus = ref<'idle' | 'processing' | 'completed'>('idle');
const ngramSize = ref(3);

// 对话框状态
const logDialogVisible = ref(false);
const reportDialogVisible = ref(false);
const indexMetaDialogVisible = ref(false);

// 日志和报告数据
const processLogs = ref<LogEntry[]>([]);
const preprocessingReport = ref<PreprocessingReport | null>(null);
const indexMetadata = ref<IndexMetadata | null>(null);
const sourceStats = ref<{ source: string, count: number }[]>([]);

// 预处理设置
const preprocessingSettings = reactive<PreprocessingSettings>({
    tokenization: true,
    removeStopwords: true,
    stemming: false,
    lemmatization: true,
    caseFolding: true,
    removeNumbers: false,
    removePunctuation: true
});

// TF-IDF设置
const tfIdfSettings = reactive<TfIdfSettings>({
    minDf: 2,
    maxDf: 0.95
});

// 索引设置
const indexSettings = reactive<IndexSettings>({
    preprocessedDataDir: '../data/preprocessed_data',
    outputDir: '../data/preprocessed_data/inverted_index',
    indexType: 'inverted',
    compressionEnabled: true,
    includePositions: true,
    includeFrequency: true,
    storeOriginalText: true,
    optimize: true,
    minTfIdf: 0.01
});

// 处理结果统计
const preprocessingStats = reactive<ProcessingStats>({
    docCount: 0,
    vocabSize: 0,
    duplicationRate: 0
});

// 索引统计
const indexingStats = reactive<IndexingStats>({
    termCount: 0,
    entryCount: 0,
    indexSize: ''
});


// 添加日志
const addLog = (level: string, message: string) => {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    processLogs.value.push({
        time: timeStr,
        level,
        message
    });
};

// 预处理相关方法
const startPreprocessing = async () => {
    if (processingStatus.value === 'processing') {
        return;
    }

    processingStatus.value = 'processing';
    processLogs.value = []; // 清空日志
    addLog('INFO', '开始文档预处理...');

    try {
        // 调用预处理API
        // 假设有一个API端点 /api/preprocess
        addLog('INFO', '正在调用预处理API...');

        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 3000));

        // 模拟API响应
        const response = {
            success: true,
            data: {
                docCount: 1256,
                vocabSize: 23654,
                duplicationRate: 12.5,
                processingTime: 45.6,
                matrixDimension: "1256 x 23654",
                matrixSparsity: 0.994,
                avgTitleLength: 32.5,
                avgContentLength: 1458.7,
                avgTitleTokens: 8.3,
                avgContentTokens: 342.1,
                originalDocCount: 1435,
                duplicatesRemoved: 179,
                sourceStats: [
                    { source: "新闻网站", count: 756 },
                    { source: "政府公告", count: 324 },
                    { source: "学术文章", count: 176 }
                ]
            }
        };

        // 处理响应
        if (response.success) {
            // 更新预处理统计信息
            preprocessingStats.docCount = response.data.docCount;
            preprocessingStats.vocabSize = response.data.vocabSize;
            preprocessingStats.duplicationRate = response.data.duplicationRate;

            // 保存预处理报告
            preprocessingReport.value = response.data;
            sourceStats.value = response.data.sourceStats;

            addLog('INFO', '预处理成功完成!');
            processingStatus.value = 'completed';

            // 设置索引构建的预处理数据目录
            indexSettings.preprocessedDataDir = '../data/preprocessed_data';
        } else {
            throw new Error('API返回处理失败');
        }
    } catch (error) {
        addLog('ERROR', `预处理失败: ${error}`);
        ElMessage.error('预处理失败，请查看日志获取详细信息。');
        processingStatus.value = 'idle';
    }
};

// 索引构建相关方法
const startIndexing = async () => {
    if (indexingStatus.value === 'processing') {
        return;
    }

    indexingStatus.value = 'processing';
    processLogs.value = []; // 清空日志
    addLog('INFO', '开始构建索引...');

    try {
        // 构建索引请求参数
        const params = {
            preprocessedDataDir: indexSettings.preprocessedDataDir,
            outputDir: indexSettings.outputDir,
            indexType: indexSettings.indexType,
            optimize: indexSettings.optimize,
            minTfIdf: indexSettings.minTfIdf,
            compressionEnabled: indexSettings.compressionEnabled,
            includePositions: indexSettings.includePositions,
            includeFrequency: indexSettings.includeFrequency,
            storeOriginalText: indexSettings.storeOriginalText,
            ngramSize: indexSettings.indexType === 'ngram' ? ngramSize.value : null
        };

        // 调用索引构建API
        addLog('INFO', '正在调用索引构建API...');

        // 模拟API调用
        await new Promise(resolve => setTimeout(resolve, 2500));

        // 模拟API响应
        const response = {
            success: true,
            data: {
                termCount: 15420,
                entryCount: 985632,
                indexSize: '3.75 MB',
                metadata: {
                    indexCreatedTime: '2025-05-14 15:30:45',
                    totalDocuments: 1256,
                    vocabularySize: 15420,
                    totalIndexEntries: 985632,
                    averagePostingsPerTerm: 63.9,
                    optimized: true,
                    optimizationThreshold: 0.01,
                    originalTerms: 23654,
                    originalEntries: 1458963,
                    optimizedTerms: 15420,
                    optimizedEntries: 985632,
                    reductionPercentage: {
                        terms: 34.8,
                        entries: 32.4
                    }
                }
            }
        };

        // 处理响应
        if (response.success) {
            // 更新索引统计信息
            indexingStats.termCount = response.data.termCount;
            indexingStats.entryCount = response.data.entryCount;
            indexingStats.indexSize = response.data.indexSize;

            // 保存索引元数据
            indexMetadata.value = response.data.metadata;

            addLog('INFO', '索引构建成功完成!');
            indexingStatus.value = 'completed';
        } else {
            throw new Error('API返回处理失败');
        }
    } catch (error) {
        addLog('ERROR', `索引构建失败: ${error}`);
        ElMessage.error('索引构建失败，请查看日志获取详细信息。');
        indexingStatus.value = 'idle';
    }
};

// 下载日志
const downloadLogs = () => {
    const logText = processLogs.value.map(log => `${log.time} [${log.level}] ${log.message}`).join('\n');
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'processing_logs.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// 查看预处理报告
const viewPreprocessingReport = () => {
    if (preprocessingReport.value) {
        reportDialogVisible.value = true;
    } else {
        ElMessage.warning('预处理报告不可用');
    }
};

// 下载预处理报告
const downloadReport = () => {
    if (!preprocessingReport.value) return;

    const reportText = JSON.stringify(preprocessingReport.value, null, 2);
    const blob = new Blob([reportText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'preprocessing_report.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// 查看索引元数据
const viewIndexMetadata = () => {
    if (indexMetadata.value) {
        indexMetaDialogVisible.value = true;
    } else {
        ElMessage.warning('索引元数据不可用');
    }
};

// 下载索引元数据
const downloadIndexMetadata = () => {
    if (!indexMetadata.value) return;

    const metadataText = JSON.stringify(indexMetadata.value, null, 2);
    const blob = new Blob([metadataText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'index_metadata.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// 导航到索引构建
const goToIndexing = () => {
    activeTab.value = 'indexing';
};

// 导航到搜索页面
const goToSearch = () => {
    // 这里实现导航到搜索页面的逻辑
    ElMessage.success('正在跳转到搜索页面...');
    // 例如: router.push('/search');
};

// 监听数据源类型变化
watch(dataSourceType, (newType) => {
    if (newType === 'files') {
        selectedFiles.value = [];
    }
});
</script>

<style scoped>
.doc-processing-container {
    width: 100%;
}

.tab-label {
    display: flex;
    align-items: center;
    gap: 5px;
}

.section-title {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: 500;
    margin-bottom: 20px;
    color: #303133;
}

.section-title .el-icon {
    margin-right: 8px;
    color: #409EFF;
}

.subsection-title {
    font-size: 16px;
    font-weight: 500;
    margin: 20px 0 10px 0;
    color: #697ba0;
}

.tab-content {
    padding: 20px 0;
}

.data-source-panel,
.preprocessing-panel,
.indexing-panel {
    margin-bottom: 30px;
}

.setting-item {
    margin-bottom: 15px;
    transition: all 0.3s;
}

.setting-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.setting-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.language-section,
.stopwords-section,
.tfidf-settings,
.index-type-section,
.data-path-section,
.advanced-options {
    margin-top: 30px;
    padding: 15px;
    background-color: #f9f9f9;
    border-radius: 8px;
}

.language-select,
.index-type-select,
.weighting-select {
    width: 100%;
    max-width: 300px;
}

.form-label {
    font-size: 14px;
    margin-bottom: 8px;
    color: #606266;
    text-align: left;
}

.form-group {
    margin-bottom: 20px;
}

.sub-setting {
    margin-top: 10px;
    padding-left: 20px;
    border-left: 2px solid #e6e6e6;
}

.slider-value {
    font-size: 12px;
    color: #909399;
    text-align: right;
    margin-top: 5px;
}

.action-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
}

.status-panel {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #606266;
}

.action-buttons {
    display: flex;
    gap: 10px;
}

.btn-icon {
    margin-right: 5px;
}

.result-panel {
    margin-top: 30px;
    padding: 20px;
    background-color: #f9fafc;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.stats-grid {
    margin: 20px 0;
}

.stat-card {
    text-align: center;
    transition: all 0.3s;
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.stat-label {
    font-size: 14px;
    color: #909399;
}

.stat-value {
    font-size: 24px;
    font-weight: 600;
    color: #303133;
    margin-top: 8px;
}

.result-actions {
    margin-top: 20px;
    display: flex;
    justify-content: center;
    gap: 16px;
}

.log-container {
    height: 400px;
    overflow-y: auto;
    padding: 10px;
    font-family: monospace;
    background-color: #1e1e1e;
    color: #d4d4d4;
    border-radius: 4px;
}

.log-item {
    padding: 4px 0;
    border-bottom: 1px solid #333;
    line-height: 1.5;
}

.log-time {
    color: #6a9955;
    margin-right: 10px;
}

.log-level {
    font-weight: bold;
    margin-right: 10px;
    padding: 2px 5px;
    border-radius: 3px;
}

.info .log-level {
    background-color: #294e80;
    color: #ffffff;
}

.error .log-level {
    background-color: #a31515;
    color: #ffffff;
}

.warning .log-level {
    background-color: #966000;
    color: #ffffff;
}

.log-message {
    color: #d4d4d4;
}

.report-container,
.meta-container {
    max-height: 500px;
    overflow-y: auto;
    padding: 15px;
}

.report-container h3,
.meta-container h3 {
    margin-top: 20px;
    margin-bottom: 10px;
    color: #409EFF;
    font-weight: 500;
}

/* 适配移动设备 */
@media (max-width: 768px) {
    .settings-grid {
        display: block;
    }

    .stats-grid .el-col {
        margin-bottom: 15px;
    }

    .action-bar {
        flex-direction: column;
        gap: 15px;
    }

    .status-panel,
    .action-buttons {
        width: 100%;
    }
}
</style>