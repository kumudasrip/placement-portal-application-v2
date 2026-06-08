<template>
  <div v-if="visible" class="modal d-block" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Company Details</h5>
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
              <p><strong>Company Name:</strong> {{ company.name }}</p>
              <p><strong>Email:</strong> {{ company.email }}</p>
              <p><strong>Company Email:</strong> {{ company.company_email || 'N/A' }}</p>
              <p><strong>Industry:</strong> {{ company.industry || 'N/A' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Location:</strong> {{ company.location || 'N/A' }}</p>
              <p><strong>HR Contact:</strong> {{ company.hr_contact || 'N/A' }}</p>
              <p><strong>Website:</strong> <a v-if="company.website" :href="company.website" target="_blank">{{ company.website }}</a><span v-else>N/A</span></p>
              <p><strong>Registration #:</strong> {{ company.registration_number || 'N/A' }}</p>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-md-6">
              <p><strong>Status:</strong>
                <span class="badge" :class="company.approval_status === 'approved' ? 'bg-success' : company.approval_status === 'pending' ? 'bg-warning' : 'bg-danger'">
                  {{ company.approval_status }}
                </span>
              </p>
            </div>
            <div class="col-md-6">
              <p><strong>Active:</strong>
                <span class="badge" :class="company.is_active ? 'bg-success' : 'bg-danger'">
                  {{ company.is_active ? 'Yes' : 'No' }}
                </span>
              </p>
            </div>
          </div>
          <p><strong>Joined:</strong> {{ company.created_at }}</p>
          <div v-if="company.drives_count > 0" class="mt-4">
            <h6>Active Drives ({{ company.drives_count }})</h6>
            <table class="table table-sm table-bordered">
              <thead>
                <tr>
                  <th>Job Title</th>
                  <th>Status</th>
                  <th>Applicants</th>
                  <th>Deadline</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="drive in company.drives" :key="drive.id">
                  <td>{{ drive.job_title }}</td>
                  <td><span class="badge bg-info">{{ drive.status }}</span></td>
                  <td>{{ drive.applicants }}</td>
                  <td>{{ drive.deadline || 'N/A' }}</td>
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
  companyId: {
    type: Number,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  }
  ,
  apiBase: {
    type: String,
    default: '/admin/companies'
  }
})

const emit = defineEmits(['close'])

const company = ref({})
const loading = ref(false)

const close = () => {
  emit('close')
}

watch(() => props.visible, async (newVal) => {
  if (newVal && props.companyId) {
    loading.value = true
    try {
      const response = await api.get(`${props.apiBase}/${props.companyId}`)
      company.value = response.data
    } catch (e) {
      console.error('Failed to load company details:', e)
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
