<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <a class="navbar-brand" href="#">SmartPrep</a>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <div class="d-flex flex-grow-1 align-items-center justify-content-between">
          <ul class="navbar-nav mb-2 mb-lg-0 d-flex flex-row align-items-center gap-3">
            </ul>
          <div class="d-flex align-items-center gap-2">
            <router-link
              v-if="isLoggedIn"
              :to="homeRoute"
              class="btn btn-outline-primary mx-2">Home</router-link>
            <button
              v-if="isLoggedIn"
              class="btn btn-outline-danger"
              @click="handleLogout"
            >
              Logout
            </button> 
            <div v-if="!isLoggedIn">
              <router-link
                v-if="$route.path === '/register'"
                to="/"
                class="btn btn-primary"
              >Login</router-link>
              <router-link
                v-else
                to="/register"
                class="btn btn-primary"> Sign Up</router-link>
            </div>         
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import { useAuthStore } from '@/stores/authStore';
import { mapState } from 'pinia';
export default {
  name: "NavBar",
  computed: {
    // Maps state from your Pinia store
    ...mapState(useAuthStore, {
      isLoggedIn: 'isLoggedIn',
      userRole: 'role'
    }),
    homeRoute() {
      if (this.userRole === 'admin') {
        return '/admin/dashboard';
      }
      if (this.userRole === 'user') {
        return '/user-dashboard';
      }
      return '/';
    }
  },
  methods: {
    handleLogout() {
      const authStore = useAuthStore();
      authStore.logout(); 
      this.$router.push('/');
    },
  },
};
</script>