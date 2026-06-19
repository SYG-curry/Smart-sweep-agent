import apiClient from './index'

function getApiBaseUrl(){
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

function getToken(){
    return localStorage.getItem('token')
}

async function sendMessageStream({query, sessionId, onEvent}){
    // 获取JWT token
    const token = getToken()
    // 发起fetch请求, 这里没有await完整的响应, 而是只await连接建立
    const response = await fetch(`${getApiBaseUrl()}/api/chat/stream`,{
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            // 如果用户已登录, 则携带JWT
            // 未登录也可以发起匿名对话
            // ...：将上面得对象解构并合并到外层headers对象中
            ...(token ? {Authorization: `Bearer ${token}`}: {}),
        },
        body: JSON.stringify({
            query,
            session_id: sessionId,
        }),
    })
    if(!response.ok){
        let message = '请求失败, 请稍后重试'

        try{
            const errorData = await response.json()
            message = 
                errorData.message ||
                errorData.detail?.message ||
                errorData.detail ||
                message
        }catch{
            // 如果不是 JSON, 就保持默认错误
        }

        throw new Error(message)
    }
    if(!response.body){
        throw new Error('当前浏览器不支持流式响应')
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')

    let buffer = ''

    while(true){
        const { done, value } = await reader.read()

        if(done) break

        // 把二进制 chunk 解码为字符串
        buffer += decoder.decode(value, { stream: true })

        // SSE事件之间用 \n\n 分割
        const parts = buffer.split('\n\n')

        // 最后一段可能是不完整事件, 先留在buffer中
        buffer = parts.pop() || ''

        for(const part of parts){
            const line = part.split('\n').find(item => item.startsWith('data: '))
            if(!line) continue
            const jsonText = line.replace(/^data:\s*/, '')

            try{
                const event = JSON.parse(jsonText)
                onEvent(event)
            }catch(e){
                console.warn('SSE 事件解析失败:', jsonText, e)
            }
        }
    }
}


export default {
    sendMessage(query, sessionId = null){
        return apiClient.post('/api/chat', {query, session_id: sessionId})
    },
    
    sendMessageStream,
    
    getSessions(){
        return apiClient.get('/api/sessions')
    },

    getMessages(sessionId){
        return apiClient.get(`/api/session/${sessionId}/messages`)
    },

    deleteSession(sessionId){
        return apiClient.delete(`/api/session/${sessionId}`)
    },
}













