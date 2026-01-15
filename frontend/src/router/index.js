import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import ProjectsList from '@/views/projects/ProjectsList.vue'
import ExampleView from '@/views/ExampleView.vue'
import ProjectForm from "@/views/projects/ProjectForm.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        {
          path: 'projects',
          name: 'projects-list',
          component: ProjectsList,
          meta: {
            title: "Projects"
          },
        },
        {
            path: 'projects/add',
            name: 'project-add',
            component: ProjectForm,
            meta: {
                title: 'New Project'
            }
        },
        {
          path: 'example',
          name: 'example',
          component: ExampleView,
          meta: {
            title: "Example"
          }
        },
      ],
    },
  ],
})

export default router
