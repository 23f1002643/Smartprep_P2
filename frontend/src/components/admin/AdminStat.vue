<template>
  <div class="container py-4">
    <h3 class="text-center mb-4">Admin Statistics</h3>

    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="chartData" class="row">
      <!-- 1. Quiz Attempts by Subject (for Pie Chart) -->
      <div class="col-md-6 mb-4">
        <canvas id="attemptsBySubjectChart" height="200"></canvas>
      </div>

      <!-- 2. Average Score by Quiz (for Bar Chart) -->
      <div class="col-md-6 mb-4">
        <canvas id="avgScoreByQuizChart" height="200"></canvas>
      </div>

      <!-- 3. Total Attempts per Quiz (for Bar Chart) -->
      <div class="col-md-6 mb-4">
        <canvas id="attemptsPerQuizChart" height="200"></canvas>
      </div>

      <!-- 4. Average Score by Subject (for Bar Chart) -->
      <div class="col-md-6 mb-4">
        <canvas id="avgScoreBySubjectChart" height="200"></canvas>
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
  mounted() {
    this.fetchAdminStatistics();
  },
  methods: {
    async fetchAdminStatistics() {
      this.loading = true;
      try {
        const token = localStorage.getItem('token');
        if (!token) throw new Error("Not logged in");

        const response = await fetch('/api/admin/statistics', {
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
      // Destroy previous charts to prevent memory leaks
      this.chartInstances.forEach(chart => chart.destroy());
      this.chartInstances = [];
      // === 1. Quiz Attempts by Subject (Pie Chart) ===
      const attemptsBySubjectLabels = Object.keys(this.chartData.attempts_by_subject);
      const attemptsBySubjectData = Object.values(this.chartData.attempts_by_subject);
      const attemptsBySubjectCtx = document.getElementById("attemptsBySubjectChart")?.getContext("2d");
      if (attemptsBySubjectCtx) {
        const chart = new Chart(attemptsBySubjectCtx, {
          type: "pie",
          data: {
            labels: attemptsBySubjectLabels,
            datasets: [{
              label: "Quiz Attempts",
              data: attemptsBySubjectData,
              backgroundColor: ["#20BDFF", "#FFD700", "#FF8C00", "#FF69B4", "#00BFFF"],
              hoverBorderColor: "#fff"
            }]
          },
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: "Quiz Attempts by Subject"
              },
              legend: {
                position: "right"
              }
            }
          }
        });
        this.chartInstances.push(chart);
      }
      // === 2. Average Score by Quiz (Bar Chart) ===
      const avgScoreByQuizLabels = Object.keys(this.chartData.avg_score_by_quiz);
      const avgScoreByQuizData = Object.values(this.chartData.avg_score_by_quiz);
      const avgScoreByQuizCtx = document.getElementById("avgScoreByQuizChart")?.getContext("2d");
      if (avgScoreByQuizCtx) {
        const chart = new Chart(avgScoreByQuizCtx, {
          type: "bar",
          data: {
            labels: avgScoreByQuizLabels,
            datasets: [{
              label: "Average Score (%)",
              data: avgScoreByQuizData,
              backgroundColor: "#20BDFF"
            }]
          },
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: "Average Score by Quiz"
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 100
              }
            }
          }
        });
        this.chartInstances.push(chart);
      }
      // === 3. Total Attempts per Quiz (Bar Chart) ===
      const attemptsPerQuizLabels = Object.keys(this.chartData.attempts_per_quiz);
      const attemptsPerQuizData = Object.values(this.chartData.attempts_per_quiz);
      const attemptsPerQuizCtx = document.getElementById("attemptsPerQuizChart")?.getContext("2d");
      if (attemptsPerQuizCtx) {
        const chart = new Chart(attemptsPerQuizCtx, {
          type: "bar",
          data: {
            labels: attemptsPerQuizLabels,
            datasets: [{
              label: "Total Attempts",
              data: attemptsPerQuizData,
              backgroundColor: "#00BFFF"
            }]
          },
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: "Total Attempts per Quiz"
              }
            },
            scales: {
              y: {
                beginAtZero: true
              }
            }
          }
        });
        this.chartInstances.push(chart);
      }
      // === 4. Average Score by Subject (Bar Chart) ===
      const avgScoreBySubjectLabels = Object.keys(this.chartData.avg_score_by_subject);
      const avgScoreBySubjectData = Object.values(this.chartData.avg_score_by_subject);
      const avgScoreBySubjectCtx = document.getElementById("avgScoreBySubjectChart")?.getContext("2d");
      if (avgScoreBySubjectCtx) {
        const chart = new Chart(avgScoreBySubjectCtx, {
          type: "bar",
          data: {
            labels: avgScoreBySubjectLabels,
            datasets: [{
              label: "Average Score (%)",
              data: avgScoreBySubjectData,
              backgroundColor: "#FF8C00"
            }]
          },
          options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: "Average Score by Subject"
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 100
              }
            }
          }
        });
        this.chartInstances.push(chart);
      }
    }
  }
};
</script>

<style scoped>
canvas {
  background: white;
  padding: 15px;
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}
</style>
