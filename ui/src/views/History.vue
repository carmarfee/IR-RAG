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
    display: flex;
    flex-direction: column;
}
</style>