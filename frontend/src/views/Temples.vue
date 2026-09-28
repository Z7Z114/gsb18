<template>
  <div class="temples-page">
    <div class="page-header">
      <h1 class="ancient-title">寺庙名录</h1>
      <p class="ancient-subtitle">千年古刹，静待护持</p>
      <button class="ancient-btn" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        登记新寺
      </button>
    </div>

    <div class="temples-grid" v-if="temples.length > 0">
      <div
        v-for="temple in temples"
        :key="temple.id"
        class="temple-card ancient-card"
        @click="$router.push(`/temples/${temple.id}`)"
      >
        <div class="temple-icon">🏯</div>
        <h3 class="temple-name font-ancient">{{ temple.name }}</h3>
        <p class="temple-location">
          <el-icon><Location /></el-icon>
          {{ temple.location }}
        </p>
        <p class="temple-desc">{{ temple.description || '暂无描述' }}</p>
        <div class="temple-footer">
          <span class="view-halls-text">查看殿堂详情</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无寺庙信息" />

    <el-dialog
      v-model="showCreateDialog"
      title="登记新寺庙"
      width="500px"
    >
      <el-form :model="newTemple" label-width="80px">
        <el-form-item label="寺庙名称">
          <el-input v-model="newTemple.name" placeholder="请输入寺庙名称" />
        </el-form-item>
        <el-form-item label="所在地">
          <el-input v-model="newTemple.location" placeholder="请输入寺庙所在地" />
        </el-form-item>
        <el-form-item label="寺庙介绍">
          <el-input
            v-model="newTemple.description"
            type="textarea"
            :rows="4"
            placeholder="请输入寺庙历史沿革、现状等介绍"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createTemple">确认登记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Location, ArrowRight } from '@element-plus/icons-vue'
import { templeApi } from '../api'

const temples = ref([])
const showCreateDialog = ref(false)
const newTemple = ref({
  name: '',
  location: '',
  description: ''
})

onMounted(async () => {
  await loadTemples()
})

const loadTemples = async () => {
  try {
    const res = await templeApi.getTemples()
    temples.value = res.data
  } catch (error) {
    ElMessage.error('加载寺庙列表失败')
  }
}

const createTemple = async () => {
  if (!newTemple.value.name || !newTemple.value.location) {
    ElMessage.warning('请填写寺庙名称和所在地')
    return
  }

  try {
    await templeApi.createTemple(newTemple.value)
    ElMessage.success('寺庙登记成功')
    showCreateDialog.value = false
    newTemple.value = { name: '', location: '', description: '' }
    await loadTemples()
  } catch (error) {
    ElMessage.error('登记失败，请重试')
  }
}
</script>

<style scoped>
.temples-page {
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

.temples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.temple-card {
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.temple-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px var(--shadow-color);
}

.temple-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.temple-name {
  font-size: 1.8rem;
  color: var(--primary-dark);
  margin-bottom: 0.5rem;
}

.temple-location {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-light);
  margin-bottom: 1rem;
}

.temple-desc {
  color: var(--text-color);
  line-height: 1.8;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.temple-footer {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--primary-color);
  font-weight: 500;
  padding-top: 1rem;
  border-top: 1px dashed var(--border-color);
}

@media (max-width: 768px) {
  .page-header .ancient-btn {
    position: static;
    transform: none;
    margin-top: 1rem;
  }

  .temples-grid {
    grid-template-columns: 1fr;
  }
}
</style>
