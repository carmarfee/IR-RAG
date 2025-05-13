import axios from "axios";

const history_api = axios.create({
    baseURL: "http://localhost:8000/history",
    timeout: 10000,
});

export async function RecordHistory(search_query: string, time: string, num: number) {
    try {
        const response = await history_api.get("/record_history", {
            params: {
                search_query: search_query,
                time: time,
                num: num
            }
        });
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("RecordHistory error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function GetAllHistory() {
    try {
        const response = await history_api.get("/get_history")
        return response.data;
    }
    catch (error) {
        console.error("GetAllHistory error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function DeleteHistory(id: number) {
    try {
        const response = await history_api.get("/remove_history", {
            params: {
                id: id
            }
        });
        return response.data;
    } catch (error) {
        console.error("DeleteHistory error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function DeleteAllHistory() {
    try {
        const response = await history_api.get("/remove_all_history");
        return response.data;
    } catch (error) {
        console.error("DeleteAllHistory error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}