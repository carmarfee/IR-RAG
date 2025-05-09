<!-- 搜索历史记录组件 -->
<template>
    <div class="search-history">
        <!-- 顶部搜索框和操作区 -->
        <div class="search-header">
            <div class="search-input-wrapper">
                <el-input v-model="searchKeyword" placeholder="搜索历史记录..." :prefix-icon="Search" clearable
                    @keyup.enter="searchHistoryRecords" class="search-input" />
            </div>
            <div class="search-actions">
                <el-button type="primary" :icon="Delete" @click="confirmClearAll" plain size="small">
                    清空记录
                </el-button>
                <el-select v-model="timeRange" placeholder="时间范围" size="small" style="width: 120px;">
                    <el-option label="全部时间" value="all" />
                    <el-option label="今天" value="today" />
                    <el-option label="本周" value="week" />
                    <el-option label="本月" value="month" />
                </el-select>
            </div>
        </div>

        <!-- 历史记录列表 -->
        <div class="history-list-container">
            <el-empty v-if="filteredRecords.length === 0" description="暂无搜索记录" />

            <div v-else class="history-list">
                <div v-for="(record, index) in filteredRecords" :key="index" class="history-item">
                    <div class="history-item-content">
                        <el-icon class="history-icon">
                            <Clock />
                        </el-icon>
                        <div class="history-details">
                            <div class="history-keyword">{{ record.keyword }}</div>
                            <div class="history-meta">
                                <span class="history-time">{{ formatTime(record.time) }}</span>
                                <el-tag size="small" effect="plain" type="info">{{ record.resultCount }} 个结果</el-tag>
                            </div>
                        </div>
                    </div>
                    <div class="history-actions">
                        <el-button text type="primary" @click="searchAgain(record.keyword)">
                            <el-icon>
                                <Search />
                            </el-icon>
                        </el-button>
                        <el-button text type="danger" @click="deleteRecord(index)">
                            <el-icon>
                                <Delete />
                            </el-icon>
                        </el-button>
                    </div>
                </div>
            </div>

            <!-- 分页 -->
            <div class="pagination-container">
                <el-pagination v-if="filteredRecords.length > 0" background layout="prev, pager, next"
                    :total="totalRecords" :current-page="currentPage" :page-size="pageSize"
                    @current-change="handlePageChange" />
            </div>
        </div>

        <!-- 确认清空的对话框 -->
        <el-dialog v-model="clearDialogVisible" title="确认清空" width="30%" center>
            <span>确定要清空所有搜索记录吗？此操作不可恢复。</span>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="clearDialogVisible = false">取消</el-button>
                    <el-button type="danger" @click="clearAllRecords">确定</el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Search, Delete, Clock } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';

// 数据
const searchKeyword = ref('');
const timeRange = ref('all');
const currentPage = ref(1);
const pageSize = ref(10);
const clearDialogVisible = ref(false);

// 模拟的搜索记录数据
const searchRecords = ref([
    {
        keyword: '武汉大学新闻',
        time: new Date('2025-05-08T14:30:00'),
        resultCount: 153
    },
    {
        keyword: '人工智能技术',
        time: new Date('2025-05-08T11:15:00'),
        resultCount: 225
    },
    {
        keyword: '校园活动',
        time: new Date('2025-05-07T16:45:00'),
        resultCount: 78
    },
    {
        keyword: '科研成果',
        time: new Date('2025-05-06T09:20:00'),
        resultCount: 192
    },
    {
        keyword: '招生信息',
        time: new Date('2025-05-06T08:30:00'),
        resultCount: 64
    },
    {
        keyword: '国际交流',
        time: new Date('2025-05-05T15:10:00'),
        resultCount: 87
    },
    {
        keyword: '学术讲座',
        time: new Date('2025-05-04T10:25:00'),
        resultCount: 112
    },
    {
        keyword: '师资力量',
        time: new Date('2025-05-03T16:30:00'),
        resultCount: 56
    },
    {
        keyword: '校园建设',
        time: new Date('2025-05-02T13:15:00'),
        resultCount: 43
    },
    {
        keyword: '学生活动',
        time: new Date('2025-05-01T11:50:00'),
        resultCount: 98
    },
    {
        keyword: '研究生招生',
        time: new Date('2025-04-30T14:40:00'),
        resultCount: 75
    },
    {
        keyword: '图书馆资源',
        time: new Date('2025-04-29T09:05:00'),
        resultCount: 127
    },
    {
        keyword: '校园疫情防控',
        time: new Date('2025-04-28T16:20:00'),
        resultCount: 35
    },
    {
        keyword: '学科建设',
        time: new Date('2025-04-27T10:45:00'),
        resultCount: 89
    },
    {
        keyword: '选课系统',
        time: new Date('2025-04-26T08:30:00'),
        resultCount: 42
    }
]);

// 计算属性
const filteredRecords = computed(() => {
    let filtered = [...searchRecords.value];

    // 按关键词过滤
    if (searchKeyword.value.trim()) {
        filtered = filtered.filter(record =>
            record.keyword.toLowerCase().includes(searchKeyword.value.toLowerCase())
        );
    }

    // 按时间范围过滤
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay());
    const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);

    if (timeRange.value !== 'all') {
        filtered = filtered.filter(record => {
            const recordDate = new Date(record.time);

            switch (timeRange.value) {
                case 'today':
                    return recordDate >= today;
                case 'week':
                    return recordDate >= weekStart;
                case 'month':
                    return recordDate >= monthStart;
                default:
                    return true;
            }
        });
    }

    // 排序: 按时间降序
    filtered.sort((a, b) => b.time - a.time);

    return filtered;
});

const totalRecords = computed(() => filteredRecords.value.length);

const paginatedRecords = computed(() => {
    const start = (currentPage.value - 1) * pageSize.value;
    const end = start + pageSize.value;
    return filteredRecords.value.slice(start, end);
});

// 方法
const formatTime = (date) => {
    const now = new Date();
    const recordDate = new Date(date);

    // 如果是今天
    if (recordDate.toDateString() === now.toDateString()) {
        return `今天 ${recordDate.getHours().toString().padStart(2, '0')}:${recordDate.getMinutes().toString().padStart(2, '0')}`;
    }

    // 如果是昨天
    const yesterday = new Date(now);
    yesterday.setDate(now.getDate() - 1);
    if (recordDate.toDateString() === yesterday.toDateString()) {
        return `昨天 ${recordDate.getHours().toString().padStart(2, '0')}:${recordDate.getMinutes().toString().padStart(2, '0')}`;
    }

    // 其他日期
    return `${recordDate.getFullYear()}-${(recordDate.getMonth() + 1).toString().padStart(2, '0')}-${recordDate.getDate().toString().padStart(2, '0')} ${recordDate.getHours().toString().padStart(2, '0')}:${recordDate.getMinutes().toString().padStart(2, '0')}`;
};

const searchHistoryRecords = () => {
    currentPage.value = 1;
    if (searchKeyword.value.trim()) {
        ElMessage({
            message: `搜索包含 "${searchKeyword.value}" 的历史记录`,
            type: 'success'
        });
    }
};

const searchAgain = (keyword) => {
    ElMessage({
        message: `重新搜索: ${keyword}`,
        type: 'info'
    });
    // 这里可以跳转到搜索页面或触发搜索事件
};

const deleteRecord = (index) => {
    ElMessageBox.confirm(
        '确定要删除这条搜索记录吗?',
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    )
        .then(() => {
            searchRecords.value.splice(index, 1);
            ElMessage({
                type: 'success',
                message: '删除成功',
            });
        })
        .catch(() => {
            // 取消删除操作
        });
};

const confirmClearAll = () => {
    clearDialogVisible.value = true;
};

const clearAllRecords = () => {
    searchRecords.value = [];
    clearDialogVisible.value = false;
    ElMessage({
        message: '已清空所有搜索记录',
        type: 'success'
    });
};

const handlePageChange = (page) => {
    currentPage.value = page;
};

// 生命周期钩子
onMounted(() => {
    // 实际应用中可能会从localStorage或后端API获取搜索历史
    console.log('搜索历史组件已加载');
});
</script>

<style scoped>
.search-history {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
}

.search-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 0 20px 0;
}

.search-input-wrapper {
    flex: 1;
    max-width: 500px;
}

.search-input :deep(.el-input__wrapper) {
    background-color: #f0f0ff;
    box-shadow: none;
    border: 1px solid transparent;
}

.search-input :deep(.el-input__wrapper:hover) {
    border-color: #6366f1;
}

.search-input :deep(.el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #6366f1 inset;
}

.search-actions {
    display: flex;
    gap: 10px;
}

.history-list-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    padding: 15px;
}

.history-list {
    flex: 1;
    overflow-y: auto;
}

.history-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.2s;
}

.history-item:hover {
    background-color: #f9f9ff;
}

.history-item:last-child {
    border-bottom: none;
}

.history-item-content {
    display: flex;
    align-items: center;
    gap: 12px;
}

.history-icon {
    color: #6366f1;
    font-size: 18px;
}

.history-details {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.history-keyword {
    font-size: 16px;
    color: #333;
    font-weight: 500;
}

.history-meta {
    display: flex;
    align-items: center;
    gap: 15px;
    font-size: 12px;
    color: #909399;
}

.history-time {
    color: #909399;
}

.history-actions {
    display: flex;
    gap: 5px;
}

.pagination-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}

.pagination-container :deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
    background-color: #6366f1;
}

/* 添加全局样式覆盖 */
:deep(.el-button--primary) {
    --el-button-bg-color: #6366f1;
    --el-button-border-color: #6366f1;
    --el-button-hover-bg-color: #4f46e5;
    --el-button-hover-border-color: #4f46e5;
}

:deep(.el-button--text) {
    --el-button-hover-text-color: #6366f1;
    --el-button-active-text-color: #4f46e5;
}

:deep(.el-select .el-input__wrapper.is-focus) {
    box-shadow: 0 0 0 1px #6366f1 inset !important;
}

:deep(.el-pagination.is-background .el-pager li:not(.is-disabled).is-active) {
    background-color: #6366f1 !important;
}

:deep(.el-tag--info) {
    --el-tag-bg-color: #f4f4f8;
    --el-tag-border-color: #e9e9f0;
    --el-tag-text-color: #606266;
}
</style>