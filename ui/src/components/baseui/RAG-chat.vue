<template>
    <div class="rag-chat">
        <!-- 消息区域 - 内部滚动 -->
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
                        {{ message.content }}
                    </div>
                </div>
            </div>

            <!-- 加载中指示器 -->
            <div v-if="isLoading" class="message bot">
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

            <!-- 底部占位空间，防止最后的消息被输入框遮挡 -->
            <div class="bottom-spacer"></div>
        </div>

        <!-- 输入区域 - 固定在底部 -->
        <div class="input-container">
            <div class="input-area">
                <textarea v-model="inputValue" @keypress.enter.prevent="handleKeyPress" :placeholder="inputPlaceholder"
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
import { ref, nextTick, onMounted, watch, onBeforeUnmount } from 'vue'

// Props定义
const props = defineProps({
    // 标题
    title: {
        type: String,
        default: 'RAG智能对话'
    },
    // 初始消息列表
    initialMessages: {
        type: Array,
        default: () => [
            { id: 1, type: 'bot', content: '您好！我是RAG助手，有什么可以帮助您的吗？' }
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
        default: '按 Enter 发送消息，Shift + Enter 换行'
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
    // 组件是否在tabs中
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

// Emits定义
const emit = defineEmits(['send-message', 'messages-update'])

// 响应式数据
const messages = ref([...props.initialMessages])
const inputValue = ref('')
const isLoading = ref(false)
const messageContainer = ref(null)
const resizeObserver = ref(null)

// 监听初始消息变化
watch(() => props.initialMessages, (newMessages) => {
    messages.value = [...newMessages]
})

// 监听isActiveTab变化，当变为活动tab时，滚动到底部
watch(() => props.isActiveTab, (isActive) => {
    if (isActive && props.autoScroll) {
        nextTick(() => {
            scrollToBottom()
        })
    }
})

// 发送消息
const handleSend = async () => {
    if (!inputValue.value.trim() || isLoading.value) return

    const userMessage = {
        id: Date.now(),
        type: 'user',
        content: inputValue.value
    }

    messages.value.push(userMessage)
    const messageCopy = inputValue.value
    inputValue.value = ''

    // 触发发送消息事件
    emit('send-message', {
        content: messageCopy,
        callback: (response) => {
            // 处理回调响应
            if (response) {
                addBotMessage(response)
            }
        }
    })

    // 更新消息列表事件
    emit('messages-update', messages.value)

    if (props.autoScroll) {
        await nextTick()
        scrollToBottom()
    }
}

// 添加机器人消息
const addBotMessage = (content) => {
    const botMessage = {
        id: Date.now(),
        type: 'bot',
        content
    }
    messages.value.push(botMessage)
    emit('messages-update', messages.value)

    if (props.autoScroll) {
        nextTick(() => {
            scrollToBottom()
        })
    }
}

// 设置加载状态
const setLoading = (loading) => {
    isLoading.value = loading
}

// 处理键盘事件
const handleKeyPress = (e) => {
    if (!e.shiftKey) {
        handleSend()
    }
}

// 滚动到底部
const scrollToBottom = () => {
    if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
}

// 清空消息
const clearMessages = () => {
    messages.value = []
    emit('messages-update', messages.value)
}

// 添加消息
const addMessage = (message) => {
    messages.value.push({
        id: Date.now(),
        ...message
    })
    emit('messages-update', messages.value)

    if (props.autoScroll) {
        nextTick(() => {
            scrollToBottom()
        })
    }
}

// 调整消息容器大小的函数
const adjustMessageContainerHeight = () => {
    if (messageContainer.value) {
        const inputContainerHeight = document.querySelector('.input-container')?.offsetHeight || 0
        messageContainer.value.style.paddingBottom = `${inputContainerHeight}px`
        scrollToBottom()
    }
}

// 组件挂载时设置
onMounted(() => {
    // 初始滚动
    if (props.autoScroll) {
        scrollToBottom()
    }
    
    // 设置ResizeObserver监听容器大小变化
    if (window.ResizeObserver) {
        resizeObserver.value = new ResizeObserver(() => {
            adjustMessageContainerHeight()
        })
        
        if (messageContainer.value) {
            resizeObserver.value.observe(messageContainer.value)
        }
        
        // 初始调整高度
        nextTick(() => {
            adjustMessageContainerHeight()
        })
    }
    
    // 监听窗口大小变化
    window.addEventListener('resize', adjustMessageContainerHeight)
})

// 组件卸载前清理
onBeforeUnmount(() => {
    // 移除事件监听
    window.removeEventListener('resize', adjustMessageContainerHeight)
    
    // 销毁ResizeObserver
    if (resizeObserver.value) {
        resizeObserver.value.disconnect()
    }
})

// 暴露给父组件的方法
defineExpose({
    setLoading,
    addBotMessage,
    clearMessages,
    addMessage,
    scrollToBottom,
    adjustMessageContainerHeight
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
    overflow: hidden;
}

/* 消息容器 - 可滚动区域 */
.messages-container {
    flex: 1;
    position: relative;
    height: 100%;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 16px;
    /* 底部空间会在JS中动态设置，确保不被输入框遮挡 */
}

/* 底部空间 */
.bottom-spacer {
    height: 20px;
    width: 100%;
}

/* 输入容器 - 固定在底部 */
.input-container {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: white;
    border-top: 1px solid #e5e7eb;
    padding: 16px;
    box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.08);
    z-index: 10;
}

/* 输入区域布局 */
.input-area {
    display: flex;
    flex-direction: column;
    gap: 12px;
    max-width: 800px;
    margin: 0 auto;
}

.message-input {
    width: 100%;
    resize: none;
    border: 1px solid #d1d5db;
    border-radius: 12px;
    padding: 12px 16px;
    font-size: 16px;
    outline: none;
    transition: all 0.2s;
    font-family: inherit;
    max-height: 150px;
    overflow-y: auto;
    box-sizing: border-box;
}

.message-input:focus {
    border-color: #a78bfa;
    box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
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
    width: 40px;
    height: 40px;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    transition: all 0.2s;
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
    opacity: 0.5;
    cursor: not-allowed;
}

.send-button svg {
    width: 18px;
    height: 18px;
}

/* 消息样式 */
.message {
    display: flex;
    margin-bottom: 16px;
    animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
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
    gap: 8px;
    max-width: 80%;
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
}

.message.user .avatar {
    background: #7c3aed;
    color: white;
}

.message.bot .avatar {
    background: #d1d5db;
    color: #4b5563;
}

.avatar svg {
    width: 16px;
    height: 16px;
}

.message-bubble {
    padding: 4px 16px;
    border-radius: 16px;
    line-height: 1.5;
    word-wrap: break-word;
    word-break: break-word;
    font-size: small;
}

.message.user .message-bubble {
    background: #7c3aed;
    color: white;
    border-bottom-right-radius: 4px;
}

.message.bot .message-bubble {
    background: white;
    border: 1px solid #e5e7eb;
    border-bottom-left-radius: 4px;
}

/* 加载动画 */
.loading-dots {
    display: flex;
    gap: 4px;
    padding: 4px 0;
}

.loading-dots span {
    width: 8px;
    height: 8px;
    background: #6b7280;
    border-radius: 50%;
    animation: bounce 1s infinite;
}

.loading-dots span:nth-child(2) {
    animation-delay: 0.2s;
}

.loading-dots span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes bounce {

    0%,
    100% {
        transform: translateY(-25%);
        opacity: 0.6;
    }

    50% {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
    width: 6px;
}

.messages-container::-webkit-scrollbar-track {
    background: transparent;
}

.messages-container::-webkit-scrollbar-thumb {
    background: #d1d5db;
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
        padding: 12px;
    }
}
</style>