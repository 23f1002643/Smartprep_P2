<template>
  <div class="container mt-4">
    <div class="dashboard">
      <h2 class="text-white mb-4">Available Quizzes</h2>
      <div v-if="quizzes.length > 0" class="row row-cols-1 row-cols-md-2 row-cols-lg-4 g-4">
        <div v-for="quiz in quizzes" :key="quiz.id" class="col">
          <div class="card quiz-card h-100 bg-dark text-white border-light shadow-sm">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">Subject : {{ quiz.chapter.course.s_name }}</h5>
              <h6 class="card-subtitle " >Chapter: {{ quiz.chapter.name }}</h6>
              <hr class="text-white-50">
              <p><strong>Quiz Name:</strong> {{ quiz.q_name }}</p>
              <p><strong>No. of Questions:</strong> {{ quiz.questions }}</p>
              <p><strong>Duration:</strong> {{ quiz.time_duration }}</p>
              <p><strong>Date:</strong> {{ quiz.date_of_quiz }}</p>
              <div class="mt-auto d-flex gap-2">
                <router-link :to="{ name: 'start_assessment', params: { quiz_id: quiz.id } }" class="btn btn-warning text-dark fw-semibold" style="width: 100%;">
                  Start Quiz
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center text-white-50 py-5">
        <p>No quizzes found for this chapter.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    chapId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      quizzes: [],
    };
  },
  methods: {
    async getQuizzes() {
      const tkn = localStorage.getItem('token');
      if (!tkn) {
        console.error('No token found, redirecting to login.');
        this.$router.push({ name: 'login-page' });
        return;
      }
      
      try {
        const response = await fetch(`/api/user/chap/${this.chapId}`, {
          headers: {
            'Authorization': `Bearer ${tkn}`,
          },
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        this.quizzes = data.quizzes;

      } catch (error) {
        console.error("Failed to fetch quizzes:", error);
      }
    },
  },
  mounted() {
    this.getQuizzes();
  },
};
</script>

<style scoped>
.dashboard {
  background-color: #343a40;
  padding: 20px;
  border-radius: 10px;
}

.quiz-card {
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  min-height: 320px; 
}

.text-white {
  color: #fff;
}
</style>
