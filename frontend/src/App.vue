<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useLayout } from '@/composables/layout'

const { applyTheme } = useLayout()

onMounted(() => {
  applyTheme()
})
</script>
