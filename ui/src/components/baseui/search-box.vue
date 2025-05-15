<style scoped>
.input-container {
    padding: 20px;
    position: relative;
}

.icon {
    position: absolute;
    right: 25px;
    top: calc(50% + 5px);
    transform: translateY(calc(-50% - 5px));
}

.input {
    width: 100%;
    height: 40px;
    padding: 10px;
    transition: .2s linear;
    border: 2.5px solid rgb(91, 76, 76);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 2px;
    background-color: transparent;
}

.input:focus {
    outline: none;
    border: 0.5px solid black;
    box-shadow: -5px -5px 0px black;
}

.input-container:hover>.icon {
    animation: anim 1s linear infinite;
}

@keyframes anim {

    0%,
    100% {
        transform: translateY(calc(-50% - 5px)) scale(1);
    }

    50% {
        transform: translateY(calc(-50% - 5px)) scale(1.1);
    }
}
</style>

<template>
    <div class="input-container">
        <input type="text" name="text" class="input" placeholder="search..." v-model="searchQuery"
            @keyup.enter="handleSearch">
        <button class="icon" style="background-color: transparent;border: none;" @click="handleSearch">
            <svg width="19px" height="19px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                <g id="SVGRepo_iconCarrier">
                    <path opacity="1" d="M14 5H20" stroke="#000" stroke-width="1.5" stroke-linecap="round"
                        stroke-linejoin="round"></path>
                    <path opacity="1" d="M14 8H17" stroke="#000" stroke-width="1.5" stroke-linecap="round"
                        stroke-linejoin="round"></path>
                    <path d="M21 11.5C21 16.75 16.75 21 11.5 21C6.25 21 2 16.75 2 11.5C2 6.25 6.25 2 11.5 2"
                        stroke="#000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"></path>
                    <path opacity="1" d="M22 22L20 20" stroke="#000" stroke-width="3.5" stroke-linecap="round"
                        stroke-linejoin="round"></path>
                </g>
            </svg>
        </button>

    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { useSearchStore } from '../../stores/searchStore';
import { RecordHistory } from '../../api/history';


const searchStore = useSearchStore();
const searchQuery = ref(searchStore.query);
//-------------------------------分割线--------------------------------
const handleSearch = async () => {
    if (!searchQuery.value.trim()) return;
    await searchStore.search(searchQuery.value);
    // 记录搜索历史
    const currentTime = new Date().toISOString();
    await RecordHistory(searchQuery.value, currentTime, searchStore.results.length);
};

</script>
