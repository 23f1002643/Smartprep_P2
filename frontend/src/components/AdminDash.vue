<template>
  <div class="container admin-dashboard mt-4">
    
  <h2 class="mb-4 text-center">Admin Dashboard</h2>

  <div class="row">
    <!-- Subjects Card -->
    <div class="col-md-4 mb-4">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">Subjects</h5>
          <p class="card-text">Access and manage subjects, chapters, quizzes, and questions.</p>
          <router-link to="/admin/sub" class="btn btn-primary">Manage Subjects</router-link>
        </div>
      </div>
    </div>

    <!-- Users Card -->
    <div class="col-md-4 mb-4">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">Users</h5>
          <p class="card-text">Review and handle registered user accounts.</p>
          <router-link to="/admin/users" class="btn btn-primary">Manage Users</router-link>
        </div>
      </div>
    </div>

    <!-- Statistics Card -->
    <div class="col-md-4 mb-4">
      <div class="card h-100 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">Statistics</h5>
          <p class="card-text">Explore quiz-related insights and performance metrics.</p>
          <router-link to="/admin/stats" class="btn btn-primary">View Reports</router-link>
        </div>
      </div>
    </div>
  </div>
</div>

</template>

<script>
import NavBar from '@/components/NavBar.vue';
export default {
  name: 'AdminDashboard',
  components: {
    NavBar,
  },
  data() {
    return {
      availableQuizzes: [],
    };
  },
  mounted() {
    const role = localStorage.getItem('role');
    if (role !== 'admin') {
      alert('Access denied. Admins only.');
      this.$router.push('/api/login'); // Redirect non-admin users
    } else {
      this.loadAdminData();

    }
  },
  methods: {
    async loadAdminData() {
      try {
        const res = await fetch('/api/admin/dashboard', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const data = await res.json();
        this.availableQuizzes = data.quizzes || [];
      } catch (err) {
        console.error('Failed to fetch admin dashboard data:', err);
      }
    },
  },
};
</script>