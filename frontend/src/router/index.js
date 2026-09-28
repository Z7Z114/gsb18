import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/temples',
    name: 'Temples',
    component: () => import('../views/Temples.vue')
  },
  {
    path: '/temples/:id',
    name: 'TempleDetail',
    component: () => import('../views/TempleDetail.vue')
  },
  {
    path: '/halls/:id',
    name: 'HallDetail',
    component: () => import('../views/HallDetail.vue')
  },
  {
    path: '/meetings',
    name: 'Meetings',
    component: () => import('../views/Meetings.vue')
  },
  {
    path: '/meetings/:id',
    name: 'MeetingDetail',
    component: () => import('../views/MeetingDetail.vue')
  },
  {
    path: '/donors',
    name: 'Donors',
    component: () => import('../views/Donors.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
