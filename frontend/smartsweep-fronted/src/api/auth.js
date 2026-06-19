import apiClient from './index'


export default {
    register(username, password) {
        return apiClient.post('/api/auth/register', {username, password})
    },
    login(username, password) {
        return apiClient.post('/api/auth/login', {username, password})
    },
    getMe(){
        return apiClient.get('/api/auth/me')
    },
}



















