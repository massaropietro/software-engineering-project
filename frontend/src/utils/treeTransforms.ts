
/**
 * Transforms the backend file structure into PrimeVue TreeNode format.
 * @param items List of file structure items from backend
 * @param parentKey Key of the parent node
 * @returns Array of TreeNodes
 */
export const transformToTreeNode = (items: any[], parentKey = ''): any[] => {
  if (!items) return [];

  return items.map((item, index) => {
    // Generate a unique key for the tree node
    const key = parentKey ? `${parentKey}-${index}` : `${index}`;

    // Determine icon based on type
    let icon = 'pi pi-fw pi-file';
    if (item.type === 'directory') {
      icon = 'pi pi-fw pi-folder';
    }

    return {
      key: key,
      label: item.name,
      data: item.path, // Store the full relative path in data
      icon: icon,
      children: item.children ? transformToTreeNode(item.children, key) : undefined
    };
  });
};
