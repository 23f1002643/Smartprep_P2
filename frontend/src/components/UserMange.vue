<template>
  <div class="container mt-5">
    <div class="card shadow-sm">
      <div class="card-header bg-dark text-white">
        <h4 class="mb-0">User Management</h4>
      </div>
      <div class="card-body">
        <div v-if="isLoading" class="text-center">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2">Loading users...</p>
        </div>
        <div v-else-if="users.length === 0" class="text-center text-muted">
          <p>No users found.</p>
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover align-middle">
            <thead class="table-light">
              <tr>
                <th>Full Name</th>
                <th>Username</th>
                <th>Email</th>
                <th>Quizzes Taken</th>
                <th>Accuracy</th>
                <th>Status</th>
                <th class="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.f_name }} {{ user.l_name }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.quizzes_taken }}</td>
                <td>
                  <span v-if="user.quizzes_taken > 0" class="badge" :class="getAccuracyBadge(user.accuracy)">
                    {{ user.accuracy }}%
                  </span>
                  <span v-else class="text-muted">N/A</span>
                </td>
                <td>
                  <span class="badge" :class="user.active ? 'bg-success-subtle text-success-emphasis' : 'bg-danger-subtle text-danger-emphasis'">
                    {{ user.active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td class="text-center">
                  <button
                    @click="toggleUserStatus(user)"
                    class="btn btn-sm"
                    :class="user.active ? 'btn-outline-danger' : 'btn-outline-success'"
                  >
                    {{ user.active ? 'Deactivate' : 'Activate' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'UserManagement',
  setup() {
    const users = ref([]);
    const isLoading = ref(true);

    const loadUsers = async () => {
      isLoading.value = true;
      try {
        const res = await fetch('/api/admin/user', { 
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        if (!res.ok) {
            throw new Error('Failed to fetch users');
        }
        const data = await res.json();
        users.value = data;
      } catch (err) {
        console.error('Failed to fetch users:', err);
        alert('Could not load user data. Please try again.');
      } finally {
        isLoading.value = false;
      }
    };

    const toggleUserStatus = async (user) => {
      if (!confirm(`Are you sure you want to ${user.active ? 'deactivate' : 'activate'} the user '${user.username}'?`)) {
          return;
      }
      try {
        const res = await fetch(`/api/admin/user/${user.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const data = await res.json();
        if (res.ok) {
          alert(data.msg);
          loadUsers(); // Refresh the user list
        } else {
          alert(`Error: ${data.msg}`);
          console.warn('Toggle status API error:', data);
        }
      } catch (err) {
        alert('An unexpected error occurred. Please try again.');
        console.error('Toggle user status failed:', err);
      }
    };

    const getAccuracyBadge = (accuracy) => {
      if (accuracy >= 90) return 'bg-success text-white';
      if (accuracy >= 75) return 'bg-info text-white';
      if (accuracy >= 50) return 'bg-warning text-dark';
      return 'bg-danger text-white';
    };

    onMounted(loadUsers);

    return { users, isLoading, toggleUserStatus, getAccuracyBadge };
  },
};
</script>

<style scoped>
.table th {
  font-weight: 600;
}
.badge {
  font-size: 0.9em;
  padding: 0.4em 0.7em;
}
.card-header {
    border-bottom: 0;
}
</style>
