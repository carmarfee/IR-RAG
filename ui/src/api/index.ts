import axios from "axios";

const index_api = axios.create({
    baseURL: "http://localhost:8000/index",
    timeout: 10000,
});

export async function CheckIndexFile() {
    try {
        const response = await index_api.get("/check_index_file");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("CheckIndexFile error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function StartInvertedIndex() {
    try {
        const response = await index_api.get("/start_inverted_index");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("StartInvertedIndex error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}