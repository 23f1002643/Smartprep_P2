<template>
  <div class="container py-4">
    <h3 class="text-center mb-4">User Statistics</h3>
    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>
    <div v-if="chartData">
      <!-- Row 1: Avg Score & Score Comparison -->
      <div class="row mb-4">
        <div class="col-lg-6 col-md-12 mb-4">
          <canvas id="avgScoreChart"></canvas>
        </div>
        <div class="col-lg-6 col-md-12 mb-4">
          <canvas id="scoreComparisonChart"></canvas>
        </div>
      </div>
      <!-- Row 2: Quiz Scores & Attempt Pie Chart -->
      <div class="row mb-4">
        <div class="col-lg-6 col-md-12 mb-4">
          <canvas id="quizScoresChart"></canvas>
        </div>
        <div class="col-lg-6 col-md-12 mb-4">
          <canvas id="attemptChart"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import Chart from 'chart.js/auto';

export default {
  data() {
    return {
      loading: false,
      error: null,
      chartData: null,
      chartInstances: []
    };
  },
  methods: {
    async fetchMyStatistics() {
      this.loading = true;
      try {
        const token = localStorage.getItem('token');
        if (!token) throw new Error("Not logged in");
        const response = await fetch('/api/user/statistics', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!response.ok) throw new Error("Failed to fetch stats");
        const data = await response.json();
        this.chartData = data;
        await nextTick();
        this.renderCharts();
      } catch (err) {
        this.error = err.message || "Something went wrong";
      } finally {
        this.loading = false;
      }
    },

    renderCharts() {
      // Destroy previous charts
      this.chartInstances.forEach(chart => chart.destroy());
      this.chartInstances = [];
      // 1. Average Score by Subject
      const avgLabels = Object.keys(this.chartData.my_avg_score_by_subject || {});
      const avgData = Object.values(this.chartData.my_avg_score_by_subject || {});
      const avgCtx = document.getElementById("avgScoreChart")?.getContext("2d");
      if (avgCtx) {
        const chart = new Chart(avgCtx, {
          type: "bar",
          data: {
            labels: avgLabels,
            datasets: [{
              label: "Average Score (%)",
              data: avgData,
              backgroundColor: "#20BDFF"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: { display: true, text: "Average Score by Subject" }
            },
            scales: {
              y: { beginAtZero: true, max: 100 }
            }
          }
        });
        this.chartInstances.push(chart);
      }

      // 2. Score Comparison
      const compLabels = Object.keys(this.chartData.my_score_comparison || {});
      const avgComp = compLabels.map(sub => this.chartData.my_score_comparison[sub].average);
      const highComp = compLabels.map(sub => this.chartData.my_score_comparison[sub].highest);
      const compCtx = document.getElementById("scoreComparisonChart")?.getContext("2d");
      if (compCtx) {
        const chart = new Chart(compCtx, {
          type: "bar",
          data: {
            labels: compLabels,
            datasets: [
              { label: "Average", data: avgComp, backgroundColor: "#00BFFF" },
              { label: "Highest", data: highComp, backgroundColor: "#FF5733" }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: { display: true, text: "Average vs Highest Score per Subject" }
            },
            scales: {
              y: { beginAtZero: true, max: 100 }
            }
          }
        });
        this.chartInstances.push(chart);
      }

      // 3. Quiz Scores
      const attemptedQuizzes = this.chartData.my_quiz_scores || [];
      const quizLabels = attemptedQuizzes.map(q => q.name);
      const quizData = attemptedQuizzes.map(q => q.score);
      const quizCtx = document.getElementById("quizScoresChart")?.getContext("2d");
      if (quizCtx) {
        const chart = new Chart(quizCtx, {
          type: "bar",
          data: {
            labels: quizLabels,
            datasets: [{
              label: "Score (%)",
              data: quizData,
              backgroundColor: "#FFC300"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: { display: true, text: "Score in Each Attempted Quiz" }
            },
            scales: {
              y: { beginAtZero: true, max: 100 }
            }
          }
        });
        this.chartInstances.push(chart);
      }

      // 4. Attempt Distribution Pie Chart
      const attemptLabels = Object.keys(this.chartData.my_attempt_distribution || {});
      const attemptData = Object.values(this.chartData.my_attempt_distribution || {});
      const attemptCtx = document.getElementById("attemptChart")?.getContext("2d");
      if (attemptCtx) {
        const chart = new Chart(attemptCtx, {
          type: "pie",
          data: {
            labels: attemptLabels,
            datasets: [{
              label: "Quiz Attempts",
              data: attemptData,
              backgroundColor: ["#5433FF", "#A5FECB", "#20BDFF", "#FF5733", "#FFC300"]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              title: { display: true, text: "Quiz Attempt Distribution" }
            }
          }
        });
        this.chartInstances.push(chart);
      }
    }
  },
  mounted() {
    this.fetchMyStatistics();
  }
};
</script>

<style scoped>
canvas {
  background: white;
  padding: 10px;
  height: 300px !important;
  width: 100% !important;
  border-radius: 12px;
  box-shadow: 0 0 12px rgba(0,0,0,0.1);
}
</style>
