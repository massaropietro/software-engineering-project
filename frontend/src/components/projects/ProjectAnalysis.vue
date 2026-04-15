<template>
  <div class="w-full flex flex-col gap-6 p-4">
    <div v-if="loading" class="flex justify-center items-center h-40">
      <ProgressSpinner />
    </div>

    <Message v-else-if="error" severity="error" :closable="false">
      {{ typeof error === 'string' ? error : error?.message || 'Errore' }}
    </Message>

    <template v-else-if="projectData">
      <div class="flex flex-col gap-2">
        <h1 class="text-2xl font-bold">{{ projectData.name }}</h1>
        <p v-if="projectData.description" class="text-surface-500">
          {{ projectData.description }}
        </p>
      </div>

      <Message severity="info" :closable="false">
        <span v-html="$t('project_analysis.selection_limit_info', { max: MAX_ITEMS })"></span>
      </Message>

      <div class="rounded-xl border border-surface-200 dark:border-surface-700 p-4 bg-surface-0 dark:bg-surface-900">

        <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div class="flex flex-wrap gap-2 items-center">
            <Button
              icon="pi pi-plus"
              :label="$t('project_analysis.expand')"
              outlined
              size="small"
              @click="expandAll"
            />
            <Button
              icon="pi pi-minus"
              :label="$t('project_analysis.collapse')"
              outlined
              size="small"
              @click="collapseAll"
            />
            <Button
              icon="pi pi-times"
              :label="$t('project_analysis.deselect_all')"
              outlined
              severity="secondary"
              size="small"
              @click="deselectAll"
            />
            <Button
              :label="$t('project_analysis.run_analysis')"
              icon="pi pi-play"
              size="small"
              :disabled="currentTotalFiles === 0 || currentTotalFiles > MAX_ITEMS"
              :loading="runningAnalysis"
              @click="runAnalysis"
            />
          </div>

          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold">{{ $t('project_analysis.selected_files') }}:</span>
            <Tag
              :value="`${currentTotalFiles}/${MAX_ITEMS}`"
              :severity="currentTotalFiles > MAX_ITEMS ? 'danger' : 'primary'"
            />
          </div>
        </div>

        <div class="mb-4 bg-surface-50 dark:bg-surface-800 p-3 rounded-lg border border-surface-100 dark:border-surface-700 min-h-[3rem] flex items-center">
          <ul v-if="selectedPaths.length > 0" class="flex flex-wrap gap-2 w-full m-0 p-0 list-none">
            <li
              v-for="path in selectedPaths"
              :key="path"
              class="text-[11px] rounded bg-surface-200 dark:bg-surface-600 px-2 py-1 break-all flex-shrink-0"
            >
              {{ path }}
            </li>
          </ul>
          <p v-else class="text-sm text-surface-500 m-0">
            {{ $t('project_analysis.no_selection') }}
          </p>
        </div>

        <Tree
          v-model:selectionKeys="selectionKeys"
          v-model:expandedKeys="expandedKeys"
          :value="treeNodes"
          selectionMode="checkbox"
          :filter="true"
          filterMode="lenient"
          class="w-full border-none p-0 bg-transparent"
        >
          <template #default="slotProps">
            <div v-if="slotProps.node" class="flex items-center gap-2">
              <div class="flex flex-col">
                <span :class="{ 'text-surface-400 italic opacity-60': !slotProps.node.selectable }">
                  {{ slotProps.node.label }}
                </span>
                <small v-if="slotProps.node.data.type === 'directory'" class="text-[10px] opacity-50">
                  ({{ slotProps.node.data.totalFiles }} {{ $t('project_analysis.files_label') }})
                </small>
              </div>
            </div>
          </template>
        </Tree>
        <div ref="resultsContainerRef">
          <AnalysisResults v-if="activeAnalysisId" :analysisId="activeAnalysisId" />
      </div>
      </div>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import { useApi } from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';
import { transformToSelectableTreeNode, type TreeNode } from '@/utils/treeTransforms';
import AnalysisResults from "@/components/analyses/AnalysisResults.vue";
// UI Components
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import Tree from 'primevue/tree';
import Button from 'primevue/button';
import Tag from 'primevue/tag';

const { t } = useI18n();
const MAX_ITEMS = 10;
const route = useRoute();
const toast = useToast();
const secretToken = String(route.params.secretToken || '');

const { data: apiData, loading, error, execute: fetchProject } = useApi(() =>
  ProjectService.getProjectByToken(secretToken)
);

const projectData = computed(() => apiData.value?.data || apiData.value);

/**
 * TRASFORMAZIONE ALBERO
 * Utilizza il campo 'total_files' inviato dal backend per gestire il peso.
 */
const treeNodes = computed(() => {
  if (!projectData.value?.file_structure) return [];

  const baseNodes = transformToSelectableTreeNode(projectData.value.file_structure);

  const enrichNodes = (nodes: TreeNode[]): TreeNode[] => {
    return nodes.map(node => {
      // Directory: usa total_files dal backend | File: peso 1
      const totalFiles = node.data.type === 'directory' ? (node.data.total_files || 0) : 1;

      return {
        ...node,
        data: {
          ...node.data,
          totalFiles // mapping camelCase per consistenza frontend
        },
        // Selezionabile solo se il contenuto non eccede il limite massimo
        selectable: node.selectable && totalFiles <= MAX_ITEMS,
        children: node.children ? enrichNodes(node.children) : undefined
      };
    });
  };

  return enrichNodes(baseNodes);
});

// State
const selectionKeys = ref<Record<string, any>>({});
const expandedKeys = ref<Record<string, any>>({});
const previousValidSelectionKeys = ref<Record<string, any>>({});
const runningAnalysis = ref(false);
const activeAnalysisId = ref<string | null>(null);
const resultsContainerRef = ref<HTMLElement | null>(null);
/**
 * Conteggio dinamico basato sui pesi dei nodi selezionati
 */
const currentTotalFiles = computed(() => {
  let total = 0;
  const traverse = (nodes: TreeNode[]) => {
    for (const node of nodes) {
      const state = selectionKeys.value[node.key];
      if (state?.checked) {
        total += node.data.totalFiles;
      } else if (state?.partialChecked && node.children) {
        traverse(node.children);
      }
    }
  };
  traverse(treeNodes.value);
  return total;
});

/**
 * Estrazione dei path per la chiamata API
 */
const selectedPaths = computed(() => {
  const paths: string[] = [];
  const extract = (nodes: TreeNode[]) => {
    for (const node of nodes) {
      if (selectionKeys.value[node.key]?.checked) {
        paths.push(node.key);
      } else if (selectionKeys.value[node.key]?.partialChecked && node.children) {
        extract(node.children);
      }
    }
  };
  extract(treeNodes.value);
  return paths;
});

// Watcher per validazione limite (Rollback immediato)
watch(selectionKeys, (newVal) => {
  if (currentTotalFiles.value > MAX_ITEMS) {
    nextTick(() => {
      selectionKeys.value = JSON.parse(JSON.stringify(previousValidSelectionKeys.value));
    });
    toast.add({
      severity: 'warn',
      summary: t('project_analysis.limit_reached'),
      detail: t('project_analysis.limit_reached_detail', { max: MAX_ITEMS }),
      life: 3000
    });
  } else {
    previousValidSelectionKeys.value = JSON.parse(JSON.stringify(newVal));
  }
}, { deep: true });

// UI Actions
const expandAll = () => {
  const keys: Record<string, boolean> = {};
  const helper = (nodes: TreeNode[]) => {
    nodes.forEach(n => { if (n.children?.length) { keys[n.key] = true; helper(n.children); } });
  };
  helper(treeNodes.value);
  expandedKeys.value = keys;
};

const collapseAll = () => { expandedKeys.value = {}; };

const deselectAll = () => {
  selectionKeys.value = {};
};

const runAnalysis = async () => {
  if (!projectData.value || selectedPaths.value.length === 0) return;
  runningAnalysis.value = true;
  activeAnalysisId.value = null;

  try {
    const payload = {
      project: projectData.value.id,
      files: selectedPaths.value.map((file) => {
        const idx = file.indexOf('/src/');
        return idx !== -1 ? file.slice(idx + 1) : file;
      }),
      language: 'python',
      secret_token: secretToken
    };

    const res = await ProjectService.runAnalysisByToken(payload);
    activeAnalysisId.value = res.data.id;

    nextTick(() => {
      if (resultsContainerRef.value) {
        resultsContainerRef.value.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });

    toast.add({
      severity: 'success',
      summary: t('project_analysis.analysis_started'),
      detail: t('project_analysis.analysis_started_detail')
    });
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: err?.message || 'Error occurred during analysis start'
    });
  } finally {
    runningAnalysis.value = false;
  }
};onMounted(() => fetchProject());
</script>
