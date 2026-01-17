import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import ProjectsList from '@/views/projects/ProjectsList.vue'
import ExampleView from '@/views/ExampleView.vue'
import ProjectDetails from '@/views/projects/ProjectDetails.vue'
import NotFoundView from '@/views/NotFoundView.vue'

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
          path: "projects",
          children: [
            {
              path: ':projectId',
              name: 'project-details',
              component: ProjectDetails,
              props: true
            }
          ]
        },
        {
          path: 'example',
          name: 'example',
          component: ExampleView,
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    },
  ],
})

export default router
