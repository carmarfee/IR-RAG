// stores/search.ts
import { defineStore } from 'pinia';
import { Search } from '../api/search';

interface SearchResult { 
    doc_id: number;
    title: string;
    content: string;
    source: string;
    pubilish_time: string;
    [key: string]: any;
}

export const useSearchStore = defineStore('search', {
    state: () => ({
        results: [] as SearchResult[],  // 替换为你的数据类型
        query: '',
        isLoading: false,
        error: null as Error | null,
    }),
    actions: {
        async search(query: string) {
            this.query = query;
            this.isLoading = true;
            this.error = null;

            try {
                const response = await Search(query); // 调用你的API
                this.results = response;
                console.log(response)
                return response.data;
            } catch (error) {
                this.error = error as Error;
                throw error;
            } finally {
                this.isLoading = false;
            }
        },
    },
});