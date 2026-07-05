<template>
  <div v-if="visible" class="modal d-block" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Drive Details</h5>
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
              <p><strong>Job Title:</strong> {{ drive.job_title }}</p>
              <p><strong>Company:</strong> {{ drive.company_name }}</p>
              <p><strong>Company Email:</strong> {{ drive.company_email || 'N/A' }}</p>
              <p><strong>Salary:</strong> {{ drive.salary || 'N/A' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Location:</strong> {{ drive.location || 'N/A' }}</p>
              <p><strong>Positions:</strong> {{ drive.num_positions }}</p>
              <p><strong>Status:</strong> <span class="badge" :class="drive.is_closed ? 'bg-secondary' : (drive.is_ended ? 'bg-dark' : 'bg-info')">{{ drive.status_label || drive.status }}</span></p>
              <p><strong>Deadline:</strong> {{ drive.application_deadline || 'N/A' }}</p>
            </div>
          </div>
          <div v-if="drive.job_description" class="mb-3">
            <p><strong>Job Description:</strong></p>
            <p class="text-muted">{{ drive.job_description }}</p>
          </div>
          <div v-if="drive.min_cgpa || drive.min_experience_years || drive.min_year || drive.skills_required || drive.notes || drive.eligibility_criteria" class="mb-3">
            <p><strong>Eligibility Criteria:</strong></p>
            <ul class="text-muted mb-0">
              <li v-if="drive.min_cgpa">CGPA &ge; {{ drive.min_cgpa }}</li>
              <li v-if="drive.min_experience_years">Experience &ge; {{ drive.min_experience_years }} years</li>
              <li v-if="drive.min_year">Study Year &ge; {{ drive.min_year }}</li>
              <li v-if="drive.skills_required">Skills: {{ drive.skills_required }}</li>
              <li v-if="drive.notes">Notes: {{ drive.notes }}</li>
              <li v-if="drive.eligibility_criteria && !drive.min_cgpa && !drive.min_experience_years && !drive.min_year && !drive.skills_required && !drive.notes">{{ drive.eligibility_criteria }}</li>
            </ul>
          </div>
          <p><strong>Posted:</strong> {{ drive.created_at }}</p>
          <div v-if="drive.applications_count > 0" class="mt-4">
            <h6>Applications ({{ drive.applications_count }})</h6>
            <table class="table table-sm table-bordered">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Email</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in drive.applications" :key="app.id">
                  <td>{{ app.student }}</td>
                  <td>{{ app.student_email }}</td>
                  <td><span class="badge bg-secondary">{{ app.status }}</span></td>
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
  driveId: {
    type: Number,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  },
  apiBase: {
    type: String,
    default: '/drives'
  }
})

const emit = defineEmits(['close'])

const drive = ref({})
const loading = ref(false)

const close = () => {
  emit('close')
}

watch(() => props.visible, async (newVal) => {
  if (newVal && props.driveId) {
    loading.value = true
    try {
      const response = await api.get(`${props.apiBase}/${props.driveId}`)
      drive.value = response.data
    } catch (e) {
      console.error('Failed to load drive details:', e)
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
