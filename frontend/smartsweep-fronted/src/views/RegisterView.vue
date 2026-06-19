<template>
  <div class="auth-page">
    <section class="intro-panel">
      <div class="brand-mark">智</div>
      <h1>创建你的智能客服账号</h1>
      <p>保存历史对话，让扫地机器人选购和维护建议可以持续追踪。</p>
      <div class="intro-card">
        <span>账号能力</span>
        <strong>历史会话、连续追问、个性化排障建议</strong>
      </div>
    </section>

    <section class="auth-card">
      <div class="auth-header">
        <h2>注册账号</h2>
        <p>几秒钟完成注册，开始你的第一次咨询</p>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>用户名</label>
          <input v-model="username" type="text" placeholder="请输入用户名" required />
        </div>

        <div class="form-group">
          <label>密码</label>
          <div class="password-wrapper">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="请输入密码"
              required
            />
            <button
              type="button"
              class="eye-btn"
              @click="showPassword = !showPassword"
            >
              {{ showPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <button class="submit-btn" type="submit" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>

        <div class="tip">
          已有账号？<router-link to="/login">去登录</router-link>
        </div>
      </form>

      <div v-if="error" class="error">{{ error }}</div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const showPassword = ref(false)

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await authStore.register(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.message || '注册失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(360px, 1.1fr);
  background:
    radial-gradient(circle at 12% 18%, rgba(16, 163, 127, 0.14), transparent 34%),
    radial-gradient(circle at 92% 86%, rgba(32, 33, 35, 0.08), transparent 30%),
    #f7f7f8;
  color: #202123;
}

.intro-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 56px;
  border-right: 1px solid #ececf1;
}

.brand-mark {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  margin-bottom: 24px;
  color: #fff;
  font-size: 22px;
  font-weight: 850;
  background: #10a37f;
  box-shadow: 0 18px 42px rgba(16, 163, 127, 0.2);
}

.intro-panel h1 {
  max-width: 420px;
  margin: 0 0 14px;
  font-size: 42px;
  line-height: 1.08;
  letter-spacing: -0.05em;
}

.intro-panel p {
  max-width: 420px;
  color: #6b7280;
  font-size: 16px;
  line-height: 1.8;
}

.intro-card {
  width: min(420px, 100%);
  margin-top: 34px;
  padding: 18px;
  border: 1px solid #ececf1;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 16px 38px rgba(0, 0, 0, 0.05);
}

.intro-card span {
  display: block;
  margin-bottom: 8px;
  color: #8a8f98;
  font-size: 13px;
}

.intro-card strong {
  color: #202123;
  font-size: 15px;
}

.auth-card {
  align-self: center;
  justify-self: center;
  width: min(420px, calc(100% - 48px));
  padding: 34px;
  border: 1px solid #ececf1;
  border-radius: 24px;
  background: #fff;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.08);
}

.auth-header {
  margin-bottom: 26px;
}

.auth-header h2 {
  margin: 0;
  font-size: 28px;
  letter-spacing: -0.03em;
}

.auth-header p {
  margin-top: 8px;
  color: #8a8f98;
  font-size: 14px;
}

.form-group {
  margin-bottom: 18px;
}

label {
  display: block;
  margin-bottom: 8px;
  color: #374151;
  font-size: 14px;
  font-weight: 650;
}

input {
  width: 100%;
  height: 46px;
  padding: 0 13px;
  border: 1px solid #d9d9e3;
  border-radius: 13px;
  background: #fff;
  color: #202123;
  font-size: 15px;
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

input:focus {
  outline: none;
  border-color: rgba(16, 163, 127, 0.65);
  box-shadow: 0 0 0 4px rgba(16, 163, 127, 0.12);
}

.password-wrapper {
  position: relative;
}

.password-wrapper input {
  padding-right: 64px;
}

.eye-btn {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  width: auto;
  height: 32px;
  padding: 0 10px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #0f766e;
  font-size: 13px;
  cursor: pointer;
}

.eye-btn:hover:not(:disabled) {
  background: #eef8f4;
}

.submit-btn {
  width: 100%;
  height: 46px;
  margin-top: 6px;
  border: none;
  border-radius: 13px;
  background: #10a37f;
  color: white;
  font-size: 15px;
  font-weight: 750;
  cursor: pointer;
  transition: transform 0.18s ease, background 0.18s ease, opacity 0.18s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #0e8f70;
}

button:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.tip {
  text-align: center;
  margin-top: 18px;
  color: #6b7280;
  font-size: 14px;
}

.tip a {
  color: #0f766e;
  font-weight: 700;
  text-decoration: none;
}

.error {
  margin-top: 16px;
  padding: 12px;
  border: 1px solid #fecaca;
  background: #fff1f2;
  color: #b91c1c;
  border-radius: 13px;
  text-align: center;
  font-size: 14px;
}

@media (max-width: 860px) {
  .auth-page {
    grid-template-columns: 1fr;
    padding: 24px 0;
  }

  .intro-panel {
    display: none;
  }
}
</style>
