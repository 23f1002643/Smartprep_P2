<template>
  <div class="container py-4">
    <h3 class="text-center mb-4">Admin Statistics</h3>

    <div v-if="loading" class="text-center my-4">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-if="chartData" class="row g-4">
      <!-- Pie Chart -->
      <div class="col-md-6">
        <div class="chart-wrapper">
          <canvas id="attemptsBySubjectChart"></canvas>
        </div>
      </div>

      <!-- Bar Charts -->
      <div class="col-md-6">
        <div class="chart-wrapper">
          <canvas id="avgScoreByQuizChart"></canvas>
        </div>
      </div>

      <div class="col-md-6">
        <div class="chart-wrapper">
          <canvas id="attemptsPerQuizChart"></canvas>
        </div>
      </div>

      <div class="col-md-6">
        <div class="chart-wrapper">
          <canvas id="avgScoreBySubjectChart"></canvas>
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
  mounted() {
    this.fetchAdminStatistics();
    window.addEventListener("resize", this.redrawCharts);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.redrawCharts);
    this.destroyCharts();
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
    destroyCharts() {
      this.chartInstances.forEach(chart => chart.destroy());
      this.chartInstances = [];
    },
    redrawCharts() {
      if (this.chartData) {
        this.destroyCharts();
        this.$nextTick(() => this.renderCharts());
      }
    },
    renderCharts() {
      this.destroyCharts();

      const charts = [
        {
          id: "attemptsBySubjectChart",
          type: "pie",
          data: {
            labels: Object.keys(this.chartData.attempts_by_subject),
            datasets: [{
              data: Object.values(this.chartData.attempts_by_subject),
              backgroundColor: ["#20BDFF", "#FFD700", "#FF8C00", "#FF69B4", "#00BFFF"]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: "Quiz Attempts by Subject" }, legend: { position: 'right' } }
          }
        },
        {
          id: "avgScoreByQuizChart",
          type: "bar",
          data: {
            labels: Object.keys(this.chartData.avg_score_by_quiz),
            datasets: [{
              label: "Avg. Score (%)",
              data: Object.values(this.chartData.avg_score_by_quiz),
              backgroundColor: "#20BDFF"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: "Average Score by Quiz" } },
            scales: { y: { beginAtZero: true, max: 100 } }
          }
        },
        {
          id: "attemptsPerQuizChart",
          type: "bar",
          data: {
            labels: Object.keys(this.chartData.attempts_per_quiz),
            datasets: [{
              label: "Total Attempts",
              data: Object.values(this.chartData.attempts_per_quiz),
              backgroundColor: "#00BFFF"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: "Total Attempts per Quiz" } },
            scales: { y: { beginAtZero: true } }
          }
        },
        {
          id: "avgScoreBySubjectChart",
          type: "bar",
          data: {
            labels: Object.keys(this.chartData.avg_score_by_subject),
            datasets: [{
              label: "Avg. Score (%)",
              data: Object.values(this.chartData.avg_score_by_subject),
              backgroundColor: "#FF8C00"
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { title: { display: true, text: "Average Score by Subject" } },
            scales: { y: { beginAtZero: true, max: 100 } }
          }
        }
      ];

      charts.forEach(({ id, type, data, options }) => {
        const ctx = document.getElementById(id)?.getContext("2d");
        if (ctx) {
          const chart = new Chart(ctx, { type, data, options });
          this.chartInstances.push(chart);
        }
      });
    }
  }
};
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  height: 350px;
  background: #fff;
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
