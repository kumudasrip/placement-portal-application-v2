<template>
  <table class="table table-bordered table-sm">
    <thead><tr><th>Name</th><th>Department</th><th>Actions</th></tr></thead>
    <tbody>
      <tr v-for="s in students" :key="s.id">
        <td>{{ s.name }}</td>
        <td>{{ s.department }}</td>
        <td>
          <button v-if="!s.is_blacklisted" class="btn btn-warning btn-sm" @click="$emit('blacklist', s.id)">Blacklist</button>
          <button v-else class="btn btn-success btn-sm" @click="$emit('unblacklist', s.id)">Unblacklist</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup>
const props = defineProps({ students: Array })
</script>
