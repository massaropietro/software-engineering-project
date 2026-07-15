<template>
    <div class="card">
        <div class="flex justify-between items-center mb-4">
            <div class="font-semibold text-xl">{{ $t('projects') }}</div>
            <Button :label="$t('project_list.new_project')" icon="pi pi-plus" @click="showCreateDialog = true" />
        </div>
        
        <DataTable
            v-model:filters="filters"
            :value="projects"
            :lazy="true" 
            paginator
            :rows="10"
            :totalRecords="totalRecords"
            dataKey="repo_url"
            filterDisplay="row"
            :loading="loading"
            :globalFilterFields="['name', 'repo_url', 'status', 'created']"
            @page="onPage($event)"
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
                    <Button :label="data.name" class="p-button-text" @click="navigateToProject(data)" />
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
                    <Select v-model="filterModel.value" @change="filterCallback()" :options="statuses" :placeholder="$t('project_list.placeholders.select_one')" showClear>
                        <template #option="slotProps">
                            <Tag :value="getTranslatedStatus(slotProps.option)" :severity="getSeverity(slotProps.option)" />
                        </template>
                    </Select>
                </template>
            </Column>

            <!-- Colonna Azioni -->
            <Column :header="$t('project_list.headers.actions')" style="min-width: 6rem">
                <template #body="{ data }">
                    <Button 
                        icon="pi pi-trash" 
                        class="p-button-rounded p-button-danger p-button-text" 
                        @click="confirmDeleteProject(data)" 
                    />
                </template>
            </Column>
        </DataTable>

        <ProjectCreateDialog v-model:visible="showCreateDialog" />
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useToast } from 'primevue/usetoast';
import { PROJECT_STATUSES, PROJECT_FILTERS } from "@/constants/constants.js";
import { useApi } from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';
import { formatDate, getSeverity } from "@/utils/utils";

const { t } = useI18n();
const router = useRouter();
const toast = useToast();

const projects = ref([]);
const filters = ref(PROJECT_FILTERS);
const statuses = ref(PROJECT_STATUSES);
const showCreateDialog = ref(false);


const totalRecords = ref(0);

const {
    data: projectsData,
    loading,
    error: backendError,
    execute: fetchProjects
} = useApi(ProjectService.getProjects);

const navigateToProject = (project) => {
    router.push({ name: 'project-details', params: { projectId: project?.id } });
};

const confirmDeleteProject = async (project) => {
    const confirmed = window.confirm(
        t('project_list.delete_confirm_message', { name: project.name })
    );
    if (!confirmed) return;

    try {
        await ProjectService.deleteProject(project.id);
        toast.add({
            severity: 'success',
            summary: t('project_list.delete_confirm_title'),
            detail: t('project_list.delete_success'),
            life: 3000
        });
        loadProjects(1);
    } catch (err) {
        toast.add({
            severity: 'error',
            summary: 'Errore',
            detail: err.response?.data?.detail || 'Errore durante l\'eliminazione del progetto',
            life: 3000
        });
    }
};

const loadProjects = async (page = 1) => {
    await fetchProjects({ page });
    
    if (projectsData.value) {
        projects.value = projectsData.value.results || [];
        totalRecords.value = projectsData.value.count || 0;
    }
};

const onPage = (event) => {
    const pageNumber = event.page + 1;
    loadProjects(pageNumber);
};

const getTranslatedStatus = (status) => {
    if (!status) return '';
    const key = status.toLowerCase().replace(' ', '_');
    const translationKey = `project_list.status.${key}`;
    const translated = t(translationKey);
    return translated !== translationKey ? translated : status;
};

onMounted(() => {
    loadProjects(1);
});
</script>
