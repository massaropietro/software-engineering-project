import { FilterMatchMode } from '@primevue/core/api';

export const endpoints = {
    projects: '/api/projects/',
};

export const PROJECT_STATUSES = ['uploaded', 'processing', 'completed', 'error'];

export const PROJECT_FILTERS = {
    global: { value: null, matchMode: FilterMatchMode.CONTAINS },
    name: { value: null, matchMode: FilterMatchMode.CONTAINS },
    repo_url: { value: null, matchMode: FilterMatchMode.CONTAINS },
    created: { value: null, matchMode: FilterMatchMode.CONTAINS },
    status: { value: null, matchMode: FilterMatchMode.EQUALS }
};
