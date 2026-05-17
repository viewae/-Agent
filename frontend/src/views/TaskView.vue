<template>
  <div class="page-container">
    <div class="task-header">
      <h2>任务执行</h2>
      <p>输入自然语言指令，AI 将自动拆解并执行任务</p>
    </div>

    <!-- Input -->
    <div class="task-input-card glass-card">
      <div class="input-row">
        <input
          v-model="instruction"
          class="task-input"
          placeholder="输入任务指令，例如：总结这份文档并提取关键数据..."
          @keydown.enter.exact="execute"
          :disabled="loading"
        />
        <button class="execute-btn" @click="execute" :disabled="!instruction.trim() || loading">
          <svg v-if="!loading" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="5 3 19 12 5 21 5 3"/>
          </svg>
          <span v-else class="btn-spinner"></span>
          <span>{{ loading ? '执行中' : '执行' }}</span>
        </button>
      </div>
    </div>

    <!-- Result -->
    <transition name="fade">
      <div v-if="result" class="task-result glass-card">
        <!-- Header -->
        <div class="result-header">
          <span :class="['intent-tag', intentTagClass]">{{ result.intent }}</span>
          <span class="task-id">任务 ID: {{ result.task_id }}</span>
          <span :class="['status-tag', result.status]">{{ statusText }}</span>
        </div>

        <!-- Steps Timeline -->
        <div v-if="result.steps?.length" class="steps-section">
          <h3>执行步骤</h3>
          <div class="steps-timeline">
            <div
              v-for="(s, idx) in result.steps"
              :key="s.step"
              :class="['step-item', s.status]"
            >
              <div class="step-indicator">
                <div class="step-dot">
                  <svg v-if="s.status === 'completed'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                  <span v-else>{{ idx + 1 }}</span>
                </div>
                <div v-if="idx < result.steps.length - 1" class="step-line"></div>
              </div>
              <div class="step-content">
                <div class="step-title">{{ s.description }}</div>
                <span class="step-status-text">{{ s.status === 'completed' ? '已完成' : '执行中' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Result card -->
        <div v-if="result.status === 'completed'" class="result-final">
          <h3>执行结果</h3>
          <div class="result-content">{{ result.result }}</div>
        </div>
        <div v-else-if="result.status === 'failed'" class="result-final error">
          <h3>执行失败</h3>
          <div class="result-content">{{ result.result || '未知错误' }}</div>
        </div>
      </div>
    </transition>

    <!-- History -->
    <div v-if="history.length > 0" class="history-section">
      <h3>历史任务</h3>
      <div class="history-card glass-card">
        <el-table :data="history" stripe size="small" style="width:100%">
          <el-table-column prop="task_id" label="任务 ID" width="160">
            <template #default="{ row }">
              <span class="mono-text">{{ row.task_id?.slice(0, 12) }}...</span>
            </template>
          </el-table-column>
          <el-table-column label="意图" width="110">
            <template #default="{ row }">
              <span class="intent-tag mini">{{ row.intent }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="90">
            <template #default="{ row }">
              <span :class="['status-tag', 'mini', row.status]">{{ statusMap[row.status] || row.status }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="result" label="结果" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="result-preview">{{ row.result?.slice(0, 100) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { executeTask } from '../api/chat'

const instruction = ref('')
const loading = ref(false)
const result = ref(null)
const history = ref([])

const statusMap = {
  completed: '已完成',
  running: '执行中',
  pending: '等待中',
  failed: '失败',
}
const statusText = computed(() => statusMap[result.value?.status] || result.value?.status)

const intentTagClass = computed(() => {
  const m = { qa: '', summarize: 'accent', extract: 'warning', compare: 'info', translate: '' }
  return m[result.value?.intent] || ''
})

async function execute() {
  const text = instruction.value.trim()
  if (!text || loading.value) return
  loading.value = true
  result.value = null
  try {
    const res = await executeTask(text, null)
    result.value = res.data
    await loadHistory()
  } catch (e) {
    ElMessage.error(e.message)
    result.value = { status: 'failed', result: e.message, steps: [], intent: '', task_id: '' }
  } finally {
    loading.value = false
  }
}

async function loadHistory() {
  try {
    const { default: api } = await import('../api/chat')
    const res = await api.get('/api/tasks/history')
    history.value = res.data?.data || []
  } catch { history.value = [] }
}

onMounted(loadHistory)
</script>

<style scoped>
.task-header {
  margin-bottom: 24px;
}
.task-header h2 { font-size: 1.5rem; font-weight: 700; }
.task-header p { color: var(--text-muted); font-size: 14px; margin-top: 4px; }

/* Input */
.task-input-card {
  padding: 8px;
  margin-bottom: 24px;
}
.input-row {
  display: flex;
  gap: 10px;
}
.task-input {
  flex: 1;
  border: none;
  background: transparent;
  padding: 12px 16px;
  font-size: 15px;
  color: var(--text-primary);
  outline: none;
  font-family: inherit;
}
.task-input::placeholder { color: var(--text-muted); }
.task-input:disabled { opacity: 0.5; }

.execute-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 22px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
  flex-shrink: 0;
}
.execute-btn:hover {
  background: var(--color-primary-dark);
  box-shadow: var(--shadow-glow);
}
.execute-btn:disabled {
  background: var(--border-color);
  color: var(--text-muted);
  cursor: not-allowed;
  box-shadow: none;
}
.btn-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Result */
.task-result {
  padding: 24px;
  margin-bottom: 32px;
}
.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
}
.intent-tag {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  background: var(--color-primary-bg);
  color: var(--color-primary);
}
.intent-tag.accent { background: rgba(16,185,129,0.1); color: var(--color-accent); }
.intent-tag.warning { background: rgba(245,158,11,0.1); color: var(--color-warning); }
.intent-tag.info { background: rgba(99,102,241,0.1); color: var(--color-primary); }
.intent-tag.mini { font-size: 11px; padding: 2px 8px; }

.task-id { font-size: 13px; color: var(--text-muted); font-family: 'Fira Code', monospace; }

.status-tag {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  margin-left: auto;
}
.status-tag.completed { background: rgba(16,185,129,0.1); color: var(--color-accent); }
.status-tag.running { background: rgba(99,102,241,0.1); color: var(--color-primary); }
.status-tag.pending { background: rgba(148,163,184,0.15); color: var(--text-secondary); }
.status-tag.failed { background: rgba(239,68,68,0.1); color: var(--color-danger); }
.status-tag.mini { font-size: 11px; padding: 2px 8px; }

/* Steps */
.steps-section h3, .result-final h3 {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 14px;
}
.steps-timeline { margin-bottom: 24px; }
.step-item { display: flex; gap: 12px; margin-bottom: 4px; }
.step-indicator { display: flex; flex-direction: column; align-items: center; }
.step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  background: var(--bg-surface-hover);
  color: var(--text-muted);
  flex-shrink: 0;
}
.step-item.completed .step-dot {
  background: rgba(16,185,129,0.15);
  color: var(--color-accent);
}
.step-item.running .step-dot {
  background: var(--color-primary-bg);
  color: var(--color-primary);
}
.step-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: var(--border-color);
  margin: 4px 0;
}
.step-item.completed .step-line { background: var(--color-accent); }
.step-content {
  padding: 2px 0 16px;
}
.step-title { font-size: 14px; font-weight: 500; color: var(--text-primary); }
.step-status-text { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

/* Result final */
.result-final {
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--bg-app);
}
.result-final.error {
  background: rgba(239,68,68,0.05);
}
.result-content {
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: 14px;
  color: var(--text-primary);
}
.result-final.error .result-content {
  color: var(--color-danger);
}

/* History */
.history-section { margin-top: 32px; }
.history-section h3 { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
.history-card {
  padding: 4px;
  overflow: hidden;
}
.history-card :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-surface-hover);
}
.mono-text { font-family: 'Fira Code', monospace; font-size: 12px; color: var(--text-muted); }
.result-preview { color: var(--text-secondary); font-size: 13px; }
</style>
