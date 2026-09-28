<template>
  <div class="app-container">
    <header class="ancient-header">
      <div class="header-content">
        <div class="logo-section" @click="$router.push('/')">
          <span class="logo-icon">🏯</span>
          <h1 class="font-ancient">古刹修缮功德纪要</h1>
        </div>
        <nav class="nav-menu">
          <router-link to="/" class="nav-item">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/temples" class="nav-item">
            <el-icon><OfficeBuilding /></el-icon>
            <span>寺庙殿堂</span>
          </router-link>
          <router-link to="/meetings" class="nav-item">
            <el-icon><ChatDotRound /></el-icon>
            <span>会议纪要</span>
          </router-link>
          <router-link to="/donors" class="nav-item">
            <el-icon><UserFilled /></el-icon>
            <span>功德主</span>
          </router-link>
        </nav>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <footer class="ancient-footer">
      <div class="footer-content">
        <p class="font-ancient">愿以此功德，普及于一切</p>
        <p class="font-ancient">我等与众生，皆共成佛道</p>
        <p class="copyright">寺庙修缮募捐功德纪要系统 © 2024</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { HomeFilled, OfficeBuilding, ChatDotRound, UserFilled } from '@element-plus/icons-vue'
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.ancient-header {
  background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 50%, var(--secondary-color) 100%);
  box-shadow: 0 4px 20px var(--shadow-color);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 70px;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
}

.logo-icon {
  font-size: 2.5rem;
}

.logo-section h1 {
  color: #fff;
  font-size: 1.8rem;
  margin: 0;
  letter-spacing: 4px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.nav-menu {
  display: flex;
  gap: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.3s ease;
  font-size: 1rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 500;
}

.main-content {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem;
}

.ancient-footer {
  background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-color) 100%);
  color: rgba(255, 255, 255, 0.9);
  padding: 2rem;
  margin-top: 3rem;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  text-align: center;
}

.footer-content p {
  margin: 0.5rem 0;
}

.copyright {
  font-size: 0.85rem;
  opacity: 0.7;
  margin-top: 1rem !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    height: auto;
    padding: 1rem;
    gap: 1rem;
  }

  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }

  .nav-item {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }

  .logo-section h1 {
    font-size: 1.4rem;
  }
}
</style>
