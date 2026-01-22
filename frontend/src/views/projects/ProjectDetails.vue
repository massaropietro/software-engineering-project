<template>
    <div v-if="loading">Loading...</div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <div v-else-if="project">
      <div v-if="project.file_structure" class="card">
          <Tree :value="treeNodes" class="w-full"></Tree>
      </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';
import Tree from 'primevue/tree';
import { transformToTreeNode } from '@/utils/treeTransforms';

const props = defineProps({
  projectId: {
    type: String,
    required: true
  }
});

const {
  data: project,
  loading,
  error,
  execute: fetchProject
} = useApi(() => ProjectService.getProject(props.projectId));

const treeNodes = computed(() => {
  if (!project.value || !project.value.file_structure) return [];
  return transformToTreeNode(project.value.file_structure);
});

onMounted(() => {
  fetchProject();
});
</script>
