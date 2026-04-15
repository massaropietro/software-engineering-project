<template>
  <Dialog
    :draggable="false"
    :visible="visible"
    modal
    :header="$t('project_form.title')"
    :style="{ width: '50rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    @update:visible="(val) => $emit('update:visible', val)"
    :pt="{ content: { class: '!pb-8' } }"
  >
    <ProjectForm :showTitle="false" class="w-full" @success="closeDialog" />
  </Dialog>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['update:visible']);

const closeDialog = () => {
  emit('update:visible', false);
};
</script>
