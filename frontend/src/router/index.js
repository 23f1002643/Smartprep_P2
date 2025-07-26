import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '@/components/LoginPage.vue';
import Register from '@/components/Register.vue';
import AdminDash from '@/components/admin/AdminDash.vue';
import SubMange from '@/components/admin/SubMange.vue';
import ChapMange from '@/components/admin/ChapMange.vue';
import Assessment from '@/components/admin/Assessment.vue';
import ProblemStatement from '@/components/admin/ProblemStatement.vue';
import UserMange from '@/components/admin/UserMange.vue';
import UserDash from '@/components/user/UserDash.vue';
import AvailableChap from '@/components/user/AvailableChap.vue';
import ViewQuizzes from '@/components/user/ViewQuizzes.vue';
import QuizStart from '@/components/user/QuizStart.vue';
import QuizResult from '@/components/user/QuizResult.vue';
import ScoreHistory from '@/components/user/ScoreHistory.vue';
import UserStat from '@/components/user/UserStat.vue';
import AdminStat from '@/components/admin/AdminStat.vue';
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
      component: AdminDash,
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
    },
    {
      path: '/user-dashboard',
      name: 'user_dash',
      component: UserDash,
    },
    {
      path: '/user/subject/:subId/chapters',
      name: 'available_chap',
      component: AvailableChap,
      props: true
    },
    {
      path: '/user/chapters/:chapId/assesments',
      name: 'available_quiz',
      component: ViewQuizzes,
      props: true
    },
    {
      path: '/user/quiz/:quiz_id/Assessment',
      name: 'start_assessment',
      component: QuizStart,
      props: true
    },
    {
      path: '/user/quiz/:quiz_id/Assessment/:score/:max_marks',
      name: 'quiz_result',
      component: QuizResult,
      props: true
    },
    {
      path: '/user/:user_id/score_history',
      name: 'score_history',
      component: ScoreHistory,
    },
    {
      path: '/user/:user_id/summary-statistics',
      name: 'summary_statistics',
      component: UserStat,
    },
    {
      path: '/admin/statistics',
      name: 'admin_stat',
      component: AdminStat,
    },
  ],
})

export default router
