// frontend/src/validators/validators.js
import * as yup from 'yup';
import i18n from '@/plugins/i18n.js';

// Estraiamo la funzione t direttamente dall'istanza globale
const { t } = i18n.global;

export const projectSchema = yup.object({
    name: yup.string()
        .required(() => t('project_form.errors.required_name') || 'Name is required'),

    description: yup.string()
        .required(() => t('project_form.errors.required_desc') || 'Description is required'),

    repo_url: yup.string()
        .nullable()
        .transform((value) => (value === '' ? null : value))
        .url(() => t('project_form.errors.url_invalid') || 'Must be a valid URL')
        // Verifica: se zip_file è vuoto, repo_url è obbligatorio
        .test(
            'at-least-one-repo',
            () => t('project_form.errors.repo_or_zip_required') || 'Repo URL or Zip File is required',
            function (value) {
                const { zip_file } = this.parent;
                return !!(value || zip_file);
            }
        ),

    zip_file: yup.mixed()
        .nullable()
        // Verifica speculare: se repo_url è vuoto, zip_file è obbligatorio
        .test(
            'at-least-one-zip',
            () => t('project_form.errors.repo_or_zip_required') || 'Repo URL or Zip File is required',
            function (value) {
                const { repo_url } = this.parent;
                return !!(value || repo_url);
            }
        )
});
