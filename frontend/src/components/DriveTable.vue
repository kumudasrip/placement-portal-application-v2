<template>
  <table class="table table-bordered table-sm">
    <thead><tr><th>Title</th><th>Company</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
      <tr v-for="d in drives" :key="d.id">
        <td>{{ d.title }}</td>
        <td>{{ d.company }}</td>
        <td>{{ d.status }}</td>
        <td>
          <button v-if="d.status==='pending'" class="btn btn-success btn-sm me-1" @click="$emit('approve', d.id)">Approve</button>
          <button v-if="d.status==='pending'" class="btn btn-danger btn-sm" @click="$emit('reject', d.id)">Reject</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup>
const props = defineProps({ drives: Array })
</script>
