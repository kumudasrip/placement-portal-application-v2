<template>
  <div v-if="visible" class="modal d-block" style="background-color: rgba(0,0,0,0.5);">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Application Details</h5>
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
              <p><strong>Student:</strong> {{ application.student_name }}</p>
              <p><strong>Email:</strong> {{ application.student_email }}</p>
              <p><strong>Phone:</strong> {{ application.student_phone_number || 'N/A' }}</p>
              <p><strong>College:</strong> {{ application.student_college_name || 'N/A' }}</p>
              <p><strong>Degree:</strong> {{ application.student_degree || 'N/A' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Department:</strong> {{ application.student_department || 'N/A' }}</p>
              <p><strong>Year:</strong> {{ application.student_year || 'N/A' }}</p>
              <p><strong>CGPA:</strong> {{ application.student_cgpa || 'N/A' }}</p>
              <p><strong>Skills:</strong> {{ application.student_skills || 'N/A' }}</p>
            </div>
          </div>
          <div class="row mb-3">
            <div class="col-md-12">
              <p><strong>Experience:</strong></p>
              <p class="text-muted">{{ application.student_experience || 'N/A' }}</p>
            </div>
          </div>
          <hr />
          <div class="row mb-3">
            <div class="col-md-6">
              <p><strong>Drive:</strong> {{ application.drive_title }}</p>
              <p><strong>Description:</strong></p>
              <p class="text-muted">{{ application.drive_description || 'N/A' }}</p>
              <p><strong>Salary:</strong> {{ application.salary || 'N/A' }}</p>
            </div>
            <div class="col-md-6">
              <p><strong>Company:</strong> {{ application.company_name }}</p>
              <p><strong>Company Email:</strong> {{ application.company_email || 'N/A' }}</p>
              <p><strong>Location:</strong> {{ application.location || 'N/A' }}</p>
              <p><strong>Deadline:</strong> {{ application.application_deadline || 'N/A' }}</p>
            </div>
          </div>
          <div v-if="application.eligibility_criteria || application.eligibility_skills || application.eligibility_min_cgpa || application.eligibility_min_experience_years || application.eligibility_min_year" class="mb-3 p-3 bg-light rounded">
            <p><strong>Eligibility</strong></p>
            <ul class="mb-0">
              <li v-if="application.eligibility_min_cgpa">CGPA &ge; {{ application.eligibility_min_cgpa }}</li>
              <li v-if="application.eligibility_min_experience_years">Experience &ge; {{ application.eligibility_min_experience_years }} years</li>
              <li v-if="application.eligibility_min_year">Year &ge; {{ application.eligibility_min_year }}</li>
              <li v-if="application.eligibility_skills">Skills: {{ application.eligibility_skills.join(', ') }}</li>
              <li v-if="application.eligibility_notes">Notes: {{ application.eligibility_notes }}</li>
              <li v-if="application.eligibility_criteria && !application.eligibility_min_cgpa && !application.eligibility_min_experience_years && !application.eligibility_min_year && !application.eligibility_skills && !application.eligibility_notes">{{ application.eligibility_criteria }}</li>
            </ul>
          </div>
          <div class="row mb-3">
            <div class="col-md-6">
              <p><strong>Status:</strong> <span class="badge bg-info">{{ application.status }}</span></p>
            </div>
            <div class="col-md-6">
              <p><strong>Application Date:</strong> {{ application.application_date }}</p>
            </div>
          </div>
          <div v-if="application.feedback" class="mt-3 p-3 bg-light rounded">
            <p><strong>Feedback:</strong></p>
            <p>{{ application.feedback }}</p>
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
  applicationId: {
    type: Number,
    default: null
  },
  visible: {
    type: Boolean,
    default: false
  },
  apiBase: {
    type: String,
    default: '/admin/applications'
  }
})

const emit = defineEmits(['close'])

const application = ref({})
const loading = ref(false)

const close = () => {
  emit('close')
}

watch(() => props.visible, async (newVal) => {
  if (newVal && props.applicationId) {
    loading.value = true
    try {
      const response = await api.get(`${props.apiBase}/${props.applicationId}`)
      application.value = response.data
    } catch (e) {
      console.error('Failed to load application details:', e)
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
