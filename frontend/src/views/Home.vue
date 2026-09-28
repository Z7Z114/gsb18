<template>
  <div class="home-page">
    <section class="hero-section scroll-decoration">
      <div class="hero-content">
        <h1 class="font-ancient hero-title">古刹重光，功德无量</h1>
        <p class="hero-subtitle">
          千年古刹，历经风雨，殿堂颓败，佛像蒙尘。<br>
          祈盼十方善信，发心护持，共襄盛举，俾使祖庭重辉，佛法久住。
        </p>
        <div class="hero-actions">
          <button class="ancient-btn" @click="$router.push('/temples')">
            查看殿堂详情
          </button>
          <button class="ancient-btn-outline" @click="$router.push('/meetings')">
            查阅会议纪要
          </button>
        </div>
      </div>
    </section>

    <div class="content-section">
      <div class="stats-grid">
        <div class="stat-card ancient-card">
          <div class="stat-icon">🏯</div>
          <div class="stat-number">{{ stats.temples }}</div>
          <div class="stat-label">在册寺庙</div>
        </div>
        <div class="stat-card ancient-card">
          <div class="stat-icon">⛩️</div>
          <div class="stat-number">{{ stats.halls }}</div>
          <div class="stat-label">待修殿堂</div>
        </div>
        <div class="stat-card ancient-card">
          <div class="stat-icon">📜</div>
          <div class="stat-number">{{ stats.meetings }}</div>
          <div class="stat-label">会议纪要</div>
        </div>
        <div class="stat-card ancient-card">
          <div class="stat-icon">🙏</div>
          <div class="stat-number">{{ stats.donors }}</div>
          <div class="stat-label">功德施主</div>
        </div>
      </div>

      <div class="ancient-divider"></div>

      <div class="feature-section">
        <h2 class="ancient-title">功德纪要系统</h2>
        <p class="ancient-subtitle">智能化管理寺庙修缮募捐全过程</p>

        <div class="features-grid">
          <div class="feature-card ancient-card">
            <div class="feature-icon">🎙️</div>
            <h3 class="feature-title">智能语音转写</h3>
            <p class="feature-desc">
              采用Whisper AI技术，自动转写住持与工匠对话，精确记录木构替换、彩绘重绘等修缮细节。
            </p>
          </div>

          <div class="feature-card ancient-card">
            <div class="feature-icon">👥</div>
            <h3 class="feature-title">说话人自动标记</h3>
            <p class="feature-desc">
              基于pyannote技术，自动区分寺方与设计方发言，清晰呈现各方观点与诉求。
            </p>
          </div>

          <div class="feature-card ancient-card">
            <div class="feature-icon">✨</div>
            <h3 class="feature-title">AI智能摘要</h3>
            <p class="feature-desc">
              OpenAI深度分析会议内容，自动生成专业募捐文案与功德回向清单，典雅如法。
            </p>
          </div>

          <div class="feature-card ancient-card">
            <div class="feature-icon">📧</div>
            <h3 class="feature-title">信众邮件通知</h3>
            <p class="feature-desc">
              精美的古风Markdown格式，一键发送给十方信众，广结善缘，共植福田。
            </p>
          </div>
        </div>
      </div>

      <div class="ancient-divider"></div>

      <div class="wisdom-section">
        <div class="ancient-quote">
          <p class="quote-text font-ancient">
            "若人发心造塔寺，其人所得功德利，<br>
            假使劫石可消磨，此福无边不可尽。"
          </p>
          <p class="quote-source">—— 《佛说造塔功德经》</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { templeApi, meetingApi, donorApi } from '../api'

const router = useRouter()

const stats = ref({
  temples: 0,
  halls: 0,
  meetings: 0,
  donors: 0
})

onMounted(async () => {
  try {
    const [templesRes, meetingsRes, donorsRes] = await Promise.all([
      templeApi.getTemples(),
      meetingApi.getMeetings(),
      donorApi.getDonors()
    ])
    
    stats.value.temples = templesRes.data.length || 0
    stats.value.meetings = meetingsRes.data.length || 0
    stats.value.donors = donorsRes.data.length || 0
    
    let hallCount = 0
    for (const temple of templesRes.data) {
      try {
        const hallsRes = await templeApi.getHalls(temple.id)
        hallCount += hallsRes.data.length || 0
      } catch (e) {}
    }
    stats.value.halls = hallCount
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
}

.hero-section {
  background: linear-gradient(135deg, rgba(139, 69, 19, 0.9) 0%, rgba(184, 134, 11, 0.8) 100%),
              url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cpath d='M50 0 L100 50 L50 100 L0 50 Z' fill='none' stroke='rgba(255,255,255,0.1)' stroke-width='1'/%3E%3C/svg%3E");
  padding: 6rem 2rem;
  text-align: center;
  color: #fff;
  border-radius: 12px;
  margin-bottom: 3rem;
}

.hero-title {
  font-size: 3.5rem;
  margin-bottom: 1.5rem;
  text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.3);
  letter-spacing: 8px;
}

.hero-subtitle {
  font-size: 1.2rem;
  line-height: 2;
  max-width: 800px;
  margin: 0 auto 2.5rem;
  opacity: 0.95;
}

.hero-actions {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  flex-wrap: wrap;
}

.hero-actions .ancient-btn {
  background: #fff;
  color: var(--primary-color);
}

.hero-actions .ancient-btn:hover {
  background: var(--bg-secondary);
  color: var(--primary-dark);
}

.hero-actions .ancient-btn-outline {
  border-color: #fff;
  color: #fff;
}

.hero-actions .ancient-btn-outline:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: #fff;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  text-align: center;
  padding: 2rem 1.5rem;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--primary-color);
  font-family: 'Ma Shan Zheng', cursive;
}

.stat-label {
  color: var(--text-light);
  font-size: 1rem;
  margin-top: 0.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.feature-card {
  padding: 2rem;
  text-align: center;
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 30px var(--shadow-color);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.feature-title {
  font-family: 'Ma Shan Zheng', cursive;
  color: var(--primary-dark);
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.feature-desc {
  color: var(--text-light);
  line-height: 1.8;
}

.wisdom-section {
  max-width: 800px;
  margin: 0 auto;
}

.quote-text {
  font-size: 1.5rem;
  line-height: 2;
  color: var(--primary-dark);
  margin-bottom: 1rem;
}

.quote-source {
  text-align: right;
  color: var(--text-light);
  font-style: italic;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
    letter-spacing: 4px;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-section {
    padding: 3rem 1rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .stat-number {
    font-size: 2rem;
  }
}
</style>
