import { defineStore } from 'pinia'
import chatApi from '@/api/chat'



export const useChatStore = defineStore('chat', {
    state:() => ({
        sessions: [],                   // 会话列表
        currentSessionId: null,         // 当前会话ID
        messages: [],                   // 当前会话的消息
    }),

    getters:{
        currentSession: (state) => {
            return state.sessions.find(s => s.id === state.currentSessionId)
        },
    },

    actions:{
        // 只要用户身份变化, 就清空聊天状态: sessions清空 + currentSessionId清空 + messages清空
        reset(){
            this.sessions = []
            this.currentSessionId = null
            this.messages = []
        },
        async fetchSessions(){
            const data = await chatApi.getSessions()
            this.sessions = data.sessions
        },

        async loadMessages(sessionId){
            const data = await chatApi.getMessages(sessionId)
            this.messages = data.messages
            this.currentSessionId = sessionId
        },

        async sendMessage(query) {
            this.messages.push({
              role: 'user',
              content: query,
              created_at: new Date().toISOString(),
            })
          
            const data = await chatApi.sendMessage(query, this.currentSessionId)
          
            this.currentSessionId = data.session_id
          
            this.messages.push({
              role: 'assistant',
              content: data.answer,
              created_at: new Date().toISOString(),
            })
          
            await this.fetchSessions()
          },

        async sendMessageStream(query){
            // 1. 先立即显示用户消息
            this.messages.push({
                role: 'user',
                content: query,
                created_at: new Date().toISOString(),
            })

            // 2. 创建一条助手消息, 但先不填最终答案
            // thinking 用灰色小字过程
            // content 用于正常最终答案
            this.messages.push({
                role: 'assistant',
                thinking: '',
                content: '',
                isStreaming: true,
                created_at: new Date().toISOString(),
            })
            // 3. 取出"已经进入响应式数组里的那一项"
            // 之后所有更新, 都改这个响应式对象
            const assistantMessage = this.messages[this.messages.length - 1]

            try{
                await chatApi.sendMessageStream({
                    query,
                    sessionId: this.currentSessionId,

                    // 每收到后端一个SSE事件, 就执行一次 onEvent
                    onEvent: async(event) => {
                        if(event.type === 'session'){
                            this.currentSessionId = event.session_id
                        }
                        if(event.type === 'thinking'){
                            assistantMessage.thinking += event.content || ''
                        }
                        if(event.type === 'answer'){
                            assistantMessage.content += event.content || ''
                        }
                        if(event.type === 'error'){
                            assistantMessage.content += event.message || '生成失败'
                            assistantMessage.isStreaming = false
                        }
                        if(event.type === 'done'){
                            assistantMessage.isStreaming = false
                            await this.fetchSessions()
                        }
                    },
                })
            } catch (err){
                assistantMessage.isStreaming = false
                assistantMessage.content = err?.message || '请求失败, 请稍后再试'
            }
        },

        async deleteSession(sessionId){
            await chatApi.deleteSession(sessionId)
            this.sessions = this.sessions.filter(s => s.id !== sessionId)
            if(this.currentSessionId === sessionId){
                this.currentSessionId = null
                this.messages = []
            } 
        },
    },
})










