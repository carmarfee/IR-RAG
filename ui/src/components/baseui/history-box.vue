<template>
    <div class="ui-input-container">
        <input placeholder="搜索历史记录..." class="ui-input" type="text" />
        <div class="ui-input-underline"></div>
        <div class="ui-input-highlight"></div>
        <div class="ui-input-icon">
            <button style="background-color: transparent;border: none;">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <path stroke-linejoin="round" stroke-linecap="round" stroke-width="2" stroke="currentColor"
                        d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z">
                    </path>
                </svg>
            </button>
        </div>
    </div>
</template>

<style scoped>
.ui-input-container {
    position: relative;
    margin: 0 auto;
    width: calc(100% - 50px);
}

.ui-input {
    width: 100%;
    padding: 10px 10px 10px 40px;
    font-size: 1em;
    border: none;
    border-bottom: 2px solid #ccc;
    outline: none;
    background-color: transparent;
    transition: border-color 0.3s;
}

.ui-input:focus {
    border-color: #6c63ff;
}

.ui-input-underline {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 2px;
    width: 100%;
    background-color: #6c63ff;
    transform: scaleX(0);
    transition: transform 0.3s;
}

.ui-input:focus+.ui-input-underline {
    transform: scaleX(1);
}

.ui-input-highlight {
    position: absolute;
    bottom: 0;
    left: 0;
    height: 100%;
    width: 0;
    background-color: rgba(108, 99, 255, 0.1);
    transition: width 0.3s;
}

.ui-input:focus~.ui-input-highlight {
    width: 100%;
}

.ui-input-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #999;
    transition: color 0.3s;
}

.ui-input:focus~.ui-input-icon {
    color: #6c63ff;
}

.ui-input-icon svg {
    width: 20px;
    height: 20px;
}
</style>
