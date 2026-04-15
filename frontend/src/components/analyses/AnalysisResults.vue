<template>
  <div class="w-full flex flex-col gap-6 mt-6">

    <div
      v-if="status === 'pending' || status === 'running'"
      class="flex flex-col items-center justify-center p-12 bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700"
    >
      <ProgressSpinner class="mb-6" strokeWidth="4" />
      <h3 class="text-xl font-bold text-surface-700 dark:text-surface-100 mb-2">
        {{ $t('analysis_results.loading_title') }}
      </h3>
      <p class="text-surface-500 text-center max-w-md">
        {{ $t('analysis_results.loading_desc') }}
      </p>
    </div>

    <Message v-else-if="status === 'failed'" severity="error" :closable="false">
      {{ $t('analysis_results.error') }}
    </Message>

    <div v-else-if="status === 'completed'" class="flex flex-col gap-6">

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col items-center justify-center">
          <span class="text-surface-500 text-sm font-semibold uppercase mb-1">{{ $t('analysis_results.global_score') }}</span>
          <span class="text-4xl font-bold text-primary">{{ stats?.score ?? 0 }}%</span>
        </div>
        <div class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col items-center justify-center">
          <span class="text-surface-500 text-sm font-semibold uppercase mb-1">{{ $t('analysis_results.total_mutants') }}</span>
          <span class="text-4xl font-bold text-surface-900 dark:text-surface-0">{{ stats?.total ?? 0 }}</span>
        </div>
        <div class="bg-surface-0 dark:bg-surface-900 p-6 rounded-xl border border-surface-200 dark:border-surface-700 flex flex-col items-center justify-center">
          <span class="text-surface-500 text-sm font-semibold uppercase mb-1">{{ $t('analysis_results.survived') }}</span>
          <span class="text-4xl font-bold text-orange-500">{{ stats?.breakdown?.survived ?? 0 }}</span>
        </div>
      </div>

      <div class="bg-surface-0 dark:bg-surface-900 rounded-xl border border-surface-200 dark:border-surface-700 p-4">
        <h3 class="text-xl font-bold mb-4 ml-2">{{ $t('analysis_results.details_title') }}</h3>

        <DataTable
          :value="mutants"
          responsiveLayout="scroll"
          :paginator="true"
          :rows="10"
          :rowsPerPageOptions="[10, 20, 50]"
          class="p-datatable-sm"
        >
          <Column field="mutant_id" :header="$t('analysis_results.table.id')" :sortable="true" style="width: 10%"></Column>

          <Column field="file" :header="$t('analysis_results.table.file')" :sortable="true" style="width: 30%">
            <template #body="{ data }">
              <span class="font-mono text-sm break-all text-surface-600 dark:text-surface-300">
                {{ data.file }}
              </span>
            </template>
          </Column>

          <Column field="line" :header="$t('analysis_results.table.line')" :sortable="true" style="width: 10%"></Column>

          <Column field="status" :header="$t('analysis_results.table.status')" :sortable="true" style="width: 15%">
            <template #body="{ data }">
              <Tag
                :severity="data.status === 'survived' ? 'warning' : 'success'"
                :value="data.status"
                class="uppercase text-xs"
              />
            </template>
          </Column>

          <Column field="is_equivalent" :header="$t('analysis_results.table.ai_result')" :sortable="true" style="width: 20%">
            <template #body="{ data }">
              <Tag v-if="data.is_equivalent === true" severity="success" :value="$t('analysis_results.tags.equivalent')" />
              <Tag v-else-if="data.is_equivalent === false" severity="danger" :value="$t('analysis_results.tags.divergent')" />
              <span v-else class="text-surface-400 text-sm italic">{{ $t('analysis_results.tags.to_verify') }}</span>
            </template>
          </Column>

          <Column :header="$t('analysis_results.table.actions')" style="width: 15%; text-align: left">
            <template #body="{ data }">
              <Button
                v-if="data.description"
                icon="pi pi-align-left"
                :label="$t('analysis_results.details_btn')"
                size="small"
                outlined
                @click="openDescription(data)"
              />
              <span v-else class="text-surface-400 text-sm italic">
                {{ $t('analysis_results.no_description') }}
              </span>
            </template>
          </Column>
        </DataTable>
      </div>

    </div>

      <Dialog
            v-model:visible="displayDialog"
            modal
            :draggable="false"
            :header="selectedMutant ? $t('analysis_results.dialog_title', { id: selectedMutant.mutant_id }) : ''"
            :style="{ width: '50vw' }"
            :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
            dismissableMask
          >
      <div v-if="selectedMutant" class="text-left bg-surface-50 dark:bg-surface-800 p-4 rounded border border-surface-200 dark:border-surface-700 max-h-[60vh] overflow-y-auto">
        <pre v-if="selectedMutant.description" class="font-mono text-sm whitespace-pre-wrap m-0 text-surface-800 dark:text-surface-100">{{ selectedMutant.description }}</pre>
        <p v-else class="text-sm text-surface-500 italic m-0">{{ $t('analysis_results.no_description') }}</p>
      </div>
    </Dialog>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import ProjectService from '@/services/ProjectService';
import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

const { t } = useI18n();
const props = defineProps<{
  analysisId: string;
}>();

const status = ref<string>('pending');
const stats = ref<any>(null);
const mutants = ref<any[]>([]);
let pollInterval: ReturnType<typeof setInterval> | null = null;

// Gestione Dialog
const displayDialog = ref(false);
const selectedMutant = ref<any>(null);

const openDescription = (mutant: any) => {
  selectedMutant.value = mutant;
  displayDialog.value = true;
};

const fetchResults = async () => {
  try {
    const res = await ProjectService.getMutantResults(props.analysisId);
    mutants.value = res.data.results || [];
  } catch (error) {
    console.error("Errore nel recupero dei risultati:", error);
  }
};

const checkStatus = async () => {
  try {
    const res = await ProjectService.getAnalysisStats(props.analysisId);
    stats.value = res.data;
    status.value = res.data.status;

    if (status.value === 'completed' || status.value === 'failed') {
      stopPolling();
      if (status.value === 'completed') {
        await fetchResults();
      }
    }
  } catch (error) {
    console.error("Errore durante il polling dello status:", error);
  }
};

const startPolling = () => {
  checkStatus();
  pollInterval = setInterval(checkStatus, 3000);
};

const stopPolling = () => {
  if (pollInterval) {
    clearInterval(pollInterval);
    pollInterval = null;
  }
};

onMounted(() => {
  startPolling();
});

onUnmounted(() => {
  stopPolling();
});
</script>
