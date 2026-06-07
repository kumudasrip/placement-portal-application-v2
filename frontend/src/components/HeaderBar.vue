<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <a class="navbar-brand" href="#" @click.prevent="goHome">PPA</a>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
          <li class="nav-item" v-if="isAuthenticated">
            <button class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isAuthenticated = ref(!!localStorage.getItem('token'))
const role = ref(localStorage.getItem('role'))

const goHome = () => {
  if (!isAuthenticated.value) {
    router.push('/login')
    return
  }
  if (role.value === 'admin') router.push('/admin')
  else if (role.value === 'company') router.push('/company')
  else if (role.value === 'student') router.push('/student')
  else router.push('/login')
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>
