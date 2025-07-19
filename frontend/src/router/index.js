import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/components/LoginPage.vue';
import Register from '@/components/Register.vue';
import DashBoard from '@/components/AdminDash.vue';
import SubMange from '@/components/SubMange.vue';
import ChapMange from '@/components/ChapMange.vue';
import Assessment from '@/components/Assessment.vue';
import ProblemStatement from '@/components/ProblemStatement.vue';
import UserMange from '@/components/UserMange.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login-page',
      component: LoginPage,
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
    },
    {
      path: '/admin/dashboard',
      name: 'dashboard',
      component: DashBoard,
    },
    {
      path: '/logout',
      name: 'logout',
    },
    {
      path: '/sub',
      name: 'submange',
      component: SubMange,
    },
    {
      path: '/sub/:subId/chapters',
      name: 'chap_mange',
      component: ChapMange,
      props: true, 
    },
    {
      path: '/sub/:subId/chapters/:chapId/quiz',
      name: 'quiz_manage',
      component: Assessment,
      props: true, 
    },
    {
      path: '/sub/:subId/chapters/:chapId/quiz/:examId/questions',
      name: 'problem_statement',
      component: ProblemStatement,
      props: true,
    },
    {
      path: '/admin/users',
      name: 'user_mange',
      component: UserMange,
    }

  ],
})

export default router
