<template>
  <li v-if="item.separator" class="border-t border-primary-400 dark:border-primary-300 my-0"></li>
  <li v-else>
    <!-- Root Item (Collapsible Header) -->
    <div
      v-if="root && item.items"
      v-styleclass="{
        selector: '@next',
        enterFromClass: 'hidden',
        enterActiveClass: 'animate-slidedown',
        leaveToClass: 'hidden',
        leaveActiveClass: 'animate-slideup',
      }"
      class="flex items-center cursor-pointer p-3 gap-4 rounded-lg text-surface-0 hover:bg-primary-emphasis"
    >
      <span class="font-semibold text-base leading-tight text-primary-contrast">
        {{ $t(item.label) }}
        }}</span
      >
      <i class="pi pi-angle-down text-base! leading-none! text-primary-contrast ml-auto" />
    </div>

    <!-- Submenu Item (Nested Collapsible) -->
    <a
      v-else-if="item.items"
      v-styleclass="{
        selector: '@next',
        enterFromClass: 'hidden',
        enterActiveClass: 'animate-slidedown',
        leaveToClass: 'hidden',
        leaveActiveClass: 'animate-slideup',
      }"
      class="flex items-center cursor-pointer p-3 gap-2 rounded-lg text-primary-contrast hover:bg-primary-emphasis select-none"
    >
      <i :class="[item.icon, 'text-base! leading-none! text-primary-contrast']" />
      <span class="font-medium text-base leading-tight">{{ $t(item.label) }}</span>
      <i class="pi pi-angle-down text-base! leading-none! text-primary-contrast ml-auto" />
    </a>

    <!-- Leaf Item (Link) -->
    <router-link
      v-else-if="item.route"
      :to="{ name: item.route }"
      :class="{ 'bg-primary-emphasis font-bold': item.route === $route.name }"
      class="flex items-center cursor-pointer p-3 gap-2 rounded-lg text-primary-contrast hover:bg-primary-emphasis select-none transition-colors"
    >
      <i :class="[item.icon, 'text-base! leading-none! text-primary-contrast']" />
      <span class="font-medium text-base leading-tight">{{ $t(item.label) }}</span>

      <Badge
        v-if="item.badge"
        :value="item.badge.value"
        :severity="item.badge.severity"
        class="ml-auto h-5! min-w-5! text-xs! font-bold! leading-tight! rounded-xl! bg-primary-contrast text-primary"
      />
    </router-link>

    <!-- Leaf Item (No Link - e.g. placeholder) -->
    <a
      v-else
      class="flex items-center cursor-pointer p-3 gap-2 rounded-lg text-primary-contrast hover:bg-primary-emphasis select-none"
    >
      <i :class="[item.icon, 'text-base! leading-none! text-primary-contrast']" />
      <span class="font-medium text-base leading-tight">{{ $t(item.label) }}</span>
      <Badge
        v-if="item.badge"
        :value="item.badge.value"
        :severity="item.badge.severity"
        class="ml-auto h-5! min-w-5! text-xs! font-bold! leading-tight! rounded-xl! bg-primary-contrast text-primary"
      />
    </a>

    <!-- Children (Recursive render) -->
    <ul
      v-if="item.items"
      class="list-none m-0 overflow-hidden flex flex-col gap-1"
      :class="{ 'pl-8': !root, 'mt-1': !root, hidden: !root }"
    >
      <template v-for="(child, i) in item.items" :key="i">
        <AppMenuItem :item="child" :index="i" :root="false" />
      </template>
    </ul>
  </li>
</template>

<script setup>
import Badge from 'primevue/badge'

defineProps({
  item: {
    type: Object,
    default: () => ({}),
  },
  index: {
    type: Number,
    default: 0,
  },
  root: {
    type: Boolean,
    default: true,
  },
})
</script>
