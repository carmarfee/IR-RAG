import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router';
import 'element-plus/dist/index.css';
import '@/assets/css/fonts.css'
import 'nes.css/css/nes.min.css';


const app = createApp(App)
app.use(router)
app.mount('#app')