<template>
  <div class="w-full flex flex-col gap-4 mt-8">
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-surface-900 dark:text-surface-0">
        {{ $t('analysis_history.title') }}
      </h2>
    </div>

    <div v-if="loading" class="flex justify-center items-center h-32">
      <ProgressSpinner strokeWidth="4" />
    </div>

    <Message v-else-if="error" severity="error" :closable="false">
      {{ error.message || $t('analysis_history.error') }}
    </Message>

    <div v-else-if="analyses.length === 0" class="bg-surface-0 dark:bg-surface-900 p-8 rounded-xl border border-surface-200 dark:border-surface-700 text-center">
      <i class="pi pi-history text-4xl text-surface-300 dark:text-surface-600 mb-4"></i>
      <p class="text-surface-500 m-0">{{ $t('analysis_history.empty') }}</p>
    </div>

    <Accordion v-else multiple v-model:value="activeAccordions" class="w-full">

      <AccordionPanel v-for="analysis in analyses" :key="analysis.id" :value="analysis.id">

        <AccordionHeader>
          <div class="flex items-center justify-between w-full pr-4 gap-4 flex-wrap">
            <span class="font-semibold text-lg">
              <i class="pi pi-calendar mr-2 text-primary"></i>
              {{ formatDate(analysis.created) }}
            </span>

            <div class="flex items-center gap-4">
              <span v-if="analysis.score !== null && analysis.score !== undefined" class="font-bold text-surface-700 dark:text-surface-200">
                {{ $t('analysis_history.score') }} <span class="text-primary">{{ analysis.score }}%</span>
              </span>

              <Tag
                :value="analysis.status"
                :severity="getStatusSeverity(analysis.status)"
                class="uppercase text-xs"
              />
            </div>
          </div>
        </AccordionHeader>

        <AccordionContent>
          <div class="pt-4 border-t border-surface-200 dark:border-surface-700 mt-2">
            <AnalysisResults :analysisId="analysis.id" />
          </div>
        </AccordionContent>

      </AccordionPanel>
    </Accordion>
  </div>
</template>

<script setup>
import {ref, computed, onMounted, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useApi} from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';

import ProgressSpinner from 'primevue/progressspinner';
import Message from 'primevue/message';
import Accordion from 'primevue/accordion';
import AccordionPanel from 'primevue/accordionpanel';
import AccordionHeader from 'primevue/accordionheader';
import AccordionContent from 'primevue/accordioncontent';
import Tag from 'primevue/tag';
import AnalysisResults from '@/components/analyses/AnalysisResults.vue';

const {t, locale} = useI18n();

const props = defineProps({
  projectId: {
    type: String,
    required: true
  }
});

// ORA È UN ARRAY: gestisce la modalità multipla dell'Accordion
const activeAccordions = ref([]);

const {
  data: apiData,
  loading,
  error,
  execute: fetchHistory
} = useApi(() => ProjectService.getAnalyses({project: props.projectId}));

const analyses = computed(() => {
  return apiData.value?.results || apiData.value || [];
});

// Appena arrivano i dati, inseriamo l'ID della prima analisi nell'array
watch(analyses, (newAnalyses) => {
  if (newAnalyses.length > 0 && activeAccordions.value.length === 0) {
    activeAccordions.value = [newAnalyses[0].id];
  }
}, {immediate: true});

const formatDate = (dateString) => {
  if (!dateString) return '';
  const currentLocale = locale.value === 'it' ? 'it-IT' : 'en-US';
  return new Date(dateString).toLocaleString(currentLocale, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getStatusSeverity = (status) => {
  switch (status?.toLowerCase()) {
    case 'completed':
      return 'success';
    case 'running':
      return 'info';
    case 'failed':
      return 'danger';
    case 'pending':
      return 'warning';
    default:
      return 'secondary';
  }
};

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
:deep(.p-accordionheader) {
  background-color: var(--surface-50);
}

.dark :deep(.p-accordionheader) {
  background-color: var(--surface-800);
}
</style>
