import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import ChatView from '@/views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'chat',
      component: ChatView,
      meta: { requiresAuth: true },   // 需要登录
    },
  ],
})

// 路由守卫: 未登录跳转到登录页
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if(!to.meta.requiresAuth){
    next()
    return
  }

  if(!authStore.token){
    next('/login')
    return
  }

  const valid = await authStore.ensureUserInfo()

  if(!valid){
    next('/login')
    return
  }

  next()
})

export default router
