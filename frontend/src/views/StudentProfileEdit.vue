<template>
  <HeaderBar />
  <div class="container mt-4">
    <h2>Edit Profile</h2>
    <div class="row mt-4">
      <div class="col-md-8">
        <form @submit.prevent="updateProfile">
          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Name</label>
              <input v-model="profile.name" class="form-control" required />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Email</label>
              <input v-model="profile.email" type="email" class="form-control" disabled />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Phone Number</label>
              <input v-model="profile.phone_number" class="form-control" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Location</label>
              <input v-model="profile.location" class="form-control" />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">College Name</label>
              <input v-model="profile.college_name" class="form-control" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Degree</label>
              <input v-model="profile.degree" class="form-control" />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">Department</label>
              <input v-model="profile.department" class="form-control" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Year</label>
              <input v-model.number="profile.year" type="number" class="form-control" />
            </div>
          </div>

          <div class="row">
            <div class="col-md-6 mb-3">
              <label class="form-label">CGPA</label>
              <input v-model.number="profile.cgpa" type="number" step="0.01" class="form-control" />
            </div>
            <div class="col-md-6 mb-3">
              <label class="form-label">Skills</label>
              <input v-model="profile.skills" class="form-control" placeholder="e.g., Java, Python, SQL" />
            </div>
          </div>

          <div class="mb-3">
            <label class="form-label">Education</label>
            <textarea v-model="profile.education" class="form-control" rows="2"></textarea>
          </div>

          <div class="mb-3">
            <label class="form-label">Experience (years)</label>
            <input v-model.number="profile.experience" type="number" min="0" class="form-control" placeholder="e.g., 0, 1, 2" />
          </div>

          <div class="mb-3">
            <label class="form-label">Resume</label>
            <div class="input-group mb-2">
              <input type="file" @change="handleResumeUpload" class="form-control" accept=".pdf,.doc,.docx" />
              <button type="button" class="btn btn-outline-secondary" @click="uploadResume" :disabled="!selectedResume || uploadingResume">
                <span v-if="uploadingResume" class="spinner-border spinner-border-sm me-2"></span>
                {{ uploadingResume ? 'Uploading...' : 'Upload' }}
              </button>
            </div>
            <small v-if="profile.resume" class="text-muted">Current resume: {{ profile.resume }}</small>
            <div v-if="resumeSuccess" class="alert alert-success mt-2">{{ resumeSuccess }}</div>
            <div v-if="resumeError" class="alert alert-danger mt-2">{{ resumeError }}</div>
          </div>

          <div class="row mt-4">
            <div class="col-md-6">
              <button type="submit" class="btn btn-primary w-100" :disabled="updating">
                <span v-if="updating" class="spinner-border spinner-border-sm me-2"></span>
                {{ updating ? 'Updating...' : 'Update Profile' }}
              </button>
            </div>
            <div class="col-md-6">
              <router-link to="/student" class="btn btn-secondary w-100">Cancel</router-link>
            </div>
          </div>

          <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
          <div v-if="success" class="alert alert-success mt-3">{{ success }}</div>
        </form>
      </div>

      <div class="col-md-4">
        <div class="card">
          <div class="card-body">
            <h5 class="card-title">Profile Summary</h5>
            <p><strong>Name:</strong> {{ profile.name }}</p>
            <p><strong>Email:</strong> {{ profile.email }}</p>
            <p><strong>College:</strong> {{ profile.college_name || 'N/A' }}</p>
            <p><strong>Department:</strong> {{ profile.department || 'N/A' }}</p>
            <p><strong>CGPA:</strong> {{ profile.cgpa || 'N/A' }}</p>
            <p><strong>Year:</strong> {{ profile.year || 'N/A' }}</p>
            <p><strong>Location:</strong> {{ profile.location || 'N/A' }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'

const profile = ref({
  name: '',
  email: '',
  phone_number: '',
  college_name: '',
  degree: '',
  department: '',
  cgpa: null,
  year: null,
  location: '',
  skills: '',
  education: '',
  experience: '',
  resume: ''
})

const selectedResume = ref(null)
const error = ref('')
const success = ref('')
const updating = ref(false)
const uploadingResume = ref(false)
const resumeError = ref('')
const resumeSuccess = ref('')

const fetchProfile = async () => {
  try {
    const response = await api.get('/student/profile')
    profile.value = response.data
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to load profile'
  }
}

const handleResumeUpload = (event) => {
  selectedResume.value = event.target.files[0]
}

const uploadResume = async () => {
  if (!selectedResume.value) return

  uploadingResume.value = true
  resumeError.value = ''
  resumeSuccess.value = ''

  try {
    const formData = new FormData()
    formData.append('file', selectedResume.value)
    
    const response = await api.post('/student/upload_resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    profile.value.resume = response.data.resume
    resumeSuccess.value = 'Resume uploaded successfully!'
    selectedResume.value = null
    setTimeout(() => { resumeSuccess.value = '' }, 3000)
  } catch (e) {
    resumeError.value = e.response?.data?.msg || 'Failed to upload resume'
    setTimeout(() => { resumeError.value = '' }, 3000)
  } finally {
    uploadingResume.value = false
  }
}

const updateProfile = async () => {
  error.value = ''
  success.value = ''
  updating.value = true

  try {
    await api.put('/student/profile', {
      name: profile.value.name,
      phone_number: profile.value.phone_number,
      college_name: profile.value.college_name,
      degree: profile.value.degree,
      department: profile.value.department,
      cgpa: profile.value.cgpa,
      year: profile.value.year,
      location: profile.value.location,
      skills: profile.value.skills,
      education: profile.value.education,
      experience: profile.value.experience,
      resume: profile.value.resume
    })
    
    success.value = 'Profile updated successfully!'
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to update profile'
  } finally {
    updating.value = false
  }
}

onMounted(fetchProfile)
</script>
