<template>
  <table class="table table-bordered table-sm">
    <thead><tr><th>Name</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
      <tr v-for="c in companies" :key="c.id">
        <td>{{ c.name }}</td>
        <td>{{ c.status }}</td>
        <td>
          <button v-if="c.status==='pending'" class="btn btn-success btn-sm me-1" @click="$emit('approve', c.id)">Approve</button>
          <button v-if="c.status==='pending'" class="btn btn-danger btn-sm me-1" @click="$emit('reject', c.id)">Reject</button>
          <button v-if="!c.is_blacklisted" class="btn btn-warning btn-sm" @click="$emit('blacklist', c.id)">Blacklist</button>
          <button v-else class="btn btn-success btn-sm" @click="$emit('unblacklist', c.id)">Unblacklist</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup>
const props = defineProps({ companies: Array })
</script>
