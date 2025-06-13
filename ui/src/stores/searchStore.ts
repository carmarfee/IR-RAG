// stores/search.ts
import { defineStore } from 'pinia';
import { Search } from '../api/search';
import { setKnowledge } from '../utils/RAG';

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
        knowledge: { data: '' } as object,  // 用于存储知识库内容
    }),
    actions: {
        async search(query: string) {
            this.query = query;
            this.isLoading = true;
            this.error = null;

            try {
                const response = await Search(query); // 调用你的API
                this.results = response;
                return response.data;
            } catch (error) {
                this.error = error as Error;
                throw error;
            } finally {
                this.isLoading = false;
            }
        },
        async getAllDocIDs() {
            this.error = null;

            try {
                let allDocs = this.results.map(doc => ({ doc_id: doc.doc_id }));
                return allDocs;
            } catch (error) {
                this.error = error as Error;
                throw error;
            }
        }
    },
});