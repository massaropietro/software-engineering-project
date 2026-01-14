import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import ProjectsList from '@/views/projects/ProjectsList.vue'
import ExampleView from '@/views/ExampleView.vue'
import {routerPaths} from "@/constants/constants.js";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: routerPaths.home.path,
          name: routerPaths.home.name,
          component: ProjectsList,
        },
        {
          path: 'example',
          name: 'example',
          component: ExampleView,
        },
      ],
    },
  ],
})

export default router
