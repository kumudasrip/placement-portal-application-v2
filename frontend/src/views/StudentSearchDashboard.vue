<template>
  <HeaderBar />
  <div class="container mt-4">
    <h2>Explore Companies & Drives</h2>
    
    <div class="row mt-4 mb-4">
      <div class="col-md-12">
        <div class="input-group input-group-lg">
          <span class="input-group-text">🔍</span>
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control" 
            placeholder="Search companies and drives..."
            @input="performSearch"
          />
        </div>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col-md-12 d-flex align-items-center">
        <div class="form-check me-3">
          <input class="form-check-input" type="checkbox" v-model="eligibleOnly" id="searchEligibleOnly" @change="performSearch">
          <label class="form-check-label" for="searchEligibleOnly">Show eligible drives only</label>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-md-6">
        <h4>Companies</h4>
        <div v-if="companies.length === 0" class="alert alert-info">
          <span v-if="searchQuery.length === 0">Search to find companies</span>
          <span v-else>No companies found</span>
        </div>
        <div v-for="company in companies" :key="company.id" class="card mb-3">
          <div class="card-body">
            <h5 class="card-title">{{ company.name }}</h5>
            <p class="card-text">
              <strong>Industry:</strong> {{ company.industry || 'N/A' }}<br/>
              <strong>Location:</strong> {{ company.location || 'N/A' }}<br/>
              <strong>Website:</strong> <a v-if="company.website" :href="company.website" target="_blank">{{ company.website }}</a><span v-else>N/A</span>
            </p>
            <button class="btn btn-primary btn-sm" @click="openCompanyModal(company.id)">View Details</button>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <h4>Placement Drives</h4>
        <div v-if="drives.length === 0" class="alert alert-info">
          <span v-if="searchQuery.length === 0">Search to find drives</span>
          <span v-else>No drives found</span>
        </div>
        <div v-for="drive in drives" :key="drive.id" class="card mb-3">
          <div class="card-header">
            <h5 class="card-title mb-0">{{ drive.title }}</h5>
          </div>
          <div class="card-body">
            <p class="card-text">
              <strong>Company:</strong> {{ drive.company }}<br/>
              <strong>Salary:</strong> {{ drive.salary || 'N/A' }}<br/>
              <strong>Location:</strong> {{ drive.location || 'N/A' }}<br/>
              <strong>Deadline:</strong> {{ drive.deadline || 'N/A' }}<br/>
              <strong>Status:</strong> <span class="badge" :class="getDriveStatusBadgeClass(drive)">{{ getDriveStatusLabel(drive) }}</span>
            </p>
            <div v-if="driveEligibility[drive.id]" class="mb-2">
              <span v-if="driveEligibility[drive.id].eligible" class="badge bg-success">Eligible</span>
              <span v-else class="badge bg-danger">Not Eligible: {{ driveEligibility[drive.id].reasons[0] }}</span>
            </div>
            <button class="btn btn-info btn-sm me-2" @click="openDriveModal(drive.id)">View Details</button>
            <button v-if="driveEligibility[drive.id]?.eligible" class="btn btn-success btn-sm" @click="applyDrive(drive.id)" :disabled="!drive.can_apply || drive.applied">
              {{ drive.applied ? 'Already Applied' : (drive.can_apply ? 'Apply' : (drive.is_closed ? 'Closed' : 'Drive Ended')) }}
            </button>
            <button v-else disabled class="btn btn-success btn-sm">Apply</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <CompanyDetailModal api-base="/student/companies" :company-id="selectedCompanyId" :visible="showCompanyModal" @close="showCompanyModal = false" />
  <DriveDetailModal :drive-id="selectedDriveId" :visible="showDriveModal" @close="showDriveModal = false" />
</template>

<script setup>
import { ref } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'
import CompanyDetailModal from '../components/CompanyDetailModal.vue'
import DriveDetailModal from '../components/DriveDetailModal.vue'

const searchQuery = ref('')
const companies = ref([])
const drives = ref([])
const driveEligibility = ref({})
const eligibleOnly = ref(false)

const selectedCompanyId = ref(null)
const selectedDriveId = ref(null)

const showCompanyModal = ref(false)
const showDriveModal = ref(false)

const openCompanyModal = (id) => {
  selectedCompanyId.value = id
  showCompanyModal.value = true
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

let searchTimeout
const performSearch = () => {
  clearTimeout(searchTimeout)
  if (searchQuery.value.length === 0) {
    companies.value = []
    drives.value = []
    driveEligibility.value = {}
    return
  }

  searchTimeout = setTimeout(async () => {
    try {
      const [companiesResponse, drivesResponse] = await Promise.all([
        api.get('/student/companies', { params: { search: searchQuery.value } }),
        api.get('/student/drives', { params: { search: searchQuery.value, eligible_only: eligibleOnly.value } })
      ])
      
      companies.value = companiesResponse.data
      drives.value = drivesResponse.data
      
      for (const drive of drives.value) {
        try {
          const eligibilityResponse = await api.get(`/student/drives/${drive.id}/check_eligibility`)
          driveEligibility.value[drive.id] = eligibilityResponse.data
        } catch (e) {
          driveEligibility.value[drive.id] = { eligible: false, reasons: ['Could not check eligibility'] }
        }
      }
    } catch (e) {
      console.error('Search failed:', e)
    }
  }, 300)
}

const applyDrive = async (id) => {
  try {
    await api.post(`/student/drives/${id}/apply`)
    const drive = drives.value.find(d => d.id === id)
    if (drive) {
      drive.applied = true
    }
    alert('Application submitted successfully!')
  } catch (e) {
    alert(e.response?.data?.msg || 'Failed to apply to drive')
  }
}
</script>
