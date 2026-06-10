<template>
  <HeaderBar />
  <div class="container mt-4">
    <h2>Student Dashboard</h2>
    <div class="mb-3">
      <router-link to="/student/edit-profile" class="btn btn-primary me-2">Edit Profile</router-link>
      <router-link to="/student/search" class="btn btn-info me-2">Search Companies & Drives</router-link>
      
    </div>
    <div class="row mt-4">
      <div class="col-md-6">
        <h4>Available Drives</h4>
        <table class="table table-bordered table-sm">
          <thead><tr><th>Title</th><th>Company</th><th>Deadline</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td>{{ d.title }}</td>
              <td>{{ d.company }}</td>
              <td>{{ d.deadline }}</td>
              <td>
                <button class="btn btn-primary btn-sm" @click="applyDrive(d.id)">Apply</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="col-md-6">
        <h4>My Applications</h4>
        <ApplicationTable :columns="['Drive', 'Company', 'Status', 'Date']" :rows="applications" :showActions="true">
          <template #actions="{ row }">
            <button class="btn btn-sm btn-primary" @click="openApplicationModal(row.id)">View</button>
          </template>
        </ApplicationTable>
        <button class="btn btn-success mt-2" @click="exportCSV">Export Applications as CSV</button>
        <div v-if="exportMsg" class="alert alert-info mt-2">{{ exportMsg }}</div>
      </div>
    </div>
    <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
  </div>
  <ApplicationDetailModal :application-id="selectedApplicationId" api-base="/student/applications" :visible="showApplicationModal" @close="showApplicationModal = false" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'
import ApplicationTable from '../components/ApplicationTable.vue'
import ApplicationDetailModal from '../components/ApplicationDetailModal.vue'

const drives = ref([])
const applications = ref([])
const error = ref('')
const exportMsg = ref('')
const selectedApplicationId = ref(null)
const showApplicationModal = ref(false)

const fetchAll = async () => {
  drives.value = (await api.get('/student/drives')).data
  applications.value = (await api.get('/student/applications')).data
}

const applyDrive = async (id) => {
  try {
    await api.post(`/student/drives/${id}/apply`)
    fetchAll()
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to apply.'
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
    link.parentElement.removeChild(link)
    exportMsg.value = 'CSV exported successfully!'
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to export.'
  }
}

const openApplicationModal = (id) => {
  selectedApplicationId.value = id
  showApplicationModal.value = true
}

onMounted(fetchAll)
</script>
