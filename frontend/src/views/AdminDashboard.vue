<template>
  <HeaderBar />
  <div class="container-fluid mt-4">
    <h2>Admin Dashboard</h2>

    <div class="row mt-4 mb-4">
      <div class="col-md-3">
        <div class="card text-bg-primary mb-3">
          <div class="card-body">
            <h5 class="card-title">Students</h5>
            <p class="card-text fs-3">{{ summary.students }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-success mb-3">
          <div class="card-body">
            <h5 class="card-title">Companies</h5>
            <p class="card-text fs-3">{{ summary.companies }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-warning mb-3">
          <div class="card-body">
            <h5 class="card-title">Drives</h5>
            <p class="card-text fs-3">{{ summary.drives }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-info mb-3">
          <div class="card-body">
            <h5 class="card-title">Applications</h5>
            <p class="card-text fs-3">{{ summary.applications }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4 mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-body">
            <div class="input-group input-group-lg">
              <span class="input-group-text">🔍</span>
              <input 
                v-model="searchQuery" 
                type="text" 
                class="form-control" 
                placeholder="Search students, companies, drives, or applications..."
                @input="performSearch"
              />
            </div>
            <div v-if="showResults && searchQuery.length > 0" class="mt-3">
              <div v-if="searchLoading" class="text-center text-muted">
                <div class="spinner-border spinner-border-sm"></div> Searching...
              </div>
              <div v-else>
                <div v-if="searchResults.students.length > 0" class="mb-3">
                  <h6 class="text-muted">Students</h6>
                  <div v-for="student in searchResults.students" :key="`student-${student.id}`" class="d-flex justify-content-between align-items-center p-2 border-bottom">
                    <div>
                      <strong>{{ student.name }}</strong><br/>
                      <small class="text-muted">{{ student.email }}</small>
                    </div>
                    <button class="btn btn-sm btn-primary" @click="openStudentModal(student.id)">View</button>
                  </div>
                </div>
                <div v-if="searchResults.companies.length > 0" class="mb-3">
                  <h6 class="text-muted">Companies</h6>
                  <div v-for="company in searchResults.companies" :key="`company-${company.id}`" class="d-flex justify-content-between align-items-center p-2 border-bottom">
                    <div>
                      <strong>{{ company.name }}</strong><br/>
                      <small class="text-muted">{{ company.industry || 'N/A' }}</small>
                    </div>
                    <button class="btn btn-sm btn-success" @click="openCompanyModal(company.id)">View</button>
                  </div>
                </div>
                <div v-if="searchResults.drives.length > 0" class="mb-3">
                  <h6 class="text-muted">Drives</h6>
                  <div v-for="drive in searchResults.drives" :key="`drive-${drive.id}`" class="d-flex justify-content-between align-items-center p-2 border-bottom">
                    <div>
                      <strong>{{ drive.title }}</strong><br/>
                      <small class="text-muted">{{ drive.company }}</small>
                    </div>
                    <button class="btn btn-sm btn-warning" @click="openDriveModal(drive.id)">View</button>
                  </div>
                </div>
                <div v-if="searchResults.applications.length > 0" class="mb-3">
                  <h6 class="text-muted">Applications</h6>
                  <div v-for="app in searchResults.applications" :key="`app-${app.id}`" class="d-flex justify-content-between align-items-center p-2 border-bottom">
                    <div>
                      <strong>{{ app.student }}</strong> → {{ app.company }}<br/>
                      <small class="text-muted">{{ app.drive }}</small>
                    </div>
                    <button class="btn btn-sm btn-info" @click="openApplicationModal(app.id)">View</button>
                  </div>
                </div>
                <div v-if="Object.values(searchResults).every(arr => arr.length === 0)" class="text-center text-muted p-3">
                  No results found
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-md-12">
        <ul class="nav nav-tabs" role="tablist">
          <li class="nav-item" role="presentation">
            <button class="nav-link active" id="students-tab" type="button" role="tab" aria-selected="true" @click="activeTab = 'students'">Students</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="companies-tab" type="button" role="tab" aria-selected="false" @click="activeTab = 'companies'">Companies</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="drives-tab" type="button" role="tab" aria-selected="false" @click="activeTab = 'drives'">Drives</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="applications-tab" type="button" role="tab" aria-selected="false" @click="activeTab = 'applications'">Applications</button>
          </li>
          <li class="nav-item" role="presentation">
            <button class="nav-link" id="placements-tab" type="button" role="tab" aria-selected="false" @click="activeTab = 'placements'">Placements</button>
          </li>
        </ul>

        <div v-show="activeTab === 'students'" class="tab-pane fade show active mt-3">
          <table class="table table-bordered table-sm">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Department</th>
                <th>Status</th>
                <th>Blacklisted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="students.length === 0">
                <td colspan="6" class="text-center text-muted">No students found</td>
              </tr>
              <tr v-for="student in students" :key="student.id">
                <td>{{ student.name }}</td>
                <td>{{ student.email }}</td>
                <td>{{ student.department || 'N/A' }}</td>
                <td><span class="badge" :class="student.is_active ? 'bg-success' : 'bg-danger'">{{ student.is_active ? 'Active' : 'Inactive' }}</span></td>
                <td><span class="badge" :class="student.is_blacklisted ? 'bg-danger' : 'bg-success'">{{ student.is_blacklisted ? 'Yes' : 'No' }}</span></td>
                <td>
                  <button class="btn btn-primary btn-sm me-1" @click="openStudentModal(student.id)">View</button>
                  <button v-if="!student.is_blacklisted" class="btn btn-danger btn-sm" @click="blacklistStudent(student.id)">Blacklist</button>
                  <button v-else class="btn btn-warning btn-sm" @click="unblacklistStudent(student.id)">Unblacklist</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-show="activeTab === 'companies'" class="tab-pane fade show mt-3">
          <table class="table table-bordered table-sm">
            <thead>
              <tr>
                <th>Name</th>
                <th>Industry</th>
                <th>Status</th>
                <th>Blacklisted</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="companies.length === 0">
                <td colspan="5" class="text-center text-muted">No companies found</td>
              </tr>
              <tr v-for="company in companies" :key="company.id">
                <td>{{ company.name }}</td>
                <td>{{ company.industry || 'N/A' }}</td>
                <td>
                  <span class="badge" :class="company.status === 'approved' ? 'bg-success' : company.status === 'pending' ? 'bg-warning' : 'bg-danger'">
                    {{ company.status }}
                  </span>
                </td>
                <td><span class="badge" :class="company.is_blacklisted ? 'bg-danger' : 'bg-success'">{{ company.is_blacklisted ? 'Yes' : 'No' }}</span></td>
                <td>
                  <button class="btn btn-primary btn-sm me-1" @click="openCompanyModal(company.id)">View</button>
                  <button v-if="company.status === 'pending'" class="btn btn-success btn-sm me-1" @click="approveCompany(company.id)">Approve</button>
                  <button v-if="company.status === 'pending'" class="btn btn-danger btn-sm me-1" @click="rejectCompany(company.id)">Reject</button>
                  <button v-if="!company.is_blacklisted" class="btn btn-danger btn-sm" @click="blacklistCompany(company.id)">Blacklist</button>
                  <button v-else class="btn btn-warning btn-sm" @click="unblacklistCompany(company.id)">Unblacklist</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-show="activeTab === 'drives'" class="tab-pane fade show mt-3">
          <table class="table table-bordered table-sm">
            <thead>
              <tr>
                <th>Title</th>
                <th>Company</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="drives.length === 0">
                <td colspan="4" class="text-center text-muted">No drives found</td>
              </tr>
              <tr v-for="drive in drives" :key="drive.id">
                <td>{{ drive.title }}</td>
                <td>{{ drive.company }}</td>
                <td>
                  <span class="badge" :class="drive.status === 'approved' ? 'bg-success' : drive.status === 'pending' ? 'bg-warning' : 'bg-danger'">
                    {{ drive.status }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-primary btn-sm me-1" @click="openDriveModal(drive.id)">View</button>
                  <button v-if="drive.status === 'pending'" class="btn btn-success btn-sm me-1" @click="approveDrive(drive.id)">Approve</button>
                  <button v-if="drive.status === 'pending'" class="btn btn-danger btn-sm" @click="rejectDrive(drive.id)">Reject</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-show="activeTab === 'applications'" class="tab-pane fade show mt-3">
          <table class="table table-bordered table-sm">
            <thead>
              <tr>
                <th>Student</th>
                <th>Email</th>
                <th>Company</th>
                <th>Drive</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="applications.length === 0">
                <td colspan="7" class="text-center text-muted">No applications found</td>
              </tr>
              <tr v-for="app in applications" :key="app.id">
                <td>{{ app.student }}</td>
                <td>{{ app.student_email }}</td>
                <td>{{ app.company }}</td>
                <td>{{ app.drive }}</td>
                <td><span class="badge bg-info">{{ app.status }}</span></td>
                <td>{{ app.date }}</td>
                <td>
                  <button class="btn btn-primary btn-sm" @click="openApplicationModal(app.id)">View</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-show="activeTab === 'placements'" class="tab-pane fade show mt-3">
          <table class="table table-bordered table-sm">
            <thead>
              <tr>
                <th>Student</th>
                <th>Email</th>
                <th>Company</th>
                <th>Drive</th>
                <th>Salary</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="placements.length === 0">
                <td colspan="7" class="text-center text-muted">No placements found</td>
              </tr>
              <tr v-for="p in placements" :key="p.id">
                <td>{{ p.student }}</td>
                <td>{{ p.student_email }}</td>
                <td>{{ p.company }}</td>
                <td>{{ p.drive }}</td>
                <td>{{ p.salary || 'N/A' }}</td>
                <td>{{ p.date }}</td>
                <td>
                  <button class="btn btn-primary btn-sm" @click="openApplicationModal(p.id)">View</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <StudentDetailModal :student-id="selectedStudentId" :visible="showStudentModal" @close="showStudentModal = false" />
  <CompanyDetailModal :company-id="selectedCompanyId" :visible="showCompanyModal" @close="showCompanyModal = false" />
  <DriveDetailModal :drive-id="selectedDriveId" api-base="/admin/drives" :visible="showDriveModal" @close="showDriveModal = false" />
  <ApplicationDetailModal :application-id="selectedApplicationId" :visible="showApplicationModal" @close="showApplicationModal = false" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../utils/api'
import HeaderBar from '../components/HeaderBar.vue'
import StudentDetailModal from '../components/StudentDetailModal.vue'
import CompanyDetailModal from '../components/CompanyDetailModal.vue'
import DriveDetailModal from '../components/DriveDetailModal.vue'
import ApplicationDetailModal from '../components/ApplicationDetailModal.vue'

const activeTab = ref('students')
const summary = ref({ students: 0, companies: 0, drives: 0, applications: 0 })
const students = ref([])
const companies = ref([])
const drives = ref([])
const applications = ref([])
const placements = ref([])
const searchQuery = ref('')
const showResults = ref(false)
const searchLoading = ref(false)
const searchResults = ref({ students: [], companies: [], drives: [], applications: [] })

const selectedStudentId = ref(null)
const selectedCompanyId = ref(null)
const selectedDriveId = ref(null)
const selectedApplicationId = ref(null)

const showStudentModal = ref(false)
const showCompanyModal = ref(false)
const showDriveModal = ref(false)
const showApplicationModal = ref(false)

const openStudentModal = (id) => {
  selectedStudentId.value = id
  showStudentModal.value = true
  showResults.value = false
}

const openCompanyModal = (id) => {
  selectedCompanyId.value = id
  showCompanyModal.value = true
  showResults.value = false
}

const openDriveModal = (id) => {
  selectedDriveId.value = id
  showDriveModal.value = true
  showResults.value = false
}

const openApplicationModal = (id) => {
  selectedApplicationId.value = id
  showApplicationModal.value = true
  showResults.value = false
}

let searchTimeout
const performSearch = () => {
  clearTimeout(searchTimeout)
  if (searchQuery.value.length === 0) {
    showResults.value = false
    return
  }

  searchLoading.value = true
  searchTimeout = setTimeout(async () => {
    try {
      const response = await api.get('/admin/search', {
        params: { q: searchQuery.value }
      })
      searchResults.value = response.data
      showResults.value = true
    } catch (e) {
      console.error('Search failed:', e)
    } finally {
      searchLoading.value = false
    }
  }, 300)
}

const fetchSummary = async () => {
  try {
    const response = await api.get('/admin/summary')
    const data = response.data || {}
    if (typeof data.students === 'number' && typeof data.companies === 'number' && typeof data.drives === 'number' && typeof data.applications === 'number') {
      summary.value = data
    } else {
      const [sRes, cRes, dRes, aRes] = await Promise.all([
        api.get('/admin/students'),
        api.get('/admin/companies'),
        api.get('/admin/drives'),
        api.get('/admin/applications')
      ])
      summary.value = {
        students: Array.isArray(sRes.data) ? sRes.data.length : 0,
        companies: Array.isArray(cRes.data) ? cRes.data.length : 0,
        drives: Array.isArray(dRes.data.items) ? dRes.data.items.length : 0,
        applications: Array.isArray(aRes.data.items) ? aRes.data.items.length : 0,
        placements: data.placements || 0,
        avg_placement_salary: data.avg_placement_salary || null
      }
    }
  } catch (e) {
    console.error('Failed to fetch summary:', e)
  }
}

const fetchStudents = async () => {
  try {
    const response = await api.get('/admin/students')
    students.value = response.data
  } catch (e) {
    console.error('Failed to fetch students:', e)
  }
}

const fetchCompanies = async () => {
  try {
    const response = await api.get('/admin/companies')
    companies.value = response.data
  } catch (e) {
    console.error('Failed to fetch companies:', e)
  }
}

const fetchDrives = async () => {
  try {
    const response = await api.get('/admin/drives')
    drives.value = response.data.items
  } catch (e) {
    console.error('Failed to fetch drives:', e)
  }
}

const fetchApplications = async () => {
  try {
    const response = await api.get('/admin/applications')
    applications.value = response.data.items
  } catch (e) {
    console.error('Failed to fetch applications:', e)
  }
}

const fetchPlacements = async () => {
  try {
    const r = await api.get('/admin/placements')
    placements.value = Array.isArray(r.data && r.data.items) ? r.data.items : []
    if ((!placements.value || placements.value.length === 0) && Array.isArray(applications.value) && applications.value.length > 0) {
      const selected = applications.value.filter(a => a.status === 'selected')
      if (selected.length > 0) {
        placements.value = selected.map(a => ({
          id: a.id,
          student: a.student,
          student_email: a.student_email,
          company: a.company,
          drive: a.drive,
          salary: a.salary || 'N/A',
          date: a.date
        }))
      }
    }
  } catch (e) {
    console.error('Failed to fetch placements:', e)
  }
}

const formatSalary = (val) => {
  if (val === null || val === undefined) return 'N/A'
  try { return Math.round(val).toString() } catch (e) { return String(val) }
}

const approveCompany = async (id) => {
  try {
    await api.post(`/admin/companies/${id}/approve`)
    await fetchCompanies()
  } catch (e) {
    console.error('Failed to approve company:', e)
  }
}

const rejectCompany = async (id) => {
  try {
    await api.post(`/admin/companies/${id}/reject`)
    await fetchCompanies()
  } catch (e) {
    console.error('Failed to reject company:', e)
  }
}

const blacklistCompany = async (id) => {
  try {
    await api.post(`/admin/companies/${id}/blacklist`)
    await fetchCompanies()
  } catch (e) {
    console.error('Failed to blacklist company:', e)
  }
}

const unblacklistCompany = async (id) => {
  try {
    await api.post(`/admin/companies/${id}/unblacklist`)
    await fetchCompanies()
  } catch (e) {
    console.error('Failed to unblacklist company:', e)
  }
}

const blacklistStudent = async (id) => {
  try {
    await api.post(`/admin/students/${id}/blacklist`)
    await fetchStudents()
  } catch (e) {
    console.error('Failed to blacklist student:', e)
  }
}

const unblacklistStudent = async (id) => {
  try {
    await api.post(`/admin/students/${id}/unblacklist`)
    await fetchStudents()
  } catch (e) {
    console.error('Failed to unblacklist student:', e)
  }
}

const approveDrive = async (id) => {
  try {
    await api.post(`/admin/drives/${id}/approve`)
    await fetchDrives()
  } catch (e) {
    console.error('Failed to approve drive:', e)
  }
}

const rejectDrive = async (id) => {
  try {
    await api.post(`/admin/drives/${id}/reject`)
    await fetchDrives()
  } catch (e) {
    console.error('Failed to reject drive:', e)
  }
}

onMounted(async () => {
  await fetchSummary()
  await fetchStudents()
  await fetchCompanies()
  await fetchDrives()
  await fetchApplications()
  await fetchPlacements()
})
</script>
