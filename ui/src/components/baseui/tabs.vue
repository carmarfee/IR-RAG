<template><el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
    <el-tab-pane label="搜索结果" name="first">
        <div v-if="searchStore.isLoading">加载中...</div>
        <div v-else-if="searchStore.error">错误: {{ searchStore.error.message }}</div>
        <div v-else class="search-container">
            <div class="search-results">
                <transition-group name="fade" :key="currentPageKey">
                    <resultcard v-for="item in displayResults" :key="item.doc_id" :doc_id="item.doc_id"
                        :title="item.title" :content="item.content_preview" :source="item.source"
                        :publish_time="item.publish_time">
                    </resultcard>
                </transition-group>
                <div v-if="isLoading" class="loading-indicator">
                    <el-icon class="is-loading">
                        <Loading />
                    </el-icon> 加载中...
                </div>
                <div v-if="displayResults.length == 0 && !isLoading" class="empty-state">
                    <el-empty description="输入关键词进行查询" />
                </div>
            </div>

            <!-- 添加分页组件 -->
            <div class="pagination-container">
                <el-pagination v-if="searchStore.results.length > 0" v-model:current-page="currentPage"
                    :page-size="pageSize" :total="searchStore.results.length" layout="prev, pager, next"
                    @current-change="handlePageChange" :disabled="isLoading" background />
                <div v-if="searchStore.results.length > 0" class="result-count">
                    共 {{ searchStore.results.length }} 条结果
                </div>
            </div>
        </div>
    </el-tab-pane>
    <el-tab-pane label="RAG对话" name="second">
        <RAG></RAG>
    </el-tab-pane>
</el-tabs></template>

<script lang="ts" setup>
import { ref, nextTick, type Ref } from 'vue'
import type { TabsPaneContext } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import resultcard from '@/components/baseui/resultcard.vue';
import RAG from '@/components/baseui/RAG-chat.vue';
import { useSearchStore } from '../../stores/searchStore';
import { setKnowledge } from '@/utils/RAG';


const activeName = ref('first')
const searchStore = useSearchStore();

// 分页相关
const currentPage = ref(1);
const pageSize = 8; // 每页显示8条结果
const currentPageKey = ref(0); // 用于强制重新渲染
const isLoading = ref(false); // 页面切换加载状态
const displayResults = ref([]) as Ref<any[]>; // 当前显示的结果

//-------------------------------分割线--------------------------------

// 初始化显示结果
displayResults.value = getCurrentPageResults();

// 获取当前页的结果
function getCurrentPageResults() {
    const startIndex = (currentPage.value - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return searchStore.results.slice(startIndex, endIndex);
}

// 页码变化处理函数
const handlePageChange = async (page: any) => {
    // 设置加载中状态
    isLoading.value = true;

    // 清空当前结果
    displayResults.value = [];

    // 更新页码
    currentPage.value = page;

    // 增加一个小延迟，创建清空效果
    setTimeout(async () => {
        // 增加currentPageKey使transition-group重新渲染
        currentPageKey.value++;

        // 滚动到顶部
        document.querySelector('.search-results')?.scrollTo({
            top: 0,
            behavior: 'smooth'
        });

        // 加载新页面数据
        await nextTick();
        displayResults.value = getCurrentPageResults();

        // 取消加载状态
        isLoading.value = false;
    }, 300); // 300ms延迟，可根据需要调整
};

// 监听搜索结果变化，重置为第一页
import { watch } from 'vue';
watch(() => searchStore.results, () => {
    currentPage.value = 1;
    currentPageKey.value++;
    displayResults.value = getCurrentPageResults();
}, { deep: true });



const handleClick = async (tab: TabsPaneContext, event: Event) => {
    if (tab.index == '1') {
        let docids: Array<{ doc_id: number }> = await searchStore.getAllDocIDs();
        await setKnowledge(docids);
    }
}
</script>

<style>
.demo-tabs>.el-tabs__content {
    color: #6b778c;
    font-weight: 600;
    padding: 10px;
}

.el-tabs__item {
    color: #9370DB !important;
}

.el-tabs__active-bar {
    background-color: #9370DB !important;
}

.demo-tabs>.el-tabs__content>.el-tab-pane {
    height: 550px;
}

.search-container {
    display: flex;
    flex-direction: column;
    height: 550px;
}

.search-results {
    display: flex;
    flex-direction: column;
    gap: 5px;
    flex: 1;
    overflow-y: auto;
    padding-right: 5px;
    margin-bottom: 10px;
    position: relative;
    min-height: 400px;
    /* 保持一个最小高度，避免闪烁 */
}

.pagination-container {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 10px 0;
    margin-top: auto;
    flex-wrap: wrap;
    gap: 10px;
}

.result-count {
    color: #909399;
    font-size: 14px;
    margin-left: 10px;
}

.loading-indicator {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    gap: 8px;
    color: #409eff;
}

/* 淡入淡出动画 */
.fade-enter-active,
.fade-leave-active {
    transition: all 0.3s ease;
}

.fade-enter-from {
    opacity: 0;
    transform: translateY(10px);
}

.fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* 响应式调整 */
@media (max-width: 768px) {
    .pagination-container {
        flex-direction: column;
        gap: 5px;
    }

    .result-count {
        margin-left: 0;
    }
}
</style>