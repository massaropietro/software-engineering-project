<script setup>
import { ref } from 'vue';

const nodes = ref([
    {
        key: '0',
        label: 'Progetto Principale',
        icon: 'pi pi-fw pi-folder',
        children: [
            { key: '0-0', label: 'src', icon: 'pi pi-fw pi-folder', children: [
                { key: '0-0-0', label: 'App.vue', icon: 'pi pi-fw pi-file' },
                { key: '0-0-1', label: 'main.js', icon: 'pi pi-fw pi-file' }
            ]},
            { key: '0-1', label: 'assets', icon: 'pi pi-fw pi-folder' }
        ]
    },
    {
        key: '1',
        label: 'README.md',
        icon: 'pi pi-fw pi-file'
    }
]);
</script>

<template>
  <div class="card p-4">
    <h1 class="text-3xl font-bold mb-4">{{ $t('project.details_title') }}</h1>

    <div class="grid">

      <div class="col-12 md:col-3">
        <Panel :header="$t('project.file_explorer')">
          <Tree :value="nodes" class="w-full" />
        </Panel>
      </div>

      <div class="col-12 md:col-9">
        <Panel :header="$t('project.overview')">
          <p>{{ $t('project.health_placeholder') }}</p>
          </Panel>
      </div>

    </div>
  </div>
</template>
