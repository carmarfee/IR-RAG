<template>
    <div class="search-history">
        <el-card>
            <!-- 顶部搜索框 -->
            <div class="search-header">
                <div class="search-filters" style="width: 120px;">
                    <el-select v-model="timeRange" placeholder="时间范围" @change="filterRecords">
                        <el-option label="所有时间" value="all" />
                        <el-option label="今天" value="today" />
                        <el-option label="本周" value="week" />
                        <el-option label="本月" value="month" />
                    </el-select>
                </div>
                <div class="search-actions">
                    <el-button type="danger" plain @click="confirmClearAll" :disabled="searchRecords.length === 0">
                        <el-icon>
                            <Delete />
                        </el-icon>
                        清空
                    </el-button>
                    <el-button type="primary" @click="refreshHistory">
                        <el-icon>
                            <RefreshRight />
                        </el-icon>
                        刷新
                    </el-button>
                </div>
            </div>

            <!-- 历史记录列表 -->
            <div class="history-list-container">
                <el-skeleton :loading="loading" animated :rows="5" v-if="loading">
                </el-skeleton>

                <div v-else>
                    <div v-if="filteredRecords.length > 0" class="history-list">
                        <div v-for="(record, index) in paginatedRecords" :key="record.id" class="history-item">
                            <div class="history-item-content">
                                <el-icon class="history-icon">
                                    <Clock />
                                </el-icon>
                                <div class="history-details">
                                    <div class="history-keyword">{{ record.search_query }}</div>
                                    <div class="history-meta">
                                        <span class="history-time">{{ formatTime(new Date(record.time)) }}</span>
                                        <el-tag size="small" effect="plain" type="info">{{ record.num }} 个结果</el-tag>
                                    </div>
                                </div>
                            </div>
                            <div class="history-actions">
                                <el-tooltip content="重新搜索" placement="top">
                                    <el-button text type="primary" @click="searchAgain(record.search_query)">
                                        <el-icon>
                                            <Search />
                                        </el-icon>
                                    </el-button>
                                </el-tooltip>
                                <el-tooltip content="删除记录" placement="top">
                                    <el-button text type="danger"
                                        @click="deleteRecord(index + (currentPage - 1) * pageSize)">
                                        <el-icon>
                                            <Delete />
                                        </el-icon>
                                    </el-button>
                                </el-tooltip>
                            </div>
                        </div>
                    </div>
                    <div v-else class="empty-state">
                        <el-empty description="暂无搜索记录" />
                    </div>

                    <!-- 分页 -->
                    <div class="pagination-container" v-if="totalPages > 1">
                        <el-pagination background layout="prev, pager, next" :total="filteredRecords.length"
                            :current-page="currentPage" :page-size="pageSize" @current-change="handlePageChange" />
                    </div>
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
        </el-card>
    </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, watch } from 'vue';
import { Search, Delete, Clock, RefreshRight } from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox, ElLoading } from 'element-plus';
import { GetAllHistory, DeleteHistory, DeleteAllHistory } from '../../api/history';
import { useRouter } from 'vue-router';

const router = useRouter();

// 数据
const searchKeyword = ref('');
const timeRange = ref('all');
const currentPage = ref(1);
const pageSize = ref(10);
const clearDialogVisible = ref(false);
const loading = ref(true);

interface SearchRecord {
    id: number;
    search_query: string;
    time: string;
    num: number;
}

// 搜索记录数据
const searchRecords = ref<SearchRecord[]>([]);

//-------------------------------分割线--------------------------------

// 监听搜索关键词变化，自动切换到第一页
watch(searchKeyword, () => {
    currentPage.value = 1;
});

// 监听时间范围变化，自动切换到第一页
watch(timeRange, () => {
    currentPage.value = 1;
});

// 过滤记录
const filteredRecords = computed(() => {
    let filtered = [...searchRecords.value];

    // 根据搜索关键词过滤
    if (searchKeyword.value.trim()) {
        filtered = filtered.filter(record =>
            record.search_query.toLowerCase().includes(searchKeyword.value.toLowerCase())
        );
    }

    // 根据时间范围过滤
    if (timeRange.value !== 'all') {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        if (timeRange.value === 'today') {
            filtered = filtered.filter(record => new Date(record.time) >= today);
        } else if (timeRange.value === 'week') {
            const weekStart = new Date(today);
            weekStart.setDate(today.getDate() - today.getDay());
            filtered = filtered.filter(record => new Date(record.time) >= weekStart);
        } else if (timeRange.value === 'month') {
            const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
            filtered = filtered.filter(record => new Date(record.time) >= monthStart);
        }
    }

    // 按时间倒序排序，最新的排在前面
    return filtered.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());
});

// 计算当前页显示的记录
const paginatedRecords = computed(() => {
    const startIndex = (currentPage.value - 1) * pageSize.value;
    const endIndex = startIndex + pageSize.value;
    return filteredRecords.value.slice(startIndex, endIndex);
});

// 总页数
const totalPages = computed(() => {
    return Math.ceil(filteredRecords.value.length / pageSize.value);
});

// 格式化时间
const formatTime = (date: Date) => {
    try {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        if (date >= today) {
            return `今天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        } else if (date >= yesterday) {
            return `昨天 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        } else {
            return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
        }
    } catch (error) {
        console.error('日期格式化错误:', error);
        return '日期无效';
    }
};

// 过滤记录
const filterRecords = () => {
    currentPage.value = 1; // 重置到第一页
};


// 重新搜索
const searchAgain = (keyword: string) => {
    try {
        // 跳转到搜索页面
        router.push({
            path: '/search',
            query: { q: keyword }
        });
    } catch (error) {
        ElMessage({
            message: `搜索跳转失败: ${error}`,
            type: 'error'
        });
    }
};

// 删除记录
const deleteRecord = async (index: number) => {
    try {
        await ElMessageBox.confirm(
            '确定要删除这条搜索记录吗?',
            '删除确认',
            {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning',
            }
        );

        // 要删除的记录
        const recordToDelete = searchRecords.value[index];

        // 避免删除不存在的记录
        if (!recordToDelete) {
            throw new Error('记录不存在');
        }

        // 显示加载状态
        const loadingInstance = ElLoading.service({
            lock: true,
            text: '正在删除...',
            background: 'rgba(0, 0, 0, 0.7)',
        });

        try {
            // 调用API删除记录
            await DeleteHistory(recordToDelete.id);

            // 从本地数组中删除
            searchRecords.value.splice(index, 1);

            // 如果当前页没有记录了，则回到上一页（除非已经是第一页）
            if (paginatedRecords.value.length === 0 && currentPage.value > 1) {
                currentPage.value--;
            }

            ElMessage({
                type: 'success',
                message: '删除成功',
            });
        } finally {
            // 确保关闭加载状态
            loadingInstance.close();
        }
    } catch (error: any) {
        // 用户取消删除操作不显示错误
        if (error === 'cancel' || error.toString().includes('cancel')) {
            return;
        }

        // 显示错误消息
        ElMessage({
            type: 'error',
            message: '删除失败: ' + error,
        });
    }
};

// 确认清空所有记录
const confirmClearAll = () => {
    if (searchRecords.value.length === 0) {
        ElMessage({
            message: '没有记录可清空',
            type: 'info'
        });
        return;
    }
    clearDialogVisible.value = true;
};

// 清空所有记录
const clearAllRecords = async () => {
    // 显示加载状态
    const loadingInstance = ElLoading.service({
        lock: true,
        text: '正在清空历史记录...',
        background: 'rgba(0, 0, 0, 0.7)',
    });

    try {
        await DeleteAllHistory();
        searchRecords.value = [];
        clearDialogVisible.value = false;
        currentPage.value = 1;

        ElMessage({
            message: '已清空所有搜索记录',
            type: 'success'
        });
    } catch (error) {
        ElMessage({
            message: '清空记录失败: ' + error,
            type: 'error'
        });
    } finally {
        // 确保关闭加载状态
        loadingInstance.close();
    }
};

// 刷新历史记录
const refreshHistory = async () => {
    // 重新获取历史记录
    await getHistory();

    ElMessage({
        message: '历史记录已刷新',
        type: 'success'
    });
};

// 处理页码变化
const handlePageChange = (page: number) => {
    currentPage.value = page;
};

// 获取历史记录
const getHistory = async () => {
    loading.value = true;

    try {
        const historyData = await GetAllHistory();
        searchRecords.value = historyData;
    } catch (error) {
        ElMessage({
            message: '获取搜索历史失败: ' + error,
            type: 'error'
        });
        // 保留之前的数据，避免清空
    } finally {
        loading.value = false;
    }
};

// 生命周期钩子
onMounted(async () => {
    // 从API获取搜索历史
    await getHistory();
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
    gap: 20px;
}

.search-input-wrapper {
    flex: 1;
    max-width: 320px;
}

.search-filters {
    display: flex;
    gap: 12px;
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
    background-color: var(--secondar-color);
    border-color: var(--border-color);
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
    text-align: left;
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

.empty-state {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40px 0;
}

/* 添加全局样式覆盖 */
:deep(.el-button--primary) {
    --el-button-bg-color: #6366f1;
    --el-button-border-color: #6366f1;
    --el-button-hover-bg-color: #4f46e5;
    --el-button-hover-border-color: #4f46e5;
    --el-button-text-color: white
}

:deep(.el-button--danger) {
    --el-button-bg-color: #f43f5e;
    --el-button-border-color: #f43f5e;
    --el-button-hover-bg-color: #e11d48;
    --el-button-hover-border-color: #e11d48;
    --el-button-text-color: white
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