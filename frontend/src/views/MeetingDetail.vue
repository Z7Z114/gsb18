<template>
  <div class="meeting-detail-page" v-if="meeting">
    <button class="back-btn" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      返回
    </button>

    <div class="meeting-hero ancient-card">
      <div class="meeting-status">
        <el-tag :type="getStatusType(meeting.status)" size="large">
          {{ getStatusText(meeting.status) }}
        </el-tag>
      </div>
      <h1 class="font-ancient meeting-title">{{ meeting.title }}</h1>
      <div class="meeting-meta">
        <span>
          <el-icon><Calendar /></el-icon>
          {{ formatDate(meeting.date) }}
        </span>
        <span v-if="meeting.participants">
          <el-icon><User /></el-icon>
          {{ meeting.participants.join('、') }}
        </span>
      </div>
    </div>

    <div class="action-bar" v-if="meeting.status === 'created' || meeting.status === 'audio_uploaded'">
      <el-upload
        :show-file-list="false"
        :before-upload="handleAudioUpload"
        accept="audio/*"
        class="upload-btn"
      >
        <button class="ancient-btn-outline">
          <el-icon><UploadFilled /></el-icon>
          上传会议音频
        </button>
      </el-upload>
      <button
        class="ancient-btn"
        :disabled="meeting.status !== 'audio_uploaded'"
        @click="processMeeting"
      >
        <el-icon><MagicStick /></el-icon>
        AI处理会议
      </button>
    </div>

    <div class="processing-indicator" v-if="meeting.status === 'processing'">
      <el-result icon="info" title="正在处理会议音频">
        <template #sub-title>
          <div class="processing-steps">
            <div class="step" :class="{ active: processingStep >= 1 }">
              <span class="step-icon">🎙️</span>
              <span>语音转写</span>
            </div>
            <div class="step-arrow">→</div>
            <div class="step" :class="{ active: processingStep >= 2 }">
              <span class="step-icon">👥</span>
              <span>说话人标记</span>
            </div>
            <div class="step-arrow">→</div>
            <div class="step" :class="{ active: processingStep >= 3 }">
              <span class="step-icon">✨</span>
              <span>智能摘要</span>
            </div>
            <div class="step-arrow">→</div>
            <div class="step" :class="{ active: processingStep >= 4 }">
              <span class="step-icon">📜</span>
              <span>生成文案</span>
            </div>
          </div>
        </template>
      </el-result>
    </div>

    <div class="content-tabs" v-if="meeting.status === 'completed'">
      <div class="tab-buttons">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'summary' }"
          @click="activeTab = 'summary'"
        >
          📋 会议纪要
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'fundraising' }"
          @click="activeTab = 'fundraising'"
        >
          💰 募捐文案
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'merit' }"
          @click="activeTab = 'merit'"
        >
          🙏 功德回向
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'dialogue' }"
          @click="activeTab = 'dialogue'"
        >
          💬 对话实录
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'summary'" class="summary-section ancient-card">
          <h2 class="font-ancient section-title">会议纪要</h2>
          <div class="markdown-content" v-html="renderMarkdown(meeting.summary)"></div>
        </div>

        <div v-if="activeTab === 'fundraising'" class="fundraising-section ancient-card">
          <h2 class="font-ancient section-title">募捐文案</h2>
          <div class="markdown-content" v-html="renderMarkdown(meeting.fundraising_copy)"></div>
        </div>

        <div v-if="activeTab === 'merit'" class="merit-section ancient-card">
          <h2 class="font-ancient section-title">功德回向清单</h2>
          <div class="markdown-content" v-html="renderMarkdown(meeting.merit_list)"></div>
        </div>

        <div v-if="activeTab === 'dialogue'" class="dialogue-section ancient-card">
          <h2 class="font-ancient section-title">会议对话实录</h2>
          <div class="dialogue-list">
            <div
              v-for="(turn, index) in dialogue"
              :key="index"
              class="dialogue-item"
              :class="{ 'temple-side': isTempleSide(turn.speaker_role) }"
            >
              <div class="dialogue-header">
                <span class="speaker-name font-ancient">
                  {{ turn.speaker }}
                </span>
                <el-tag size="small" :type="getRoleTagType(turn.speaker_role)">
                  {{ turn.speaker_role }}
                </el-tag>
                <span class="timestamp">{{ turn.timestamp }}</span>
              </div>
              <div class="dialogue-content">{{ turn.content }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="output-actions">
        <button class="ancient-btn-outline" @click="downloadMarkdown">
          <el-icon><Download /></el-icon>
          下载Markdown纪要
        </button>
        <button class="ancient-btn" @click="showEmailDialog = true">
          <el-icon><Message /></el-icon>
          邮寄给信众
        </button>
      </div>
    </div>

    <el-dialog
      v-model="showEmailDialog"
      title="发送功德纪要邮件"
      width="600px"
    >
      <el-form :model="emailForm" label-width="100px">
        <el-form-item label="收件人">
          <el-select
            v-model="emailForm.to_emails"
            multiple
            filterable
            allow-create
            placeholder="输入邮箱地址，回车添加"
            style="width: 100%;"
          >
            <el-option
              v-for="email in donorEmails"
              :key="email"
              :label="email"
              :value="email"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="邮件主题">
          <el-input v-model="emailForm.subject" placeholder="请输入邮件主题" />
        </el-form-item>
        <el-form-item label="邮件内容">
          <el-input
            v-model="emailForm.markdown_content"
            type="textarea"
            :rows="10"
            placeholder="邮件正文（支持Markdown）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEmailDialog = false">取消</el-button>
        <el-button type="primary" @click="sendEmails">发送邮件</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft, Calendar, User, UploadFilled, MagicStick,
  Download, Message
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { meetingApi, donorApi } from '../api'

const route = useRoute()
const meeting = ref(null)
const dialogue = ref([])
const activeTab = ref('summary')
const showEmailDialog = ref(false)
const processingStep = ref(0)
const donorEmails = ref([])

const emailForm = ref({
  to_emails: [],
  subject: '',
  markdown_content: ''
})

onMounted(async () => {
  await loadMeeting()
  await loadDonors()
  startPolling()
})

const loadMeeting = async () => {
  try {
    const res = await meetingApi.getMeeting(route.params.id)
    meeting.value = res.data

    if (meeting.value.status === 'completed' && meeting.value.fundraising_copy) {
      emailForm.value.subject = `【${meeting.value.title}】修缮募捐功德纪要`
      emailForm.value.markdown_content = meeting.value.fundraising_copy
    }
  } catch (error) {
    ElMessage.error('加载会议信息失败')
  }
}

const loadDonors = async () => {
  try {
    const res = await donorApi.getDonors()
    donorEmails.value = res.data.map(d => d.email).filter(Boolean)
  } catch (error) {
    console.error('加载功德主列表失败', error)
  }
}

const loadDialogue = async () => {
  try {
    const res = await meetingApi.getDialogue(route.params.id)
    dialogue.value = res.data
  } catch (error) {
    console.error('加载对话记录失败', error)
  }
}

watch(() => meeting.value?.status, (newStatus) => {
  if (newStatus === 'completed') {
    loadDialogue()
  }
})

const startPolling = () => {
  const pollInterval = setInterval(async () => {
    if (meeting.value?.status === 'processing') {
      processingStep.value = Math.min(processingStep.value + 1, 4)
      await loadMeeting()
    } else if (meeting.value?.status !== 'processing') {
      clearInterval(pollInterval)
    }
  }, 3000)
}

const handleAudioUpload = async (file) => {
  try {
    await meetingApi.uploadAudio(route.params.id, file)
    ElMessage.success('音频上传成功')
    processingStep.value = 0
    await loadMeeting()
  } catch (error) {
    ElMessage.error('音频上传失败')
  }
  return false
}

const processMeeting = async () => {
  try {
    await meetingApi.processMeeting(route.params.id)
    processingStep.value = 1
    await loadMeeting()
    ElMessage.success('会议处理已开始，请稍候...')
  } catch (error) {
    ElMessage.error('处理失败，请重试')
  }
}

const downloadMarkdown = async () => {
  try {
    const res = await meetingApi.downloadMarkdown(route.params.id)
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `功德纪要_${meeting.value.id}.md`)
    document.body.appendChild(link)
    link.click()
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

const sendEmails = async () => {
  if (emailForm.value.to_emails.length === 0) {
    ElMessage.warning('请至少添加一个收件人')
    return
  }

  try {
    const res = await meetingApi.sendEmails(route.params.id, emailForm.value)
    if (res.data.success) {
      ElMessage.success(res.data.message)
      showEmailDialog.value = false
    } else {
      ElMessage.error(res.data.message)
    }
  } catch (error) {
    ElMessage.error('发送失败，请重试')
  }
}

const renderMarkdown = (content) => {
  if (!content) return ''
  return marked(content)
}

const getStatusType = (status) => {
  const types = {
    created: 'info',
    audio_uploaded: '',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    created: '已创建',
    audio_uploaded: '已上传音频',
    processing: '处理中',
    completed: '已完成',
    failed: '处理失败'
  }
  return texts[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const isTempleSide = (role) => {
  const templeRoles = ['住持', '监院', '僧人']
  return templeRoles.includes(role)
}

const getRoleTagType = (role) => {
  const types = {
    '住持': 'primary',
    '监院': 'success',
    '工匠': 'warning',
    '设计师': 'info',
    '居士': ''
  }
  return types[role] || 'info'
}
</script>

<style scoped>
.meeting-detail-page {
  min-height: 100vh;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: var(--primary-color);
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 1.5rem;
  font-family: 'Noto Serif SC', serif;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.back-btn:hover {
  background: var(--bg-dark);
}

.meeting-hero {
  text-align: center;
  padding: 2.5rem 2rem;
  margin-bottom: 2rem;
}

.meeting-status {
  margin-bottom: 1rem;
}

.meeting-title {
  font-size: 2.2rem;
  color: var(--primary-dark);
  margin-bottom: 1rem;
}

.meeting-meta {
  display: flex;
  gap: 2rem;
  justify-content: center;
  color: var(--text-light);
  flex-wrap: wrap;
}

.meeting-meta span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.action-bar {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
}

.upload-btn {
  display: inline-block;
}

.processing-indicator {
  margin-bottom: 2rem;
}

.processing-steps {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.4;
  transition: opacity 0.3s ease;
}

.step.active {
  opacity: 1;
}

.step-icon {
  font-size: 2rem;
}

.step-arrow {
  font-size: 1.5rem;
  color: var(--primary-light);
}

.content-tabs {
  margin-top: 2rem;
}

.tab-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border-color);
  flex-wrap: wrap;
}

.tab-btn {
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  font-size: 1rem;
  font-family: 'Noto Serif SC', serif;
  color: var(--text-light);
  cursor: pointer;
  position: relative;
  bottom: -2px;
  transition: all 0.3s ease;
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom: 3px solid var(--primary-color);
  font-weight: 500;
}

.tab-btn:hover:not(.active) {
  color: var(--primary-color);
}

.section-title {
  font-size: 1.8rem;
  color: var(--primary-dark);
  margin-bottom: 1.5rem;
  text-align: center;
}

.markdown-content {
  line-height: 2;
  color: var(--text-color);
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  color: var(--primary-dark);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-family: 'Ma Shan Zheng', cursive;
}

.markdown-content :deep(p) {
  margin-bottom: 1rem;
  text-indent: 2em;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 1rem 0;
  padding-left: 2rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0.5rem;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid var(--secondary-color);
  padding-left: 1rem;
  margin: 1.5rem 0;
  font-style: italic;
  color: var(--text-light);
  background: rgba(218, 165, 32, 0.05);
  padding: 1rem 1.5rem;
  border-radius: 0 8px 8px 0;
}

.dialogue-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.dialogue-item {
  padding: 1.5rem;
  background: var(--bg-secondary);
  border-radius: 8px;
  border-left: 4px solid var(--primary-light);
}

.dialogue-item.temple-side {
  background: rgba(184, 134, 11, 0.08);
  border-left-color: var(--secondary-color);
}

.dialogue-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.speaker-name {
  font-size: 1.2rem;
  color: var(--primary-dark);
}

.timestamp {
  color: var(--text-light);
  font-size: 0.85rem;
  margin-left: auto;
}

.dialogue-content {
  color: var(--text-color);
  line-height: 1.8;
}

.output-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.summary-section,
.fundraising-section,
.merit-section,
.dialogue-section {
  padding: 2.5rem;
}

@media (max-width: 768px) {
  .tab-buttons {
    justify-content: center;
  }

  .tab-btn {
    padding: 0.75rem 1rem;
    font-size: 0.9rem;
  }

  .summary-section,
  .fundraising-section,
  .merit-section,
  .dialogue-section {
    padding: 1.5rem;
  }

  .meeting-title {
    font-size: 1.6rem;
  }
}
</style>
