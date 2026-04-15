<template>
  <div class="w-full">

    <!-- ── Stato post-creazione: mostra il link segreto ─────────── -->
    <div
      v-if="generatedSecretToken"
      class="flex flex-col items-center justify-center py-4 gap-4 text-center"
    >
      <i class="pi pi-check-circle text-green-500 text-6xl mb-2" />
      <h2 class="text-2xl font-bold">{{ $t('project_form.success') }}</h2>

      <Message severity="warn" :closable="false" class="w-full text-left mt-2">
        <span class="font-semibold block mb-1">
          {{ $t('project_form.secret_link.warning_title') }}
        </span>
        {{ $t('project_form.secret_link.warning_message') }}
      </Message>

      <div
        class="flex items-center gap-2 mt-2 p-2 bg-surface-100 dark:bg-surface-800
               rounded border border-surface-200 dark:border-surface-700 w-full"
      >
        <InputText :modelValue="generatedLink" readonly class="w-full" />
        <Button
          icon="pi pi-copy"
          :label="$t('project_form.secret_link.copy_button')"
          @click="copyLink"
        />
      </div>

      <Button
        :label="$t('project_form.secret_link.go_to_analysis')"
        icon="pi pi-arrow-right"
        class="mt-4 w-full"
        @click="goToAnalysis"
      />
    </div>

    <!-- ── Form ──────────────────────────────────────────────────── -->
    <template v-else>
      <h2 v-if="showTitle" class="text-2xl font-semibold mb-6">
        {{ $t('project_form.title') }}
      </h2>

      <Message severity="info" :closable="false" class="mb-6">
        <div class="flex flex-col gap-2">
          <span class="font-semibold">{{ $t('project_form.requirements.title') }}</span>
          <ul class="list-disc list-inside text-sm space-y-1">
            <li>{{ $t('project_form.requirements.mutmut') }}</li>
            <li>{{ $t('project_form.requirements.src_folder') }}</li>
          </ul>
        </div>
      </Message>

      <PrimeForm
        ref="formRef"
        :resolver="resolver"
        @submit="onFormSubmit"
        class="flex flex-col gap-6 w-full"
      >

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
          <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
            {{ $field.error?.message }}
          </Message>
        </FormField>

        <FormField v-slot="$field" name="description" initialValue="" class="flex flex-col gap-2">
          <label for="description" class="font-medium text-surface-900 dark:text-surface-0">
            {{ $t('project_form.description') }}
          </label>
          <Textarea
            id="description"
            rows="4"
            :placeholder="$t('project_form.description')"
            class="w-full"
            v-model="$field.value"
            :invalid="$field.invalid"
          />
          <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
            {{ $field.error?.message }}
          </Message>
        </FormField>

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
          <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
            {{ $field.error?.message }}
          </Message>
        </FormField>

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
            :pt="{ chooseButton: { root: { class: '!w-auto flex-grow-0' } } }"
            :disabled="isRepoUrlFilled"
            @select="onZipSelect"
            @remove="onZipClear"
            @clear="onZipClear"
          >
            <template #content="{ files, removeFileCallback }">
              <div
                v-if="files.length > 0"
                class="flex items-center gap-3 p-3 bg-surface-50 dark:bg-surface-800
                       border border-surface-200 dark:border-surface-700 rounded-md
                       w-full justify-between"
              >
                <div class="flex items-center gap-2 overflow-hidden">
                  <i class="pi pi-file-zip text-primary text-xl" />
                  <span class="font-medium truncate">{{ files[0].name }}</span>
                  <span class="text-xs text-surface-500">
                    {{ (files[0].size / 1024).toFixed(0) }} KB
                  </span>
                </div>
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

          <Message v-if="$field.invalid" severity="error" size="small" variant="simple">
            {{ $field.error?.message }}
          </Message>
        </FormField>

        <Message v-if="backendError" severity="error">
          {{ backendError.message || backendError }}
        </Message>

        <Button
          type="submit"
          :label="$t('project_form.submit')"
          class="mt-2"
          :loading="loading"
        />
      </PrimeForm>
    </template>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
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

const emit = defineEmits(['success']);

const router = useRouter();
const { t }  = useI18n();
const toast  = useToast();

const formRef       = ref(null);
const fileUploadRef = ref(null);

const currentRepoUrl = ref('');
const hasZipFile     = ref(false);

// Stato post-creazione
const generatedSecretToken = ref('');
const generatedLink        = ref('');

const resolver = zodResolver(projectSchema);

const {
  loading,
  error: backendError,
  execute: createProject
} = useApi(ProjectService.createProject);

const isRepoUrlFilled = computed(() =>
  (currentRepoUrl.value || '').trim().length > 0
);

// ── Gestione file ZIP ────────────────────────────────────────────

const onZipSelect = (event) => {
  const file = event.files?.length > 0 ? event.files[0] : null;
  formRef.value?.setFieldValue('zip_file', file);
  hasZipFile.value = !!file;
};

const onZipClear = () => {
  formRef.value?.setFieldValue('zip_file', null);
  hasZipFile.value = false;
};

// ── Azioni post-creazione ────────────────────────────────────────

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(generatedLink.value);
    toast.add({
      severity : 'info',
      summary  : t('project_form.secret_link.copied_summary'),
      detail   : t('project_form.secret_link.copied_detail'),
      life     : 2000,
    });
  } catch (err) {
    console.error('Impossibile copiare', err);
  }
};

const goToAnalysis = () => {
  emit('success');
  router.push({
    name   : 'project-analysis',
    params : { secretToken: generatedSecretToken.value },
  });
};

// ── Submit ───────────────────────────────────────────────────────

const onFormSubmit = async ({ valid, values }) => {
  if (!valid) return;

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
    const response = await createProject(payload);
    const token = response?.data?.secret_token || response?.secret_token;

    if (token) {
      generatedSecretToken.value = token;
      generatedLink.value = `${window.location.origin}/analyses/${token}`;
      toast.add({
        severity : 'success',
        summary  : t('project_form.success'),
        life     : 3000,
      });
    } else {
      toast.add({
        severity : 'success',
        summary  : t('project_form.success'),
        life     : 3000,
      });
      emit('success');
    }
  } catch (e) {
    console.error('Error creating project:', e);
  }
};
</script>
