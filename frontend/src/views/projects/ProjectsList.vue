<!-- frontend/src/views/projects/ProjectsList.vue -->
<template>
    <div class="card">
        <div class="font-semibold text-xl mb-4">{{ $t('projects') }}</div>
        <DataTable
            v-model:filters="filters"
            :value="projects"
            paginator
            :rows="10"
            dataKey="repo_url"
            filterDisplay="row"
            :loading="loading"
            :globalFilterFields="['name', 'repo_url', 'status', 'created']"
        >
            <template #empty>
                <div v-if="backendError" class="text-center text-red-500">
                    <i class="pi pi-exclamation-circle mr-2"></i>
                    <span class="font-bold">{{ $t('project_list.error_loading_projects') }}: </span>
                    <span> {{ backendError }}</span>
                </div>
                <div v-else>
                    {{ $t('project_list.no_projects_found') }}
                </div>
            </template>

            <template #loading> {{ $t('project_list.loading') }} </template>

            <!-- Colonna Name -->
            <Column field="name" :header="$t('project_list.headers.name')" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ data.name }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()" :placeholder="$t('project_list.placeholders.search_by_name')" />
                </template>
            </Column>

            <!-- Colonna Repo URL -->
            <Column field="repo_url" :header="$t('project_list.headers.repository')" style="min-width: 12rem">
                 <template #body="{ data }">
                    <a v-if="data.repo_url" :href="data.repo_url" target="_blank" class="text-blue-500 hover:underline">{{ data.repo_url }}</a>
                    <span v-else>-</span>
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()" placeholder="Search URL" />
                </template>
            </Column>

            <!-- Colonna Created -->
            <Column field="created" :header="$t('project_list.headers.created')" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ formatDate(data.created) }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()" placeholder="Search Date" />
                </template>
            </Column>

            <!-- Colonna Status -->
            <Column field="status" :header="$t('project_list.headers.status')" :showFilterMenu="false" style="min-width: 12rem">
                <template #body="{ data }">
                    <Tag :value="getTranslatedStatus(data.status)" :severity="getSeverity(data.status)" />
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <!-- Nome aggiornato: PrimeSelect -> Select (come in main.js) -->
                    <Select v-model="filterModel.value" @change="filterCallback()" :options="statuses" :placeholder="$t('project_list.placeholders.select_one')" showClear>
                        <template #option="slotProps">
                            <Tag :value="getTranslatedStatus(slotProps.option)" :severity="getSeverity(slotProps.option)" />
                        </template>
                    </Select>
                </template>
            </Column>

        </DataTable>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { PROJECT_STATUSES, PROJECT_FILTERS } from "@/constants/constants.js";
import { getProjects } from '@/backend/backend';
import { formatDate, getSeverity } from "@/utils/utils";

const { t } = useI18n();

const projects = ref([]);
const loading = ref(true);
const backendError = ref(null);
const filters = ref(PROJECT_FILTERS);
const statuses = ref(PROJECT_STATUSES);

// Metodi
const loadProjects = () => {
    getProjects({
        loading: (state) => loading.value = state,
        setBackendError: (msg) => backendError.value = msg,
        onSuccess: (data) => {
            if (data && data.results && Array.isArray(data.results)) {
                projects.value = data.results;
            }
        },
    });
};

const getTranslatedStatus = (status) => {
    if (!status) return '';
    const key = status.toLowerCase().replace(' ', '_');
    const translationKey = `project_list.status.${key}`;
    const translated = t(translationKey);
    return translated !== translationKey ? translated : status;
};

onMounted(() => {
    loadProjects();
});


</script>
