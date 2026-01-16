import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import ProjectsList from '@/views/projects/ProjectsList.vue'
import ExampleView from '@/views/ExampleView.vue'
import ProjectDetailsView from "@/views/projects/ProjectDetailsView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: '',
          name: 'home',
          component: ProjectsList,
        },
        {
          path: 'example',
          name: 'example',
          component: ExampleView,
        },
        {
          path: '/project-details',
          name: 'project-details',
          component: ProjectDetailsView
        },
      ],
    },
  ],
})

export default router
