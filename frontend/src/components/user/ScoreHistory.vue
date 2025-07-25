<template>
  <div class="container mt-4">
    <h2 class="text-white">Score History</h2>
    <div class="table-responsive">
      <table class="table table-hover align-middle">
        <thead class="table-light">
          <tr>
            <th>Subject</th>
            <th>Chapter</th>
            <th>Quiz Name</th>
            <th>Score</th>
            <th>Date of Attempt</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="score in scores" :key="score.id">
            <td>{{ score.subject }}</td>
            <td>{{ score.chapter }}</td>
            <td>{{ score.quiz_name }}</td>
            <td>{{ score.score }}</td>
            <td>{{ score.date_of_attempt }}</td>
          </tr>
          <tr v-if="scores.length === 0">
            <td colspan="5" class="text-center">No scores found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      scores: []
    }
  },
  mounted() {
    this.fetchScoreHistory();
  },
  methods: {
    async fetchScoreHistory() {
      const token = localStorage.getItem('token');
      try {
        const res = await fetch(`/api/user/${this.$route.params.user_id}/score-history`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!res.ok) throw new Error('Failed to fetch score history');

        const scores = await res.json();
        this.scores = scores;

      } catch (err) {
        console.error('Error fetching score history:', err);
      }
    }
  }
}
</script>
