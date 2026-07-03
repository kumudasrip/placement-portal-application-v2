<template>
  <HeaderBar />
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <div>
        <h2>Application History</h2>
        <p class="text-muted">Review all your applications and view detailed history for each one.</p>
      </div>
      <button class="btn btn-success" @click="exportCSV">Export Applications as CSV</button>
    </div>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="card">
      <div class="card-body">
        <ApplicationTable :columns="['Drive', 'Company', 'Status', 'Date']" :rows="applications" :showActions="true">
          <template #actions="{ row }">
            <button class="btn btn-sm btn-primary" @click="openApplicationModal(row.id)">View</button>
          </template>
        </ApplicationTable>
      </div>
    </div>

    <ApplicationDetailModal
      :application-id="selectedApplicationId"
      api-base="/student/applications"
      :visible="showApplicationModal"
      @close="showApplicationModal = false"
    />
    <div v-if="exportMsg" class="alert alert-success mt-3">{{ exportMsg }}</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'
import ApplicationTable from '../components/ApplicationTable.vue'
import ApplicationDetailModal from '../components/ApplicationDetailModal.vue'

const applications = ref([])
const error = ref('')
const exportMsg = ref('')
const selectedApplicationId = ref(null)
const showApplicationModal = ref(false)

const fetchApplications = async () => {
  try {
    const response = await api.get('/student/applications')
    applications.value = response.data
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to load application history.'
  }
}

const exportCSV = async () => {
  try {
    const response = await api.post('/student/export_applications', {}, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'applications.csv')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    exportMsg.value = 'CSV exported successfully!'
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to export.'
  }
}

const openApplicationModal = (id) => {
  selectedApplicationId.value = id
  showApplicationModal.value = true
}

onMounted(fetchApplications)
</script>
