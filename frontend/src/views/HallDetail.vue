<template>
  <div class="hall-detail-page" v-if="hall">
    <button class="back-btn" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      返回
    </button>

    <div class="hall-hero ancient-card">
      <div class="hall-icon-large">⛩️</div>
      <h1 class="font-ancient hall-title">{{ hall.name }}</h1>
      <p class="hall-desc">{{ hall.description }}</p>
      <div class="estimated-cost" v-if="hall.estimated_cost">
        预估修缮费用：<span class="cost-amount">{{ hall.estimated_cost }}</span>
      </div>
    </div>

    <div class="content-tabs">
      <div class="tab-buttons">
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'damage' }"
          @click="activeTab = 'damage'"
        >
          🏚️ 殿堂病害
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'repair' }"
          @click="activeTab = 'repair'"
        >
          🔨 修缮方案
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeTab === 'meetings' }"
          @click="activeTab = 'meetings'"
        >
          📜 会议纪要
        </button>
      </div>

      <div class="tab-content">
        <div v-if="activeTab === 'damage'" class="damage-section">
          <div class="section-header-inline">
            <h2 class="ancient-title">殿堂病害详情</h2>
            <button class="ancient-btn-outline" @click="showDamageDialog = true">
              编辑病害信息
            </button>
          </div>

          <div class="damage-grid" v-if="hall.damage_details && Object.keys(hall.damage_details).length > 0">
            <div
              v-for="(value, key) in hall.damage_details"
              :key="key"
              class="damage-card ancient-card"
            >
              <div class="damage-header">
                <span class="damage-name font-ancient">{{ key }}</span>
                <span class="damage-badge" :class="getDamageClass(value)">
                  {{ getDamageLevel(value) }}
                </span>
              </div>
              <p class="damage-desc">{{ value }}</p>
            </div>
          </div>
          <el-empty v-else description="暂无病害信息，请先添加" />
        </div>

        <div v-if="activeTab === 'repair'" class="repair-section">
          <div class="section-header-inline">
            <h2 class="ancient-title">修缮方案</h2>
            <button class="ancient-btn-outline" @click="showRepairDialog = true">
              编辑修缮方案
            </button>
          </div>

          <div class="repair-list" v-if="hall.repair_plan && Object.keys(hall.repair_plan).length > 0">
            <div
              v-for="(value, key) in hall.repair_plan"
              :key="key"
              class="repair-item ancient-card"
            >
              <div class="repair-icon">🛠️</div>
              <div class="repair-content">
                <h3 class="repair-name font-ancient">{{ key }}</h3>
                <p class="repair-desc">{{ value }}</p>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无修缮方案，请先添加" />
        </div>

        <div v-if="activeTab === 'meetings'" class="meetings-section">
          <div class="section-header-inline">
            <h2 class="ancient-title">相关会议纪要</h2>
            <button class="ancient-btn" @click="showMeetingDialog = true">
              <el-icon><Plus /></el-icon>
              创建会议
            </button>
          </div>

          <div class="meetings-list" v-if="meetings.length > 0">
            <div
              v-for="meeting in meetings"
              :key="meeting.id"
              class="meeting-card ancient-card"
              @click="$router.push(`/meetings/${meeting.id}`)"
            >
              <div class="meeting-header">
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
              <div class="meeting-footer">
                <span class="view-detail">查看详情</span>
                <el-icon><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无会议记录" />
        </div>
      </div>
    </div>

    <el-dialog
      v-model="showDamageDialog"
      title="编辑殿堂病害"
      width="700px"
    >
      <el-form label-width="120px">
        <el-form-item
          v-for="(item, index) in damageForm"
          :key="index"
          :label="`病害 ${index + 1}`"
        >
          <div class="form-row">
            <el-input
              v-model="item.key"
              placeholder="病害名称"
              style="width: 200px; margin-right: 10px;"
            />
            <el-input
              v-model="item.value"
              placeholder="病害详情描述"
              style="flex: 1; margin-right: 10px;"
            />
            <el-button
              type="danger"
              :icon="Delete"
              circle
              @click="removeDamageItem(index)"
            />
          </div>
        </el-form-item>
        <el-button type="primary" :icon="Plus" @click="addDamageItem">
          添加病害项
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="showDamageDialog = false">取消</el-button>
        <el-button type="primary" @click="saveDamageDetails">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showRepairDialog"
      title="编辑修缮方案"
      width="700px"
    >
      <el-form label-width="120px">
        <el-form-item
          v-for="(item, index) in repairForm"
          :key="index"
          :label="`项目 ${index + 1}`"
        >
          <div class="form-row">
            <el-input
              v-model="item.key"
              placeholder="修缮项目名称"
              style="width: 200px; margin-right: 10px;"
            />
            <el-input
              v-model="item.value"
              placeholder="修缮方案描述"
              style="flex: 1; margin-right: 10px;"
            />
            <el-button
              type="danger"
              :icon="Delete"
              circle
              @click="removeRepairItem(index)"
            />
          </div>
        </el-form-item>
        <el-button type="primary" :icon="Plus" @click="addRepairItem">
          添加修缮项目
        </el-button>
      </el-form>
      <template #footer>
        <el-button @click="showRepairDialog = false">取消</el-button>
        <el-button type="primary" @click="saveRepairPlan">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="showMeetingDialog"
      title="创建新会议"
      width="500px"
    >
      <el-form :model="newMeeting" label-width="100px">
        <el-form-item label="会议标题">
          <el-input v-model="newMeeting.title" placeholder="请输入会议标题" />
        </el-form-item>
        <el-form-item label="会议日期">
          <el-date-picker
            v-model="newMeeting.date"
            type="datetime"
            placeholder="选择会议日期时间"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="参会人员">
          <el-select
            v-model="newMeeting.participants"
            multiple
            filterable
            allow-create
            placeholder="输入参会人员姓名，回车添加"
            style="width: 100%;"
          >
            <el-option
              v-for="p in ['住持', '监院', '工匠师', '设计师', '居士代表']"
              :key="p"
              :label="p"
              :value="p"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showMeetingDialog = false">取消</el-button>
        <el-button type="primary" @click="createMeeting">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus, Delete, Calendar, User, ArrowRight } from '@element-plus/icons-vue'
import { templeApi, meetingApi } from '../api'

const route = useRoute()
const hall = ref(null)
const meetings = ref([])
const activeTab = ref('damage')
const showDamageDialog = ref(false)
const showRepairDialog = ref(false)
const showMeetingDialog = ref(false)

const damageForm = ref([])
const repairForm = ref([])
const newMeeting = ref({
  title: '',
  date: null,
  participants: []
})

onMounted(async () => {
  await loadHall()
  await loadMeetings()
})

const loadHall = async () => {
  try {
    const res = await templeApi.getHall(route.params.id)
    hall.value = res.data
    initDamageForm()
    initRepairForm()
  } catch (error) {
    ElMessage.error('加载殿堂信息失败')
  }
}

const loadMeetings = async () => {
  try {
    const res = await meetingApi.getMeetings(route.params.id)
    meetings.value = res.data
  } catch (error) {
    console.error('加载会议列表失败', error)
  }
}

const initDamageForm = () => {
  if (hall.value?.damage_details) {
    damageForm.value = Object.entries(hall.value.damage_details).map(([key, value]) => ({
      key, value
    }))
  } else {
    damageForm.value = [{ key: '', value: '' }]
  }
}

const initRepairForm = () => {
  if (hall.value?.repair_plan) {
    repairForm.value = Object.entries(hall.value.repair_plan).map(([key, value]) => ({
      key, value
    }))
  } else {
    repairForm.value = [{ key: '', value: '' }]
  }
}

const addDamageItem = () => {
  damageForm.value.push({ key: '', value: '' })
}

const removeDamageItem = (index) => {
  if (damageForm.value.length > 1) {
    damageForm.value.splice(index, 1)
  }
}

const addRepairItem = () => {
  repairForm.value.push({ key: '', value: '' })
}

const removeRepairItem = (index) => {
  if (repairForm.value.length > 1) {
    repairForm.value.splice(index, 1)
  }
}

const saveDamageDetails = async () => {
  const damage_details = {}
  for (const item of damageForm.value) {
    if (item.key && item.value) {
      damage_details[item.key] = item.value
    }
  }

  try {
    await templeApi.updateHall(hall.value.id, {
      ...hall.value,
      damage_details
    })
    ElMessage.success('病害信息保存成功')
    showDamageDialog.value = false
    await loadHall()
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  }
}

const saveRepairPlan = async () => {
  const repair_plan = {}
  for (const item of repairForm.value) {
    if (item.key && item.value) {
      repair_plan[item.key] = item.value
    }
  }

  try {
    await templeApi.updateHall(hall.value.id, {
      ...hall.value,
      repair_plan
    })
    ElMessage.success('修缮方案保存成功')
    showRepairDialog.value = false
    await loadHall()
  } catch (error) {
    ElMessage.error('保存失败，请重试')
  }
}

const createMeeting = async () => {
  if (!newMeeting.value.title || !newMeeting.value.date) {
    ElMessage.warning('请填写会议标题和日期')
    return
  }

  try {
    await meetingApi.createMeeting({
      hall_id: parseInt(route.params.id),
      title: newMeeting.value.title,
      date: newMeeting.value.date,
      participants: newMeeting.value.participants
    })
    ElMessage.success('会议创建成功')
    showMeetingDialog.value = false
    newMeeting.value = { title: '', date: null, participants: [] }
    await loadMeetings()
  } catch (error) {
    ElMessage.error('创建失败，请重试')
  }
}

const getDamageClass = (value) => {
  if (typeof value === 'string') {
    if (value.includes('严重') || value.includes('危') || value.includes('重')) {
      return 'damage-severe'
    } else if (value.includes('中') || value.includes('一般')) {
      return 'damage-moderate'
    }
  }
  return 'damage-minor'
}

const getDamageLevel = (value) => {
  if (typeof value === 'string') {
    if (value.includes('严重') || value.includes('危') || value.includes('重')) {
      return '严重'
    } else if (value.includes('中') || value.includes('一般')) {
      return '中等'
    }
  }
  return '轻微'
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
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
</script>

<style scoped>
.hall-detail-page {
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

.hall-hero {
  text-align: center;
  padding: 3rem 2rem;
  margin-bottom: 2rem;
}

.hall-icon-large {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.hall-title {
  font-size: 2.5rem;
  color: var(--primary-dark);
  margin-bottom: 0.5rem;
}

.hall-desc {
  max-width: 700px;
  margin: 0 auto 1.5rem;
  line-height: 2;
  color: var(--text-color);
}

.estimated-cost {
  font-size: 1.1rem;
  color: var(--text-light);
}

.cost-amount {
  color: var(--secondary-color);
  font-weight: 600;
  font-size: 1.3rem;
  font-family: 'Ma Shan Zheng', cursive;
}

.content-tabs {
  margin-top: 2rem;
}

.tab-buttons {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border-color);
}

.tab-btn {
  padding: 1rem 2rem;
  background: none;
  border: none;
  font-size: 1.1rem;
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

.section-header-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header-inline .ancient-title {
  margin: 0;
  text-align: left;
  font-size: 1.8rem;
}

.damage-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.damage-card {
  padding: 1.5rem;
}

.damage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.damage-name {
  font-size: 1.3rem;
  color: var(--primary-dark);
}

.damage-desc {
  color: var(--text-color);
  line-height: 1.8;
}

.repair-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.repair-item {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem;
  align-items: flex-start;
}

.repair-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.repair-content {
  flex: 1;
}

.repair-name {
  font-size: 1.3rem;
  color: var(--primary-dark);
  margin-bottom: 0.5rem;
}

.repair-desc {
  color: var(--text-color);
  line-height: 1.8;
}

.meetings-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
}

.meeting-card {
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.meeting-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px var(--shadow-color);
}

.meeting-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.meeting-title {
  font-size: 1.3rem;
  color: var(--primary-dark);
  flex: 1;
}

.meeting-meta {
  display: flex;
  gap: 1.5rem;
  color: var(--text-light);
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.meeting-meta span {
  display: flex;
  align-items: center;
  gap: 0.3rem;
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

.form-row {
  display: flex;
  align-items: center;
  width: 100%;
}

@media (max-width: 768px) {
  .section-header-inline {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .tab-buttons {
    flex-wrap: wrap;
  }

  .tab-btn {
    padding: 0.75rem 1rem;
    font-size: 1rem;
  }

  .damage-grid,
  .meetings-list {
    grid-template-columns: 1fr;
  }

  .form-row {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .form-row .el-input {
    width: 100% !important;
  }
}
</style>
