import { defineStore } from 'pinia'
import { useStorage } from '@vueuse/core'
import authApi from '@/api/auth'
import { useChatStore } from '@/stores/chat'


// 定义一个Store, 'auth'是Store的唯一标识符
export const useAuthStore = defineStore('auth', {
    // state: 数据
    // useStorage: 把token和userInfo自动持久化到LocalStorage, 刷新页面不丢失
    state: () => ({
        token: useStorage('token', null),   
        userInfo: useStorage('userInfo', null),
        tokenExpiresAt: useStorage('tokenExpiresAt', null)
    }),
    // getters: 计算属性
    getters: {
        isLoggedIn: (state) => {
            if(!state.token) return false
            if(!state.tokenExpiresAt) return true
            return Date.now() < Number(state.tokenExpiresAt)
        }
    },
    // actions: 方法
    actions: {
        // 确保当前用户信息存在(token存在就默认用户已经登录的情况)
        async ensureUserInfo(){
            if(!this.token){
                this.logout()
                return false
            }
            if(this.tokenExpiresAt && Date.now() > Number(this.tokenExpiresAt)){
                this.logout()
                return false
            }

            try{
                const data = await authApi.getMe()
                this.userInfo = data
                return true
            } catch {
                this.logout()
                return false
            }
        },
        async login(username, password){
            const chatStore = useChatStore()
            // 登录前先清空上一位用户的聊天状态
            chatStore.reset()
            const data = await authApi.login(username, password)
            this.token = data.access_token
            this.tokenExpiresAt = Date.now() + data.expires_in * 1000
            // token 更新后, 立即拉取当前用户信息
            await this.fetchUserInfo()
            // 登录成功后再清一次, 确保当前页面不会残留旧状态
            chatStore.reset()
        },
        async register(username, password){
            await authApi.register(username, password)
            // 注册成功后自动登录
            await this.login(username, password)
        },

        async fetchUserInfo(){
            const data = await authApi.getMe()
            this.userInfo = data
        },

        logout(){
            this.token = null
            this.userInfo = null
            this.tokenExpiresAt = null
            // 退出当前用户时, 聊天状态同步清除
            const chatStore = useChatStore()
            chatStore.reset()
        },
    },
})














