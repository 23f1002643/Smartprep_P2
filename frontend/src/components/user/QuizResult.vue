<template>
  <div class="container mt-5">
    <div class="row g-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h4 v-if="quiz">Quiz: {{ quiz.q_name }}</h4>
            <h4 v-else>Loading quiz...</h4>
          </div>
          <div class="card-body">
            <p class="mb-2">Chapter: {{ quiz?.chapter?.name || 'N/A' }}</p>
            <p class="mb-2">Subject: {{ quiz?.chapter?.course?.s_name || 'N/A' }}</p>
            <p class="mb-2">Date: {{ quiz?.date_of_quiz || 'N/A' }}</p>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-warning text-white">
            <h4 class="mb-0">Your Result</h4>
          </div>
          <div class="card-body">
            <h1 class="display-4">
              {{ scoreNumber }}/{{ maxMarksNumber }}
              <span class="badge" :class="getClass(scoreNumber / maxMarksNumber)">
                {{ getPercentage(scoreNumber / maxMarksNumber) }}%
              </span>
            </h1>
            <p class="mb-2">You scored {{ getPercentage(scoreNumber / maxMarksNumber) }}%</p>
            <p v-if="scoreNumber / maxMarksNumber < 0.4" class="text-danger">
              <i class="bi bi-emoji-frown"></i> You need to work harder!
            </p>
            <p v-else-if="scoreNumber / maxMarksNumber < 0.7" class="text-warning">
              <i class="bi bi-emoji-neutral"></i> You did okay!
            </p>
            <p v-else class="text-success">
              <i class="bi bi-emoji-smile"></i> Well done!
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    quiz_id: [String, Number],
    score: [String, Number],
    max_marks: [String, Number],
  },
  data() {
    return {
      quiz: null
    };
  },
  computed: {
    scoreNumber() {
      return Number(this.score);
    },
    maxMarksNumber() {
      return Number(this.max_marks);
    }
  },
  mounted() {
    this.fetchQuizData();
  },
  methods: {
    async fetchQuizData() {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`/api/user/quiz/${this.quiz_id}/start`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('Failed to fetch quiz');

        const data = await res.json();
        this.quiz = data.quiz;

      } catch (err) {
        console.error('Quiz fetch error:', err);
      }
    },
    getClass(percentage) {
      if (percentage < 0.4) return 'bg-danger';
      if (percentage < 0.7) return 'bg-warning';
      return 'bg-success';
    },
    getPercentage(percentage) {
      return Math.round(percentage * 100);
    }
  }
};
</script>

<style scoped>
.card-header {
  border-bottom: 0;
}
</style>
