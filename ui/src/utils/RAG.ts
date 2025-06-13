import { GetContent } from '../api/search';
import { Mistral } from '@mistralai/mistralai';

const apiKey = 'vEdRTBIUtLy46rGOE5rVDH2aYuvQpOWd';

const client = new Mistral({ apiKey: apiKey });

let knowledge: string = '';

export async function setKnowledge(allDocs: Array<{ doc_id: number }>) {
    knowledge = ' ';
    for (const doc of allDocs) {
        GetContent(doc.doc_id).then(response => {
            if (response.data && response.data.content) {
                knowledge += `\n\n${response.data.content}`;
            }
        }).catch(error => {
            console.error(`Error fetching content for doc_id ${doc.doc_id}:`, error);
        });
    }
};

export async function streamChat(
    question: string,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string) => void,
    onError: (error: Error) => void,) {
    try {
        // 构建完整的消息数组，包含系统提示
        const fullMessages = [
            {
                role: 'user' as const,
                content: `你是一个基于知识库的AI助手。
                你的问题是：
                ${question},
                请根据以下知识库内容和用户的问题提供准确的回答
                知识库内容：
                    ${knowledge}

                    请注意：
                    1. 优先使用知识库中的信息来回答问题
                    2. 如果问题在知识库中找不到相关信息，请明确说明并提供你的一般性建议
                    3. 回答要准确、简洁、有用
                    4. 如果引用知识库内容，请保持信息的准确性`
            }
        ];
        // 调用Mistral的流式API
        const stream = await client.chat.stream({
            model: 'mistral-tiny', // 或者使用其他模型如 'mistral-medium'
            messages: fullMessages
        });
        let fullResponse = '';

        //处理流式响应
        for await (const event of stream) {
            const content = event.data?.choices[0]?.delta.content;
            if (!content) {
                continue;
            }
            fullResponse += content;
            if (content !== undefined) {
                if (typeof content === 'string') {
                    onChunk(content);
                } else {
                    console.warn('Received unexpected content type:', content);
                }
            }
        }
        onComplete(fullResponse);
    } catch (error) {
        console.error('Stream chat error:', error);
        if (error instanceof Error) {
            onError(error);
        } else {
            onError(new Error('An unknown error occurred'));
        }
    }
}

export default {
    client,
    streamChat,
    setKnowledge,
};