<template>
  <HeaderBar />
  <div class="container mt-4">
    <h2>Student Dashboard</h2>
    <div class="mb-3">
      <router-link to="/student/edit-profile" class="btn btn-primary me-2">Edit Profile</router-link>
      <router-link to="/student/search" class="btn btn-info me-2">Search Companies & Drives</router-link>
      <router-link to="/student/history" class="btn btn-secondary">View History</router-link>
    </div>
    <div class="row mt-4">
      <div class="col-md-6">
        <h4>Available Drives</h4>
        <table class="table table-bordered table-sm">
          <thead><tr><th>Title</th><th>Company</th><th>Status</th><th>Deadline</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td>{{ d.title }}</td>
              <td>{{ d.company }}</td>
              <td>
                <span class="badge" :class="getDriveStatusBadgeClass(d)">{{ getDriveStatusLabel(d) }}</span>
              </td>
              <td>{{ d.deadline }}</td>
              <td class="text-nowrap">
                <div class="btn-group" role="group">
                  <button class="btn btn-primary btn-sm" @click="applyDrive(d.id)" :disabled="!d.can_apply">
                    {{ d.can_apply ? 'Apply' : (d.is_closed ? 'Closed' : 'Drive Ended') }}
                  </button>
                  <button class="btn btn-outline-secondary btn-sm" @click="openDriveModal(d.id)">View</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="col-md-6">
        <h4>Companies</h4>
        <table class="table table-bordered table-sm">
          <thead><tr><th>Name</th><th>Industry</th><th>Location</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td>{{ c.name }}</td>
              <td>{{ c.industry }}</td>
              <td>{{ c.location }}</td>
              <td class="text-nowrap">
                <button class="btn btn-outline-secondary btn-sm" @click="openCompanyModal(c.id)">View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
  </div>
  <DriveDetailModal :drive-id="selectedDriveId" api-base="/drives" :visible="showDriveModal" @close="showDriveModal = false" />
  <CompanyDetailModal api-base="/student/companies" :company-id="selectedCompanyId" :visible="showCompanyModal" @close="showCompanyModal = false" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'
import CompanyDetailModal from '../components/CompanyDetailModal.vue'
import DriveDetailModal from '../components/DriveDetailModal.vue'

const drives = ref([])
const companies = ref([])
const error = ref('')
const selectedDriveId = ref(null)
const selectedCompanyId = ref(null)
const showDriveModal = ref(false)
const showCompanyModal = ref(false)

const fetchAll = async () => {
  try {
    drives.value = (await api.get('/student/drives')).data
    companies.value = (await api.get('/student/companies')).data
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to load dashboard data.'
  }
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

const getDriveStatusLabel = (drive) => {
  if (drive.is_closed) return 'Closed'
  if (drive.is_ended) return 'Drive Ended'
  return 'Open'
}

const getDriveStatusBadgeClass = (drive) => {
  if (drive.is_closed) return 'bg-secondary'
  if (drive.is_ended) return 'bg-dark'
  return 'bg-success'
}

const openDriveModal = (id) => {
  selectedDriveId.value = id
  showDriveModal.value = true
}

const openCompanyModal = (id) => {
  selectedCompanyId.value = id
  showCompanyModal.value = true
}

onMounted(fetchAll)
</script>
