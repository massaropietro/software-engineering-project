<template>
  <div class="w-full flex flex-col gap-6 p-4">
    <div v-if="loading" class="flex justify-center items-center h-40">
      <ProgressSpinner />
    </div>

    <Message v-else-if="error" severity="error" :closable="false">
      {{ typeof error === 'string' ? error : error?.message || 'Errore di caricamento' }}
    </Message>

    <template v-else-if="projectData">
      <div class="flex flex-col gap-2">
        <h1 class="text-2xl font-bold">{{ projectData.name }}</h1>
        <p v-if="projectData.description" class="text-surface-500">
          {{ projectData.description }}
        </p>
      </div>

      <Message severity="info" :closable="false">
        Seleziona fino a 10 elementi (file o directory sotto <b>src/</b>) su cui eseguire l'analisi.
      </Message>

      <div class="grid grid-cols-1 xl:grid-cols-[minmax(0,1fr)_320px] gap-6">

        <div class="rounded-xl border border-surface-200 dark:border-surface-700 p-4 overflow-hidden bg-surface-0 dark:bg-surface-900">
          <div class="flex flex-wrap items-center gap-2 mb-4">
            <Button icon="pi pi-plus" label="Espandi tutto" outlined size="small" @click="expandAll" />
            <Button icon="pi pi-minus" label="Chiudi tutto" outlined size="small" @click="collapseAll" />
          </div>

          <Tree
            v-model:selectionKeys="selectionKeys"
            v-model:expandedKeys="expandedKeys"
            :value="treeNodes"
            selectionMode="checkbox"
            :filter="true"
            filterMode="lenient"
            class="w-full"
          >
            <template #default="{ node }">
              <div class="flex items-center gap-2 min-w-0">

                <span class="truncate" :class="{ 'text-surface-400 italic': !node.selectable }">
                  {{ node.label }}
                </span>
              </div>
            </template>
          </Tree>
        </div>

        <div class="rounded-xl border border-surface-200 dark:border-surface-700 p-4 h-fit bg-surface-50 dark:bg-surface-800">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">Selezionati</h2>
            <Tag :value="`${selectedPaths.length}/${MAX_ITEMS}`" :severity="selectedPaths.length > MAX_ITEMS ? 'danger' : 'primary'" />
          </div>

          <ul v-if="selectedPaths.length > 0" class="flex flex-col gap-2 mb-4 max-h-60 overflow-y-auto">
            <li
              v-for="path in selectedPaths"
              :key="path"
              class="text-xs rounded-md bg-surface-100 dark:bg-surface-700 px-3 py-2 break-all border border-surface-200 dark:border-surface-600"
            >
              {{ path }}
            </li>
          </ul>

          <p v-else class="text-sm text-surface-500 mb-4">
            Nessun elemento selezionato.
          </p>

          <Button
            label="Avvia analisi"
            icon="pi pi-play"
            class="w-full"
            :disabled="selectedPaths.length === 0 || selectedPaths.length > MAX_ITEMS"
            :loading="runningAnalysis"
            @click="runAnalysis"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue';
import { useRoute } from 'vue-router';
import { useToast } from 'primevue/usetoast';
import { useApi } from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';
import { transformToSelectableTreeNode, type TreeNode } from '@/utils/treeTransforms';

// UI Components (Assicurati che siano importati globalmente o qui se necessario)
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import Tree from 'primevue/tree';
import Button from 'primevue/button';
import Tag from 'primevue/tag';

const MAX_ITEMS = 10;
const route = useRoute();
const toast = useToast();
const secretToken = String(route.params.secretToken || '');

// API Logic
const {
  data: apiData,
  loading,
  error,
  execute: fetchProject
} = useApi(() => ProjectService.getProjectByToken(secretToken));

// Computed data per gestire la reattività in modo fluido
const projectData = computed(() => {
  if (!apiData.value) return null;
  return (apiData.value as any).data || apiData.value;
});

const treeNodes = computed(() => {
  if (!projectData.value?.file_structure) return [];
  return transformToSelectableTreeNode(projectData.value.file_structure);
});

// Tree State
const selectionKeys = ref<Record<string, any>>({});
const expandedKeys = ref<Record<string, any>>({});
const previousValidSelectionKeys = ref<Record<string, any>>({});
const runningAnalysis = ref(false);

// Helper per estrarre i path selezionati
const getExplicitlySelectedPaths = (nodes: TreeNode[], selection: Record<string, any>): string[] => {
  let paths: string[] = [];
  for (const node of nodes) {
    const state = selection[node.key];
    if (state?.checked) {
      paths.push(node.key);
    } else if (state?.partialChecked && node.children) {
      paths = paths.concat(getExplicitlySelectedPaths(node.children, selection));
    }
  }
  return paths;
};

const selectedPaths = computed(() => {
  return getExplicitlySelectedPaths(treeNodes.value, selectionKeys.value);
});

// Watcher per validazione limite massimo
watch(selectionKeys, (newVal) => {
  const currentPaths = getExplicitlySelectedPaths(treeNodes.value, newVal);

  if (currentPaths.length <= MAX_ITEMS) {
    previousValidSelectionKeys.value = JSON.parse(JSON.stringify(newVal));
  } else {
    // Rollback al prossimo ciclo di update per evitare conflitti con l'evento di PrimeVue
    nextTick(() => {
      selectionKeys.value = JSON.parse(JSON.stringify(previousValidSelectionKeys.value));
    });

    toast.add({
      severity: 'warn',
      summary: 'Limite raggiunto',
      detail: `Puoi selezionare al massimo ${MAX_ITEMS} elementi.`,
      life: 3000
    });
  }
}, { deep: true });

// Espandi / Chiudi tutto
const expandAll = () => {
  const keys: Record<string, boolean> = {};
  const helper = (nodes: TreeNode[]) => {
    nodes.forEach(node => {
      if (node.children && node.children.length > 0) {
        keys[node.key] = true;
        helper(node.children);
      }
    });
  };
  helper(treeNodes.value);
  expandedKeys.value = keys;
};

const collapseAll = () => {
  expandedKeys.value = {};
};

// Esecuzione Analisi
const runAnalysis = async () => {
  if (!projectData.value || selectedPaths.value.length === 0) return;

  runningAnalysis.value = true;
  try {
    const payload = {
      project: projectData.value.id,
      files: selectedPaths.value.join(','),
      language: 'python'
    };

    await ProjectService.runAnalysisByToken(secretToken, payload);

    toast.add({
      severity: 'success',
      summary: 'Analisi avviata',
      detail: `${selectedPaths.value.length} elementi inviati con successo.`,
      life: 3000
    });
  } catch (err: any) {
    toast.add({
      severity: 'error',
      summary: 'Errore',
      detail: err?.response?.data?.detail || err?.message || 'Errore durante l’invio.',
      life: 3000
    });
  } finally {
    runningAnalysis.value = false;
  }
};

onMounted(() => {
  fetchProject();
});
</script>
