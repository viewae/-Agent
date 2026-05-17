<template>
  <div class="page-container">
    <div class="list-header">
      <div>
        <h2>文档列表</h2>
        <p>共 {{ total }} 个文档</p>
      </div>
      <el-input
        v-model="search"
        placeholder="搜索文件名..."
        clearable
        :prefix-icon="null"
        class="search-input"
        @input="onSearch"
      >
        <template #prefix>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:6px">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
        </template>
      </el-input>
    </div>

    <div class="table-card glass-card">
      <el-table
        :data="filteredDocs"
        stripe
        v-loading="loading"
        @row-click="showContent"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="filename" label="文件名" min-width="240">
          <template #default="{ row }">
            <div class="file-cell">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="file-icon">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <span>{{ row.filename }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <span class="type-tag">{{ row.file_type }}</span>
          </template>
        </el-table-column>
        <el-table-column label="大小" width="100">
          <template #default="{ row }">{{ formatSize(row.file_size) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span :class="['status-dot', row.status]"></span>
            {{ row.status === 'completed' ? '已完成' : row.status === 'failed' ? '失败' : '处理中' }}
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="170" />
        <el-table-column label="操作" width="90" fixed="right">
          <template #default="{ row }">
            <button class="table-action danger" @click.stop="confirmDelete(row)">删除</button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pagination-wrap">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @current-change="fetchList"
        @size-change="fetchList"
      />
    </div>

    <!-- Content dialog -->
    <el-dialog v-model="dialogVisible" :title="selectedDoc?.filename" width="680px" class="content-dialog">
      <div class="content-body">{{ selectedContent }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listDocuments, getDocumentContent, deleteDocument } from '../api/documents'
import { formatSize } from '../utils/format'

const loading = ref(false)
const documents = ref([])
const search = ref('')
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const dialogVisible = ref(false)
const selectedDoc = ref(null)
const selectedContent = ref('')

const filteredDocs = computed(() => {
  if (!search.value) return documents.value
  const q = search.value.toLowerCase()
  return documents.value.filter(d => d.filename.toLowerCase().includes(q))
})

function onSearch() {
  page.value = 1
}

async function fetchList() {
  loading.value = true
  try {
    const res = await listDocuments(page.value, pageSize.value)
    documents.value = res.data.items
    total.value = res.data.total
  } catch (e) {
    ElMessage.error(e.message)
  } finally {
    loading.value = false
  }
}

async function showContent(row) {
  selectedDoc.value = row
  dialogVisible.value = true
  selectedContent.value = '加载中...'
  try {
    const res = await getDocumentContent(row.id)
    selectedContent.value = res.data.content || '(无文本内容)'
  } catch (e) {
    selectedContent.value = '加载失败: ' + e.message
  }
}

async function confirmDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.filename}」？`, '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await handleDelete(row.id)
  } catch { /* cancelled */ }
}

async function handleDelete(id) {
  try {
    await deleteDocument(id)
    ElMessage.success('删除成功')
    fetchList()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(fetchList)
</script>

<style scoped>
.list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  gap: 20px;
}
.list-header h2 { font-size: 1.5rem; font-weight: 700; }
.list-header p { color: var(--text-muted); font-size: 13px; margin-top: 2px; }

.search-input {
  width: 280px;
}

.table-card {
  padding: 4px;
  overflow: hidden;
}

.table-card :deep(.el-table) {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-surface-hover);
  --el-table-row-hover-bg-color: var(--color-primary-bg);
  --el-table-border-color: var(--border-light);
}
.table-card :deep(.el-table th) {
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  border-bottom: 2px solid var(--border-color);
}
.table-card :deep(.el-table td) { font-size: 14px; }

.file-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}
.file-icon { color: var(--text-muted); flex-shrink: 0; }

.type-tag {
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--bg-surface-hover);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
}

.status-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}
.status-dot.completed { background: var(--color-accent); }
.status-dot.processing { background: var(--color-warning); }
.status-dot.failed { background: var(--color-danger); }

.table-action {
  padding: 4px 12px;
  border: none;
  border-radius: var(--radius-sm);
  background: transparent;
  font-size: 13px;
  cursor: pointer;
  transition: all var(--transition-fast);
}
.table-action.danger {
  color: var(--color-danger);
}
.table-action.danger:hover {
  background: rgba(239, 68, 68, 0.1);
}

.pagination-wrap {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.content-body {
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 500px;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.7;
  background: var(--bg-app);
  padding: 20px;
  border-radius: var(--radius-md);
  color: var(--text-primary);
}
</style>
