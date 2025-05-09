<script setup>
import { ref } from 'vue'
import searchBox from '../components/baseui/search-box.vue';
import tabs from '../components/baseui/tabs.vue';
</script>

<template>
    <div class="doc-search">
        <searchBox></searchBox>
        <tabs></tabs>
    </div>
</template>