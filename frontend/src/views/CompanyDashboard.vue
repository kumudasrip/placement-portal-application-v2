<template>
  <HeaderBar />
  <div class="container mt-4">
    <h2>Company Dashboard</h2>
    
    <div class="row mt-4 mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h5 class="card-title mb-0">Company Details</h5>
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-6">
                <p><strong>Company Name:</strong> {{ company.name }}</p>
                <p><strong>Email:</strong> {{ company.email }}</p>
                <p><strong>Company Email:</strong> {{ company.company_email || 'N/A' }}</p>
                <p><strong>Industry:</strong> {{ company.industry || 'N/A' }}</p>
              </div>
              <div class="col-md-6">
                <p><strong>Location:</strong> {{ company.location || 'N/A' }}</p>
                <p><strong>HR Contact:</strong> {{ company.hr_contact || 'N/A' }}</p>
                <p><strong>Website:</strong> <a v-if="company.website" :href="company.website" target="_blank">{{ company.website }}</a><span v-else>N/A</span></p>
                <p><strong>Approval Status:</strong> <span class="badge" :class="company.approval_status === 'approved' ? 'bg-success' : 'bg-warning'">{{ company.approval_status }}</span></p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4 mb-4">
      <div class="col-md-3">
        <div class="card text-bg-info">
          <div class="card-body">
            <h5 class="card-title">Total Drives</h5>
            <p class="card-text fs-3">{{ totalDrives }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-success">
          <div class="card-body">
            <h5 class="card-title">Total Applicants</h5>
            <p class="card-text fs-3">{{ totalApplicants }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-warning">
          <div class="card-body">
            <h5 class="card-title">Selected Candidates</h5>
            <p class="card-text fs-3">{{ totalSelected }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-secondary">
          <div class="card-body">
            <h5 class="card-title">Avg Applicants/Drive</h5>
            <p class="card-text fs-3">{{ avgApplicants }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-md-7">
        <h4>My Drives</h4>
        <table class="table table-bordered table-sm">
          <thead>
            <tr>
              <th>Title</th>
              <th>Status</th>
              <th>Applicants</th>
              <th>Selected</th>
              <th>Deadline</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="drives.length === 0">
              <td colspan="6" class="text-center text-muted">No drives yet. Create one!</td>
            </tr>
            <tr v-for="d in drives" :key="d.id">
              <td>{{ d.job_title }}</td>
              <td>
                <span class="badge" :class="getDriveStatusBadgeClass(d)">
                  {{ getDriveStatusLabel(d) }}
                </span>
              </td>
              <td>{{ d.total_applicants }}</td>
              <td>{{ d.approved_applicants }}</td>
              <td>{{ d.application_deadline || 'N/A' }}</td>
              <td>
                <button class="btn btn-info btn-sm me-1" @click="viewApplications(d.id)">View</button>
                <button v-if="d.status === 'approved' && !isPastDeadline(d.application_deadline)" class="btn btn-outline-danger btn-sm" @click="closeDrive(d.id)">Close</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="selectedDrive">
          <h5 class="mt-3">Applications for {{ selectedDriveTitle }}</h5>
          <ApplicationTable
            :columns="['Student', 'Status', 'Date']"
            :rows="applications"
            :showActions="true"
          >
            <template #actions="{ row }">
              <button class="btn btn-outline-primary btn-sm me-1" @click="viewStudentProfile(row.id)">View Profile</button>
              <select v-model="row.status" class="form-select form-select-sm d-inline w-auto me-1">
                <option>applied</option>
                <option>shortlisted</option>
                <option>selected</option>
                <option>rejected</option>
              </select>
              <button class="btn btn-success btn-sm" @click="openStatusModal(row.id, row.status, row.student)">Update</button>
            </template>
          </ApplicationTable>
        </div>
      </div>

      <div class="col-md-5">
        <h4>Create Drive</h4>
        <CreateDriveForm ref="driveFormRef" @submit="createDrive" />
        <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success mt-2">{{ success }}</div>
      </div>
    </div>

    <div class="modal" :class="{ show: showStatusModal }" :style="{ display: showStatusModal ? 'block' : 'none' }">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Update Application Status</h5>
            <button type="button" class="btn-close" @click="showStatusModal = false"></button>
          </div>
          <div class="modal-body">
            <p><strong>Student:</strong> {{ selectedStudentName }}</p>
            <div class="mb-3">
              <label class="form-label">Status</label>
              <select v-model="statusForm.status" class="form-select">
                <option>applied</option>
                <option>shortlisted</option>
                <option>selected</option>
                <option>rejected</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Interview Date <small class="text-muted">(optional)</small></label>
              <input v-model="statusForm.interview_date" type="date" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Feedback <small class="text-muted">(optional)</small></label>
              <textarea v-model="statusForm.feedback" class="form-control" rows="3" placeholder="e.g., Interview scheduled for May 27"></textarea>
            </div>
            <div v-if="statusForm.status === 'selected'">
              <div class="mb-3">
                <label class="form-label">Joining Date <small class="text-muted">(optional)</small></label>
                <input v-model="statusForm.joining_date" type="date" class="form-control" />
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showStatusModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="submitStatusUpdate">Update</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showStatusModal" class="modal-backdrop fade show" @click="showStatusModal = false"></div>

    <div v-if="showProfileModal" class="modal d-block" style="background-color: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Applicant Profile</h5>
            <button type="button" class="btn-close" @click="showProfileModal = false"></button>
          </div>
          <div v-if="studentLoading" class="modal-body text-center">
            <div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div>
          </div>
          <div v-else class="modal-body">
            <div v-if="studentProfile">
              <p><strong>Name:</strong> {{ studentProfile.name }}</p>
              <p><strong>Email:</strong> {{ studentProfile.email }}</p>
              <p><strong>Phone:</strong> {{ studentProfile.phone_number || 'N/A' }}</p>
              <p><strong>College:</strong> {{ studentProfile.college_name || 'N/A' }}</p>
              <p><strong>Degree:</strong> {{ studentProfile.degree || 'N/A' }}</p>
              <p><strong>CGPA:</strong> {{ studentProfile.cgpa || 'N/A' }}</p>
              <p><strong>Skills:</strong> {{ studentProfile.skills || 'N/A' }}</p>
              <p><strong>Experience:</strong></p>
              <p class="text-muted">{{ studentProfile.experience || 'N/A' }}</p>
              <p><strong>Application Status:</strong> {{ studentProfile.application?.status }}</p>
              <div class="mt-3">
                <button v-if="studentProfile.resume" class="btn btn-outline-primary btn-sm" @click="downloadResume(studentProfile.application.id)">Download Resume</button>
              </div>
            </div>
            <div v-else>
              <p class="text-muted">Profile not available.</p>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showProfileModal = false">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'
import ApplicationTable from '../components/ApplicationTable.vue'
import CreateDriveForm from '../components/CreateDriveForm.vue'

const driveFormRef = ref(null)
const company = ref({
  name: '',
  email: '',
  company_email: '',
  hr_contact: '',
  website: '',
  industry: '',
  location: '',
  approval_status: ''
})
const drives = ref([])
const applications = ref([])
const selectedDrive = ref(null)
const selectedDriveTitle = ref('')
const error = ref('')
const success = ref('')
const showStatusModal = ref(false)
const selectedApplicationId = ref(null)
const selectedStudentName = ref('')
const statusForm = ref({
  status: 'applied',
  interview_date: '',
  feedback: '',
  joining_date: ''
})

const totalDrives = computed(() => drives.value.length)
const totalApplicants = computed(() => drives.value.reduce((sum, d) => sum + d.total_applicants, 0))
const totalSelected = computed(() => drives.value.reduce((sum, d) => sum + d.approved_applicants, 0))
const avgApplicants = computed(() => totalDrives.value > 0 ? (totalApplicants.value / totalDrives.value).toFixed(1) : 0)

const fetchDashboard = async () => {
  try {
    const response = await api.get('/company/dashboard')
    company.value = response.data.company
    drives.value = response.data.drives
  } catch (e) {
    console.error('Failed to fetch dashboard:', e)
    error.value = e.response?.data?.msg || 'Failed to load dashboard'
  }
}

const viewApplications = async (driveId) => {
  selectedDrive.value = driveId
  const drive = drives.value.find(d => d.id === driveId)
  selectedDriveTitle.value = drive ? drive.job_title : ''
  applications.value = (await api.get(`/company/drives/${driveId}/applications`)).data
}

const isPastDeadline = (deadline) => {
  if (!deadline) return false
  const [year, month, day] = deadline.split('-').map(Number)
  const deadlineDate = new Date(year, month - 1, day)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  deadlineDate.setHours(0, 0, 0, 0)
  return deadlineDate < today
}

const getDriveStatusLabel = (drive) => {
  if (drive.status === 'closed') return 'Closed'
  if (isPastDeadline(drive.application_deadline)) return 'Drive Ended'
  if (drive.status === 'pending') return 'Pending Approval'
  return 'Open'
}

const getDriveStatusBadgeClass = (drive) => {
  if (drive.status === 'closed') return 'bg-secondary'
  if (isPastDeadline(drive.application_deadline)) return 'bg-dark'
  if (drive.status === 'pending') return 'bg-warning'
  return 'bg-success'
}

const closeDrive = async (driveId) => {
  try {
    await api.put(`/company/drives/${driveId}/status`, { status: 'closed' })
    success.value = 'Drive closed successfully.'
    await fetchDashboard()
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to close drive.'
    setTimeout(() => { error.value = '' }, 3000)
  }
}

const openStatusModal = (appId, status, studentName) => {
  selectedApplicationId.value = appId
  selectedStudentName.value = studentName
  statusForm.value = {
    status: status,
    interview_date: '',
    feedback: '',
    joining_date: ''
  }
  showStatusModal.value = true
}

const submitStatusUpdate = async () => {
  try {
    await api.post(`/company/applications/${selectedApplicationId.value}/status`, {
      status: statusForm.value.status,
      interview_date: statusForm.value.interview_date,
      feedback: statusForm.value.feedback,
      joining_date: statusForm.value.joining_date
    })
    success.value = 'Application status updated and email sent!'
    showStatusModal.value = false
    setTimeout(() => { success.value = '' }, 3000)
    if (selectedDrive.value) await viewApplications(selectedDrive.value)
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to update status'
    setTimeout(() => { error.value = '' }, 3000)
  }
}

const studentProfile = ref(null)
const studentLoading = ref(false)
const showProfileModal = ref(false)

const viewStudentProfile = async (applicationId) => {
  studentLoading.value = true
  showProfileModal.value = true
  try {
    const r = await api.get(`/company/applications/${applicationId}/student`)
    studentProfile.value = r.data
  } catch (e) {
    console.error('Failed to load applicant profile:', e)
    studentProfile.value = null
  } finally {
    studentLoading.value = false
  }
}

const downloadResume = async (applicationId) => {
  try {
    const r = await api.get(`/company/applications/${applicationId}/student_resume`, { responseType: 'blob' })
    const blob = new Blob([r.data])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = studentProfile.value?.resume || 'resume'
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Failed to download resume:', e)
    alert(e.response?.data?.msg || 'Failed to download resume')
  }
}

const createDrive = async (form) => {
  error.value = ''
  success.value = ''
  try {
    const formData = { ...form }
    await api.post('/company/drives', formData)
    success.value = 'Drive created! Pending admin approval.'
    await fetchDashboard()
    driveFormRef.value?.resetForm()
    setTimeout(() => { success.value = '' }, 3000)
  } catch (e) {
    error.value = e.response?.data?.msg || 'Failed to create drive.'
    setTimeout(() => { error.value = '' }, 3000)
  }
}

onMounted(fetchDashboard)
</script>

