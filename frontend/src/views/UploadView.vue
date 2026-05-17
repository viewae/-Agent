<template>
  <div class="page-container">
    <div class="upload-header">
      <h2>上传文档</h2>
      <p>支持 PDF、DOCX、TXT 格式，单个文件最大 50MB</p>
    </div>

    <div class="upload-card glass-card">
      <el-upload
        class="upload-area"
        drag
        action="/api/documents/upload"
        :before-upload="beforeUpload"
        :on-success="onSuccess"
        :on-error="onError"
        :show-file-list="false"
      >
        <div class="upload-icon-wrap">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
        </div>
        <div class="upload-text">
          <span class="upload-primary">将文件拖到此处，或 <em>点击上传</em></span>
          <span class="upload-hint">PDF / DOCX / TXT</span>
        </div>
      </el-upload>

      <!-- Supported formats -->
      <div class="format-hints">
        <span class="format-badge">PDF</span>
        <span class="format-badge">DOCX</span>
        <span class="format-badge">TXT</span>
      </div>
    </div>

    <!-- Upload result -->
    <transition name="fade">
      <div v-if="lastResult" class="result-card glass-card">
        <div class="result-banner">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <span>上传成功</span>
        </div>
        <div class="result-grid">
          <div class="result-item">
            <span class="result-label">文件 ID</span>
            <span class="result-value">{{ lastResult.id }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">文件名</span>
            <span class="result-value">{{ lastResult.filename }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">类型</span>
            <span class="result-value">{{ lastResult.file_type }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">大小</span>
            <span class="result-value">{{ formatSize(lastResult.file_size) }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">处理状态</span>
            <span :class="['status-tag', lastResult.status]">{{ lastResult.status === 'completed' ? '已完成' : '处理中' }}</span>
          </div>
          <div class="result-item">
            <span class="result-label">上传时间</span>
            <span class="result-value">{{ lastResult.upload_time }}</span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { formatSize } from '../utils/format'

const lastResult = ref(null)

function beforeUpload(file) {
  const allowed = ['pdf', 'docx', 'txt']
  const ext = file.name.split('.').pop().toLowerCase()
  if (!allowed.includes(ext)) {
    ElMessage.error(`不支持 .${ext} 格式，仅支持: ${allowed.join(', ')}`)
    return false
  }
  if (file.size > 50 * 1024 * 1024) {
    ElMessage.error('文件大小不能超过 50MB')
    return false
  }
  return true
}

function onSuccess(response) {
  lastResult.value = response.data
}

function onError(err) {
  ElMessage.error(err.message || '上传失败')
}
</script>

<style scoped>
.upload-header {
  text-align: center;
  margin-bottom: 28px;
}
.upload-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}
.upload-header p {
  color: var(--text-muted);
  font-size: 14px;
  margin-top: 4px;
}

.upload-card {
  max-width: 560px;
  margin: 0 auto;
  padding: 32px;
}

.upload-area :deep(.el-upload-dragger) {
  background: var(--bg-app);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  padding: 40px 20px;
  transition: all var(--transition-normal);
}
.upload-area :deep(.el-upload-dragger:hover) {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.upload-icon-wrap {
  color: var(--color-primary);
  margin-bottom: 16px;
}
.upload-text {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.upload-primary {
  font-size: 15px;
  color: var(--text-primary);
}
.upload-primary em {
  color: var(--color-primary);
  font-style: normal;
  font-weight: 600;
}
.upload-hint {
  font-size: 12px;
  color: var(--text-muted);
}

.format-hints {
  display: flex;
  gap: 8px;
  justify-content: center;
  margin-top: 16px;
}
.format-badge {
  padding: 4px 14px;
  border-radius: 20px;
  background: var(--bg-surface-hover);
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
}

/* Result */
.result-card {
  max-width: 560px;
  margin: 24px auto 0;
  padding: 24px;
}
.result-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-accent);
  font-weight: 600;
  font-size: 15px;
  margin-bottom: 20px;
}
.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.result-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.result-label {
  font-size: 12px;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.result-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}
.status-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  width: fit-content;
}
.status-tag.completed {
  background: rgba(16, 185, 129, 0.1);
  color: var(--color-accent);
}
.status-tag.processing {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-warning);
}
</style>
