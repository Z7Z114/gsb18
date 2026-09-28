<template>
  <div class="meetings-page">
    <div class="page-header">
      <h1 class="ancient-title">会议纪要</h1>
      <p class="ancient-subtitle">记录每一次护法兴寺的重要时刻</p>
    </div>

    <div class="meetings-list" v-if="meetings.length > 0">
      <div
        v-for="meeting in meetings"
        :key="meeting.id"
        class="meeting-card ancient-card"
        @click="$router.push(`/meetings/${meeting.id}`)"
      >
        <div class="meeting-card-header">
          <h3 class="meeting-title font-ancient">{{ meeting.title }}</h3>
          <el-tag :type="getStatusType(meeting.status)">
            {{ getStatusText(meeting.status) }}
          </el-tag>
        </div>
        <div class="meeting-meta">
          <span>
            <el-icon><Calendar /></el-icon>
            {{ formatDate(meeting.date) }}
          </span>
          <span v-if="meeting.participants">
            <el-icon><User /></el-icon>
            {{ meeting.participants.length }} 人参会
          </span>
        </div>
        <div class="meeting-progress" v-if="meeting.status === 'completed'">
          <div class="progress-item">
            <el-icon color="#67c23a"><Check /></el-icon>
            <span>语音转写完成</span>
          </div>
          <div class="progress-item">
            <el-icon color="#67c23a"><Check /></el-icon>
            <span>说话人标记完成</span>
          </div>
          <div class="progress-item">
            <el-icon color="#67c23a"><Check /></el-icon>
            <span>摘要生成完成</span>
          </div>
        </div>
        <div class="meeting-footer">
          <span class="view-detail">查看详情</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无会议记录" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Calendar, User, Check, ArrowRight } from '@element-plus/icons-vue'
import { meetingApi } from '../api'

const meetings = ref([])

onMounted(async () => {
  try {
    const res = await meetingApi.getMeetings()
    meetings.value = res.data.sort((a, b) => new Date(b.date) - new Date(a.date))
  } catch (error) {
    ElMessage.error('加载会议列表失败')
  }
})

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
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.meetings-page {
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
}

.meetings-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.meeting-card {
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.meeting-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 12px 40px var(--shadow-color);
}

.meeting-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.meeting-title {
  font-size: 1.4rem;
  color: var(--primary-dark);
  flex: 1;
  margin-right: 1rem;
}

.meeting-meta {
  display: flex;
  gap: 1.5rem;
  color: var(--text-light);
  font-size: 0.9rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.meeting-meta span {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.meeting-progress {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.85rem;
  color: var(--text-light);
}

.meeting-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.3rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--border-color);
  color: var(--primary-color);
  font-weight: 500;
}

@media (max-width: 768px) {
  .meetings-list {
    grid-template-columns: 1fr;
  }
}
</style>
