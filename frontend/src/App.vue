<template>
  <Toast/>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { useLayout } from '@/composables/layout'
import Toast from "primevue/toast";

const { applyTheme } = useLayout()

onMounted(() => {
  applyTheme()
})
</script>
