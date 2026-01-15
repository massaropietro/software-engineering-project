<!-- frontend/src/views/projects/ProjectForm.vue -->
<template>
  <div class="card flex flex-col justify-center items-center p-8">
    <h2 class="text-2xl font-semibold mb-6">{{ $t('project_form.title') }}</h2>
    <Toast />

    <PrimeForm ref="form" :resolver="resolver" @submit="onFormSubmit" class="flex flex-col gap-6 w-full max-w-lg">

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
        <PrimeTextarea
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

        <!--
          FileUpload:
          - class="w-full": estende il background/contenitore a tutta la riga.
          - pt.chooseButton: forza il bottone a !w-auto per evitare l'effetto "pulsantone".
        -->
        <FileUpload
          ref="fileUpload"
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
                    <PrimeButton
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

        <Message v-if="$field.invalid" severity="error" size="small" variant="simple">{{ $field.error?.message }}</Message>
      </FormField>

      <PrimeButton type="submit" :label="$t('project_form.submit')" class="mt-2" />
    </PrimeForm>
  </div>
</template>

<script>
import Toast from 'primevue/toast';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import FileUpload from 'primevue/fileupload';
import Message from 'primevue/message';
import { Form, FormField } from '@primevue/forms';
import { yupResolver } from '@primevue/forms/resolvers/yup';
import { projectSchema } from '@/validators/validators.js';

export default {
  components: {
    Toast,
    InputText,
    PrimeTextarea: Textarea,
    PrimeButton: Button,
    PrimeForm: Form,
    FormField,
    FileUpload,
    Message
  },
  data() {
    return {
      currentRepoUrl: '',
      hasZipFile: false,
      resolver: yupResolver(projectSchema)
    };
  },
  computed: {
    isRepoUrlFilled() {
      return (this.currentRepoUrl || '').trim().length > 0;
    }
  },
  methods: {
    onZipSelect(event) {
      const file = event.files && event.files.length > 0 ? event.files[0] : null;
      this.$refs.form.setFieldValue('zip_file', file);
      this.hasZipFile = !!file;
    },
    onZipClear() {
      this.$refs.form.setFieldValue('zip_file', null);
      this.hasZipFile = false;
    },
    onFormSubmit({ valid, values }) {
      if (valid) {
        console.log('Form Values:', values);
        this.$toast.add({ severity: 'success', summary: this.$t('project_form.success'), life: 3000 });
      }
    }
  }
};
</script>
