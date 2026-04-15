// src/utils/treeTransforms.ts

export interface FileStructureItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size?: number;
  children?: FileStructureItem[];
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
 * @param isUnderSrc Boolean tracking if the current tree level is inside 'src/'
 * @returns Array of TreeNodes
 */
export const transformToSelectableTreeNode = (
  items: FileStructureItem[],
  isUnderSrc: boolean = false
): TreeNode[] => {
  if (!items) return [];

  return items.map((item) => {
    const isDirectory = item.type === 'directory';

    const isSrcFolder = item.name === 'src' && isDirectory;
    const currentlyUnderSrc = isUnderSrc || isSrcFolder;

    return {
      key: item.path,
      label: item.name,
      data: item,
      icon: isDirectory ? 'pi pi-fw pi-folder' : 'pi pi-fw pi-file',
      leaf: !isDirectory,
      selectable: currentlyUnderSrc,
      children: item.children
        ? transformToSelectableTreeNode(item.children, currentlyUnderSrc)
        : undefined
    };
  });
};
