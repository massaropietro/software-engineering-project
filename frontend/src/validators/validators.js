import * as yup from "yup";

export const projectSchema = yup.object().shape({
    projectName: yup.string().required("Il nome del progetto è obbligatorio"),
    description: yup.string()
        .required("La descrizione è obbligatoria")
        .min(10, "La descrizione deve essere di almeno 10 caratteri"),
    repoUrl: yup.string()
        .ensure()
        // Se c'è il file zip, l'URL non è richiesto, altrimenti sì
        .when('zipFile', {
            is: (zipFile) => zipFile && zipFile.length > 0,
            then: (schema) => schema.notRequired(),
            otherwise: (schema) => schema.required("L'URL della repository è obbligatorio")
        })
        // Validazione regex manuale per permettere stringa vuota se non obbligatorio
        .test('is-valid-url', "Inserisci un URL valido", (value) => {
            if (!value) return true;
            return /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/.test(value);
        }),
    zipFile: yup.mixed()
        // Se c'è l'URL, il file non è richiesto, altrimenti sì
        .when('repoUrl', {
            is: (repoUrl) => repoUrl && repoUrl.length > 0,
            then: (schema) => schema.notRequired(),
            otherwise: (schema) => schema.test("required", "Il file ZIP è obbligatorio", (value) => value && value.length > 0)
        })
        .test("fileType", "Per favore carica un file .zip", (value) => {
            if (!value || value.length === 0) return true;
            const file = value[0];
            return file.name.endsWith('.zip') || file.type === 'application/zip';
        })
}, [['repoUrl', 'zipFile']]); // Importante: abilita la dipendenza ciclica tra i due campi
