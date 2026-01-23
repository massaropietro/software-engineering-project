<template>
  <div
    class="resize-container-2 min-h-screen flex relative lg:static bg-surface-50 dark:bg-surface-950"
  >
    <div
      id="app-sidebar-colored"
      class="w-[280px] bg-primary h-screen hidden lg:block shrink-0 absolute lg:static left-0 top-0 z-10 select-none"
    >
      <div class="flex flex-col h-full">
        <div class="p-4 flex items-center gap-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="43"
            height="43"
            viewBox="0 0 43 43"
            fill="none"
            class="w-10 h-10"
          >
            <path
              fill-rule="evenodd"
              clip-rule="evenodd"
              d="M21.5 42.0498C33.098 42.0498 42.5 32.6477 42.5 21.0498C42.5 9.45183 33.098 0.0498047 21.5 0.0498047C9.902 0.0498047 0.5 9.45183 0.5 21.0498C0.5 32.6477 9.902 42.0498 21.5 42.0498ZM28.0513 9.83248C28.3702 8.69975 27.2709 8.02994 26.267 8.74516L12.2528 18.7288C11.164 19.5045 11.3353 21.0498 12.51 21.0498H16.2003V21.0212H23.3926L17.5323 23.089L14.9487 32.2671C14.6299 33.3999 15.729 34.0697 16.733 33.3544L30.7472 23.3708C31.836 22.5951 31.6646 21.0498 30.49 21.0498H24.8937L28.0513 9.83248Z"
              class="fill-primary-contrast"
            />
          </svg>
          <span class="text-lg font-semibold leading-tight text-primary-contrast">MutantCheck</span>
        </div>
        <div class="overflow-y-auto flex-1 p-2 flex flex-col gap-4">
          <AppMenu :model="navigation" />
        </div>
      </div>
    </div>
    <div class="min-h-screen flex flex-col relative flex-auto">
      <div
        class="flex justify-between items-center py-4 px-8 bg-surface-0 dark:bg-surface-900 border-b border-surface-200 dark:border-surface-700 relative lg:static"
      >
        <div class="flex items-center">
          <a
            v-styleclass="{
              selector: '#app-sidebar-colored',
              enterFromClass: 'hidden',
              enterActiveClass: 'animate-fadeinleft',
              leaveToClass: 'hidden',
              leaveActiveClass: 'animate-fadeoutleft',
              hideOnOutsideClick: true,
              resizeSelector: '.resize-container-2',
              hideOnResize: true,
            }"
            class="cursor-pointer block lg:hidden text-surface-700 dark:text-surface-100 mr-4"
          >
            <i class="pi pi-bars text-xl!" />
          </a>
        </div>
        <div class="flex items-center gap-5">
          <Button
            @click="toggleLanguage"
            class="px-2 py-1 flex items-center"
            outlined
            rounded
            text
          >
            <img
              :src="currentFlag"
              alt="Language Flag"
              class="w-4 h-auto border border-surface-300 dark:border-surface-600 rounded-sm"
            />
            <span class="font-medium text-surface-600 dark:text-surface-200 uppercase text-sm">
              {{ locale }}
            </span>
          </Button>
          <Button
            @click="toggleConfigurator"
            icon="pi pi-palette"
            class="text-xl! leading-none! text-surface-500 dark:text-surface-400 cursor-pointer"
            text
            rounded
          ></Button>
          <Button
            @click="toggleDarkMode"
            :icon="isDark ? 'pi pi-moon' : 'pi pi-sun'"
            class="text-xl! leading-none! text-surface-500 dark:text-surface-400 cursor-pointer"
            text
            rounded
          ></Button>
        </div>
      </div>
      <div class="p-8 flex flex-col flex-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </div>
    <AppConfigurator ref="appConfigurator" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLayout } from '@/composables/layout'
import AppConfigurator from '@/components/layout/AppConfigurator.vue'
import AppMenu from '@/components/layout/AppMenu.vue'
import { navigation } from '@/constants/navigation.js'
import itFlag from '@/assets/it.svg'
import usFlag from '@/assets/us.svg'
import api from '@/services/api';

const { toggleDarkMode, isDark } = useLayout()
const { locale } = useI18n()

const appConfigurator = ref(null)

function toggleConfigurator(event) {
  appConfigurator.value.toggle(event)
}

function toggleLanguage() {
  locale.value = locale.value === 'it' ? 'en' : 'it'

  localStorage.setItem('user-locale', locale.value);
}

const currentFlag = computed(() => {
  return locale.value === 'it' ? itFlag : usFlag
})
</script>

<style scoped>
/* Transizione Fade */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
