<template>
    <div class="snapshot-container">
        <el-card>
            <template #header>
                <div class="header">
                    <h3>文档快照查看器</h3>
                    <el-button type="primary" @click="goBack">返回</el-button>
                </div>
            </template>

            <htmlViewer :doc-id="route.query.doc_id" :title="route.query.title" :url="raw_url"
                :htmlContent="raw_html" />
        </el-card>
    </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import htmlViewer from '../components/baseui/html-viewer.vue';
import { GetSnapShot } from '../api/search';

const route = useRoute();
const router = useRouter();
const contentViewer = ref(null);

const raw_html = ref('')
const raw_url = ref('')

//-------------------------------分割线--------------------------------

// 返回搜索结果页
const goBack = () => {
    router.back();
};

// 获取文档基本信息
const GetDocSnapShot = async (id) => {
    try {
        const response = await GetSnapShot(id);
        raw_html.value = response.data['html_content']
        raw_url.value = response.data['url']
    } catch (error) {
        console.error('获取文档快照错误:', error);
    }
};

// 加载快照内容
const loadSnapshot = async () => {
    if (route.query.doc_id) {
        // 重置内容，确保每次都是新的加载状态
        raw_html.value = '';
        raw_url.value = '';
        await GetDocSnapShot(route.query.doc_id);
    }
};

// 监听路由参数变化，当doc_id改变时重新加载
watch(() => route.query.doc_id, (newId, oldId) => {
    if (newId && newId !== oldId) {
        loadSnapshot();
    }
}, { immediate: false });

onMounted(() => {
    loadSnapshot();
});


</script>

<style scoped>
.snapshot-container {
    max-width: 1200px;
    margin: 20px auto;
    padding: 0 15px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h3 {
    margin: 0;
    color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .snapshot-container {
        margin: 10px auto;
    }
}
</style>