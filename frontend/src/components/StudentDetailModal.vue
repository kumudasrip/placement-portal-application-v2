<template>
  <div v-if="visible" class="modal d-block" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Student Details</h5>
          <button type="button" class="btn-close" @click="close"></button>
        </div>
        <div v-if="loading" class="modal-body text-center">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        <div v-else class="modal-body">
          <div class="row mb-3">
            <div class="col-md-6">
              <p><strong>Name:</strong> {{ student.name }}</p>
              <p><strong>Email:</strong> {{ student.email }}</p>
              <p><strong>Phone:</strong> {{ student.phone_number || 'N/A' }}</p>
              <p><strong>Location:</strong> {{ student.location || 'N/A' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>College:</strong> {{ student.college_name || 'N/A' }}</p>
              <p><strong>Degree:</strong> {{ student.degree || 'N/A' }}</p>
              <p><strong>Department:</strong> {{ student.department || 'N/A' }}</p>
              <p><strong>Year:</strong> {{ student.year || 'N/A' }}</p>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-md-6">
              <p><strong>CGPA:</strong> {{ student.cgpa || 'N/A' }}</p>
              <p><strong>Status:</strong> 
                <span class="badge" :class="student.is_active ? 'bg-success' : 'bg-danger'">
                  {{ student.is_active ? 'Active' : 'Inactive' }}
                </span>
              </p>
            </div>
            <div class="col-md-6">
              <p><strong>Blacklisted:</strong>
                <span class="badge" :class="student.is_blacklisted ? 'bg-danger' : 'bg-success'">
                  {{ student.is_blacklisted ? 'Yes' : 'No' }}
                </span>
              </p>
              <p><strong>Joined:</strong> {{ student.created_at }}</p>
            </div>
          </div>
          <div v-if="student.skills" class="mb-3">
            <p><strong>Skills:</strong> {{ student.skills }}</p>
          </div>
          <div v-if="student.education" class="mb-3">
            <p><strong>Education:</strong> {{ student.education }}</p>
          </div>
          <div v-if="student.experience" class="mb-3">
            <p><strong>Experience:</strong> {{ student.experience }}</p>
          </div>
          <div v-if="student.resume" class="mb-3">
            <button type="button" class="btn btn-outline-primary btn-sm" @click="downloadResume">
              Download CV
            </button>
          </div>
          <div v-if="student.applications_count > 0" class="mt-4">
            <h6>Applications ({{ student.applications_count }})</h6>
            <table class="table table-sm table-bordered">
              <thead>
                <tr>
                  <th>Drive</th>
                  <th>Company</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in student.applications" :key="app.id">
                  <td>{{ app.drive }}</td>
                  <td>{{ app.company }}</td>
                  <td><span class="badge bg-info">{{ app.status }}</span></td>
                  <td>{{ app.date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="close">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '../utils/api'

const props = defineProps({
  studentId: {
    type: Number,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close'])

const student = ref({})
const loading = ref(false)

const close = () => {
  emit('close')
}

const downloadResume = async () => {
  if (!props.studentId) return
  try {
    const response = await api.get(`/admin/students/${props.studentId}/download_resume`, {
      responseType: 'blob'
    })
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = student.value.resume || 'resume'
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Failed to download student resume:', e)
  }
}

watch(() => props.visible, async (newVal) => {
  if (newVal && props.studentId) {
    loading.value = true
    try {
      const response = await api.get(`/admin/students/${props.studentId}`)
      student.value = response.data
    } catch (e) {
      console.error('Failed to load student details:', e)
    } finally {
      loading.value = false
    }
  }
})
</script>

<style scoped>
.modal {
  display: block;
  position: fixed;
  z-index: 1000;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
}
</style>
