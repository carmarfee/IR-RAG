import axios from "axios";

const search_api = axios.create({
    baseURL: "http://localhost:8000/search",
    timeout: 10000,
});

export async function Search(query: string) {
    try {
        const response = await search_api.get("/search_engine", {
            params: {
                query: query
            }
        });
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("Search error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}


export async function GetSnapShot(doc_id: number) {
    const response = await search_api.get("/get_snapshot", {
        params: {
            doc_id: doc_id
        }
    });
    return response;
}

export async function GetContent(doc_id: number) {
    const response = await search_api.get("/get_content", {
        params: {
            doc_id: doc_id
        }
    });
    return response;
}