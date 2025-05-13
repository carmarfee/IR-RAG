import { createRouter, createWebHashHistory } from 'vue-router'
import DocSearch from '@/views/DocSearch.vue';



const routes = [
    {
        path: '/', 
        name: '文档搜索', 
        component: DocSearch,
    },
    {
        path: '/SnapShot',
        name: '文档快照',
        component: () => import('@/views/SnapShot.vue'),
    },
    {
        path: '/History', 
        name: '搜索记录', 
        component: () => import('@/views/History.vue'),
    },
    {
        path: '/DocCrawler',
        name: '文档爬取',
        component: () => import('@/views/DocCrawler.vue'),
    },
    {
        path: '/DocCrawler/CrawlerConfig',
        name: '爬虫配置',
        component: () => import('@/views/CrawlerConfig.vue'),
    },
    {
        path: '/DocPrepare', 
        name: '文档处理', 
        component: () => import('@/views/DocPrepare.vue'),
    },
    {
        path: '/Setting',
        name: '系统设置',
        component: () => import('@/views/Setting.vue'),
    },
    

]

const router = createRouter({
    // history: createWebHistory(),
    history: createWebHashHistory(),
    routes,
})

export default router;