import { createRouter, createWebHistory } from 'vue-router'
import UploadView from '../views/UploadView.vue'
import DocumentListView from '../views/DocumentListView.vue'
import ChatView from '../views/ChatView.vue'
import TaskView from '../views/TaskView.vue'

const routes = [
  { path: '/', redirect: '/upload' },
  { path: '/upload', name: 'Upload', component: UploadView },
  { path: '/documents', name: 'Documents', component: DocumentListView },
  { path: '/chat', name: 'Chat', component: ChatView },
  { path: '/tasks', name: 'Tasks', component: TaskView },
  { path: '/:pathMatch(.*)*', redirect: '/upload' },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
