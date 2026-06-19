<template>
  <div class="chat-view">
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="brand">
          <div class="brand-mark">智</div>
          <div>
            <h2>智扫通</h2>
            <p>扫地机器人智能顾问</p>
          </div>
        </div>
        <button @click="startNewChat" class="new-chat-btn">新对话</button>
      </div>

      <SessionList
        :sessions="chatStore.sessions"
        :currentId="chatStore.currentSessionId"
        @select="loadSession"
        @delete="deleteSession"
      />

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">{{ authStore.userInfo?.username?.slice(0, 1) || 'U' }}</div>
          <div class="user-meta">
            <span>{{ authStore.userInfo?.username }}</span>
            <small>已登录</small>
          </div>
          <button @click="logout" class="logout-btn">退出</button>
        </div>
      </div>
    </aside>

    <main class="chat-area">
      <header class="chat-header">
        <div>
          <h1>{{ chatStore.currentSession?.title || '新的咨询' }}</h1>
          <p>让选购、排障和保养建议更清楚一点</p>
        </div>
      </header>

      <div class="messages-container" ref="messagesRef">
        <div v-if="chatStore.messages.length === 0" class="empty-state">
          <div class="empty-icon">智</div>
          <h2>有什么扫地机器人问题？</h2>
          <p>可以问我选购建议、故障排查、维护保养、参数对比等问题。</p>
          <div class="quick-questions">
            <button @click="sendMessage('小户型适合什么扫地机器人？')">
              <span>小户型选购</span>
              <small>适合 60㎡ 以下家庭</small>
            </button>
            <button @click="sendMessage('扫地机器人吸力变弱怎么办？')">
              <span>吸力变弱排查</span>
              <small>尘盒、滤网、主刷逐步检查</small>
            </button>
            <button @click="sendMessage('扫拖一体机器人如何维护？')">
              <span>扫拖一体维护</span>
              <small>水箱、拖布、耗材周期建议</small>
            </button>
          </div>
        </div>

        <template v-else>
          <ChatMessage
            v-for="(msg, idx) in chatStore.messages"
            :key="idx"
            :message="msg"
          />
        </template>
      </div>

      <ChatInput @send="sendMessage" :loading="sending" />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import SessionList from '@/components/SessionList.vue'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const sending = ref(false)
const messagesRef = ref(null)

onMounted(async () => {
  chatStore.messages = []
  chatStore.currentSessionId = null

  await authStore.ensureUserInfo()

  await chatStore.fetchSessions()

  if (chatStore.sessions.length > 0) {
    await loadSession(chatStore.sessions[0].id)
  }
})

const sendMessage = async (text) => {
  sending.value = true
  const timer = setInterval(scrollToBottom, 300)

  try {
    await chatStore.sendMessageStream(text)
    scrollToBottom()
  } catch (err) {
    chatStore.messages.push({
      role: 'assistant',
      content: err?.message || '请求失败，请稍后再试',
      created_at: new Date().toISOString(),
    })
  } finally {
    clearInterval(timer)
    sending.value = false
    scrollToBottom()
  }
}

const loadSession = async (sessionId) => {
  await chatStore.loadMessages(sessionId)
  scrollToBottom()
}

const deleteSession = async (sessionId) => {
  if (confirm('确定删除这个对话？')) {
    await chatStore.deleteSession(sessionId)
  }
}

const startNewChat = () => {
  if (sending.value) return
  chatStore.currentSessionId = null
  chatStore.messages = []
}

const logout = () => {
  authStore.logout()
  router.push('/login')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesRef.value) {
      messagesRef.value.scrollTop = messagesRef.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-view {
  display: flex;
  height: 100vh;
  min-width: 0;
  background: #f7f7f8;
  color: #202123;
}

.sidebar {
  width: 300px;
  flex: 0 0 300px;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-right: 1px solid #ececf1;
}

.sidebar-header {
  padding: 20px 16px 14px;
  border-bottom: 1px solid #f0f0f0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
  background: #10a37f;
  box-shadow: 0 10px 24px rgba(16, 163, 127, 0.2);
}

.brand h2 {
  margin: 0;
  font-size: 18px;
  line-height: 1.2;
  color: #111827;
}

.brand p {
  margin-top: 4px;
  font-size: 12px;
  color: #8a8f98;
}

.new-chat-btn {
  width: 100%;
  height: 42px;
  border: 1px solid #d9d9e3;
  border-radius: 12px;
  background: #fff;
  color: #202123;
  font-size: 14px;
  font-weight: 650;
  cursor: pointer;
  transition: all 0.18s ease;
}

.new-chat-btn::before {
  content: '+';
  margin-right: 8px;
  color: #10a37f;
  font-weight: 800;
}

.new-chat-btn:hover:not(:disabled) {
  border-color: #10a37f;
  background: #f2fbf8;
}

.sidebar-footer {
  padding: 14px 16px 16px;
  border-top: 1px solid #f0f0f0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  border-radius: 14px;
  background: #f7f7f8;
}

.user-avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 700;
  background: #202123;
}

.user-meta {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-meta span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #202123;
  font-size: 14px;
  font-weight: 650;
}

.user-meta small {
  margin-top: 2px;
  color: #8a8f98;
  font-size: 12px;
}

.logout-btn {
  border: none;
  border-radius: 10px;
  padding: 7px 10px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.18s ease;
}

.logout-btn:hover {
  background: #ececf1;
  color: #202123;
}

.chat-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: #f7f7f8;
}

.chat-header {
  height: 70px;
  display: flex;
  align-items: center;
  padding: 0 28px;
  background: rgba(247, 247, 248, 0.9);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid #ececf1;
}

.chat-header h1 {
  margin: 0;
  font-size: 18px;
  line-height: 1.2;
  color: #202123;
  font-weight: 750;
}

.chat-header p {
  margin-top: 5px;
  font-size: 13px;
  color: #8a8f98;
}

.messages-container {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 12px 0 24px;
  scroll-behavior: smooth;
}

.messages-container::-webkit-scrollbar {
  width: 10px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #d9d9e3;
  border: 3px solid #f7f7f8;
  border-radius: 999px;
}

.empty-state {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 40px 24px;
}

.empty-icon {
  width: 58px;
  height: 58px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  margin-bottom: 22px;
  color: #fff;
  font-size: 22px;
  font-weight: 850;
  background: #10a37f;
  box-shadow: 0 18px 40px rgba(16, 163, 127, 0.18);
}

.empty-state h2 {
  margin-bottom: 10px;
  color: #202123;
  font-size: 28px;
  letter-spacing: -0.03em;
}

.empty-state p {
  max-width: 520px;
  margin-bottom: 26px;
  color: #6b7280;
  font-size: 15px;
  line-height: 1.7;
}

.quick-questions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  width: min(860px, 100%);
}

.quick-questions button {
  min-height: 92px;
  padding: 16px;
  border: 1px solid #ececf1;
  border-radius: 16px;
  background: #fff;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.03);
}

.quick-questions button:hover {
  transform: translateY(-2px);
  border-color: rgba(16, 163, 127, 0.35);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.06);
}

.quick-questions span {
  display: block;
  margin-bottom: 8px;
  color: #202123;
  font-size: 15px;
  font-weight: 700;
}

.quick-questions small {
  display: block;
  color: #8a8f98;
  font-size: 13px;
  line-height: 1.5;
}

.new-chat-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .sidebar {
    width: 260px;
    flex-basis: 260px;
  }

  .quick-questions {
    grid-template-columns: 1fr;
    max-width: 460px;
  }
}

@media (max-width: 720px) {
  .chat-view {
    display: block;
  }

  .sidebar {
    display: none;
  }

  .chat-area {
    height: 100vh;
  }

  .chat-header {
    height: 62px;
    padding: 0 18px;
  }

  .empty-state h2 {
    font-size: 23px;
  }
}
</style>
