import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import "@/assets/main.css"
import 'primeicons/primeicons.css'

import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'

const app = createApp(App)

app.use(createPinia())
app.use(router)

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

// Directives
import StyleClass from 'primevue/styleclass';

app.directive('styleclass', StyleClass)

app.mount('#app')
