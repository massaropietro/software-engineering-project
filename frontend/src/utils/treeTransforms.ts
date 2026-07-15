// src/utils/treeTransforms.ts

export interface FileStructureItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileStructureItem[];
  selectable_for_analysis?: boolean;
  total_files?: number;
}

export interface TreeNode {
  key: string;
  label: string;
  data: any;
  icon?: string;
  leaf?: boolean;
  selectable?: boolean;
  children?: TreeNode[];
}

/**
 * Transforms the backend file structure into PrimeVue TreeNode format.
 * Uses index-based keys and stores the path in `data`.
 *
 * @param items List of file structure items from backend
 * @param parentKey Key of the parent node
 * @returns Array of TreeNodes
 */
export const transformToTreeNode = (
  items: FileStructureItem[],
  parentKey: string = ''
): TreeNode[] => {
  if (!items) return [];

  return items.map((item, index) => {
    const key = parentKey ? `${parentKey}-${index}` : `${index}`;

    // Determine icon based on type
    const isDirectory = item.type === 'directory';
    const icon = isDirectory ? 'pi pi-fw pi-folder' : 'pi pi-fw pi-file';

    return {
      key: key,
      label: item.name,
      data: item.path, // Store the full relative path in data
      icon: icon,
      children: item.children ? transformToTreeNode(item.children, key) : undefined
    };
  });
};

/**
 * Transforms the backend file structure into PrimeVue TreeNode format for the Analysis selection.
 * - Uses `item.path` as the `key` to easily track selected paths.
 * - Makes nodes selectable ONLY if they are inside the `src/` directory.
 * - Stores the full item object in `data`.
 *
 * @param items List of file structure items from backend
 * @returns Array of TreeNodes
 */
export const transformToSelectableTreeNode = (
  items: FileStructureItem[]
): TreeNode[] => {
  if (!items) return [];

  // Helper properties to deeply check selectable_for_analysis
  const checkAllFilesSelectable = (subItems: FileStructureItem[]): boolean => {
    if (!subItems || subItems.length === 0) return true;
    for (const sub of subItems) {
      if (sub.type === 'directory') {
        if (!checkAllFilesSelectable(sub.children || [])) return false;
      } else {
        if (sub.selectable_for_analysis !== true) return false;
      }
    }
    return true;
  };

  return items.map((item) => {
    const isDirectory = item.type === 'directory';

    let isSelectable = false;
    if (isDirectory) {
      const totalFiles = typeof item.total_files === 'number' ? item.total_files : 0;
      
      const allSelectable = checkAllFilesSelectable(item.children || []);
      
      // Una folder per essere selezionabile deve avere < 10 file,
      // e non essere vuota (almeno 1 file), e tutti i file devono essere selezionabili
      isSelectable = totalFiles > 0 && totalFiles < 10 && allSelectable;
    } else {
      isSelectable = item.selectable_for_analysis === true;
    }

    return {
      key: item.path,
      label: item.name,
      data: item,
      icon: isDirectory ? 'pi pi-fw pi-folder' : 'pi pi-fw pi-file',
      leaf: !isDirectory,
      selectable: isSelectable,
      children: item.children
        ? transformToSelectableTreeNode(item.children)
        : undefined
    };
  });
};
