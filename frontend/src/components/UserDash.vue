<template>
  <div class="dashboard-container container-fluid text-dark py-4">
    <header class="text-white bg-dark rounded-3 p-4 p-md-5 mb-5 shadow-lg" style="background: linear-gradient(135deg, #1a202c, #2c5282);">
      <div class="d-flex flex-column flex-md-row justify-content-between align-items-center">
        <div class="mb-4 mb-md-0 text-center text-md-start">
          <h1 class="display-4 fw-semibold">Welcome, {{ firstName }}</h1>
          <p class="lead text-white-50 mb-0">Here's a quick look at your subjects and upcoming quizzes.</p>
        </div>
        <div class="d-flex gap-3">
          <router-link :to="{ name: 'score_history', params: { user_id: userId } }" class="btn btn-outline-light d-flex align-items-center gap-2">
            <i class="bi bi-bar-chart-line-fill"></i>
            <span>Score History</span>
          </router-link>
          <router-link :to="{ name: 'summary_statistics', params: { user_id: userId } }" class="btn btn-warning d-flex align-items-center gap-2 text-dark fw-semibold">
            <i class="bi bi-pie-chart-fill"></i>
            <span>Statistics Summary</span>
          </router-link>
        </div>
      </div>
    </header>

    <div v-if="isLoading" class="d-flex justify-content-center align-items-center" style="min-height: 50vh;">
      <div class="spinner-border text-dark" role="status" style="width: 3rem; height: 3rem;">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else>
      <section class="mb-5">
        <h2 class="mb-4"><i class="bi bi-journal-bookmark-fill me-2"></i>Available Subjects</h2>
        <div class="row g-4">
          <div v-for="subject in subjects" :key="subject.id" class="col-sm-6 col-md-4 col-lg-3">
            <router-link :to="{ name: 'available_chap', params: { subId: subject.id } }" class="text-decoration-none">
              <div class="card subject-card h-100 text-white bg-dark border-light shadow-sm">
                <div class="card-body d-flex justify-content-center align-items-center">
                  <h5 class="card-title mb-0 fw-bold">{{ subject.name || subject.s_name }}</h5>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </section>
      
      <section>
        <h2 class="mb-4"><i class="bi bi-calendar-event me-2"></i>Upcoming Quizzes</h2>
        <div class="row g-4">
          <div v-for="quiz in upcomingQuizzes" :key="quiz.id" class="col-md-6 col-lg-4">
            <div class="card quiz-card h-100 bg-dark text-white border-light shadow">
              <div class="card-body d-flex flex-column">
                <h5 class="card-title text-warning fw-semibold mb-1">{{ quiz.subject }}</h5>
                <p class="text-light small mb-3">Chapter: {{ quiz.chapter }}</p>
                
                <ul class="list-unstyled mb-4">
                  <li><i class="bi bi-calendar-event-fill me-2 text-warning"></i><strong>Date:</strong> {{ formatDate(quiz.date_of_quiz) }}</li>
                  <li><i class="bi bi-clock-fill me-2 text-warning"></i><strong>Duration:</strong> {{ quiz.time_duration }}</li>
                </ul>
                
                <div class="mt-auto d-grid gap-2 d-md-flex justify-content-end">
                  <a href="#" @click.prevent class="btn btn-outline-light btn-sm px-3">Details</a>
                  <router-link :to="{ name: 'start_assessment', params: { quiz_id: quiz.id } }" class="btn btn-warning btn-sm px-3 text-dark fw-semibold">Start</router-link>
                </div>
              </div>
            </div>
          </div>

          <div v-if="upcomingQuizzes.length === 0" class="col-12 text-center text-muted">
            <p>No upcoming quizzes at the moment. Check back later!</p>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      firstName: '',
      userId: null,
      subjects: [],
      quizzes: [],
      isLoading: true, 
    };
  },
  computed: {
    upcomingQuizzes() {
      const now = new Date();
      now.setHours(0, 0, 0, 0); 
      return this.quizzes.filter(quiz => new Date(quiz.date_of_quiz) >= now);
    }
  },
  methods: {
    async fetchDashboardData() {
      this.isLoading = true;
      const token = localStorage.getItem('token');

      if (!token) {
        console.error("No token found. Redirecting to login.");
        this.$router.push('/');
        return;
      }

      try {
        const response = await fetch('/api/user-dashboard', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch dashboard data');
        }

        const data = await response.json();
        this.subjects = data.subjects;
        this.quizzes = data.quizzes;

      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        this.isLoading = false;
      }
    },
    loadUserInfo() {
      const userInfo = JSON.parse(localStorage.getItem('user_info'));
      this.firstName = userInfo?.name || 'User';
      this.userId = userInfo?.id || null;
    },
    formatDate(dateString) {
      const options = { year: 'numeric', month: 'long', day: 'numeric' };
      return new Date(dateString).toLocaleDateString(undefined, options);
    }
  },
  created() {
    this.loadUserInfo();
    this.fetchDashboardData();
  }
}
</script>

<style scoped>
.subject-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
  border-color: #ffc107; 
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.btn-warning:hover {
  filter: brightness(1.1);
}

.spinner-border.text-dark {
  color: #343a40 !important;
}
</style>
