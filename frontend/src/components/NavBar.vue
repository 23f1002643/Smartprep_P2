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
            <li class="nav-item" v-if="isLoggedIn && userRole === 'user'">
              <router-link to="/performance" class="nav-link">Performance Summary</router-link>
            </li>
           </ul>
          <div class="d-flex align-items-center gap-2">
            <form class="d-flex me-2" v-if="isLoggedIn">
              <input
                class="form-control me-2"
                type="search"
                placeholder="Search"
                aria-label="Search"
                style="max-width: 200px"
              />
              <button class="btn btn-outline-success" type="submit">Search</button>
            </form>
            <router-link
              v-if="isLoggedIn && userRole === 'admin'"
              to="#"
              class="btn btn-outline-primary mx-2">Summary</router-link>
            <button
              v-if="isLoggedIn"
              class="btn btn-outline-danger"
              @click="logout"
            >
              Logout
            </button>
            <router-link
              v-if="!isLoggedIn"
              to="/register"
              class="btn btn-primary"
            >
              Sign Up
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "NavBar",
  // These stay reactive to changes in localStorage
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem("token");
    },
    userRole() {
      return localStorage.getItem("role");
    },
  },

  // cross-tab sync
  mounted() {
    window.addEventListener("storage", this.$forceUpdate);
  },
  beforeUnmount() {
    window.removeEventListener("storage", this.$forceUpdate);
  },

  methods: {
    // Logs out the user, clears storage and navigates to home
    async logout() {
      try {
        const token = localStorage.getItem("token");
        if (token) {
          const res = await fetch("/api/logout", {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
          });
          const data = await res.json();
          if (res.ok) {
            alert(data.msg || "Logged out successfully");
          } else {
            console.warn("Logout API error:", data);
          }
        }
      } catch (err) {
        console.error("Logout failed:", err);
      }
      // Clear session info from localStorage
      localStorage.removeItem("token");
      localStorage.removeItem("user_info");
      localStorage.removeItem("role");
      // Force Vue to react to logout
      this.$forceUpdate();
      this.$router.push("/");
    },
  },
};
</script>

