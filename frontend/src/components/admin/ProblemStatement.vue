<template>
  <div class="container-fluid mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="fw-light text-primary">📝 Question Editor</h3>
      <router-link :to="{ name: 'quiz_manage', params: { subId, chapId } }" class="btn btn-danger btn-sm">
        ← Back to Quizzes
      </router-link>
    </div>

    <div class="row">
      
      <div class="col-lg-5">
        <div class="card shadow-sm" style="position: sticky; top: 20px;">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0 fw-light">
              <span v-if="editMode">✍️ Edit Question</span>
              <span v-else>➕ Add Question</span>
            </h5>
            <button class="btn btn-sm btn-outline-secondary" @click="prepareNewQuestion" v-if="editMode">
              Cancel Edit
            </button>
          </div>
          <div class="card-body p-4">
            <div v-if="message.text" :class="`alert alert-${message.type} py-2`" role="alert">
              {{ message.text }}
            </div>

            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label small">Question Statement</label>
                <textarea v-model="form.statement" class="form-control form-control-sm" rows="2" required></textarea>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3" v-for="n in 4" :key="n">
                  <label class="form-label small">Option {{ n }}</label>
                  <input v-model="form['opt' + n]" type="text" class="form-control form-control-sm" required />
                </div>
              </div>
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label class="form-label small">Question No.</label>
                  <input v-model="form.que_no" type="number" min="1" class="form-control form-control-sm" required />
                </div>
                <div class="col-md-6 mb-3">
                  <label class="form-label small">Correct Opt.</label>
                  <input v-model.number="form.cor_opt" type="number" min="1" max="4" class="form-control form-control-sm" required />
                </div>
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-sm" :class="editMode ? 'btn-primary' : 'btn-success'">
                  {{ editMode ? '✓ Update Question' : '✓ Save New Question' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <div class="col-lg-7">
        <h5 class="fw-dark " style="color:black;">Available Questions ({{ filteredQuestions.length }})</h5>
        
        <!-- Search Bar -->
        <div class="input-group shadow-sm mb-3">
            <input
              type="text"
              class="form-control border-0"
              placeholder="Search questions by statement..."
              v-model="searchQuery"
            />
        </div>

        <div v-if="!filteredQuestions.length" class="card card-body text-center text-muted">
          <p v-if="searchQuery">No questions found matching your search.</p>
          <p v-else>No questions yet. Use the form on the left to add one.</p>
        </div>
        <div class="card" v-else>
          <div class="table-responsive">
            <table class="table table-striped table-hover align-middle mb-0">
              <thead>
                <tr>
                  <th class="ps-3">#</th>
                  <th>Statement</th>
                  <th>Options</th>
                  <th>Ans</th>
                  <th class="text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="q in filteredQuestions" :key="q.id" :class="{'table-primary': selectedQuestion && selectedQuestion.id === q.id}">
                  <td class="ps-3 fw-bold">{{ q.que_no }}</td>
                  <td style="min-width: 250px;">{{ q.statement }}</td>
                  <td style="min-width: 200px;">
                    <ul class="list-unstyled mb-0 small">
                      <li :class="{'text-success fw-bold': 1 === q.cor_opt}">1. {{ q.opt1 }}</li>
                      <li :class="{'text-success fw-bold': 2 === q.cor_opt}">2. {{ q.opt2 }}</li>
                      <li :class="{'text-success fw-bold': 3 === q.cor_opt}">3. {{ q.opt3 }}</li>
                      <li :class="{'text-success fw-bold': 4 === q.cor_opt}">4. {{ q.opt4 }}</li>
                    </ul>
                  </td>
                  <td class="fw-bold text-center">{{ q.cor_opt }}</td>
                  <td class="text-center">
                    <div class="btn-group">
                      <button class="btn btn-outline-primary btn-sm" @click="selectQuestion(q)">✏️ Edit</button>
                      <button class="btn btn-outline-danger btn-sm" @click="deleteQuestion(q.id)">🗑️ Remove</button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ['subId', 'chapId', 'examId'],
  data() {
    return {
      questions: [],
      searchQuery: '', 
      form: this.getInitialFormState(),
      selectedQuestion: null,
      editMode: false,
      message: { text: '', type: '' },
    };
  },
  computed: {
    filteredQuestions() {
      let filtered = this.questions;
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = this.questions.filter(q => 
          q.statement.toLowerCase().includes(query)
        );
      }
      return [...filtered].sort((a, b) => a.que_no - b.que_no);
    }
  },
  mounted() {
    this.fetchQuestions();
  },
  methods: {
    getInitialFormState() {
      return { id: null, que_no: '', statement: '', opt1: '', opt2: '', opt3: '', opt4: '', cor_opt: '' };
    },
    displayMessage(text, type = 'danger') {
        this.message = { text, type };
        setTimeout(() => { this.message = { text: '', type: '' }; }, 4000);
    },
    async fetchQuestions() {
      try {
        const response = await fetch(`/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz/${this.examId}/que`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        if (!response.ok) throw new Error('Failed to fetch');
        this.questions = await response.json();
      } catch (err) {
        this.displayMessage('Error loading questions.');
      }
    },
    selectQuestion(question) {
      this.selectedQuestion = question;
      this.form = { ...question };
      this.editMode = true;
      this.message.text = ''; 
      if (window.innerWidth < 992) {
          this.$el.scrollIntoView({ behavior: 'smooth' });
      }
    },
    prepareNewQuestion() {
        this.selectedQuestion = null;
        this.form = this.getInitialFormState();
        this.editMode = false;
    },
    async handleSubmit() {
      const url = this.editMode
        ? `/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz/${this.examId}/que/${this.form.id}`
        : `/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz/${this.examId}/que`;
      
      const method = this.editMode ? 'PUT' : 'POST';

      try {
        const res = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('token')}` },
          body: JSON.stringify(this.form)
        });
        const data = await res.json();
        if (!res.ok) {
            this.displayMessage(data.msg || 'An error occurred.');
            return;
        }
        this.displayMessage(data.msg, 'success');
        await this.fetchQuestions();
        this.prepareNewQuestion();

      } catch (error) {
        this.displayMessage('An unexpected network error occurred.');
      }
    },
    async deleteQuestion(queId) {
      if (!confirm('Are you sure you want to delete this question?')) return;
      try {
        const res = await fetch(`/api/admin/sub/${this.subId}/chap/${this.chapId}/quiz/${this.examId}/que/${queId}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        const data = await res.json();
        alert(data.msg);
        if (res.ok) {
            if (this.selectedQuestion && this.selectedQuestion.id === queId) {
                this.prepareNewQuestion();
            }
            await this.fetchQuestions();
        }
      } catch (err) {
        alert('An unexpected error occurred during deletion.');
      }
    }
  }
};
</script>
