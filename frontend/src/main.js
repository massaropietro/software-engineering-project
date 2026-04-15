/* frontend/src/main.js */
import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import i18n from '@/plugins/i18n.js'

import "@/assets/main.css"
import 'primeicons/primeicons.css'
import ProjectAnalysis from "@/components/projects/ProjectAnalysis.vue";
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import ToastService from 'primevue/toastservice';
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(ToastService);
app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark'
    }
  }
})

// Components Imports
import Button from 'primevue/button'
import Badge from 'primevue/badge'
import Message from "primevue/message";
import Toast from 'primevue/toast';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import FileUpload from 'primevue/fileupload';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Select from 'primevue/select';
import IconField from 'primevue/iconfield';
import InputIcon from 'primevue/inputicon';
import { Form, FormField } from '@primevue/forms';
import Dialog from 'primevue/dialog';
import Card from 'primevue/card';
import {ProgressSpinner} from "primevue";
import ProjectCreateDialog from '@/views/projects/ProjectCreateDialog.vue';
import ProjectForm from '@/components/projects/ProjectForm.vue';


// Global Component Registration
app.component('Message', Message)
app.component('Button', Button)
app.component('Badge', Badge)
app.component('Toast', Toast)
app.component('InputText', InputText)
app.component('Textarea', Textarea)
app.component('FileUpload', FileUpload)
app.component('DataTable', DataTable)
app.component('Column', Column)
app.component('Tag', Tag)
app.component('Select', Select)
app.component('IconField', IconField)
app.component('InputIcon', InputIcon)
app.component('PrimeForm', Form)
app.component('FormField', FormField)
app.component('Dialog', Dialog)
app.component('Card', Card)
app.component('ProjectCreateDialog', ProjectCreateDialog)
app.component('ProjectForm', ProjectForm)
app.component('ProgressSpinner', ProgressSpinner)
app.component('ProjectAnalysis', ProjectAnalysis)
// Directives
import StyleClass from 'primevue/styleclass';


app.directive('styleclass', StyleClass)

app.mount('#app')
