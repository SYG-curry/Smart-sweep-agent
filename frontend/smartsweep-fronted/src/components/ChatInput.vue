<template>
  <div class="chat-input-shell">
    <div class="chat-input">
      <textarea
        v-model="text"
        placeholder="给智扫通发送消息"
        rows="1"
        @keydown.enter.exact.prevent="send"
        :disabled="loading"
      />
      <button @click="send" :disabled="loading || !text.trim()" aria-label="发送消息">
        {{ loading ? '···' : '发送' }}
      </button>
    </div>
    <p class="input-tip">内容由智能客服生成，请结合实际产品说明和环境判断。</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: { type: Boolean, default: false },
})
const emit = defineEmits(['send'])

const text = ref('')
const send = () => {
  if (!text.value.trim() || props.loading) return
  emit('send', text.value)
  text.value = ''
}
</script>

<style scoped>
.chat-input-shell {
  padding: 16px 24px 18px;
  background: linear-gradient(180deg, rgba(247, 247, 248, 0), #f7f7f8 32%);
}

.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  width: min(900px, 100%);
  margin: 0 auto;
  padding: 10px;
  border: 1px solid #d9d9e3;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.06);
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.chat-input:focus-within {
  border-color: rgba(16, 163, 127, 0.55);
  box-shadow: 0 16px 42px rgba(16, 163, 127, 0.11);
}

textarea {
  flex: 1;
  resize: none;
  min-height: 26px;
  max-height: 160px;
  padding: 8px 10px;
  border: none;
  outline: none;
  background: transparent;
  color: #202123;
  font-family: inherit;
  font-size: 15px;
  line-height: 1.55;
}

textarea::placeholder {
  color: #9ca3af;
}

button {
  flex: 0 0 auto;
  height: 38px;
  min-width: 66px;
  padding: 0 16px;
  border: none;
  border-radius: 12px;
  background: #10a37f;
  color: #fff;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.18s ease, background 0.18s ease, opacity 0.18s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #0e8f70;
}

button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.input-tip {
  width: min(900px, 100%);
  margin: 8px auto 0;
  text-align: center;
  color: #9ca3af;
  font-size: 12px;
}

@media (max-width: 720px) {
  .chat-input-shell {
    padding: 12px 12px 14px;
  }

  .input-tip {
    display: none;
  }
}
</style>
