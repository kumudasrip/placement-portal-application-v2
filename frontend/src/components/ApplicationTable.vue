<template>
  <table class="table table-bordered table-sm">
    <thead>
      <tr>
        <th v-for="col in columns" :key="col">{{ col }}</th>
        <th v-if="showActions">Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="row in rows" :key="row.id">
        <td v-for="col in columns" :key="col">{{ row[col.toLowerCase()] }}</td>
        <td v-if="showActions">
          <slot name="actions" :row="row"></slot>
        </td>
      </tr>
    </tbody>
  </table>
</template>
<script setup>
const props = defineProps({
  columns: Array,
  rows: Array,
  showActions: Boolean
})
</script>
