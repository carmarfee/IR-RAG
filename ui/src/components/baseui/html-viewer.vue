<template>
    <div class="html-content-viewer">
        <div v-if="loading" class="loading">
            <el-skeleton :rows="10" animated />
        </div>
        <div v-else>
            <div class="content-header">
                <h1>{{ title }}</h1>
                <div class="meta-info" >
                    <span style="width: 100%;;align-items: center;">网页地址:{{url}}</span>
                </div>
            </div>
            <div class="content-container" ref="contentContainer"></div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch,onUnmounted } from 'vue';
import DOMPurify from 'dompurify';

const props = defineProps({
    // HTML内容
    htmlContent: {
        type: String,
        default: ''
    },
    // 原始HTML (从父组件传入)
    rawHtml: {
        type: String,
        default: ''
    },
    // 文档ID，用于获取HTML内容
    docId: {
        type: [Number, String],
        default: null
    },
    // 标题
    title: {
        type: String,
        default: ''
    },
    url: {
        type: String,
        default: ''
    },
    // 是否自动加载内容
    autoLoad: {
        type: Boolean,
        default: true
    },
    // 允许的HTML标签，空数组表示允许所有标签
    allowedTags: {
        type: Array,
        default: () => []
    },
    // 允许的HTML属性，空数组表示允许所有属性
    allowedAttrs: {
        type: Array,
        default: () => []
    }
});

const loading = ref(true);
const contentContainer = ref(null);
const htmlContentToDisplay = ref('');

//-------------------------------分割线--------------------------------


// 配置DOMPurify - 允许所有内容通过，包括样式和脚本
const configureDOMPurify = () => {
    // 一个钩子函数，在DOMPurify处理之后替换所有script和img的src
    DOMPurify.addHook('afterSanitizeAttributes', (node) => {
        if (node.tagName === 'IMG') {
            node.setAttribute('src', 'assets/images/404.png');
            node.classList.add('responsive-image');
        }
        if (node.tagName === 'SCRIPT') {
            if (node.hasAttribute('src')) {
                node.setAttribute('src', 'assets/js/tmp.js');
            }
        }
    });

    // 设置DOMPurify允许所有标签和属性，包括样式和脚本
    DOMPurify.setConfig({
        ADD_TAGS: ['script', 'style'],
        ADD_ATTR: ['*'],
        ALLOW_UNKNOWN_PROTOCOLS: true,
        USE_PROFILES: { html: true, svg: true, svgFilters: true },
        FORCE_BODY: false,
        WHOLE_DOCUMENT: true
    });

    // 如果提供了特定的允许标签和属性，则优先使用它们
    if (props.allowedTags.length > 0) {
        DOMPurify.setConfig({
            ALLOWED_TAGS: props.allowedTags
        });
    }

    if (props.allowedAttrs.length > 0) {
        DOMPurify.setConfig({
            ALLOWED_ATTR: props.allowedAttrs
        });
    }
};

// 净化并渲染HTML内容 - 保留完整结构
const renderContent = (content) => {
    if (!content) return;

    configureDOMPurify();

    // 使用DOMPurify处理内容，但保留尽可能多的原始内容
    const sanitizedContent = DOMPurify.sanitize(content, {
        ADD_TAGS: ['script', 'style'],
        KEEP_CONTENT: true
    });

    if (contentContainer.value) {
        // 设置完整的HTML内容
        contentContainer.value.innerHTML = sanitizedContent;

        // 处理内部链接
        const links = contentContainer.value.querySelectorAll('a');
        links.forEach(link => {
            if (link.getAttribute('href') && !link.getAttribute('target')) {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            }
        });

        // 执行脚本标签内容（如果需要）
        executeScripts(contentContainer.value);
    }

    loading.value = false;
};

// 执行HTML中的脚本
const executeScripts = (container) => {
    // 查找所有脚本标签
    const scripts = container.querySelectorAll('script');
    scripts.forEach(oldScript => {
        const newScript = document.createElement('script');

        // 复制脚本属性
        Array.from(oldScript.attributes).forEach(attr => {
            newScript.setAttribute(attr.name, attr.value);
        });

        // 复制内联脚本内容
        newScript.appendChild(document.createTextNode(oldScript.innerHTML));

        // 替换原始脚本标签
        oldScript.parentNode.replaceChild(newScript, oldScript);
    });
};

// 获取HTML内容 - 返回完整内容而不是提取
const fetchHtmlContent = async () => {
    if (!props.docId) return;

    loading.value = true;
    try {
        const response = await fetch(`/api/get_snapshot?doc_id=${props.docId}`);
        if (response.ok) {
            const data = await response.text();
            htmlContentToDisplay.value = data;
            renderContent(data); // 渲染完整内容
        } else {
            console.error('获取HTML内容失败:', response.statusText);
            loading.value = false;
        }
    } catch (error) {
        console.error('获取HTML内容错误:', error);
        loading.value = false;
    }
};

// 监听htmlContent属性变化
watch(() => props.htmlContent, (newContent) => {
    if (newContent) {
        htmlContentToDisplay.value = newContent;
        renderContent(newContent);
    }
});

// 监听rawHtml属性变化 - 直接渲染完整内容
watch(() => props.rawHtml, (newHtml) => {
    if (newHtml) {
        htmlContentToDisplay.value = newHtml;
        renderContent(newHtml); // 渲染完整HTML而不是提取
    }
});

// 监听docId属性变化
watch(() => props.docId, (newDocId) => {
    if (newDocId && props.autoLoad) {
        fetchHtmlContent();
    }
});

onMounted(() => {
    if (props.rawHtml) {
        // 优先使用传入的rawHtml
        htmlContentToDisplay.value = props.rawHtml;
        renderContent(props.rawHtml);
    } else if (props.htmlContent) {
        // 其次使用htmlContent
        htmlContentToDisplay.value = props.htmlContent;
        renderContent(props.htmlContent);
    } else if (props.docId && props.autoLoad) {
        // 最后尝试通过docId获取内容
        fetchHtmlContent();
    } else {
        loading.value = false;
    }
});

onUnmounted(() => {
    loading.value = false
});

// 暴露方法
defineExpose({
    reload: fetchHtmlContent
});
</script>

<style scoped>
.html-content-viewer {
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading {
    padding: 20px 0;
}

.content-header {
    margin-bottom: 20px;
    border-bottom: 1px solid #eaeaea;
    padding-bottom: 15px;
}

.content-header h1 {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
}

.meta-info {
    color: #888;
    font-size: 14px;
    display: flex;
    gap: 15px;
}

.content-container {
    line-height: 1.8;
    color: #333;
}

.content-container :deep(img) {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 15px auto;
    border-radius: 4px;
}

.content-container :deep(p) {
    margin-bottom: 16px;
    text-indent: 2em;
}

.content-container :deep(h1),
.content-container :deep(h2),
.content-container :deep(h3),
.content-container :deep(h4),
.content-container :deep(h5),
.content-container :deep(h6) {
    margin-bottom: 16px;
    margin-top: 24px;
    font-weight: bold;
}

.content-container :deep(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 16px;
}

.content-container :deep(th),
.content-container :deep(td) {
    border: 1px solid #ddd;
    padding: 8px 12px;
}

.content-container :deep(th) {
    background-color: #f5f7fa;
}

.content-container :deep(a) {
    color: #409eff;
    text-decoration: none;
}

.content-container :deep(a:hover) {
    text-decoration: underline;
}

.content-container :deep(blockquote) {
    border-left: 4px solid #ddd;
    padding-left: 16px;
    color: #666;
    margin: 16px 0;
}

.content-container :deep(pre),
.content-container :deep(code) {
    background-color: #f5f7fa;
    padding: 8px;
    border-radius: 4px;
    font-family: Consolas, Monaco, 'Andale Mono', monospace;
    overflow-x: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .html-content-viewer {
        padding: 15px;
    }

    .content-header h1 {
        font-size: 20px;
    }

    .meta-info {
        flex-direction: column;
        gap: 5px;
    }
}
</style>