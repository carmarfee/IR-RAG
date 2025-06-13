<template>
<div class="rag-chat">
    <div class="messages-container" ref="messageContainer">
        <div v-for="message in messages" :key="message.id" class="message" :class="message.type">
            <div class="message-content">
                <div class="avatar">
                    <svg v-if="message.type === 'user'" viewBox="0 0 24 24" fill="currentColor">
                        <path
                            d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="currentColor">
                        <path
                            d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
                        <circle cx="12" cy="10" r="1" />
                        <circle cx="8" cy="10" r="1" />
                        <circle cx="16" cy="10" r="1" />
                    </svg>
                </div>
                <div class="message-bubble">
                    <span v-html="formatStreamingText(message.content)"></span>
                    <div v-if="message.isStreaming && message.type === 'bot'" class="loading-dots-inline small">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            </div>
        </div>

        <div v-if="isLoading && messages.length > 0 && messages[messages.length - 1].type === 'user'"
            class="message bot">
            <div class="message-content">
                <div class="avatar">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path
                            d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z" />
                        <circle cx="12" cy="10" r="1" />
                        <circle cx="8" cy="10" r="1" />
                        <circle cx="16" cy="10" r="1" />
                    </svg>
                </div>
                <div class="message-bubble">
                    <div class="loading-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        </div>


        <div class="bottom-spacer" ref="bottomSpacerEl"></div>
    </div>

    <div class="input-container">
        <div class="input-area">
            <textarea v-model="inputValue" @keypress.enter="handleKeyPress" :placeholder="inputPlaceholder"
                class="message-input" :rows="inputRows" />
            <div class="input-actions">
                <div class="input-hint">
                    {{ inputHint }}
                </div>
                <button @click="handleSend" :disabled="!inputValue.trim() || isLoading" class="send-button">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                    </svg>
                </button>
            </div>
        </div>
    </div>
</div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import { streamChat, setKnowledge } from '../../utils/RAG' // 确保路径正确
import { useSearchStore } from '../../stores/searchStore' // 确保路径正确

// Props定义
const props = defineProps({
    // 标题
    title: {
        type: String,
        default: 'RAG对话助手'
    },
    // 初始消息列表
    initialMessages: {
        type: Array,
        default: () => [
            { id: 1, type: 'bot', content: '您好！我是RAG助手，有什么可以帮助您的吗？', isStreaming: false }
        ]
    },
    // 输入框占位符
    inputPlaceholder: {
        type: String,
        default: '输入您的问题...'
    },
    // 输入框提示
    inputHint: {
        type: String,
        default: '按 Enter 发送，Shift + Enter 换行' // 更改提示以反映Shift+Enter
    },
    // 输入框行数
    inputRows: {
        type: Number,
        default: 3
    },
    // 是否自动滚动到底部
    autoScroll: {
        type: Boolean,
        default: true
    },
    // 组件是否在tabs中 (这个 prop 的用途需要根据你的具体场景决定，此处保留)
    inTabs: {
        type: Boolean,
        default: true
    },
    // 当前是否是活动Tab
    isActiveTab: {
        type: Boolean,
        default: false
    }
})
const searchStore = useSearchStore()
// Emits定义
const emit = defineEmits(['send-message', 'messages-update', 'knowledge-loaded', 'error'])

// 响应式数据
const messages = ref([])
const inputValue = ref('')
const isLoading = ref(false) // 用于控制整体API请求状态（发送按钮禁用，可选的全局加载指示）
const messageContainer = ref(null)
const bottomSpacerEl = ref(null); // Ref for the bottom spacer
const resizeObserver = ref(null)
// conversationHistory 用于发送给 streamChat API
const conversationHistory = ref([])

// 初始化 messages 和 conversationHistory
const initializeMessages = () => {
    messages.value = JSON.parse(JSON.stringify(props.initialMessages)).map(m => ({ ...m, isStreaming: m.isStreaming || false }));
    // 基于初始消息构建对话历史 (如果初始消息也需要加入历史记录)
    // conversationHistory.value = messages.value
    //   .filter(msg => msg.type === 'user' || msg.type === 'bot') // 只包括用户和助手的消息
    //   .map(msg => ({
    //     role: msg.type === 'user' ? 'user' : 'assistant',
    //     content: msg.content
    //   }));
    // 通常初始bot消息不加入发送给API的history，除非API设计如此
    conversationHistory.value = [];
};


// 监听初始消息变化 (如果父组件会动态改变 initialMessages)
watch(() => props.initialMessages, (newMessages) => {
    initializeMessages();
    nextTick(() => scrollToBottom());
}, { deep: true, immediate: true }) // immediate: true 确保初始时也执行

// 监听isActiveTab变化，当变为活动tab时，滚动到底部
watch(() => props.isActiveTab, (isActive) => {
    if (isActive && props.autoScroll) {
        nextTick(() => {
            scrollToBottom()
        })
    }
})


// 格式化流式文本（保持换行）
const formatStreamingText = (text) => {
    if (typeof text !== 'string') return '';
    return text.replace(/\n/g, '<br>')
}

// 处理 Enter 键发送
const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault() // 阻止默认的换行行为
        handleSend()
    }
    // 如果按了 Shift + Enter，textarea 会自动换行
}

// 发送消息
const handleSend = async () => {
    const trimmedInput = inputValue.value.trim()
    if (!trimmedInput || isLoading.value) return

    isLoading.value = true // 开始请求，设置加载状态

    const userMessage = {
        id: Date.now(),
        type: 'user',
        content: trimmedInput,
        isStreaming: false
    }
    messages.value.push(userMessage)
    // 滚动以显示用户消息
    if (props.autoScroll) {
        await nextTick()
        scrollToBottom()
    }

    const messageToSendToAPI = trimmedInput
    inputValue.value = '' // 清空输入框

    // 更新发送给 API 的对话历史
    conversationHistory.value.push({
        role: 'user',
        content: messageToSendToAPI
    })

    // 创建并添加临时的 bot 消息到 messages 数组用于流式显示
    const botStreamingMessage = {
        id: Date.now() + 1, // 确保ID唯一
        type: 'bot',
        content: '', // 初始为空
        isStreaming: true
    }
    messages.value.push(botStreamingMessage)

    // 再次滚动以准备显示流式消息
    if (props.autoScroll) {
        await nextTick()
        scrollToBottom()
    }

    try {
        console.log('Starting RAG chat stream with input:', trimmedInput)
        await streamChat(
            // 发送当前的对话历史
            // 注意：如果API期望每次只发送最后几条，或者有特定格式，需要调整这里
            trimmedInput, // 发送副本以防意外修改
            // onChunk - 处理流式数据块
            (chunk) => {
                const targetMessage = messages.value.find(m => m.id === botStreamingMessage.id)
                if (targetMessage) {
                    targetMessage.content += chunk
                }
                if (props.autoScroll) {
                    scrollToBottom() // 频繁滚动，可考虑节流
                }
            },

            // onComplete - 流式完成
            (fullResponse) => {
                const targetMessage = messages.value.find(m => m.id === botStreamingMessage.id)
                if (targetMessage) {
                    targetMessage.content = fullResponse // 确保最终内容是完整的
                    targetMessage.isStreaming = false // 标记流式结束
                }
                // 将完整的助手回复添加到 API 对话历史
                conversationHistory.value.push({
                    role: 'assistant',
                    content: fullResponse
                })
                emit('send-message', { // 这个事件可以表示一次完整的交互结束
                    content: messageToSendToAPI,
                    response: fullResponse
                })
                isLoading.value = false // 流式结束，解除加载状态
                if (props.autoScroll) {
                    nextTick(scrollToBottom);
                }
            },

            // onError - 错误处理
            (error) => {
                console.error('Streaming error:', error)
                const targetMessage = messages.value.find(m => m.id === botStreamingMessage.id)
                if (targetMessage) {
                    targetMessage.content = '抱歉，消息流处理失败，请稍后再试。'
                    targetMessage.isStreaming = false
                } else {
                    // 理论上 targetMessage 应该总是能找到
                    messages.value.push({
                        id: Date.now() + 2, type: 'bot', content: '抱歉，出现错误，请稍后再试。', isStreaming: false
                    });
                }
                // 也将错误信息添加到 API 对话历史中，以表示对话中断
                // conversationHistory.value.push({ role: 'assistant', content: '[STREAMING ERROR]' });
                isLoading.value = false
                emit('error', { type: 'streaming', message: '消息流处理失败', details: error })
                if (props.autoScroll) {
                    nextTick(scrollToBottom);
                }
            }
        )
    } catch (error) {
        console.error('Failed to start RAG chat stream:', error)
        const targetMessage = messages.value.find(m => m.id === botStreamingMessage.id);
        if (targetMessage) {
            targetMessage.content = '抱歉，无法启动对话服务，请检查网络或稍后再试。'
            targetMessage.isStreaming = false;
        } else {
            // 如果 botStreamingMessage 都没来得及添加
            messages.value.push({
                id: Date.now() + 2, type: 'bot', content: '抱歉，无法启动对话服务。', isStreaming: false
            });
        }
        isLoading.value = false
        emit('error', { type: 'initiation', message: '无法启动对话服务', details: error })
        if (props.autoScroll) {
            nextTick(scrollToBottom);
        }
    }
    // 可以在流开始后即触发，或在onComplete后触发，取决于具体需求
    emit('messages-update', messages.value)
}


// 滚动到底部
const scrollToBottom = () => {
    if (messageContainer.value) {
        // 使用平滑滚动效果更好
        messageContainer.value.scrollTo({
            top: messageContainer.value.scrollHeight,
            behavior: 'smooth'
        });
    }
}

// 清空消息 (保留，由父组件调用)
const clearMessages = () => {
    messages.value = []
    conversationHistory.value = [] // 同时清空API历史
    // 可以考虑是否需要重新添加初始的bot消息
    // initializeMessages();
    emit('messages-update', messages.value)
}

// 添加消息 (保留，主要用于父组件或外部控制添加非流式消息)
const addMessage = (message) => {
    messages.value.push({
        id: Date.now(),
        isStreaming: false, // 假设外部添加的消息不是流式的
        ...message
    })
    // 如果是助手消息，也应添加到 conversationHistory
    if (message.type === 'bot' || message.type === 'assistant') {
        conversationHistory.value.push({ role: 'assistant', content: message.content });
    } else if (message.type === 'user') {
        conversationHistory.value.push({ role: 'user', content: message.content });
    }

    emit('messages-update', messages.value)

    if (props.autoScroll) {
        nextTick(() => {
            scrollToBottom()
        })
    }
}

// 调整消息容器的 padding-bottom 以免被输入框遮挡
const adjustMessageContainerLayout = () => {
    if (messageContainer.value && bottomSpacerEl.value) {
        const inputContainer = document.querySelector('.input-container'); // 或者给 input-container 加一个 ref
        if (inputContainer) {
            const inputContainerHeight = inputContainer.offsetHeight;
            // 使用 bottom-spacer 的高度来推开内容
            bottomSpacerEl.value.style.height = `${inputContainerHeight + 16}px`; // 16px 是额外的间距
        }
    }
    // 确保在布局调整后，如果需要，则滚动
    if (props.autoScroll) {
        // scrollToBottom(); // 避免在调整时强制滚动，除非有新消息
    }
};

onMounted(async () => {
    initializeMessages(); // 初始化消息

    nextTick(() => { // 确保DOM渲染完毕
        adjustMessageContainerLayout();
        if (props.autoScroll) {
            scrollToBottom();
        }
    });

    if (window.ResizeObserver) {
        resizeObserver.value = new ResizeObserver(() => {
            adjustMessageContainerLayout()
        })
        // 监听输入框容器或聊天组件根元素的大小变化可能更合适
        const inputContainerEl = document.querySelector('.input-container');
        if (inputContainerEl) {
            resizeObserver.value.observe(inputContainerEl);
        }
        if (messageContainer.value) { // 也可以监听消息容器本身，如果其大小会变
            // resizeObserver.value.observe(messageContainer.value);
        }
    }
    window.addEventListener('resize', adjustMessageContainerLayout)
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', adjustMessageContainerLayout)
    if (resizeObserver.value) {
        resizeObserver.value.disconnect()
    }
})

// 暴露给父组件的方法
defineExpose({
    clearMessages,
    addMessage,
    scrollToBottom,
    adjustMessageContainerHeight: adjustMessageContainerLayout // 重命名以匹配功能
})
</script>

<style scoped>
/* 组件容器 - 相对定位，适应Tabs内容高度 */
.rag-chat {
    position: relative;
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 300px;
    /* 确保有最小高度 */
    overflow: hidden;
    background-color: #f9fafb;
    /* 添加一个背景色 */
}

/* 消息容器 - 可滚动区域 */
.messages-container {
    flex: 1;
    /* 占据所有可用空间 */
    position: relative;
    /* For absolute positioning of input-container relative to this if needed */
    /* height: 100%; 不再需要，flex:1 会处理 */
    overflow-y: auto;
    overflow-x: hidden;
    padding: 16px 16px 0 16px;
    /* 顶部和左右padding, 底部padding由spacer控制 */
    -webkit-overflow-scrolling: touch;
    /* 优化移动端滚动 */
}

/* 底部空间 */
.bottom-spacer {
    /* height is set dynamically by JS */
    width: 100%;
    flex-shrink: 0;
    /* 防止被压缩 */
}

/* 输入容器 - 固定在底部 */
.input-container {
    /* position: absolute; 改为flex布局的一部分，或保持fixed/sticky */
    /* bottom: 0;
    left: 0;
    right: 0; */
    width: 100%;
    /* 确保宽度 */
    background: white;
    border-top: 1px solid #e5e7eb;
    padding: 12px 16px;
    /* 统一padding */
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
    /* 稍微柔和的阴影 */
    z-index: 10;
    box-sizing: border-box;
    flex-shrink: 0;
    /* 防止被消息容器压缩 */
}

/* 输入区域布局 */
.input-area {
    display: flex;
    flex-direction: column;
    gap: 8px;
    /* 减小一点间距 */
    max-width: 800px;
    margin: 0 auto;
}

.message-input {
    width: 100%;
    resize: none;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    /* 稍微小一点的圆角 */
    padding: 10px 14px;
    font-size: 15px;
    /* 调整字体大小 */
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    font-family: inherit;
    line-height: 1.4;
    max-height: 120px;
    /* 调整最大高度 */
    overflow-y: auto;
    box-sizing: border-box;
}

.message-input:focus {
    border-color: #7c3aed;
    /* 使用主题色 */
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2);
}

/* 输入框下方的操作区域 */
.input-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.input-hint {
    font-size: 12px;
    color: #6b7280;
}

.send-button {
    background: #7c3aed;
    color: white;
    width: 36px;
    /* 调整大小 */
    height: 36px;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    transition: background-color 0.2s, transform 0.2s, opacity 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.send-button:hover:not(:disabled) {
    background: #6d28d9;
    transform: scale(1.05);
}

.send-button:disabled {
    background-color: #a7a7a7;
    /* 更明显的禁用颜色 */
    opacity: 0.7;
    cursor: not-allowed;
}

.send-button svg {
    width: 18px;
    height: 18px;
}

/* 消息样式 */
.message {
    display: flex;
    margin-bottom: 12px;
    /* 减小消息间距 */
    animation: fadeIn 0.3s ease-out;
    /* 动画效果 */
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message.user {
    justify-content: flex-end;
}

.message.bot {
    justify-content: flex-start;
}

.message-content {
    display: flex;
    align-items: flex-start;
    /* 头像和气泡顶部对齐 */
    gap: 8px;
    max-width: 85%;
    /* 调整最大宽度 */
}

.message.user .message-content {
    flex-direction: row-reverse;
}

.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
    /* 微调头像位置 */
}

.message.user .avatar {
    background: #7c3aed;
    color: white;
}

.message.bot .avatar {
    background: #e5e7eb;
    /* 浅灰色背景 */
    color: #4b5563;
}

.avatar svg {
    width: 16px;
    height: 16px;
}

.message-bubble {
    padding: 8px 14px;
    /* 调整内边距 */
    border-radius: 18px;
    /* 更圆润的边角 */
    line-height: 1.45;
    word-wrap: break-word;
    word-break: break-word;
    /* 确保长单词能换行 */
    font-size: 14.5px;
    /* 调整字体大小 */
    position: relative;
    /* For inline loading dots */
    text-align: left;
}

.message.user .message-bubble {
    background: #7c3aed;
    color: white;
    border-bottom-right-radius: 6px;
    /* 调整特定圆角 */
}

.message.bot .message-bubble {
    background: #ffffff;
    color: #1f2937;
    /* 深色文字提高对比度 */
    border: 1px solid #e5e7eb;
    border-bottom-left-radius: 6px;
}

/* 加载动画 (全局的和行内的) */
.loading-dots,
.loading-dots-inline {
    display: flex;
    align-items: center;
    /* 垂直居中点 */
    gap: 4px;
}

.loading-dots {
    /* 用于全局加载指示器 */
    padding: 8px 0;
}

.loading-dots-inline {
    /* 用于消息气泡内 */
    display: inline-flex;
    /* 改为inline-flex使其可以和文本在同一行 */
    margin-left: 6px;
    /* 与文本有一些间距 */
    vertical-align: middle;
    /* 尝试与文本对齐 */
}

.loading-dots span,
.loading-dots-inline span {
    width: 7px;
    /* 调整大小 */
    height: 7px;
    background: #6b7280;
    border-radius: 50%;
    animation: bounce 1.2s infinite ease-in-out;
    /* 调整动画 */
}

.loading-dots-inline.small span {
    /* 更小的点 */
    width: 5px;
    height: 5px;
}

.loading-dots span:nth-child(2),
.loading-dots-inline span:nth-child(2) {
    animation-delay: 0.15s;
}

.loading-dots span:nth-child(3),
.loading-dots-inline span:nth-child(3) {
    animation-delay: 0.3s;
}

@keyframes bounce {

    0%,
    80%,
    100% {
        transform: scale(0.5);
        /* 点更动态地变化 */
        opacity: 0.5;
    }

    40% {
        transform: scale(1.0);
        opacity: 1;
    }
}


/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-track {
    background: transparent;
    /* 使轨道透明 */
}

.messages-container::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    /* 更柔和的滚动条颜色 */
    border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
    background: #9ca3af;
}

/* 响应式适配 */
@media (max-width: 640px) {
    .message-content {
        max-width: 90%;
    }

    .input-container {
        padding: 10px 12px;
    }

    .message-input {
        font-size: 14px;
        padding: 8px 12px;
    }

    .message-bubble {
        font-size: 14px;
        padding: 7px 12px;
    }

    .send-button {
        width: 32px;
        height: 32px;
    }

    .send-button svg {
        width: 16px;
        height: 16px;
    }
}
</style>