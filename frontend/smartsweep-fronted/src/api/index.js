import axios from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// 创建专用实例
const apiClient = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    timeout: 120000,    // 尽量长一点, 因为如果没有Redis走降级路线的话, 时间很可能会很长导致timeout
})

// 统一处理错误
function resolveErrorMessage(error) {
    const data = error.response?.data
    if (!data) {
      if (error.code === 'ECONNABORTED') {
        return '请求超时，请稍后重试'
      }
      return '网络异常，请检查后端服务是否启动'
    }
    if (typeof data.message === 'string') {
      return data.message
    }
    if (typeof data.detail?.message === 'string') {
      return data.detail.message
    }
    if (typeof data.detail === 'string') {
      return data.detail
    }
    if (Array.isArray(data.detail)) {
      return data.detail.map(item => item.msg).join('；')
    }
    return error.message || '请求失败，请稍后重试'
  }

// 请求拦截器: 自动带上JWT
apiClient.interceptors.request.use(
    (config) => {
        // authStore: 状态管理中存储的token
        const authStore = useAuthStore()
        if(authStore.token){
            config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
    },
    (error) => Promise.reject(new Error(resolveErrorMessage(error)))
)

// 响应拦截器: 统一处理错误
apiClient.interceptors.response.use(
    (response) => {
        // 后端返回统一格式: {code, message, data, request_id}
        // 提取data字段, 调用方不用再data.data
        const {code, message, data} = response.data
        if(code === 200 || code === 201){
            return data
        }else{
            return Promise.reject(new Error(message || '请求失败'))
        }
    },
    (error) => {
        const status = error.response?.status
        const url = error.config?.url || ''
        const message = resolveErrorMessage(error)

        if(status === 401){
            const isRegisterRequest = url.includes('/api/auth/register')
            const isLoginRequest = url.includes('/api/auth/login')
            // 登录和注册接口本身返回401时, 不要直接跳转, 否则用户看不到“用户名或密码错误”
            if(!isLoginRequest && !isRegisterRequest){
                const authStore = useAuthStore()
                authStore.logout()
                router.push('/login')
            }
        }
        return Promise.reject(new Error(message))
    }
)

// 导出apiClient实例
export default apiClient















