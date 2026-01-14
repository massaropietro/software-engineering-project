import { createI18n } from 'vue-i18n'
import en from '@/locales/en.json'
import it from '@/locales/it.json'

const i18n = createI18n({
  legacy: false,      // Necessario per Vue 3
  locale: 'it',       // Lingua predefinita
  fallbackLocale: 'en', // Lingua di riserva
  messages: {
    en,
    it
  }
})

export default i18n
