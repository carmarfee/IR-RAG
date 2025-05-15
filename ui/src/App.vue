<script setup lang="ts">
import myheader from '@/components/layouts/header.vue';
import myfooter from '@/components/layouts/footer.vue';
import mylogo from './components/baseui/logo.vue';
import github from './components/baseui/github.vue';
import { useThemeStore } from './stores/themeStore';
import { ref, onMounted } from 'vue'
import {
  Search,
  Clock,
  Setting,
  Document,
  Fold,
  Expand
} from '@element-plus/icons-vue'


const themeStore = useThemeStore()

// 定义折叠状态
const isCollapse = ref(false)
const activeIndex = ref(location.pathname)
activeIndex.value = '/'

//-------------------------------分割线--------------------------------

// 切换折叠状态
const toggleCollapse = () => {
  console.log('change')
  isCollapse.value = !isCollapse.value
}

onMounted(() => {
  themeStore.initTheme()
})

</script>

<template>
  <div class="mainlayout">
    <div class="titlebar" style="display: flex;align-items: center;">
    </div>
    <el-container>
      <el-aside :collapse=isCollapse unique_opened class="el-menu-vertical-demo">
        <mylogo style="width: 65px;height: 50px;"></mylogo>
        <el-divider></el-divider>
        <el-menu background-color=transparent text-color="black" active-text-color="#9370DB"
          :default-active="activeIndex" router>

          <el-menu-item index="/">
            <el-icon>
              <Search></Search>
            </el-icon>
            <span class="item">文档搜索</span>
          </el-menu-item>

          <el-menu-item index="/History">
            <el-icon>
              <Clock></Clock>
            </el-icon>
            <span class="item">搜索记录</span>
          </el-menu-item>

          <el-menu-item index="/DocCrawler">
            <el-icon>
              <svg t="1746758417306" class="icon" viewBox="0 0 1024 1024" version="1.1"
                xmlns="http://www.w3.org/2000/svg" p-id="2625" width="16" height="16">
                <path
                  d="M320.597333 48.768a42.666667 42.666667 0 0 0-43.904 73.173333l63.573334 38.144A233.856 233.856 0 0 0 277.333333 320v6.101333a210.773333 210.773333 0 0 0-20.224 13.056c-2.048-1.28-4.266667-2.389333-6.613333-3.328l-85.333333-34.133333a42.666667 42.666667 0 0 0-31.658667 79.232l63.914667 25.6A209.749333 209.749333 0 0 0 170.666667 509.354667V554.666667H85.333333a42.666667 42.666667 0 1 0 0 85.333333h85.333334c0 52.138667 11.690667 101.546667 32.64 145.834667l-69.802667 27.904a42.666667 42.666667 0 1 0 31.658667 79.232l84.992-34.005334A340.608 340.608 0 0 0 512 981.333333a340.650667 340.650667 0 0 0 261.845333-122.368l84.992 34.005334a42.666667 42.666667 0 0 0 31.658667-79.232l-69.802667-27.904A340.053333 340.053333 0 0 0 853.333333 640h85.333334a42.666667 42.666667 0 0 0 0-85.333333h-85.333334v-45.312c0-37.333333-9.728-72.405333-26.752-102.826667l63.914667-25.6a42.666667 42.666667 0 1 0-31.658667-79.232l-85.333333 34.133333a42.709333 42.709333 0 0 0-6.613333 3.328 210.773333 210.773333 0 0 0-20.224-13.056V320c0-61.781333-23.893333-118.016-62.933334-159.914667l63.573334-38.144a42.666667 42.666667 0 0 0-43.946667-73.173333l-95.189333 57.130667A233.898667 233.898667 0 0 0 512 85.333333c-34.261333 0-66.816 7.338667-96.170667 20.565334l-95.232-57.173334zM381.354667 298.666667c-5.802667 0-11.52 0.256-17.237334 0.682666a149.333333 149.333333 0 0 1 295.850667 0A213.418667 213.418667 0 0 0 642.645333 298.666667H381.397333zM320 405.333333a42.624 42.624 0 0 0 35.242667-18.602666c8.405333-1.792 17.152-2.730667 26.069333-2.730667h261.376c8.96 0 17.664 0.938667 26.026667 2.730667a42.666667 42.666667 0 0 0 42.922666 17.92A125.226667 125.226667 0 0 1 768 509.354667V640a256.085333 256.085333 0 0 1-213.333333 252.458667V640a42.666667 42.666667 0 1 0-85.333334 0v252.458667A256.085333 256.085333 0 0 1 256 640v-130.645333c0-43.733333 22.4-82.261333 56.362667-104.704 2.517333 0.426667 5.034667 0.682667 7.637333 0.682666z"
                  p-id="2626"></path>
              </svg>
            </el-icon>
            <span class="item">文档爬取</span>
          </el-menu-item>

          <el-menu-item index="/DocPrepare">
            <el-icon>
              <Document></Document>
            </el-icon>
            <span class="item">文档处理</span>
          </el-menu-item>

          <el-menu-item index="/Setting">
            <el-icon>
              <Setting></Setting>
            </el-icon>
            <span class="item">系统设置</span>
          </el-menu-item>
        </el-menu>
        <div class="siderbar-bottom"
          style="height: 100px;margin-top: 50px;display: flex;flex-direction: column;align-items: center;justify-content: space-between;">
          <github>
            <p v-if="!isCollapse" style="color: black;font-weight: bolder;align-items: center;margin: 0;">GitHub</p>
          </github>
          <div class="collapse-btn" @click="toggleCollapse">
            <el-icon>
              <component :is="isCollapse ? Expand : Fold" />
            </el-icon>
          </div>

        </div>
        <p v-if="!isCollapse"
          style="font-weight: 500;font-size: x-small;position: absolute;bottom: 0%;align-items: center;width: 180px;">版本
          v 0.0.1</p>
        <p v-else
          style="font-weight: 700;font-size: small;position: absolute;bottom: 0%;align-items: center;width: 65px;"><svg
            t="1746670802972" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg"
            p-id="2631" width="25" height="25">
            <path
              d="M513.3 167.3c190.6 0 345.6 155 345.6 345.6s-155 345.6-345.6 345.6-345.6-155-345.6-345.6 155-345.6 345.6-345.6m0-69.1c-229 0-414.7 185.7-414.7 414.7s185.7 414.7 414.7 414.7S928 741.9 928 512.9 742.3 98.2 513.3 98.2z"
              fill="#93A2BB" p-id="2632"></path>
            <path d="M513.3 379.1m-34.6 0a34.6 34.6 0 1 0 69.2 0 34.6 34.6 0 1 0-69.2 0Z" fill="#93A2BB" p-id="2633">
            </path>
            <path
              d="M515.8 743.1c-19 0-34.4-15.3-34.6-34.3l-1.6-214c-0.1-19.1 15.2-34.7 34.3-34.8h0.3c19 0 34.4 15.3 34.6 34.3l1.6 214c0.1 19.1-15.2 34.7-34.3 34.8h-0.3z"
              fill="#93A2BB" p-id="2634"></path>
          </svg></p>
      </el-aside>
      <el-container>
        <el-divider></el-divider>
        <el-header>
          <myheader style="padding-left: 5px;"></myheader>
        </el-header>
        <el-main style="padding: 5px;"><router-view></router-view></el-main>
        <el-footer>
          <myfooter></myfooter>
        </el-footer>
      </el-container>
    </el-container>
  </div>
</template>


<style scoped>
.item {
  margin: 15px;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s;
}

.el-menu-vertical-demo {
  width: 180px;
  height: 100vh;
  transition: width 0.3s ease;
  /* Smooth width transition */
  border-right: 1px solid #eee;
  /* Default width when not collapsed */
}

.el-menu-vertical-demo[collapse="true"] {
  width: 65px;
  /* Reduced width when collapsed */
}

#mainlayout {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  box-shadow: 0 0 10px 5px rgba(0, 0, 0, 0.8);
}

.titlebar {
  height: 25px;
  -webkit-app-region: drag;
}

.el-container {
  height: 100vh;
}

.el-header,
.el-main,
.el-footer {
  padding: 0px;
}

.el-header {
  height: 15px;
}
</style>
