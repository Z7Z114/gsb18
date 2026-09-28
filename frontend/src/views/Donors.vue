<template>
  <div class="donors-page">
    <div class="page-header">
      <h1 class="ancient-title">功德主名录</h1>
      <p class="ancient-subtitle">随喜赞叹，功德无量</p>
      <button class="ancient-btn" @click="showAddDialog = true">
        <el-icon><Plus /></el-icon>
        登记功德主
      </button>
    </div>

    <div class="donors-grid" v-if="donors.length > 0">
      <div
        v-for="donor in donors"
        :key="donor.id"
        class="donor-card ancient-card"
      >
        <div class="donor-avatar">🙏</div>
        <h3 class="donor-name font-ancient">{{ donor.name }}</h3>
        <div class="donor-amount">
          <span class="amount-label">布施</span>
          <span class="amount-value">{{ donor.amount }}</span>
        </div>
        <div class="donor-contact" v-if="donor.email || donor.phone">
          <span v-if="donor.email">
            <el-icon><Message /></el-icon>
            {{ donor.email }}
          </span>
          <span v-if="donor.phone">
            <el-icon><Phone /></el-icon>
            {{ donor.phone }}
          </span>
        </div>
        <div class="donor-blessing" v-if="donor.blessing_content">
          <el-icon><StarFilled /></el-icon>
          <p>{{ donor.blessing_content }}</p>
        </div>
        <div class="donor-date">
          登记于 {{ formatDate(donor.created_at) }}
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无功德主信息" />

    <el-dialog
      v-model="showAddDialog"
      title="登记功德主"
      width="500px"
    >
      <el-form :model="newDonor" label-width="100px">
        <el-form-item label="功德主姓名">
          <el-input v-model="newDonor.name" placeholder="请输入姓名或法名" />
        </el-form-item>
        <el-form-item label="电子邮箱">
          <el-input v-model="newDonor.email" placeholder="用于接收功德纪要邮件" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="newDonor.phone" placeholder="请输入联系电话（选填）" />
        </el-form-item>
        <el-form-item label="布施金额">
          <el-input v-model="newDonor.amount" placeholder="如：人民币壹仟元整" />
        </el-form-item>
        <el-form-item label="回向内容">
          <el-input
            v-model="newDonor.blessing_content"
            type="textarea"
            :rows="3"
            placeholder="愿以此功德，回向..."
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addDonor">确认登记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Message, Phone, StarFilled } from '@element-plus/icons-vue'
import { donorApi } from '../api'

const donors = ref([])
const showAddDialog = ref(false)
const newDonor = ref({
  name: '',
  email: '',
  phone: '',
  amount: '',
  blessing_content: ''
})

onMounted(async () => {
  await loadDonors()
})

const loadDonors = async () => {
  try {
    const res = await donorApi.getDonors()
    donors.value = res.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (error) {
    ElMessage.error('加载功德主列表失败')
  }
}

const addDonor = async () => {
  if (!newDonor.value.name || !newDonor.value.amount) {
    ElMessage.warning('请填写功德主姓名和布施金额')
    return
  }

  try {
    await donorApi.createDonor(newDonor.value)
    ElMessage.success('功德主登记成功，随喜赞叹！')
    showAddDialog.value = false
    newDonor.value = {
      name: '',
      email: '',
      phone: '',
      amount: '',
      blessing_content: ''
    }
    await loadDonors()
  } catch (error) {
    ElMessage.error('登记失败，请重试')
  }
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
.donors-page {
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.page-header .ancient-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
}

.donors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 2rem;
}

.donor-card {
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.donor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px var(--shadow-color);
}

.donor-avatar {
  font-size: 3.5rem;
  margin-bottom: 1rem;
}

.donor-name {
  font-size: 1.5rem;
  color: var(--primary-dark);
  margin-bottom: 1rem;
}

.donor-amount {
  margin-bottom: 1rem;
}

.amount-label {
  color: var(--text-light);
  margin-right: 0.5rem;
}

.amount-value {
  font-size: 1.3rem;
  color: var(--secondary-color);
  font-weight: 600;
  font-family: 'Ma Shan Zheng', cursive;
}

.donor-contact {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  color: var(--text-light);
}

.donor-contact span {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
}

.donor-blessing {
  background: rgba(218, 165, 32, 0.08);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  text-align: left;
}

.donor-blessing p {
  margin: 0.5rem 0 0;
  color: var(--text-color);
  line-height: 1.8;
  font-size: 0.95rem;
}

.donor-date {
  color: var(--text-light);
  font-size: 0.85rem;
  padding-top: 1rem;
  border-top: 1px dashed var(--border-color);
}

@media (max-width: 768px) {
  .page-header .ancient-btn {
    position: static;
    transform: none;
    margin-top: 1rem;
  }

  .donors-grid {
    grid-template-columns: 1fr;
  }
}
</style>
