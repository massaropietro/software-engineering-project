import { z } from 'zod';
import i18n from '@/plugins/i18n.js';

const { t } = i18n.global;

export const projectSchema = z.object({
    name: z.string().min(1, { message: () => t('project_form.errors.required_name') || 'Name is required' }),

    description: z.string().min(1, { message: () => t('project_form.errors.required_desc') || 'Description is required' }),

    repo_url: z.string()
        .url({ message: () => t('project_form.errors.url_invalid') || 'Must be a valid URL' })
        .nullable()
        .or(z.literal(''))
        .optional()
        .transform((val) => (val === '' ? null : val)),

    zip_file: z.any().nullable().optional()
}).superRefine((data, ctx) => {
    if (!data.repo_url && !data.zip_file) {
        const message = t('project_form.errors.repo_or_zip_required') || 'Repo URL or Zip File is required';

        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: message,
            path: ['repo_url'],
        });

        ctx.addIssue({
            code: z.ZodIssueCode.custom,
            message: message,
            path: ['zip_file'],
        });
    }
});
