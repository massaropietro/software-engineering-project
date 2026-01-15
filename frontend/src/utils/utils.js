
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
