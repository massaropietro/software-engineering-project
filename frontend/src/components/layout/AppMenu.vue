<template>
  <ul class="list-none m-0 flex flex-col gap-1 p-0">
    <template v-for="(item, i) in model" :key="i">
      <AppMenuItem :item="item" :index="i" :root="true" />
    </template>
  </ul>
</template>

<script setup>
import AppMenuItem from './AppMenuItem.vue'

defineProps({
  model: {
    type: Array,
    default: () => [],
  },
})
</script>
