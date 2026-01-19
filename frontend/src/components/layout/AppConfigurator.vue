<template>
  <Popover ref="op" class="w-[20rem]">
    <div class="flex flex-col gap-4">
      <!-- Primary Colors -->
      <div>
        <span class="text-sm font-semibold text-surface-900 dark:text-surface-0 mb-2 block"
          >Primary</span
        >
        <div class="grid grid-cols-4 gap-2 mr-auto ml-auto">
          <button
            v-for="color in primaryColors"
            :key="color.name"
            @click="setPrimary(color.name)"
            class="w-6 h-6 rounded-full cursor-pointer flex items-center justify-center hover:scale-110 focus:outline-none"
            :style="{ backgroundColor: color.palette[500] }"
          >
            <i
              v-if="layoutConfig.primary === color.name"
              class="pi pi-check text-white text-[0.6rem]"
            ></i>
          </button>
        </div>
      </div>

      <!-- Surface Colors -->
      <div>
        <span class="text-sm font-semibold text-surface-900 dark:text-surface-0 mb-2 block"
          >Surface</span
        >
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="surface in surfaces"
            :key="surface.name"
            @click="setSurface(surface.name)"
            class="w-6 h-6 rounded-full cursor-pointer flex items-center justify-center hover:scale-110 focus:outline-none"
            :style="{ backgroundColor: surface.palette[500] }"
          >
            <i
              v-if="layoutConfig.surface === surface.name"
              class="pi pi-check text-surface-900 dark:text-surface-0 text-[0.6rem]"
            ></i>
          </button>
        </div>
      </div>
    </div>
  </Popover>
</template>

<script setup>
import { ref } from 'vue'
import { useLayout } from '@/composables/layout.js'
import Popover from 'primevue/popover'
import SelectButton from 'primevue/selectbutton'

const { layoutConfig, setPrimary, setSurface, primaryColors, surfaces } =
  useLayout()

const op = ref(null)

function toggle(event) {
  op.value.toggle(event)
}

defineExpose({
  toggle,
})
</script>
