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

.stopwords-section,
.tfidf-settings,
.index-type-section,
.advanced-options {
    margin-top: 20px;
    padding: 15px;
    background-color: var(--secondar-color);
    border-color: var(--border-color);
    border-radius: 8px;
}

.index-type-select {
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
    justify-content: center;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
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
    border-bottom: 1px solid #EBEEF5;
    padding-bottom: 10px;
}

.total-size-info {
    margin-top: 15px;
    padding: 10px;
    background-color: #f0f9ff;
    border-radius: 4px;
    border-left: 3px solid #409EFF;
}

/* 适配移动设备 */
@media (max-width: 768px) {
    .stats-grid .el-col {
        margin-bottom: 15px;
    }

    .action-bar {
        flex-direction: column;
        gap: 15px;
    }
}
</style>
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
                    <!-- <div class="data-source-panel">
                        <h2 class="section-title">
                            <el-icon><el-icon-folder-opened /></el-icon>
                            检测到已爬取数据
                        </h2>
                        <el-row :gutter="20">
                            <el-col :span="24">
                                ...
                            </el-col>
                        </el-row>
                    </div> -->

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
                    <!-- <div class="data-source-panel">
                        <h2 class="section-title">
                            <el-icon><el-icon-folder-opened /></el-icon>
                            检测到预处理数据
                        </h2>

                        <el-row :gutter="20">
                            <el-col :span="24">
                                ...
                            </el-col>
                        </el-row>
                    </div> -->

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
                            :disabled="indexingStatus === 'processing'" @click="startIndexing">
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
                        <el-descriptions-item label="处理起始时间">{{
                            preprocessingReport.performance_metrics.processing_start_time }}</el-descriptions-item>
                        <el-descriptions-item label="处理结束时间">{{
                            preprocessingReport.performance_metrics.processing_end_time }}</el-descriptions-item>
                        <el-descriptions-item label="总处理耗时">{{
                            preprocessingReport.performance_metrics.total_processing_time_seconds.toFixed(2) }}秒 ({{
                                preprocessingReport.performance_metrics.total_processing_time_minutes.toFixed(2)
                            }}分钟)</el-descriptions-item>
                    </el-descriptions>

                    <h3>文档统计</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="总文档数">{{ preprocessingReport.document_statistics.total_documents
                            }}</el-descriptions-item>
                        <el-descriptions-item label="原始文档数">{{
                            preprocessingReport.document_statistics.original_documents }}</el-descriptions-item>
                        <el-descriptions-item label="移除重复文档数">{{
                            preprocessingReport.document_statistics.duplicates_removed }}</el-descriptions-item>
                        <el-descriptions-item label="重复率">{{
                            preprocessingReport.document_statistics.duplicate_percentage.toFixed(2)
                            }}%</el-descriptions-item>
                    </el-descriptions>

                    <h3>内容统计</h3>
                    <el-tabs type="border-card">
                        <el-tab-pane label="标题">
                            <el-descriptions :column="2" border>
                                <el-descriptions-item label="平均字符长度">{{
                                    preprocessingReport.content_statistics.title_length.mean_chars.toFixed(2)
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最大字符长度">{{
                                    preprocessingReport.content_statistics.title_length.max_chars
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最小字符长度">{{
                                    preprocessingReport.content_statistics.title_length.min_chars
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="平均分词数">{{
                                    preprocessingReport.content_statistics.title_words.mean_count.toFixed(2)
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最大分词数">{{
                                    preprocessingReport.content_statistics.title_words.max_count
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最小分词数">{{
                                    preprocessingReport.content_statistics.title_words.min_count
                                    }}</el-descriptions-item>
                            </el-descriptions>
                        </el-tab-pane>
                        <el-tab-pane label="内容">
                            <el-descriptions :column="2" border>
                                <el-descriptions-item label="平均字符长度">{{
                                    preprocessingReport.content_statistics.content_length.mean_chars.toFixed(2)
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最大字符长度">{{
                                    preprocessingReport.content_statistics.content_length.max_chars
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最小字符长度">{{
                                    preprocessingReport.content_statistics.content_length.min_chars
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="平均分词数">{{
                                    preprocessingReport.content_statistics.content_words.mean_count.toFixed(2)
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最大分词数">{{
                                    preprocessingReport.content_statistics.content_words.max_count
                                    }}</el-descriptions-item>
                                <el-descriptions-item label="最小分词数">{{
                                    preprocessingReport.content_statistics.content_words.min_count
                                    }}</el-descriptions-item>
                            </el-descriptions>
                        </el-tab-pane>
                    </el-tabs>

                    <h3>向量化统计</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="词汇量大小">{{
                            preprocessingReport.vectorization_statistics.vocabulary_size }}</el-descriptions-item>
                        <el-descriptions-item label="TF-IDF矩阵维度">{{
                            preprocessingReport.vectorization_statistics.tfidf_matrix_shape.rows }} × {{
                                preprocessingReport.vectorization_statistics.tfidf_matrix_shape.columns
                            }}</el-descriptions-item>
                        <el-descriptions-item label="TF-IDF矩阵稀疏度">{{
                            (preprocessingReport.vectorization_statistics.tfidf_matrix_sparsity * 100).toFixed(2)
                            }}%</el-descriptions-item>
                        <el-descriptions-item label="非零元素数量">{{
                            preprocessingReport.vectorization_statistics.nonzero_elements }}</el-descriptions-item>
                    </el-descriptions>

                    <h3>配置参数</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="最小文档频率(min_df)">{{
                            preprocessingReport.configuration.tfidf_params.min_df }}</el-descriptions-item>
                        <el-descriptions-item label="最大文档频率(max_df)">{{
                            preprocessingReport.configuration.tfidf_params.max_df }}</el-descriptions-item>
                        <el-descriptions-item label="样本大小">{{ preprocessingReport.configuration.sample_size
                            }}</el-descriptions-item>
                        <el-descriptions-item label="停用词数量">{{ preprocessingReport.configuration.stopwords_count
                            }}</el-descriptions-item>
                    </el-descriptions>

                    <h3>输出文件</h3>
                    <el-table :data="outputFilesData" style="width: 100%">
                        <el-table-column prop="name" label="文件名" />
                        <el-table-column prop="path" label="路径" />
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
                        <el-descriptions-item label="构建开始时间">{{ indexMetadata.performance_metrics.build_start_time
                            }}</el-descriptions-item>
                        <el-descriptions-item label="构建结束时间">{{ indexMetadata.performance_metrics.build_end_time
                            }}</el-descriptions-item>
                        <el-descriptions-item label="总构建时间">{{
                            indexMetadata.performance_metrics.total_build_time_seconds.toFixed(2) }}秒 ({{
                                indexMetadata.performance_metrics.total_build_time_minutes.toFixed(2)
                            }}分钟)</el-descriptions-item>
                    </el-descriptions>

                    <h3>索引统计</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="总文档数">{{ indexMetadata.document_statistics.total_documents
                            }}</el-descriptions-item>
                        <el-descriptions-item label="总词条数">{{ indexMetadata.index_statistics.total_terms
                            }}</el-descriptions-item>
                        <el-descriptions-item label="词汇表大小">{{ indexMetadata.index_statistics.vocabulary_size
                            }}</el-descriptions-item>
                        <el-descriptions-item label="总索引条目数">{{ indexMetadata.index_statistics.total_postings
                            }}</el-descriptions-item>
                        <el-descriptions-item label="每个词条平均索引条目">{{
                            indexMetadata.index_statistics.average_postings_per_term.toFixed(2)
                            }}</el-descriptions-item>
                    </el-descriptions>

                    <h3>优化信息</h3>
                    <el-descriptions :column="2" border>
                        <el-descriptions-item label="优化阈值">{{ indexMetadata.index_statistics.optimization.threshold
                            }}</el-descriptions-item>
                        <el-descriptions-item label="原始词条数">{{
                            indexMetadata.index_statistics.optimization.original_terms }}</el-descriptions-item>
                        <el-descriptions-item label="优化后词条数">{{
                            indexMetadata.index_statistics.optimization.optimized_terms }}</el-descriptions-item>
                        <el-descriptions-item label="原始索引条目数">{{
                            indexMetadata.index_statistics.optimization.original_entries }}</el-descriptions-item>
                        <el-descriptions-item label="优化后索引条目数">{{
                            indexMetadata.index_statistics.optimization.optimized_entries }}</el-descriptions-item>
                        <el-descriptions-item label="减少率">
                            词条: {{ indexMetadata.index_statistics.optimization.reduction_percentage.terms.toFixed(2)
                            }}%，
                            条目: {{ indexMetadata.index_statistics.optimization.reduction_percentage.entries.toFixed(2)
                            }}%
                        </el-descriptions-item>
                    </el-descriptions>

                    <h3>文档结构</h3>
                    <el-descriptions :column="1" border>
                        <el-descriptions-item label="可用字段">{{ indexMetadata.document_statistics.available_fields.join(',')}}</el-descriptions-item>
                    </el-descriptions>

                    <h3>输出文件</h3>
                    <el-table :data="indexOutputFilesData" style="width: 100%">
                        <el-table-column prop="name" label="文件名" />
                        <el-table-column prop="size" label="大小" />
                    </el-table>
                    <div class="total-size-info">
                        <p>总索引大小: <strong>{{ (indexMetadata.output_files.total_size_mb).toFixed(2) }} MB</strong> ({{
                            indexMetadata.output_files.total_size_bytes }} 字节)</p>
                    </div>
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
import { ref, reactive, watch, computed } from 'vue';
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
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { StartPreprocess } from '../api/preprocess';
import { StartInvertedIndex } from '../api/index';

// 类型定义
interface TfIdfSettings {
    minDf: number;
    maxDf: number;
}

interface IndexSettings {
    indexType: string;
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

// 组件状态
const activeTab = ref('preprocessing');
const selectedFiles = ref<any[]>([]);
const dataSourceType = ref('database');
const stopwordsPath = ref('./cn_stopwords.txt');
const processingStatus = ref<'idle' | 'processing' | 'completed'>('idle');
const indexingStatus = ref<'idle' | 'processing' | 'completed'>('idle');

// 对话框状态
const logDialogVisible = ref(false);
const reportDialogVisible = ref(false);
const indexMetaDialogVisible = ref(false);

// 日志和报告数据
const processLogs = ref<LogEntry[]>([]);
const preprocessingReport = ref<any>(null);
const indexMetadata = ref<any>(null);

// TF-IDF设置
const tfIdfSettings = reactive<TfIdfSettings>({
    minDf: 2,
    maxDf: 0.95
});

// 索引设置
const indexSettings = reactive<IndexSettings>({
    indexType: 'inverted',
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

// 为预处理报告创建输出文件列表数据
const outputFilesData = computed(() => {
    if (!preprocessingReport.value || !preprocessingReport.value.output_files) return [];

    return Object.entries(preprocessingReport.value.output_files).map(([key, value]) => ({
        name: key,
        path: value
    }));
});

// 为索引输出文件创建表格数据
const indexOutputFilesData = computed(() => {
    if (!indexMetadata.value || !indexMetadata.value.output_files || !indexMetadata.value.output_files.files) return [];

    return Object.entries(indexMetadata.value.output_files.files).map(([name, size]) => ({
        name,
        size: formatFileSize(size as number)
    }));
});

// 文件大小格式化辅助函数
const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB';
    else return (bytes / 1048576).toFixed(2) + ' MB';
};

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
        const response = await StartPreprocess(tfIdfSettings.minDf, tfIdfSettings.maxDf);

        addLog('INFO', '正在调用预处理API...');
        // 处理响应
        if (response.data) {
            // 更新预处理统计信息
            preprocessingStats.docCount = response.data.document_statistics.total_documents;
            preprocessingStats.vocabSize = response.data.vectorization_statistics.vocabulary_size;
            preprocessingStats.duplicationRate = response.data.document_statistics.duplicate_percentage;

            // 保存预处理报告
            preprocessingReport.value = response.data;

            addLog('INFO', '预处理成功完成!');
            processingStatus.value = 'completed';
        } else {
            throw new Error('API返回处理失败');
        }
    } catch (error) {
        addLog('ERROR', `预处理失败: ${error}`);
        console.log(`预处理失败: ${error}`)
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
        // 调用索引构建API
        const response = await StartInvertedIndex(indexSettings.optimize, indexSettings.minTfIdf);
        addLog('INFO', '正在调用索引构建API...');

        // 处理响应
        if (response.data) {
            // 更新索引统计信息
            indexingStats.termCount = response.data.index_statistics.total_terms;
            indexingStats.entryCount = response.data.index_statistics.total_postings;
            indexingStats.indexSize = formatFileSize(response.data.output_files.total_size_bytes);

            // 保存索引元数据
            indexMetadata.value = response.data;

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