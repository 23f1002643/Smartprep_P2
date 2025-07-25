<template>
  <div class="container mt-5">
    <!-- Status Alert for Export -->
    <div v-if="exportStatus" class="alert" :class="exportAlertClass" role="alert">
      <strong>{{ exportStatus }}</strong>
      <div v-if="exporting" class="progress mt-2" style="height: 10px;">
        <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" :style="{ width: exportProgress + '%' }" aria-valuenow="exportProgress" aria-valuemin="0" aria-valuemax="100"></div>
      </div>
    </div>

    <div class="d-flex justify-content-end">
      <button @click="exportUserData" class="btn btn-danger mb-3" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ exporting ? 'Exporting...' : 'Export Users Data' }}
      </button>
    </div>
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
import { ref, onMounted, onBeforeUnmount } from 'vue'; 

export default {
  name: 'UserManagement',
  setup() {
    const users = ref([]);
    const isLoading = ref(true);
    const exporting = ref(false);
    const exportStatus = ref('');
    const exportProgress = ref(0);
    const exportAlertClass = ref('alert-info');
    let pollingInterval = null;

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
    const exportUserData = async () => {
      if (exporting.value) return;

      exporting.value = true;
      exportStatus.value = 'Initializing export...';
      exportAlertClass.value = 'alert-info';
      exportProgress.value = 0;

      try {
        const res = await fetch('/api/admin/export-user-data', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!res.ok) {
          throw new Error('Failed to start the export process.');
        }

        const data = await res.json();
        const taskId = data.task_id;
        exportStatus.value = 'Export process started. Please wait...';
        
        // Start polling for the task status
        pollingInterval = setInterval(() => {
          pollTaskStatus(taskId);
        }, 3000); // Poll every 3 seconds

      } catch (err) {
        exporting.value = false;
        exportStatus.value = `Error: ${err.message}`;
        exportAlertClass.value = 'alert-danger';
      }
    };
    const pollTaskStatus = async (taskId) => {
      try {
        const res = await fetch(`/api/admin/export-status/${taskId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        const data = await res.json();

        if (data.state === 'PROGRESS') {
          exportStatus.value = data.info.status;
          exportProgress.value = data.info.current;
        } else if (data.state === 'SUCCESS') {
          clearInterval(pollingInterval);
          exporting.value = false;
          exportStatus.value = 'Export complete! The CSV file has been sent to your email.';
          exportAlertClass.value = 'alert-success';
          exportProgress.value = 100;
        } else if (data.state === 'FAILURE') {
          clearInterval(pollingInterval);
          exporting.value = false;
          exportStatus.value = `Export failed: ${data.info.message || 'An unknown error occurred.'}`;
          exportAlertClass.value = 'alert-danger';
        }
      } catch (err) {
        clearInterval(pollingInterval);
        exporting.value = false;
        exportStatus.value = 'Error checking task status.';
        exportAlertClass.value = 'alert-danger';
      }
    };

    const getAccuracyBadge = (accuracy) => {
      if (accuracy >= 90) return 'bg-success text-white';
      if (accuracy >= 75) return 'bg-info text-white';
      if (accuracy >= 50) return 'bg-warning text-dark';
      return 'bg-danger text-white';
    };

    onMounted(loadUsers);
    onBeforeUnmount(() => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    });

    return { 
      users, 
      isLoading, 
      toggleUserStatus, 
      getAccuracyBadge,
      exporting,
      exportStatus,
      exportProgress,
      exportAlertClass,
      exportUserData,
    };
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
