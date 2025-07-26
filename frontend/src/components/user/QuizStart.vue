<template>
  <div class="quiz-page-container py-4">
    <div class="container">
      <div class="card shadow-lg quiz-main-card">
        <div class="card-header bg-dark text-white border-bottom border-secondary p-3">
          <div class="d-flex flex-column flex-md-row justify-content-between align-items-center">
            <h4 class="mb-2 mb-md-0 text-center text-md-start">{{ quiz.q_name }}</h4>
            <h5 class="text-warning font-monospace timer-display">
              <i class="bi bi-clock-fill me-2"></i>{{ timerDisplay }}
            </h5>
          </div>
          <div class="d-flex justify-content-between mt-2">
            <h6 class="text-white-50 small">Subject: {{ quiz.chapter?.course?.s_name }}</h6>
            <h6 class="text-white-50 small">Chapter: {{ quiz.chapter?.name }}</h6>
          </div>
        </div>
        <div class="card-body p-lg-4">
          <form @submit.prevent="submitQuiz">
            <div v-for="(question, index) in questions" :key="question.id" class="question-card card mb-4">
              <div class="card-body">
                <p class="question-statement">
                  <span class="question-number">{{ index + 1 }}.</span>
                  {{ question.statement }}
                </p>
                <div class="options-grid">
                  <div class="option-wrapper" v-for="opt in 4" :key="opt">
                    <input class="form-check-input visually-hidden" type="radio"
                      :name="`question_${question.id}`"
                      :id="`opt${opt}_${question.id}`"
                      :value="String(opt)"
                      v-model="answers[question.id]"
                    >
                    <label class="form-check-label option-label" :for="`opt${opt}_${question.id}`">
                      {{ question[`opt${opt}`] }}
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <button type="submit" class="btn btn-primary btn-lg w-100 mt-3 fw-bold submit-btn">
              <i class="bi bi-check-circle-fill me-2"></i>Submit Quiz
            </button>
          </form>
        </div>
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
      if (!durationStr) return 0;
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
.quiz-page-container {
  background-color: #f0f2f5; 
}

.quiz-main-card {
  border: none;
  background-color: #ffffff; 
}

.timer-display {
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 50px;
  font-size: 1.1rem;
}

.question-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0; 
  border-radius: 12px;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.question-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.question-statement {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  color: #212529; 
}
.question-number {
  color: #0d6efd; 
  font-weight: bold;
  margin-right: 0.5rem;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.option-label {
  display: block;
  background-color: #f8f9fa; 
  color: #495057;
  padding: 1rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid #e9ecef;
  width: 100%;
}

.option-label:hover {
  border-color: #0d6efd;
  color: #0d6efd;
}

.form-check-input:checked + .option-label {
  background-color: #0d6efd;
  border-color: #0d6efd;
  color: white;
  font-weight: bold;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.3);
}

.submit-btn {
  padding: 0.75rem;
  font-size: 1.2rem;
  letter-spacing: 1px;
  background-color: #0d6efd; 
  border: none;
}
</style>
