<template>
    <div class="history-page">
        <el-row style="height: 100%;">
            <el-col :span="24" style="height: 100%;">
                <search-history></search-history>
            </el-col>
        </el-row>
    </div>
</template>

<script setup>
import { Grid } from '@element-plus/icons-vue';
import SearchHistory from '../components/baseui/search-history.vue';
</script>

<style scoped>
.history-page {
    height: 100%;
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.page-title {
    font-size: 20px;
    font-weight: 600;
    color: #333;
    display: flex;
    align-items: center;
    gap: 8px;
}

.page-title .el-icon {
    color: #6366f1;
}
</style>