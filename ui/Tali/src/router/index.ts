import { createRouter, createWebHistory, createWebHashHistory } from 'vue-router'
import Home from '../views/home.vue'


const routes = [
    {
        path: '/', 
        name: 'Home', 
        component: Home
    }
]

const router = createRouter({
    // history: createWebHistory(),
    history: createWebHashHistory(),
    routes,
})

export default router;