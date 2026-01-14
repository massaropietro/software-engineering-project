import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useProjectsStore = defineStore('projects', () => {
  const projects = ref([]);

  return {
    projects
  };
})
