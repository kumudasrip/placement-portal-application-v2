import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import StudentHistory from '../views/StudentHistory.vue'
import StudentProfileEdit from '../views/StudentProfileEdit.vue'
import StudentSearchDashboard from '../views/StudentSearchDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard },
  { path: '/company', name: 'CompanyDashboard', component: CompanyDashboard },
  { path: '/company/interviews', redirect: '/company' },
  { path: '/student', name: 'StudentDashboard', component: StudentDashboard },
  { path: '/student/history', name: 'StudentHistory', component: StudentHistory },
  { path: '/student/edit-profile', name: 'StudentProfileEdit', component: StudentProfileEdit },
  { path: '/student/search', name: 'StudentSearchDashboard', component: StudentSearchDashboard },
  { path: '/student/placements', redirect: '/student' },
  { path: '/student/interviews', redirect: '/student' },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export default router
