<template>
  <div class="container mt-4">
    <!-- Add Subject Card -->
    <div class="card shadow-sm p-4 bg-white">
      <h2 class="mb-4 text-primary text-center">📚 Manage Subjects</h2>

      <!-- Add Subject Form -->
      <form @submit.prevent="addSubject">
        <div class="mb-3">
          <label for="name" class="form-label text-dark">Subject Name</label>
          <input
            type="text"
            id="name"
            v-model="s_name"
            class="form-control text-dark bg-light"
            placeholder="Enter subject name"
            required
          />
        </div>
        <div class="mb-3">
          <label for="description" class="form-label text-dark">Remarks</label>
          <textarea
            id="description"
            v-model="desc"
            class="form-control text-dark bg-light"
            rows="3"
            placeholder="Enter subject remarks"
          ></textarea>
        </div>
        <div class="text-end">
          <button type="submit" class="btn btn-success">➕ Add Subject</button>
        </div>
      </form>
    </div>

    <!-- List of Subjects -->
    <div class="mt-5">
      <h4 class="text-secondary">📋 Current Subjects</h4>

      <div
        class="card mt-3 shadow-sm bg-white"
        v-for="subject in subjects"
        :key="subject.id"
      >
        <div class="card-body d-flex justify-content-between align-items-center">
          <div class="d-flex align-items-center">
            <h5 class="card-title text-dark me-4 mb-0">{{ subject.name }}</h5>
            <p class="card-text text-muted mb-0">{{ subject.desc }}</p>
          </div>
          <div>
            <button @click="deleteSubject(subject.id)" class="btn btn-outline-danger">
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>

      <div v-if="subjects.length === 0" class="alert alert-info mt-4">
        No subjects added yet.
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      s_name: '',
      desc: '',
      subjects: [],
    };
  },
  mounted() {
    this.loadSubjects();
  },
  methods: {
    async loadSubjects() {
      try {
        const res = await fetch('/api/sub', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const data = await res.json();
        this.subjects = data || [];
      } catch (err) {
        console.error('Failed to fetch subjects:', err);
      }
    },
    async addSubject() {
      try {
        const res = await fetch('/api/sub', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            s_name: this.s_name,
            remarks: this.desc,
          }),
        });
        const data = await res.json();
        if (res.ok) {
          alert(`✅ Subject "${this.s_name}" added successfully!`);
          this.s_name = '';
          this.desc = '';
          await this.loadSubjects();
        } else {
          console.warn('Add subject API error:', data);
        }
      } catch (err) {
        console.error('Add subject failed:', err);
      }
    },
    async deleteSubject(sub_id) {
      try {
        const subject = this.subjects.find((s) => s.id === sub_id);
        const res = await fetch(`/api/sub/${sub_id}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        const data = await res.json();
        if (res.ok) {
          alert(`❌ Subject "${subject.name}" deleted successfully!`);
          await this.loadSubjects();
        } else {
          console.warn('Delete subject API error:', data);
        }
      } catch (err) {
        console.error('Delete subject failed:', err);
      }
    },
  },
};
</script>
