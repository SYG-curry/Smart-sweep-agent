<template>
  <div :class="['msg', message.role]">
    <div class="avatar" aria-hidden="true">
      {{ message.role === 'user' ? '我' : '智' }}
    </div>

    <div class="message-main">
      <div class="message-meta">
        {{ message.role === 'user' ? '你' : '智扫通' }}
      </div>

      <div class="bubble">
        <template v-if="message.role === 'user'">
          {{ message.content }}
        </template>

        <template v-else>
          <details v-if="message.thinking" class="thinking-block" :open="message.isStreaming">
            <summary>
              <span>{{ message.isStreaming ? '正在思考' : '思考过程' }}</span>
              <span class="thinking-hint">{{ message.isStreaming ? '生成中' : '已完成' }}</span>
            </summary>
            <pre>{{ message.thinking }}</pre>
          </details>

          <div v-if="message.content" class="answer-block">
            <div class="markdown-body" v-html="renderMarkdown(message.content)"></div>
            <span v-if="message.isStreaming" class="cursor">▍</span>
          </div>

          <div v-else-if="message.isStreaming" class="answer-placeholder">
            <span class="typing-dot"></span>
            正在生成回答...
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  breaks: true,
  linkify: true,
})

function normalizeMarkdown(content) {
  return (content || '')
    .replace(/\n{3,}/g, '\n\n')
    .replace(/(^|\n)(\d+)\.\s*\n+/g, '$1$2. ')
    .replace(/\n+([*-])\s+/g, '\n$1 ')
}

function renderMarkdown(content) {
  return md.render(normalizeMarkdown(content))
}

defineProps({
  message: { type: Object, required: true },
})
</script>

<style scoped>
.msg {
  display: flex;
  gap: 12px;
  margin: 0 auto;
  padding: 18px 24px;
  max-width: 900px;
}

.msg.user {
  flex-direction: row-reverse;
}

.avatar {
  flex: 0 0 32px;
  width: 32px;
  height: 32px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  background: #10a37f;
  box-shadow: 0 8px 20px rgba(16, 163, 127, 0.2);
}

.user .avatar {
  background: #202123;
  box-shadow: 0 8px 18px rgba(32, 33, 35, 0.14);
}

.message-main {
  min-width: 0;
  max-width: min(760px, calc(100vw - 150px));
}

.user .message-main {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-meta {
  margin-bottom: 6px;
  font-size: 12px;
  line-height: 1;
  color: #8a8f98;
}

.bubble {
  width: fit-content;
  max-width: 100%;
  border-radius: 18px;
  padding: 13px 16px;
  line-height: 1.75;
  font-size: 15px;
  word-break: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.user .bubble {
  color: #fff;
  background: #202123;
  border-top-right-radius: 6px;
}

.assistant .bubble {
  color: #22252b;
  background: #fff;
  border: 1px solid #ececf1;
  border-top-left-radius: 6px;
}

.thinking-block {
  margin-bottom: 12px;
  border: 1px solid #ececf1;
  border-radius: 12px;
  background: #f7f7f8;
  color: #6b7280;
  overflow: hidden;
}

.thinking-block summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 9px 12px;
  cursor: pointer;
  user-select: none;
  font-size: 13px;
  font-weight: 600;
  color: #4b5563;
  list-style: none;
}

.thinking-block summary::-webkit-details-marker {
  display: none;
}

.thinking-hint {
  padding: 2px 8px;
  border-radius: 999px;
  background: #fff;
  color: #8a8f98;
  font-size: 12px;
  font-weight: 500;
}

.thinking-block pre {
  margin: 0;
  padding: 0 12px 12px;
  white-space: pre-wrap;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.65;
}

.answer-block {
  color: #202123;
}

.answer-placeholder {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #8a8f98;
  font-size: 14px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #10a37f;
  animation: pulse 1.1s ease-in-out infinite;
}

.cursor {
  display: inline-block;
  margin-left: 2px;
  color: #10a37f;
  animation: blink 1s infinite;
}

.markdown-body {
  white-space: normal;
}

.markdown-body :deep(*) {
  line-height: 1.75;
}

.markdown-body :deep(p) {
  margin: 0.35rem 0;
}

.markdown-body :deep(p:first-child) {
  margin-top: 0;
}

.markdown-body :deep(p:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(strong) {
  font-weight: 700;
  color: #111827;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 1rem 0 0.45rem;
  font-weight: 750;
  line-height: 1.35;
  color: #111827;
}

.markdown-body :deep(h1) {
  font-size: 1.35rem;
}

.markdown-body :deep(h2) {
  font-size: 1.18rem;
}

.markdown-body :deep(h3) {
  font-size: 1.04rem;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  margin: 0.45rem 0 0.75rem;
  padding-left: 1.35rem;
}

.markdown-body :deep(li) {
  margin: 0.18rem 0;
  padding-left: 0.15rem;
}

.markdown-body :deep(li > p) {
  margin: 0.1rem 0;
}

.markdown-body :deep(blockquote) {
  margin: 0.75rem 0;
  padding: 0.35rem 0.8rem;
  border-left: 3px solid #d1d5db;
  color: #6b7280;
  background: #f9fafb;
  border-radius: 8px;
}

.markdown-body :deep(code) {
  padding: 0.16rem 0.36rem;
  border-radius: 6px;
  background: #f1f5f9;
  color: #111827;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.92em;
}

.markdown-body :deep(pre) {
  margin: 0.75rem 0;
  padding: 0.9rem 1rem;
  border-radius: 12px;
  overflow-x: auto;
  background: #0f172a;
  color: #e5e7eb;
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.markdown-body :deep(a) {
  color: #0f766e;
  text-decoration: none;
  border-bottom: 1px solid rgba(15, 118, 110, 0.25);
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0.8rem 0;
  font-size: 14px;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  border: 1px solid #e5e7eb;
  padding: 0.45rem 0.6rem;
}

.markdown-body :deep(th) {
  background: #f9fafb;
  font-weight: 700;
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.35;
    transform: scale(0.75);
  }
  50% {
    opacity: 1;
    transform: scale(1);
  }
}

@media (max-width: 720px) {
  .msg {
    padding: 14px 14px;
    gap: 9px;
  }

  .avatar {
    width: 28px;
    height: 28px;
    flex-basis: 28px;
    font-size: 12px;
  }

  .message-main {
    max-width: calc(100vw - 82px);
  }

  .bubble {
    padding: 11px 13px;
    font-size: 14px;
  }
}
</style>
