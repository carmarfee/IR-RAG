// stores/themeStore.ts
import { defineStore } from 'pinia';

export interface ThemeState {
    currentTheme: string;
    themes: Record<string, ThemeColors>;
}

export interface ThemeColors {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    sidebar: string;
    sidebarText: string;
    sidebarActive: string;
    border: string;
    icon: string;
}

export const useThemeStore = defineStore('theme', {
    state: (): ThemeState => ({
        currentTheme: localStorage.getItem('theme') || 'light',
        themes: {
            light: {
                primary: '#F8F8FF',
                secondary: '#8b5cf6',
                background: '#f9fafb',
                surface: '#ffffff',
                text: '#111827',
                sidebar: '#ffffff',
                sidebarText: '#4b5563',
                sidebarActive: '#ede9fe',
                border: '#e5e7eb',
                icon: '#6d28d9'
            },
            dark: {
                primary: '#4E4E6A',
                secondary: '#a78bfa',
                background: '#1f2937',
                surface: '#111827',
                text: '#f9fafb',
                sidebar: '#111827',
                sidebarText: '#d1d5db',
                sidebarActive: '#4c1d95',
                border: '#374151',
                icon: '#8b5cf6'
            }
        }
    }),

    getters: {
        currentThemeColors: (state) => state.themes[state.currentTheme],
    },

    actions: {
        setTheme(theme: string) {
            if (this.themes[theme]) {
                this.currentTheme = theme;
                localStorage.setItem('theme', theme);
                this.applyTheme();
            }
        },

        applyTheme() {
            const colors = this.themes[this.currentTheme];

            // 应用CSS变量到根元素
            const root = document.documentElement;

            root.style.setProperty('--primary-color', colors.primary);
            root.style.setProperty('--secondary-color', colors.secondary);
            root.style.setProperty('--background-color', colors.background);
            root.style.setProperty('--surface-color', colors.surface);
            root.style.setProperty('--text-color', colors.text);
            root.style.setProperty('--sidebar-color', colors.sidebar);
            root.style.setProperty('--sidebar-text-color', colors.sidebarText);
            root.style.setProperty('--sidebar-active-color', colors.sidebarActive);
            root.style.setProperty('--border-color', colors.border);
            root.style.setProperty('--icon-color', colors.icon);
        },

        initTheme() {
            this.applyTheme();
        }
    }
});