<template>
  <form @submit.prevent="$emit('submit', form)">
    <div class="mb-2">
      <label class="form-label">Job Title</label>
      <input v-model="form.job_title" class="form-control" required />
    </div>
    <div class="mb-2">
      <label class="form-label">Job Description</label>
      <textarea v-model="form.job_description" class="form-control" required></textarea>
    </div>
    <div class="row">
      <div class="col-md-4 mb-2">
        <label class="form-label">Minimum CGPA</label>
        <input v-model.number="form.min_cgpa" type="number" step="0.01" min="0" class="form-control" />
      </div>
      <div class="col-md-4 mb-2">
        <label class="form-label">Minimum Experience (years)</label>
        <input v-model.number="form.min_experience_years" type="number" min="0" class="form-control" />
      </div>
      <div class="col-md-4 mb-2">
        <label class="form-label">Minimum Study Year</label>
        <input v-model.number="form.min_year" type="number" min="0" class="form-control" />
      </div>
    </div>
    <div class="mb-2">
      <label class="form-label">Skills Required</label>
      <input v-model="form.skills_required" class="form-control" placeholder="e.g., Java, Python" />
    </div>
    <div class="mb-2">
      <label class="form-label">Additional Eligibility Notes</label>
      <input v-model="form.eligibility_notes" class="form-control" />
    </div>
    <div class="mb-2">
      <label class="form-label">Salary</label>
      <input v-model="form.salary" class="form-control" />
    </div>
    <div class="mb-2">
      <label class="form-label">Location</label>
      <input v-model="form.location" class="form-control" />
    </div>
    <div class="mb-2">
      <label class="form-label">Application Deadline</label>
      <input v-model="form.application_deadline" type="date" class="form-control" required />
    </div>
    <button class="btn btn-primary w-100" type="submit">Create Drive</button>
  </form>
</template>
<script setup>
import { reactive } from 'vue'
const form = reactive({
  job_title: '',
  job_description: '',
  min_cgpa: null,
  min_experience_years: null,
  min_year: null,
  skills_required: '',
  eligibility_notes: '',
  salary: '',
  location: '',
  application_deadline: ''
})

const resetForm = () => {
  form.job_title = ''
  form.job_description = ''
  form.min_cgpa = null
  form.min_experience_years = null
  form.min_year = null
  form.skills_required = ''
  form.eligibility_notes = ''
  form.salary = ''
  form.location = ''
  form.application_deadline = ''
}

defineExpose({ resetForm })
</script>
