import axios from "axios";

const preprocess_api = axios.create({
    baseURL: "http://localhost:8000/preprocess",
    timeout: 10000,
});

export async function CheckPreprocessFile() {
    try {
        const response = await preprocess_api.get("/check_preprocess_file");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("CheckPreprocessFile error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function StartPreprocess() {
    try {
        const response = await preprocess_api.get("/start_proprecess");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("StartPreprocess error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}