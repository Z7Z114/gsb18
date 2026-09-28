<template>
  <div class="temple-detail-page" v-if="temple">
    <button class="back-btn" @click="$router.back()">
      <el-icon><ArrowLeft /></el-icon>
      返回列表
    </button>

    <div class="temple-header ancient-card">
      <div class="temple-icon-large">🏯</div>
      <h1 class="font-ancient temple-title">{{ temple.name }}</h1>
      <p class="temple-location">
        <el-icon><Location /></el-icon>
        {{ temple.location }}
      </p>
      <p class="temple-description">{{ temple.description }}</p>
    </div>

    <div class="section-header">
      <h2 class="ancient-title">殿堂名录</h2>
      <button class="ancient-btn" @click="showHallDialog = true">
        <el-icon><Plus /></el-icon>
        登记殿堂
      </button>
    </div>

    <div class="halls-grid" v-if="halls.length > 0">
      <div
        v-for="hall in halls"
        :key="hall.id"
        class="hall-card ancient-card"
        @click="$router.push(`/halls/${hall.id}`)"
      >
        <div class="hall-icon">⛩️</div>
        <h3 class="hall-name font-ancient">{{ hall.name }}</h3>
        <p class="hall-desc">{{ hall.description || '暂无描述' }}</p>
        
        <div class="hall-stats" v-if="hall.damage_details">
          <div
            v-for="(value, key) in hall.damage_details"
            :key="key"
            class="damage-item"
          >
            <span class="damage-badge" :class="getDamageClass(value)">
              {{ key }}
            </span>
          </div>
        </div>

        <div class="hall-footer">
          <span class="cost" v-if="hall.estimated_cost">
            预估: {{ hall.estimated_cost }}
          </span>
          <span class="view-detail">查看详情</span>
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无殿堂信息" />

    <el-dialog
      v-model="showHallDialog"
      title="登记新殿堂"
      width="600px"
    >
      <el-form :model="newHall" label-width="100px">
        <el-form-item label="殿堂名称">
          <el-input v-model="newHall.name" placeholder="如：大雄宝殿、观音殿等" />
        </el-form-item>
        <el-form-item label="殿堂介绍">
          <el-input
            v-model="newHall.description"
            type="textarea"
            :rows="3"
            placeholder="请输入殿堂的历史、供奉等介绍"
          />
        </el-form-item>
        <el-form-item label="预估费用">
          <el-input v-model="newHall.estimated_cost" placeholder="如：约人民币伍拾万元" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showHallDialog = false">取消</el-button>
        <el-button type="primary" @click="createHall">确认登记</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Location, Plus, ArrowRight } from '@element-plus/icons-vue'
import { templeApi } from '../api'

const route = useRoute()
const temple = ref(null)
const halls = ref([])
const showHallDialog = ref(false)
const newHall = ref({
  name: '',
  description: '',
  estimated_cost: ''
})

onMounted(async () => {
  await loadTemple()
  await loadHalls()
})

const loadTemple = async () => {
  try {
    const res = await templeApi.getTemple(route.params.id)
    temple.value = res.data
  } catch (error) {
    ElMessage.error('加载寺庙信息失败')
  }
}

const loadHalls = async () => {
  try {
    const res = await templeApi.getHalls(route.params.id)
    halls.value = res.data
  } catch (error) {
    ElMessage.error('加载殿堂列表失败')
  }
}

const createHall = async () => {
  if (!newHall.value.name) {
    ElMessage.warning('请填写殿堂名称')
    return
  }

  try {
    await templeApi.createHall(route.params.id, newHall.value)
    ElMessage.success('殿堂登记成功')
    showHallDialog.value = false
    newHall.value = { name: '', description: '', estimated_cost: '' }
    await loadHalls()
  } catch (error) {
    ElMessage.error('登记失败，请重试')
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
</script>

<style scoped>
.temple-detail-page {
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

.temple-header {
  text-align: center;
  padding: 3rem 2rem;
  margin-bottom: 3rem;
}

.temple-icon-large {
  font-size: 5rem;
  margin-bottom: 1rem;
}

.temple-title {
  font-size: 2.5rem;
  color: var(--primary-dark);
  margin-bottom: 0.5rem;
}

.temple-location {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--text-light);
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.temple-description {
  max-width: 800px;
  margin: 0 auto;
  line-height: 2;
  color: var(--text-color);
  font-size: 1.05rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.section-header .ancient-title {
  margin: 0;
  text-align: left;
}

.halls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.hall-card {
  padding: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.hall-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 40px var(--shadow-color);
}

.hall-icon {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 1rem;
}

.hall-name {
  font-size: 1.6rem;
  color: var(--primary-dark);
  text-align: center;
  margin-bottom: 0.5rem;
}

.hall-desc {
  color: var(--text-light);
  text-align: center;
  margin-bottom: 1.5rem;
  line-height: 1.8;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.hall-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.hall-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px dashed var(--border-color);
}

.cost {
  color: var(--secondary-color);
  font-weight: 500;
}

.view-detail {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--primary-color);
  font-weight: 500;
}

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    gap: 1rem;
  }

  .halls-grid {
    grid-template-columns: 1fr;
  }
}
</style>
