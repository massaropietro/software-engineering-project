<template>
     <div v-if="loading" class="flex justify-center items-center h-40">
        <ProgressSpinner/>
    </div>
    <div v-else-if="error">Error: {{ error.message }}</div>
    <div v-else-if="project">
      <div v-if="project.file_structure" class="card">
        <h3 class="text-xl font-bold mb-3 mt-6 text-surface-900 dark:text-surface-0">
          {{ $t('project_analysis.project_structure') }}
        </h3>
          <Tree :value="treeNodes" class="w-full"></Tree>
          <AnalysisHistory :projectId="projectId" />
      </div>
  </div>
</template>

<script setup>
import { onMounted, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';
import Tree from 'primevue/tree';
import { transformToTreeNode } from '@/utils/treeTransforms';
import AnalysisHistory from "@/components/analyses/AnalysisHistory.vue";

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
