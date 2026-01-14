<template>
<div class="card">
        <div class="font-semibold text-xl mb-4">{{ $t('projects') }}</div>
        <DataTable v-model:filters="filters" :value="products" paginator :rows="10" dataKey="code" filterDisplay="row" :loading="loading"
                   :globalFilterFields="['name', 'code', 'status']">

            <template #header>
                <div class="flex justify-end">
                    <IconField>
                        <InputIcon>
                            <i class="pi pi-search" />
                        </InputIcon>
                        <InputText v-model="filters['global'].value" :placeholder="$t('project_list.keyword_search')" />
                    </IconField>
                </div>
            </template>

            <template #empty> {{ $t('project_list.no_projects_found') }} </template>
            <template #loading> {{ $t('project_list.loading') }} </template>

            <!-- Colonna Code -->
            <Column field="code" :header="$t('project_list.headers.code')" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ data.code }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()" :placeholder="$t('project_list.placeholders.search_by_id')" />
                </template>
            </Column>

            <!-- Colonna Name -->
            <Column field="name" :header="$t('project_list.headers.name')" style="min-width: 12rem">
                <template #body="{ data }">
                    {{ data.name }}
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <InputText v-model="filterModel.value" type="text" @input="filterCallback()" :placeholder="$t('project_list.placeholders.search_by_name')" />
                </template>
            </Column>

            <!-- Colonna URL -->
            <Column field="category" :header="$t('project_list.headers.category')" style="min-width: 12rem">
                 <template #body="{ data }">
                    <a :href="data.category" target="_blank" class="text-blue-500 hover:underline">{{ data.category }}</a>
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

            <!-- Colonna Verified -->
            <Column field="verified" :header="$t('project_list.headers.verified')" dataType="boolean" style="min-width: 6rem">
                <template #body="{ data }">
                    <i class="pi" :class="{ 'pi-check-circle text-green-500': data.verified, 'pi-times-circle text-red-400': !data.verified }"></i>
                </template>
                <template #filter="{ filterModel, filterCallback }">
                    <Checkbox v-model="filterModel.value" :indeterminate="filterModel.value === null" binary @change="filterCallback()" />
                </template>
            </Column>

        </DataTable>
    </div>
  </template>

<script>
import { FilterMatchMode } from '@primevue/core/api';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import Breadcrumb from 'primevue/breadcrumb';
import Tag from 'primevue/tag';
import Select from 'primevue/select';
import Checkbox from 'primevue/checkbox';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';

export default {
    components: {
        Breadcrumb,
        DataTable,
        Column,
        InputText,
        Tag,
        Select,
        Checkbox,
        IconField,
        InputIcon
    },
    data() {
        return {
            products: null,
            loading: true,
            filters: {
                global: { value: null, matchMode: FilterMatchMode.CONTAINS },
                code: { value: null, matchMode: FilterMatchMode.STARTS_WITH },
                name: { value: null, matchMode: FilterMatchMode.CONTAINS },
                status: { value: null, matchMode: FilterMatchMode.EQUALS },
                verified: { value: null, matchMode: FilterMatchMode.EQUALS }
            },
            statuses: ['PLANNED', 'IN PROGRESS', 'COMPLETED', 'MAINTENANCE'],
            home: { icon: 'pi pi-home', to: '/' },
            items: [
                { label: 'Projects' },
                { label: 'List' }
            ]
        };
    },
    created() {
        // Simulazione caricamento dati
        setTimeout(() => {
            this.products = [
                { code: '1001', name: 'Dashboard Analytics', category: 'https://github.com/user/dashboard-analytics', status: 'COMPLETED', verified: true },
                { code: '1002', name: 'E-commerce API', category: 'https://github.com/user/ecommerce-api', status: 'IN PROGRESS', verified: true },
                { code: '1003', name: 'Mobile App', category: 'https://github.com/user/mobile-app-v2', status: 'PLANNED', verified: false },
                { code: '1004', name: 'Landing Page', category: 'https://github.com/user/landing-page-promo', status: 'MAINTENANCE', verified: true },
                { code: '1005', name: 'Authentication Service', category: 'https://github.com/user/auth-service', status: 'COMPLETED', verified: true }
            ];
            this.loading = false;
        }, 500);
    },
    methods: {
        getSeverity(status) {
            switch (status) {
                case 'MAINTENANCE':
                    return 'danger';
                case 'COMPLETED':
                    return 'success';
                case 'IN PROGRESS':
                    return 'info';
                case 'PLANNED':
                    return 'warn';
                default:
                    return null;
            }
        },
        getTranslatedStatus(status) {
            // Converte lo status (es. "IN PROGRESS") nella chiave del json (es. "in_progress")
            const key = status.toLowerCase().replace(' ', '_');
            return this.$t(`project_list.status.${key}`);
        }
    }
};
</script>
