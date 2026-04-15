import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import ProjectsList from '@/views/projects/ProjectsList.vue'
import ExampleView from '@/views/ExampleView.vue'
import ProjectCreate from "@/views/projects/ProjectCreate.vue";
import ProjectDetails from '@/views/projects/ProjectDetails.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import ProjectService from "@/services/ProjectService.js";
import ProjectAnalysis  from "@/components/projects/ProjectAnalysis.vue";
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
            component: ProjectCreate,
            meta: {
                title: 'New Project'
            }
        },
        {
          path: "projects",
          children: [
            {
              path: ':projectId',
              name: 'project-details',
              component: ProjectDetails,
              props: true,

            }
          ]
        },
        {
          path: 'analyses/:secretToken',
          name: 'project-analysis',
          component: ProjectAnalysis,
          meta: {
            title: "Project Analysis"
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
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundView
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  try {
    const isProjectRoute =
      to.name === 'project-details' ||
      to.matched.some(m => m.path && m.path.includes(':projectId'));

    if (isProjectRoute && to.params.projectId) {
      const res = await ProjectService.getProject(to.params.projectId);
      const title = res.data.name;

      to.meta = { ...to.meta, title };
      (to.matched || []).forEach(m => {
        m.meta = { ...m.meta, title };
      });

      document.title = title;
    }
  } catch (err) {
    console.error('Errore caricamento progetto per titolo breadcrumb:', err);
  }
  next();
});

export default router
