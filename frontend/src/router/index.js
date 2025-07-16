import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/components/LoginPage.vue';
import Register from '@/components/Register.vue';
import DashBoard from '@/components/AdminDash.vue';
import SubMange from '@/components/SubMange.vue';

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
    // {
    //   path: '/subject/:sub_id/edit',
    //   name: 'update-sub',
    //   component: UpdateSubjectPage
    // },
    // {
    // path: '/subject/:sub_id/chapter',
    // name: 'add-chapter',
    // component: ChapterManager
    // }
  ],
})

export default router
