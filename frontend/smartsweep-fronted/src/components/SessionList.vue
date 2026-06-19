<template>
  <div class="session-list">
    <div
      v-for="session in sessions"
      :key="session.id"
      :class="['session-item', { active: session.id === currentId }]"
      @click="$emit('select', session.id)"
    >
      <span class="title">{{ session.title || '新对话' }}</span>
      <button class="del" @click.stop="$emit('delete', session.id)" aria-label="删除会话">×</button>
    </div>

    <div v-if="sessions.length === 0" class="empty-sessions">
      还没有历史对话
    </div>
  </div>
</template>

<script setup>
defineProps({
  sessions: { type: Array, default: () => [] },
  currentId: { type: String, default: null },
})
defineEmits(['select', 'delete'])
</script>

<style scoped>
.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 10px 14px;
}

.session-list::-webkit-scrollbar {
  width: 8px;
}

.session-list::-webkit-scrollbar-thumb {
  background: #d9d9e3;
  border: 2px solid #fff;
  border-radius: 999px;
}

.session-item {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  min-height: 42px;
  margin-bottom: 4px;
  padding: 0 8px 0 12px;
  border-radius: 11px;
  cursor: pointer;
  color: #4b5563;
  transition: background 0.16s ease, color 0.16s ease;
}

.session-item:hover {
  background: #f3f4f6;
  color: #202123;
}

.session-item.active {
  background: #eef8f4;
  color: #0f766e;
  font-weight: 650;
}

.title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
}

.del {
  flex: 0 0 auto;
  width: 26px;
  height: 26px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 8px;
  background: transparent;
  cursor: pointer;
  color: #a0a4ad;
  font-size: 18px;
  line-height: 1;
  opacity: 0;
  transition: all 0.16s ease;
}

.session-item:hover .del,
.session-item.active .del {
  opacity: 1;
}

.del:hover {
  background: #fee2e2;
  color: #dc2626;
}

.empty-sessions {
  margin: 18px 8px;
  padding: 18px 12px;
  border: 1px dashed #d9d9e3;
  border-radius: 14px;
  color: #9ca3af;
  text-align: center;
  font-size: 13px;
}
</style>
