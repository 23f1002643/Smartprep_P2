<template>
  <div class="container mt-2">
    <h3 class="text-center">📝 Manage Quizzes</h3>

    <div class="card shadow-sm p-4 mt-4 bg-white">
      <form @submit.prevent="addQuiz">
        <div class="row">
          <div class="col-md-4 mb-3">
            <label for="name" class="form-label">Quiz Name</label>
            <input v-model="newQuiz.name" type="text" id="name" class="form-control" required />
          </div>
          <div class="col-md-4 mb-3">
            <label for="date" class="form-label">Date</label>
            <input v-model="newQuiz.date" type="date" id="date" class="form-control" required />
          </div>
          <div class="col-md-4 mb-3 d-flex gap-2 align-items-end">
            <div>
              <label class="form-label">Duration</label>
              <div class="d-flex gap-2">
                <input v-model="newQuiz.hours" type="number" min="0" max="12" class="form-control" placeholder="HH" required />
                <input v-model="newQuiz.minutes" type="number" min="5" max="59" class="form-control" placeholder="MM" required />
              </div>
            </div>
          </div>
        </div>
        <div class="mb-3">
          <label for="remarks" class="form-label">Remarks</label>
          <textarea v-model="newQuiz.remarks" id="remarks" rows="1" class="form-control"></textarea>
        </div>
        <button type="submit" class="btn btn-success">➕ Add Quiz</button>
      </form>
    </div>

    <div class="mt-5">
      <h4 class="text-secondary">📋 Current Quizzes</h4>

      <!-- Search Bar -->
      <div class="row mt-3">
        <div class="col-md-6">
          <div class="input-group shadow-sm">
            <!-- <span class="input-group-text "><i class="fas fa-search"></i></span> -->
            <input
              type="text"
              class="form-control border-0"
              placeholder="Search quizzes by name or remarks..."
              v-model="searchQuery"
            />
          </div>
        </div>
      </div>
      <div class="row mt-3">
        <div v-for="quiz in filteredQuizzes" :key="quiz.id" class="col-md-3 mb-3">
          <div class="card shadow-sm bg-white h-100">
            <div class="card-body d-flex flex-column">
              <h5 class="card-title text-primary">{{ quiz.name }}</h5>
              <p class="card-text flex-grow-1">
                <small class="text-muted">
                  🕒 {{ quiz.time_duration }}<br>
                  📅 {{ quiz.date }}<br>
                  📝 {{ quiz.remarks || 'No remarks' }}
                </small>
              </p>
              <div class="d-flex gap-1 mt-auto">
                <button @click="viewQuiz(quiz)" class="btn btn-outline-info btn-sm flex-fill">📝 Manage</button>
                <button @click="openEditModal(quiz)" class="btn btn-outline-primary btn-sm flex-fill">✏️ Edit</button>
                <button @click="deleteQuiz(quiz.id)" class="btn btn-outline-danger btn-sm flex-fill">🗑️ Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="!filteredQuizzes.length" class="alert alert-info mt-4">
        <span v-if="searchQuery">No quizzes found matching your search.</span>
        <span v-else>No quizzes added yet for this chapter.</span>
      </div>
    </div>

    <!-- Edit Quiz Modal -->
    <div class="modal fade" id="editQuizModal" tabindex="-1" aria-labelledby="editQuizModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <form @submit.prevent="updateQuiz">
            <div class="modal-header">
              <h5 class="modal-title" id="editQuizModalLabel">Edit Quiz</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
              <div class="mb-3">
                <label class="form-label">Quiz Name</label>
                <input v-model="editQuiz.name" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Date</label>
                <input v-model="editQuiz.date" type="date" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Duration</label>
                <div class="d-flex gap-2">
                  <input v-model="editQuiz.hours" type="number" min="0" max="12" class="form-control" placeholder="HH" required />
                  <input v-model="editQuiz.minutes" type="number" min="5" max="59" class="form-control" placeholder="MM" required />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Remarks</label>
                <textarea v-model="editQuiz.remarks" class="form-control"></textarea>
              </div>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
              <button type="submit" class="btn btn-primary">💾 Save Changes</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- View Quiz Modal -->
    <div class="modal fade" id="viewQuizModal" tabindex="-1" aria-labelledby="viewQuizModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="viewQuizModalLabel">{{ viewQuizData.name }}</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <p><strong>Date:</strong> {{ viewQuizData.date }}</p>
                    <p><strong>Duration:</strong> {{ viewQuizData.time_duration }}</p>
                    <p><strong>Remarks:</strong> {{ viewQuizData.remarks || 'No remarks' }}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    <router-link
                      v-if="viewQuizData.id"
                      :to="{ name: 'problem_statement', params: { subId: subId, chapId: chapId, examId: viewQuizData.id } }"
                      class="btn btn-primary"
                      @click="navigateToQuestions"
                    >
                      Manage Questions
                    </router-link>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['subId', 'chapId'],
  data() {
    return {
      newQuiz: { name: '', date: '', hours: 0, minutes: 5, remarks: '' },
      editQuiz: { id: null, name: '', date: '', hours: 0, minutes: 5, remarks: '' },
      viewQuizData: { id: null, name: '', date: '', time_duration: '', remarks: '' },
      quizzes: [], 
      searchQuery: '', 
      editModalInstance: null,
      viewModalInstance: null,
    };
  },
  computed: {
    filteredQuizzes() {
      if (!this.searchQuery) {
        return this.quizzes; 
      }
      const query = this.searchQuery.toLowerCase();
      return this.quizzes.filter(quiz => {
        const name = quiz.name.toLowerCase();
        const remarks = (quiz.remarks || '').toLowerCase();
        return name.includes(query) || remarks.includes(query);
      });
    }
  },
  mounted() {
    this.loadQuizzes();
    const editModalEl = document.getElementById('editQuizModal');
    const viewModalEl = document.getElementById('viewQuizModal');

    this.editModalInstance = new bootstrap.Modal(editModalEl);
    this.viewModalInstance = new bootstrap.Modal(viewModalEl);
    
    const blurActiveElement = () => document.activeElement?.blur();
    editModalEl.addEventListener('hide.bs.modal', blurActiveElement);
    viewModalEl.addEventListener('hide.bs.modal', blurActiveElement);
  },
  beforeUnmount() {
    if (this.editModalInstance) {
      this.editModalInstance.dispose();
    }
    if (this.viewModalInstance) {
      this.viewModalInstance.dispose();
    }
    
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());
    
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';
  },
  methods: {
    async loadQuizzes() {
      try {
        const res = await fetch(`/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await res.json();
        if (res.ok) { this.quizzes = data; }
      } catch (err) { console.error('Failed to fetch quizzes:', err); }
    },
    async addQuiz() {
      const time = `${String(this.newQuiz.hours).padStart(2, '0')}:${String(this.newQuiz.minutes).padStart(2, '0')}:00`;
      const payload = { name: this.newQuiz.name, date: this.newQuiz.date, time: time, remarks: this.newQuiz.remarks };
      const res = await fetch(`/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      alert(data.msg);
      if (res.ok) {
        this.newQuiz = { name: '', date: '', hours: 0, minutes: 5, remarks: '' };
        await this.loadQuizzes();
      }
    },
    openEditModal(quiz) {
      const timeParts = quiz.time_duration.split(':');
      this.editQuiz = {
        id: quiz.id, name: quiz.name, date: quiz.date,
        hours: parseInt(timeParts[0]) || 0,
        minutes: parseInt(timeParts[1]) || 0,
        remarks: quiz.remarks || ''
      };
      this.editModalInstance.show();
    },
    async updateQuiz() {
      const time = `${String(this.editQuiz.hours).padStart(2, '0')}:${String(this.editQuiz.minutes).padStart(2, '0')}:00`;
      const payload = { name: this.editQuiz.name, date: this.editQuiz.date, time: time, remarks: this.editQuiz.remarks };
      const res = await fetch(`/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz/${this.editQuiz.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      alert(data.msg);
      if (res.ok) {
        this.editModalInstance.hide();
        await this.loadQuizzes();
      }
    },
    async deleteQuiz(quizId) {
      if (!confirm('Are you sure you want to delete this quiz?')) return;
      const res = await fetch(`/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz/${quizId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const data = await res.json();
      alert(data.msg);
      if (res.ok) { await this.loadQuizzes(); }
    },
    viewQuiz(quiz) {
      this.viewQuizData = { ...quiz };
      this.viewModalInstance.show();
    },
    navigateToQuestions() {
      if (this.viewModalInstance) {
        this.viewModalInstance.hide();
      }
    }
  }
};
</script>

<style scoped>
.card { transition: transform 0.2s; }
.card:hover { transform: translateY(-5px); }
.btn-sm { font-size: 0.75rem; padding: 0.25rem 0.5rem; }
</style>
