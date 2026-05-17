<template>
  <div class="chat-layout">
    <!-- Session Sidebar -->
    <aside class="chat-sidebar glass-card">
      <button class="new-chat-btn" @click="newChat">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        <span>新建对话</span>
      </button>

      <!-- Doc filter toggle -->
      <button class="doc-filter-toggle" @click="showDocPanel = !showDocPanel">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <span>文档范围 ({{ selectedDocIds.length }})</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: showDocPanel }" class="chevron">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button>

      <!-- Document selection panel -->
      <div v-if="showDocPanel" class="doc-panel">
        <div v-if="docs.length === 0" class="doc-empty">暂无文档，请先上传</div>
        <label v-for="d in docs" :key="d.id" class="doc-item" :class="{ checked: selectedDocIds.includes(d.id) }">
          <input type="checkbox" :value="d.id" v-model="selectedDocIds" />
          <span class="doc-name">{{ d.filename }}</span>
          <span class="doc-type">{{ d.file_type }}</span>
        </label>
      </div>

      <!-- Session list -->
      <div class="session-list">
        <div
          v-for="s in sessions"
          :key="s.session_id"
          :class="['session-item', { active: s.session_id === sessionId }]"
          @click="switchSession(s.session_id)"
        >
          <div class="session-content">
            <div class="session-title">{{ s.first_query || '(空对话)' }}</div>
            <div class="session-meta">{{ s.message_count }} 条消息</div>
          </div>
          <button class="session-delete" @click.stop="removeSession(s.session_id)" title="删除会话">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
        <div v-if="sessions.length === 0" class="no-sessions">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span>暂无对话记录</span>
        </div>
      </div>
    </aside>

    <!-- Main Chat Area -->
    <div class="chat-main">
      <!-- Empty state -->
      <div v-if="messages.length === 0 && !loading" class="chat-empty">
        <div class="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.4">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            <path d="M8 9h8" stroke-width="1.5"/><path d="M8 13h5" stroke-width="1.5"/>
          </svg>
        </div>
        <h2>开始智能问答</h2>
        <p>上传文档后，您可以对文档内容进行提问、总结、提取和分析</p>
        <div class="quick-prompts">
          <button v-for="p in quickPrompts" :key="p" class="prompt-chip" @click="input = p; send()">
            {{ p }}
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div class="messages" ref="msgBox" v-else>
        <div v-for="(m, i) in messages" :key="i" :class="['msg-row', m.role]">
          <!-- Avatar -->
          <div class="msg-avatar" v-if="m.role === 'assistant'">
            <div class="avatar-ai">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
                <line x1="12" y1="22" x2="12" y2="15.5"/><polyline points="22 8.5 12 15.5 2 8.5"/>
              </svg>
            </div>
          </div>

          <!-- Bubble -->
          <div class="msg-body">
            <div :class="['msg-bubble', m.role]">
              <div v-if="m.role === 'assistant'" class="msg-html" v-html="renderMd(m.content)"></div>
              <div v-else class="msg-text">{{ m.content }}</div>
              <span v-if="m.role === 'assistant' && m.streaming" class="streaming-cursor">|</span>
            </div>

            <!-- Sources -->
            <div v-if="m.sources?.length" class="msg-sources">
              <div class="sources-header" @click="m._showSources = !m._showSources">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                </svg>
                <span>引用 {{ m.sources.length }} 个来源</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ rotated: m._showSources }" class="chevron-sm">
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              <div v-if="m._showSources" class="sources-list">
                <div v-for="(s, j) in m.sources" :key="j" class="source-item">
                  <span class="source-badge">{{ s.filename }}</span>
                  <span class="source-excerpt">{{ s.excerpt?.slice(0, 150) }}...</span>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div v-if="m.role === 'assistant' && !m.streaming && m.content" class="msg-actions">
              <button class="action-btn" @click="copyText(m.content)" :title="m._copied ? '已复制' : '复制'">
                <svg v-if="!m._copied" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </button>
              <button
                v-if="i === messages.length - 1"
                class="action-btn"
                @click="regenerate"
                title="重新生成"
              >
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- User avatar -->
          <div class="msg-avatar" v-if="m.role === 'user'">
            <div class="avatar-user">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- Loading indicator -->
        <div v-if="loading && messages.length === 0" class="msg-row assistant">
          <div class="msg-avatar"><div class="avatar-ai"><!-- same --></div></div>
          <div class="msg-bubble assistant thinking-bubble">
            <div class="typing-dots">
              <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="input-area glass-card">
        <div class="input-row">
          <input
            ref="inputRef"
            v-model="input"
            class="chat-input"
            placeholder="输入你的问题... (Enter 发送，Shift+Enter 换行)"
            @keydown="onKeydown"
            :disabled="loading"
          />
          <button v-if="loading" class="stop-btn" @click="stopGeneration" title="停止生成">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="1"/>
            </svg>
          </button>
          <button v-else class="send-btn" @click="send" :disabled="!input.trim()" title="发送">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { sendMessage, getSessions, getSessionHistory, deleteSession } from '../api/chat'
import { listDocuments } from '../api/documents'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.min.css'

/* Markdown renderer */
marked.setOptions({
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return hljs.highlightAuto(code).value
  },
  breaks: true,
})

function renderMd(text) {
  if (!text) return ''
  return marked.parse(text)
}

/* State */
const input = ref('')
const loading = ref(false)
const messages = ref([])
const sessionId = ref(null)
const sessions = ref([])
const msgBox = ref(null)
const inputRef = ref(null)
const docs = ref([])
const selectedDocIds = ref([])
const showDocPanel = ref(false)
let abortCtrl = null

const quickPrompts = [
  '总结文档的核心内容',
  '文档中提到了哪些关键数据？',
  '提取文档的主要观点',
  '对比文档中的不同方案',
]

/* Document list */
async function loadDocs() {
  try {
    const res = await listDocuments(1, 100)
    docs.value = (res.data?.items || []).filter(d => d.status === 'completed')
  } catch { docs.value = [] }
}

/* Sessions */
async function loadSessions() {
  try {
    const res = await getSessions()
    sessions.value = res.data || []
  } catch { sessions.value = [] }
}

async function switchSession(sid) {
  sessionId.value = sid
  try {
    const res = await getSessionHistory(sid)
    messages.value = (res.data || []).map(m => ({ role: m.role, content: m.content, _showSources: false }))
  } catch {
    ElMessage.error('加载会话失败')
    messages.value = []
  }
  await scrollBottom()
}

function newChat() {
  sessionId.value = null
  messages.value = []
  selectedDocIds.value = []
  inputRef.value?.focus()
}

async function removeSession(sid) {
  try {
    await deleteSession(sid)
    sessions.value = sessions.value.filter(s => s.session_id !== sid)
    if (sessionId.value === sid) newChat()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

/* Send & Stream */
function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

async function send() {
  const q = input.value.trim()
  if (!q || loading.value) return
  input.value = ''

  messages.value.push({ role: 'user', content: q })
  const assistantMsg = { role: 'assistant', content: '', streaming: true, sources: null, _showSources: false }
  messages.value.push(assistantMsg)
  loading.value = true
  await scrollBottom()

  abortCtrl = new AbortController()

  try {
    const resp = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: q,
        session_id: sessionId.value,
        document_ids: selectedDocIds.value.length > 0 ? selectedDocIds.value : null,
      }),
      signal: abortCtrl.signal,
    })

    const reader = resp.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const segments = buffer.split('\n\n')
      buffer = segments.pop() || ''

      for (const seg of segments) {
        const lines = seg.split('\n')
        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const raw = line.slice(6).trim()
          if (raw === '[DONE]') continue
          try {
            const data = JSON.parse(raw)
            if (data.content) {
              assistantMsg.content += data.content
              await scrollBottom()
            } else if (data.sources) {
              assistantMsg.sources = data.sources
              if (data.session_id) {
                sessionId.value = data.session_id
                await loadSessions()
              }
            } else if (data.error) {
              assistantMsg.content = data.error
            }
          } catch { /* skip malformed */ }
        }
      }
    }
  } catch (e) {
    if (e.name !== 'AbortError') {
      assistantMsg.content = '请求失败：' + e.message
    }
  } finally {
    assistantMsg.streaming = false
    loading.value = false
    abortCtrl = null
  }
}

function stopGeneration() {
  if (abortCtrl) {
    abortCtrl.abort()
    const last = messages.value[messages.value.length - 1]
    if (last?.role === 'assistant') {
      last.streaming = false
      if (!last.content) last.content = '(已停止生成)'
    }
    loading.value = false
    abortCtrl = null
  }
}

async function regenerate() {
  const lastUser = [...messages.value].reverse().find(m => m.role === 'user')
  if (!lastUser) return
  // Remove last assistant message
  const lastIdx = messages.value.length - 1
  if (messages.value[lastIdx]?.role === 'assistant') {
    messages.value.pop()
  }
  input.value = lastUser.content
  // Remove the user msg too since send() will add it
  messages.value.pop()
  await send()
}

/* Copy */
async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
    const last = messages.value[messages.value.length - 1]
    if (last?.role === 'assistant') {
      last._copied = true
      setTimeout(() => { last._copied = false }, 2000)
    }
  } catch {
    ElMessage.warning('复制失败')
  }
}

/* Scroll */
async function scrollBottom() {
  await nextTick()
  if (msgBox.value) {
    msgBox.value.scrollTop = msgBox.value.scrollHeight
  }
}

watch(loading, async (v) => {
  if (!v) await scrollBottom()
})

onMounted(() => {
  loadSessions()
  loadDocs()
  inputRef.value?.focus()
})
</script>

<style scoped>
.chat-layout {
  display: flex;
  height: calc(100vh - 120px);
  gap: 16px;
  padding: 0 4px;
}

/* Sidebar */
.chat-sidebar {
  width: 270px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 14px;
  overflow-y: auto;
  border-radius: var(--radius-lg);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.new-chat-btn:hover {
  background: var(--color-primary-dark);
  box-shadow: var(--shadow-glow);
}

.doc-filter-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 10px;
  margin-top: 8px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.doc-filter-toggle:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.doc-filter-toggle .chevron {
  margin-left: auto;
  transition: transform var(--transition-fast);
}
.doc-filter-toggle .chevron.rotated {
  transform: rotate(180deg);
}

.doc-panel {
  margin-top: 6px;
  padding: 8px;
  border: 1px solid var(--border-light);
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  max-height: 200px;
  overflow-y: auto;
  animation: fadeIn 0.2s ease;
}
.doc-empty {
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  padding: 16px 0;
}
.doc-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 13px;
  transition: background var(--transition-fast);
}
.doc-item:hover { background: var(--bg-surface-hover); }
.doc-item.checked { background: var(--color-primary-bg); }
.doc-item input[type="checkbox"] {
  accent-color: var(--color-primary);
  cursor: pointer;
}
.doc-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
}
.doc-type {
  font-size: 11px;
  color: var(--text-muted);
  text-transform: uppercase;
}

/* Session list */
.session-list {
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  flex: 1;
  overflow-y: auto;
}
.session-item {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  border: 1px solid transparent;
}
.session-item:hover { background: var(--bg-surface-hover); }
.session-item.active {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}
.session-content { flex: 1; min-width: 0; }
.session-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.session-meta { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.session-delete {
  display: none;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  flex-shrink: 0;
}
.session-item:hover .session-delete { display: flex; }
.session-delete:hover { background: rgba(239, 68, 68, 0.1); color: var(--color-danger); }

.no-sessions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 32px 0;
  color: var(--text-muted);
  font-size: 13px;
}

/* Main chat */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* Empty state */
.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  text-align: center;
}
.chat-empty h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}
.chat-empty p {
  color: var(--text-muted);
  max-width: 420px;
  font-size: 14px;
  margin-bottom: 20px;
}
.quick-prompts {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 500px;
}
.prompt-chip {
  padding: 8px 16px;
  border: 1px solid var(--border-color);
  border-radius: 20px;
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.prompt-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: var(--color-primary-bg);
}

/* Messages area */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0 16px;
}

.msg-row {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  animation: fadeIn 0.3s ease;
}
.msg-row.user { flex-direction: row-reverse; }
.msg-row.assistant { flex-direction: row; }

/* Avatars */
.msg-avatar { flex-shrink: 0; }
.avatar-ai, .avatar-user {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
}
.avatar-ai {
  background: linear-gradient(135deg, var(--color-primary), #8B5CF6);
  color: #fff;
}
.avatar-user {
  background: var(--bg-surface-hover);
  color: var(--text-secondary);
}

/* Bubbles */
.msg-body { max-width: 75%; min-width: 0; }
.msg-bubble {
  padding: 12px 16px;
  border-radius: var(--radius-lg);
  font-size: 14px;
  line-height: 1.7;
}
.msg-bubble.assistant {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-light);
  border-top-left-radius: 4px;
}
.msg-bubble.user {
  background: var(--color-primary);
  color: #fff;
  border-top-right-radius: 4px;
}
.msg-bubble.assistant :deep(p) { margin-bottom: 8px; }
.msg-bubble.assistant :deep(p:last-child) { margin-bottom: 0; }
.msg-bubble.assistant :deep(pre) {
  background: #0F172A;
  color: #E2E8F0;
  padding: 14px;
  border-radius: var(--radius-md);
  overflow-x: auto;
  margin: 10px 0;
  font-size: 13px;
  line-height: 1.5;
}
.msg-bubble.assistant :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.9em;
}
.msg-bubble.assistant :deep(:not(pre) > code) {
  background: var(--bg-surface-hover);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--color-primary);
}
.msg-bubble.assistant :deep(ul), .msg-bubble.assistant :deep(ol) {
  padding-left: 20px;
  margin: 6px 0;
}
.msg-bubble.assistant :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}
.msg-bubble.assistant :deep(th), .msg-bubble.assistant :deep(td) {
  border: 1px solid var(--border-color);
  padding: 8px 12px;
  text-align: left;
  font-size: 13px;
}
.msg-bubble.assistant :deep(th) { background: var(--bg-surface-hover); font-weight: 600; }
.msg-bubble.assistant :deep(blockquote) {
  border-left: 3px solid var(--color-primary);
  padding-left: 12px;
  margin: 8px 0;
  color: var(--text-secondary);
}

.msg-text {
  white-space: pre-wrap;
  word-break: break-word;
}

.streaming-cursor {
  animation: blink 0.8s infinite;
  color: var(--color-primary);
  font-weight: 600;
}
@keyframes blink { 50% { opacity: 0; } }

.thinking-bubble {
  padding: 16px 20px;
}
.typing-dots {
  display: flex;
  gap: 5px;
}
.typing-dots .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: pulse-dot 1.2s infinite;
}
.typing-dots .dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dots .dot:nth-child(3) { animation-delay: 0.4s; }

/* Sources */
.msg-sources { margin-top: 6px; }
.sources-header {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px 0;
  transition: color var(--transition-fast);
}
.sources-header:hover { color: var(--text-secondary); }
.sources-header .chevron-sm {
  margin-left: auto;
  transition: transform var(--transition-fast);
}
.sources-header .chevron-sm.rotated { transform: rotate(180deg); }
.sources-list {
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  animation: fadeIn 0.2s ease;
}
.source-item {
  display: flex;
  gap: 8px;
  align-items: baseline;
  font-size: 12px;
}
.source-badge {
  padding: 1px 6px;
  border-radius: 3px;
  background: var(--color-primary-bg);
  color: var(--color-primary);
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}
.source-excerpt {
  color: var(--text-muted);
  line-height: 1.5;
}

/* Message actions */
.msg-actions {
  display: flex;
  gap: 4px;
  margin-top: 4px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.msg-row.assistant:hover .msg-actions { opacity: 1; }
.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}
.action-btn:hover {
  background: var(--bg-surface-hover);
  color: var(--text-primary);
}

/* Input area */
.input-area {
  padding: 12px 16px;
  margin-top: auto;
}
.input-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  line-height: 1.5;
  font-family: inherit;
}
.chat-input::placeholder { color: var(--text-muted); }
.chat-input:disabled { opacity: 0.5; }

.send-btn, .stop-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}
.send-btn {
  background: var(--color-primary);
  color: #fff;
}
.send-btn:hover {
  background: var(--color-primary-dark);
  box-shadow: var(--shadow-glow);
}
.send-btn:disabled {
  background: var(--border-color);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
}
.stop-btn {
  background: var(--color-danger);
  color: #fff;
}
.stop-btn:hover { background: #DC2626; }
</style>
