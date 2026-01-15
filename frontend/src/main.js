import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import i18n from '@/plugins/i18n.js'

import "@/assets/main.css"
import 'primeicons/primeicons.css'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import ToastService from 'primevue/toastservice';
const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(i18n)

app.use(PrimeVue, {
  theme: {
    preset: Aura,
    options: {
      darkModeSelector: '.dark'
    }
  }
})

// Components
import Button from 'primevue/button'
import Badge from 'primevue/badge'

app.component('Button', Button)
app.component('Badge', Badge)
app.use(ToastService);

// Directives
import StyleClass from 'primevue/styleclass';

app.directive('styleclass', StyleClass)

app.mount('#app')
