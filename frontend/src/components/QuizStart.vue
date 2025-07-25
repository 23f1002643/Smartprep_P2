<template>
  <div class="quiz-container container mt-4">
    <div class="card bg-dark text-white shadow-lg">
      <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
          <h4>{{ quiz.q_name }}</h4>
          <h5 class="text-warning font-monospace">Time Left: {{ timerDisplay }}</h5>
        </div>
        <div class="d-flex justify-content-between">
          <h6 class="text-white-50">Subject: {{ quiz.chapter?.course?.s_name }}</h6>
          <h6 class="text-white-50">Chapter: {{ quiz.chapter?.name }}</h6>
        </div>
      </div>

      <div class="card-body">
        <form @submit.prevent="submitQuiz">
          <div v-for="(question, index) in questions" :key="question.id" class="question-card card bg-secondary mb-3">
            <div class="card-body">
              <p class="question">{{ index + 1 }}. {{ question.statement }}</p>
              <div class="options">
                <div class="form-check" v-for="opt in 4" :key="opt">
                  <input class="form-check-input" type="radio"
                    :name="`question_${question.id}`"
                    :id="`opt${opt}_${question.id}`"
                    :value="String(opt)"
                    v-model="answers[question.id]"
                  >
                  <label class="form-check-label" :for="`opt${opt}_${question.id}`">{{ question[`opt${opt}`] }}</label>
                </div>
              </div>
            </div>
          </div>
          <button type="submit" class="btn btn-primary w-100 mt-3">Submit Quiz</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    quiz_id: {
      type: [String, Number],
      required: true,
    }
  },
  data() {
    return {
      quiz: {},
      questions: [],
      answers: {},
      countdown: 0,
      timerDisplay: '00:00',
      timerInterval: null,
    };
  },
  methods: {
    parseDurationToSeconds(durationStr) {
      const parts = durationStr.split(':').map(Number);
      return parts[0] * 3600 + parts[1] * 60 + parts[2];
    },
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    },
    async fetchQuizData() {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`/api/user/quiz/${this.quiz_id}/start`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!res.ok) throw new Error('Failed to load quiz');

        const data = await res.json();
        this.quiz = data.quiz;
        this.questions = data.questions;

        this.countdown = this.parseDurationToSeconds(data.quiz.time_duration);
        this.startCountdown();

      } catch (err) {
        console.error(err);
      }
    },
    startCountdown() {
      this.timerDisplay = this.formatTime(this.countdown);
      this.timerInterval = setInterval(() => {
        this.countdown--;
        this.timerDisplay = this.formatTime(this.countdown);
        if (this.countdown <= 0) {
          clearInterval(this.timerInterval);
          alert("Time's up! Submitting your quiz.");
          this.submitQuiz();
        }
      }, 1000);
    },
    async submitQuiz() {
      clearInterval(this.timerInterval);
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`/api/user/quiz/${this.quiz_id}/submit`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ answers: this.answers })
        });

        if (!res.ok) throw new Error('Submission failed');

        const result = await res.json();
        this.$router.push({
          name: 'quiz_result',
          params: {
            quiz_id: this.quiz_id,
            score: result.score.toString(),
            max_marks: result.max_marks.toString()
          }
        });

      } catch (err) {
        console.error('❌ Submission error:', err);
      }
    }
  },
  mounted() {
    this.fetchQuizData();
  },
  beforeUnmount() {
    clearInterval(this.timerInterval);
  }
};
</script>

<style scoped>
.quiz-container {
  padding: 20px;
}
.question-card {
  border-radius: 8px;
}
.options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
</style>
