<template>
  <div class="container mt-4">
    <div class="dashboard">
      <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 class="text-white mb-0">Chapters in {{ subject.s_name }}</h2>
        <div style="width: 30%;">
          <input
            type="text"
            class="form-control"
            placeholder="Search chapters..."
            v-model="searchQuery"/>
        </div>
      </div>
      <div class="quiz-section">
        <h5 class="text-white">Available Chapters</h5>
        <table class="table">
          <thead>
            <tr>
              <th>Chapter ID</th>
              <th>Chapter Name</th>
              <th>No. of Quizzes</th>
              <th style="text-align: left;">Actions</th>
            </tr>
          </thead>
          <tbody v-if="filteredChapters && filteredChapters.length > 0">
            <tr v-for="chapter in filteredChapters" :key="chapter.id">
              <td>{{ chapter.id }}</td>
              <td>{{ chapter.name }}</td>
              <td>{{ chapter.quizzes.length }}</td>
              <td class="text-right">
                <router-link :to="{ name: 'available_quiz', params: { chapId: chapter.id } }" class="btn btn-primary">View Quizzes</router-link>
              </td>
            </tr>
          </tbody>
          <tbody v-else>
            <tr>
              <td colspan="4" class="text-center">
                <span v-if="searchQuery">No chapters found matching your search.</span>
                <span v-else>No chapters found.</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    subId: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      subject: {},
      searchQuery: '',
    };
  },
  computed: {
    filteredChapters() {
      if (!this.searchQuery) {
        return this.subject.chapters;
      }
      const query = this.searchQuery.toLowerCase();
      if (this.subject.chapters) {
        return this.subject.chapters.filter(chapter =>
          chapter.name.toLowerCase().includes(query)
        );
      }
      return [];
    }
  },
  methods: {
    async getSubject() {
      const tkn = localStorage.getItem('token');
      if (!tkn) {
        this.$router.push({ name: '/' });
        return;
      }
      try {
        const response = await fetch(`/api/user/sub/${this.subId}/chap`, {
          headers: {
            'Authorization': `Bearer ${tkn}`,
          },
        });
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        this.subject = data;
      } catch (error) {
        console.error("Failed to fetch chapters:", error);
      }
    },
  },
  mounted() {
    this.getSubject();
  },
};
</script>

<style scoped>
.dashboard {
  background-color: #343a40;
  padding: 20px;
  border-radius: 10px;
}
.quiz-section {
  margin-top: 20px;
}
.table {
  background-color: #fff;
  border-radius: 10px;
}
.text-white {
  color: #fff;
}
</style>
