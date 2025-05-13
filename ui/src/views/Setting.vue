<template>
    <div class="setting">
        <div class="setting-section">
            <h3>主题设置</h3>

            <div class="theme-options">
                <!-- 主题选择卡片 -->
                <div v-for="(colors, themeName) in themeStore.themes" :key="themeName" class="theme-card"
                    :class="{ active: themeStore.currentTheme === themeName }" @click="selectTheme(themeName)">
                    <div class="theme-preview">
                        <div class="preview-header" :style="{ backgroundColor: colors.primary }"></div>
                        <div class="preview-sidebar" :style="{ backgroundColor: colors.sidebar }">
                            <div class="sidebar-item"
                                :style="{ backgroundColor: colors.sidebarActive, color: colors.sidebarText }"></div>
                        </div>
                        <div class="preview-content" :style="{ backgroundColor: colors.background }"></div>
                    </div>

                    <div class="theme-name">{{ getThemeName(themeName) }}</div>

                    <div v-if="themeStore.currentTheme === themeName" class="theme-selected">
                        <span class="check-icon">✓</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, } from 'vue';
import { useThemeStore, type ThemeColors } from '../stores/themeStore';

const themeStore = useThemeStore();

// 主题名称中文映射
const themeNames = {
    light: '浅色主题',
    dark: '深色主题',
};

// 获取主题的中文名称
const getThemeName = (themeName: string) => {
    return themeNames[themeName as keyof typeof themeNames] || themeName;
};

// 选择主题
const selectTheme = (theme: string) => {
    themeStore.setTheme(theme);
};

// 自定义颜色
const customColors = ref<ThemeColors>({
    ...themeStore.themes.light, // 默认从浅色主题复制
});

// 如果已有自定义主题，则加载它
onMounted(() => {
    // 初始化主题
    themeStore.initTheme();

    // 如果存在自定义主题，则加载
    if (themeStore.themes.custom) {
        customColors.value = { ...themeStore.themes.custom };
    } else {
        // 否则从当前主题复制
        customColors.value = { ...themeStore.currentThemeColors };
    }
});

// 更新自定义主题（实时预览，但不保存）
const updateCustomTheme = () => {
    // 将自定义颜色应用到CSS变量，但不保存到store
    const root = document.documentElement;

    root.style.setProperty('--primary-color', customColors.value.primary);
    root.style.setProperty('--secondary-color', customColors.value.secondary);
    root.style.setProperty('--background-color', customColors.value.background);
    root.style.setProperty('--text-color', customColors.value.text);

    // 临时将当前主题设为自定义
    if (themeStore.currentTheme !== 'custom') {
        themeStore.currentTheme = 'custom';
    }
};

// 保存自定义主题
const saveCustomTheme = () => {
    // 添加或更新自定义主题
    themeStore.$patch((state) => {
        state.themes.custom = { ...customColors.value };
    });

    // 应用自定义主题
    themeStore.setTheme('custom');

    // 显示保存成功消息（如果有消息组件）
    alert('自定义主题已保存');
};

// 重置自定义主题
const resetCustomTheme = () => {
    // 重置为当前选中的非自定义主题
    const baseTheme = themeStore.currentTheme === 'custom' ? 'light' : themeStore.currentTheme;
    customColors.value = { ...themeStore.themes[baseTheme] };
    updateCustomTheme();
};
</script>

<style scoped>
.setting {
    padding: 20px;
    max-width: 800px;
    margin: 0 auto;
    color: var(--text-color);
}

.setting-header {
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
}

.setting-header h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-color);
    margin: 0;
}

.setting-section {
    margin-bottom: 30px;
    background-color: var(--surface-color);
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.setting-section h3 {
    font-size: 1.2rem;
    margin-top: 0;
    margin-bottom: 15px;
    color: var(--text-color);
}

.theme-options {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
}

.theme-card {
    width: 120px;
    background-color: var(--surface-color);
    border: 2px solid var(--border-color);
    border-radius: 8px;
    padding: 10px;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
}

.theme-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.theme-card.active {
    border-color: var(--primary-color);
}

.theme-preview {
    height: 100px;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
    display: flex;
    flex-direction: column;
    border: 1px solid var(--border-color);
}

.preview-header {
    height: 20%;
}

.preview-content {
    flex-grow: 1;
    display: flex;
}

.preview-sidebar {
    width: 30%;
    height: 100%;
    padding: 4px;
}

.sidebar-item {
    height: 10px;
    margin-bottom: 4px;
    border-radius: 2px;
}

.theme-name {
    text-align: center;
    font-size: 0.9rem;
    color: var(--text-color);
}

.theme-selected {
    position: absolute;
    top: -8px;
    right: -8px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: var(--primary-color);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
}

.check-icon {
    font-size: 0.8rem;
    font-weight: bold;
}

.color-option {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.color-option label {
    width: 100px;
    color: var(--text-color);
}

.color-picker {
    display: flex;
    align-items: center;
    gap: 10px;
}

.color-picker input[type="color"] {
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

.color-picker span {
    font-family: monospace;
    color: var(--text-color);
}

.save-section {
    margin-top: 20px;
    display: flex;
    gap: 10px;
}

.save-button,
.reset-button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
}

.save-button {
    background-color: var(--primary-color);
    color: white;
}

.save-button:hover {
    background-color: var(--secondary-color);
}

.reset-button {
    background-color: #e5e7eb;
    color: #374151;
}

.reset-button:hover {
    background-color: #d1d5db;
}
</style>