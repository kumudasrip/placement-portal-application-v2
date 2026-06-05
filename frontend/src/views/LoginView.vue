<template>
  <div class="container mt-5" style="max-width: 400px;">
    <h2 class="mb-4 text-center">Login</h2>
    <form @submit.prevent="login">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input v-model="username" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <div class="mb-3">
        <button class="btn btn-primary w-100" type="submit">Login</button>
      </div>
      <div class="mb-2 text-center">
        <router-link to="/register">Don't have an account? Register</router-link>
      </div>
      <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'

const username = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const login = async () => {
  error.value = ''
  try {
    const res = await api.post('/login', { username: username.value, password: password.value })
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('role', res.data.role)
    if (res.data.role === 'admin') router.push('/admin')
    else if (res.data.role === 'company') router.push('/company')
    else if (res.data.role === 'student') router.push('/student')
    else error.value = 'Unknown role.'
  } catch (e) {
    error.value = e.response?.data?.msg || 'Login failed.'
  }
}
</script>
