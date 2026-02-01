<!-- frontend/src/views/projects/ProjectForm.vue -->
<template>
  <div class="w-full">
    <h2 v-if="showTitle" class="text-2xl font-semibold mb-6">{{ $t('project_form.title') }}</h2>

    <!-- Nota: 'ref' deve corrispondere al nome della variabile nello script -->
    <PrimeForm ref="formRef"  :resolver="resolver" @submit="onFormSubmit" class="flex flex-col gap-6 w-full">

      <!-- PROJECT NAME -->
      <FormField v-slot="$field" name="name" initialValue="" class="flex flex-col gap-2">
        <label for="name" class="font-medium text-surface-900 dark:text-surface-0">
          {{ $t('project_form.name') }}
        </label>
        <InputText
          id="name"
          type="text"
          :placeholder="$t('project_form.name')"
          class="w-full"
          v-model="$field.value"
          :invalid="$field.invalid"
        />
        <Message v-if="$field.invalid" severity="error" size="small" variant="simple">{{ $field.error?.message }}</Message>
      </FormField>

      <!-- PROJECT DESCRIPTION -->
      <FormField v-slot="$field" name="description" initialValue="" class="flex flex-col gap-2">
        <label for="description" class="font-medium text-surface-900 dark:text-surface-0">
          {{ $t('project_form.description') }}
        </label>
        <!-- Textarea è globale ora -->
        <Textarea
          id="description"
          rows="4"
          :placeholder="$t('project_form.description')"
          class="w-full"
          v-model="$field.value"
          :invalid="$field.invalid"
        />
        <Message v-if="$field.invalid" severity="error" size="small" variant="simple">{{ $field.error?.message }}</Message>
      </FormField>

      <!-- REPO URL -->
      <FormField v-slot="$field" name="repo_url" initialValue="" class="flex flex-col gap-2">
        <label for="repo_url" class="font-medium text-surface-900 dark:text-surface-0">
          {{ $t('project_form.repo_url') }}
        </label>
        <InputText
          id="repo_url"
          type="text"
          :placeholder="$t('project_form.repo_url')"
          class="w-full"
          v-model="$field.value"
          :invalid="$field.invalid"
          :disabled="hasZipFile"
          @update:modelValue="(val) => currentRepoUrl = val"
        />
        <Message v-if="$field.invalid" severity="error" size="small" variant="simple">{{ $field.error?.message }}</Message>
      </FormField>

      <!-- ZIP FILE -->
      <FormField v-slot="$field" name="zip_file" :initialValue="null" class="flex flex-col gap-2">
        <label class="font-medium text-surface-900 dark:text-surface-0">
          {{ $t('project_form.zip_file') }}
        </label>

        <FileUpload
          ref="fileUploadRef"
          mode="advanced"
          accept=".zip"
          :maxFileSize="10000000"
          :fileLimit="1"
          :multiple="false"
          :auto="false"
          :showUploadButton="false"
          :showCancelButton="false"
          :showChooseButton="!hasZipFile"
          :chooseLabel="$t('project_form.zip_file')"
          class="w-full"
          :pt="{
              chooseButton: { root: { class: '!w-auto flex-grow-0' } }
          }"
          :disabled="isRepoUrlFilled"
          @select="onZipSelect"
          @remove="onZipClear"
          @clear="onZipClear"
        >
            <template #content="{ files, removeFileCallback }">
                <div v-if="files.length > 0" class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800 border border-surface-200 dark:border-surface-700 rounded-md w-full justify-between">
                    <div class="flex items-center gap-2 overflow-hidden">
                        <i class="pi pi-file-zip text-primary text-xl" />
                        <span class="font-medium truncate">{{ files[0].name }}</span>
                        <span class="text-xs text-surface-500">{{ (files[0].size / 1024).toFixed(0) }} KB</span>
                    </div>
                    <!-- Button è globale ora -->
                    <Button
                        icon="pi pi-times"
                        text
                        rounded
                        severity="danger"
                        @click="removeFileCallback(0)"
                        aria-label="Remove"
                    />
                </div>
            </template>
            <template #empty>
                <div class="text-surface-500 dark:text-surface-400 text-sm p-4 text-center">
                  {{ $t('project_form.drag_and_drop') }}
                </div>
            </template>
        </FileUpload>

        <Message v-if="$field.invalid" severity="error">{{ $field.error?.message }}</Message>
      </FormField>

      <Message v-if="backendError" severity="error">{{ backendError.message || backendError }}</Message>

      <Button type="submit" :label="$t('project_form.submit')" class="mt-2" :loading="loading" />
    </PrimeForm>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useI18n } from 'vue-i18n';
import { zodResolver } from '@primevue/forms/resolvers/zod';
import { projectSchema } from '@/constants/formSchemes/projectScheme.js';
import { useApi } from '@/composables/useApi';
import ProjectService from '@/services/ProjectService';

const props = defineProps({
  showTitle: {
    type: Boolean,
    default: true
  }
});

const { t } = useI18n();
const toast = useToast();

const formRef = ref(null);
const fileUploadRef = ref(null);

const currentRepoUrl = ref('');
const hasZipFile = ref(false);

const resolver = zodResolver(projectSchema);

const {
  loading,
  error: backendError,
  execute: createProject
} = useApi(ProjectService.createProject);

const isRepoUrlFilled = computed(() => {
  return (currentRepoUrl.value || '').trim().length > 0;
});

const onZipSelect = (event) => {
  const file = event.files && event.files.length > 0 ? event.files[0] : null;

  if (formRef.value) {
    formRef.value.setFieldValue('zip_file', file);
  }

  hasZipFile.value = !!file;
};

const onZipClear = () => {
  if (formRef.value) {
    formRef.value.setFieldValue('zip_file', null);
  }
  hasZipFile.value = false;
};

const onFormSubmit = async ({ valid, values }) => {
  if (valid) {
    let payload = values;

    if (values.zip_file instanceof File) {
        payload = new FormData();
        Object.keys(values).forEach(key => {
            const value = values[key];
            if (value !== null && value !== undefined) {
                payload.append(key, value);
            }
        });
    }

    try {
        await createProject(payload);
        toast.add({ severity: 'success', summary: t('project_form.success'), life: 3000 });
    } catch (e) {
    }
  }
};
</script>
