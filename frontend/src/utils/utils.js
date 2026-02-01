/* Util functions shared across the application */

export function getBreadcrumbs(currentUrl, routerInstance) {
    const segments = currentUrl.split('/').filter(item => item);
    let currentPath = '';
    const breadcrumbs = [];

    segments.forEach(segment => {
        currentPath += `/${segment}`;

        const resolved = routerInstance.resolve(currentPath);

        let label = '';
        if (resolved.meta && resolved.meta.title) {
            label = resolved.meta.title;
        } else {
            label = segment.charAt(0).toUpperCase() + segment.slice(1);
        }

        breadcrumbs.push({
            label: label,
            route: currentPath
        });
    });

    return breadcrumbs;
}

export const formatDate = (dateString) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleString();
};

export const getSeverity = (status) => {
    const s = status ? status.toLowerCase() : '';
    switch (s) {
        case 'error':
        case 'maintenance':
            return 'danger';
        case 'completed':
            return 'success';
        case 'processing':
        case 'in progress':
            return 'info';
        case 'uploaded':
        case 'planned':
            return 'warn';
        default:
            return 'secondary';
    }
};

export const getErrorMessage = (error) => {
    if (error.response && error.response.data) {
        const data = error.response.data;

        if (data.detail) {
            return data.detail;
        }
        const errorList = [];

        for (const [key, errors] of Object.entries(data)) {
            const msgString = Array.isArray(errors) ? errors.join(', ') : errors;
            if (key === 'non_field_errors') {
                errorList.push(`• ${msgString}`);
            } else {
                const formattedKey = key.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase());
                errorList.push(`• ${formattedKey}: ${msgString}`);
            }
        }
        if (errorList.length > 0) {
            return errorList.join('\n');
        }
    }
    return error.message || "Errore sconosciuto.";
};
