<template>
  <div class="container mt-4">
    <div v-if="isLoading" class="text-center">
      <div class="spinner-border text-primary" role="status"></div>
      <p class="mt-2">Searching...</p>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else>
      <h2 class="mb-4">Results for: <em class="text-primary">"{{ query }}"</em></h2>

      <!-- Subjects Results -->
      <div v-if="results.subjects && results.subjects.length">
        <h4>Subjects</h4>
        <div class="list-group mb-4">
          <router-link v-for="subject in results.subjects" :key="subject.id" :to="`/sub/${subject.id}`" class="list-group-item list-group-item-action">
            {{ subject.name }}
          </router-link>
        </div>
      </div>

      <!-- Chapters Results -->
      <div v-if="results.chapters && results.chapters.length">
        <h4>Chapters</h4>
        <div class="list-group mb-4">
          <a v-for="chapter in results.chapters" :key="chapter.id" href="#" class="list-group-item list-group-item-action">
            {{ chapter.name }} <small class="text-muted">in {{ chapter.subject_name }}</small>
          </a>
        </div>
      </div>

      <!-- Quizzes Results -->
      <div v-if="results.quizzes && results.quizzes.length">
        <h4>Quizzes</h4>
        <div class="list-group mb-4">
          <router-link v-for="quiz in results.quizzes" :key="quiz.id" :to="`/quiz/${quiz.id}`" class="list-group-item list-group-item-action">
            {{ quiz.name }} <small class="text-muted">in {{ quiz.chapter_name }}</small>
          </router-link>
        </div>
      </div>

      <!-- Users Results (Admin Only) -->
      <div v-if="results.users && results.users.length">
        <h4>Users</h4>
        <div class="list-group mb-4">
          <router-link v-for="user in results.users" :key="user.id" to="/admin/users" class="list-group-item list-group-item-action">
            {{ user.full_name }} ({{ user.username }})
          </router-link>
        </div>
      </div>

      <!-- No Results Message -->
      <div v-if="!hasResults" class="text-center text-muted mt-5">
        <p>No results found for your query.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const query = ref(route.query.q || '');
const results = ref({});
const isLoading = ref(true);
const error = ref(null);

const hasResults = computed(() => {
  return Object.values(results.value).some(arr => arr.length > 0);
});

const fetchResults = async () => {
  if (!query.value) {
    results.value = {};
    isLoading.value = false;
    return;
  }
  isLoading.value = true;
  error.value = null;
  try {
    const res = await fetch(`/api/search?q=${encodeURIComponent(query.value)}`, {
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    if (!res.ok) throw new Error('Failed to fetch search results.');
    results.value = await res.json();
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

// Fetch results when the component is first loaded
onMounted(fetchResults);

// Watch for changes in the route query and re-fetch results
watch(() => route.query.q, (newQuery) => {
  query.value = newQuery;
  fetchResults();
});
</script>
<style scoped>
.list-group-item {
  cursor: pointer;
}
</style>