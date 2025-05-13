import axios from "axios";

const crawler_api = axios.create({
    baseURL: "http://localhost:8000/crawler",
    timeout: 10000,
});

export async function StartCrawler() {
    try {
        const response = await crawler_api.get("/start_crawler");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("StartCrawler error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function StopCrawler() {
    try {
        const response = await crawler_api.get("/stop_crawler");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("StopCrawler error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function ContinueCrawler() {
    try {
        const response = await crawler_api.get("/continue_crawler");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("ContinueCrawler error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function GetCrawlerConfig() {
    try {
        const response = await crawler_api.get("/get_crawler_config");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("GetCrawlerConfig error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}

export async function SaveCrawlerConfig() {
    try {
        const response = await crawler_api.get("/save_crawler_config");
        return response.data;  // 返回实际数据而不是整个响应对象
    } catch (error) {
        console.error("SaveCrawlerConfig error:", error);
        throw error;  // 重新抛出错误以便调用者处理
    }
}