<template>
  <div class="container mt-5" style="max-width: 500px;">
    <h2 class="mb-4 text-center">Register</h2>
    <div class="d-flex justify-content-center mb-3">
      <button class="btn btn-outline-primary me-2" :class="{active: role==='student'}" @click="role='student'">Student</button>
      <button class="btn btn-outline-success" :class="{active: role==='company'}" @click="role='company'">Company</button>
    </div>
    <form @submit.prevent="register">
      <div class="mb-3">
        <label class="form-label">Username</label>
        <input v-model="username" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" required />
      </div>
      <div v-if="role==='student'">
        <div class="mb-3">
          <label class="form-label">Name</label>
          <input v-model="name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">College Name</label>
          <input v-model="college_name" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Degree</label>
          <input v-model="degree" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Department</label>
          <input v-model="department" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Year</label>
          <input v-model="year" type="number" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">CGPA</label>
          <input v-model="cgpa" type="number" step="0.01" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Location</label>
          <input v-model="location" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Phone Number</label>
          <input v-model="phone_number" class="form-control" />
        </div>
      </div>
      <div v-if="role==='company'">
        <div class="mb-3">
          <label class="form-label">Company Name</label>
          <input v-model="name" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">HR Contact</label>
          <input v-model="hr_contact" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Website</label>
          <input v-model="website" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Industry</label>
          <input v-model="industry" class="form-control" />
        </div>
        <div class="mb-3">
          <label class="form-label">Location</label>
          <input v-model="location_company" class="form-control" />
        </div>
      </div>
      <div class="mb-3">
        <button class="btn btn-primary w-100" type="submit">Register</button>
      </div>
      <div class="mb-2 text-center">
        <router-link to="/login">Already have an account? Login</router-link>
      </div>
      <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
      <div v-if="success" class="alert alert-success mt-2">{{ success }}</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '../utils/api'

const role = ref('student')
const username = ref('')
const email = ref('')
const password = ref('')
const name = ref('')
const college_name = ref('')
const degree = ref('')
const department = ref('')
const cgpa = ref('')
const year = ref('')
const location = ref('')
const phone_number = ref('')
const hr_contact = ref('')
const website = ref('')
const industry = ref('')
const location_company = ref('')
const error = ref('')
const success = ref('')
const router = useRouter()

const register = async () => {
  error.value = ''
  success.value = ''
  try {
    let payload = { username: username.value, email: email.value, password: password.value }
    if (role.value === 'student') {
      payload = { 
        ...payload, 
        name: name.value, 
        college_name: college_name.value,
        degree: degree.value,
        department: department.value, 
        cgpa: cgpa.value, 
        year: year.value,
        location: location.value,
        phone_number: phone_number.value
      }
      await api.post('/register/student', payload)
      success.value = 'Student registered! Please login.'
    } else {
      payload = { ...payload, name: name.value, hr_contact: hr_contact.value, website: website.value, industry: industry.value, location: location_company.value }
      await api.post('/register/company', payload)
      success.value = 'Company registered! Wait for admin approval.'
    }
    setTimeout(() => router.push('/login'), 1500)
  } catch (e) {
    error.value = e.response?.data?.msg || 'Registration failed.'
  }
}
</script>
