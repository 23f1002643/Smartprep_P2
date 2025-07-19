<template>
  <div class="container chapter-management mt-5">
    <h2 class="text-center">Chapter Management</h2>

    <!-- Add Chapter -->
    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h5 class="card-title">Add Chapter</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="addChap">
              <div class="form-group">
                <label for="new-chapter-name">Chapter Name</label>
                <input
                  type="text"
                  class="form-control"
                  id="new-chapter-name"
                  v-model="newChapter.name"
                  required
                />
              </div>
              <div class="form-group">
                <label for="new-chapter-desc">Chapter Description</label>
                <textarea
                  class="form-control"
                  id="new-chapter-desc"
                  v-model="newChapter.desc"
                  rows="2"
                ></textarea>
              </div>
              <button type="submit" class="btn btn-primary mt-2">
                Add Chapter
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Chapter Modal -->
    <div
      class="modal fade"
      id="editChapterModal"
      tabindex="-1"
      aria-labelledby="editChapterModalLabel"
      aria-hidden="true"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="editChapterModalLabel">Edit Chapter</h5>
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="modal"
              aria-label="Close"
            ></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateChapter">
              <div class="mb-3">
                <label for="edit-chapter-name" class="form-label"
                  >Chapter Name</label
                >
                <input
                  type="text"
                  id="edit-chapter-name"
                  v-model="updateChapterData.name"
                  class="form-control"
                  required
                />
              </div>
              <div class="mb-3">
                <label for="edit-chapter-desc" class="form-label"
                  >Chapter Description</label
                >
                <textarea
                  id="edit-chapter-desc"
                  v-model="updateChapterData.desc"
                  class="form-control"
                  rows="3"
                ></textarea>
              </div>
              <button type="submit" class="btn btn-primary">
                Save changes
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Chapters List -->
    <div class="mt-5">
      <h4 class="text-secondary">📋 Current Chapters</h4>

      <div
        class="card mt-3 shadow-sm bg-white"
        v-for="chapter in chapters"
        :key="chapter.id"
      >
        <div
          class="card-body d-flex justify-content-between align-items-center"
        >
          <div class="d-flex align-items-center">
            <h5 class="card-title text-dark me-4 mb-0">{{ chapter.name }}</h5>
            <p class="card-text text-muted mb-0">{{ chapter.description }}</p>
          </div>
          <div>
            <router-link
              :to="{
                name: 'quiz_manage',
                params: { subId: subId, chapId: chapter.id },
              }"
              class="btn btn-outline-secondary me-2"
            >
              📖 View
            </router-link>
            <button
              class="btn btn-outline-primary me-2"
              @click="populateUpdateForm(chapter)"
            >
              ✏️ Edit
            </button>
            <button
              class="btn btn-outline-danger"
              @click="deleteChapter(chapter.id)"
            >
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>

      <div v-if="chapters.length === 0" class="alert alert-info mt-4">
        No chapters added yet.
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: ["subId"],
  data() {
    return {
      newChapter: {
        name: "",
        desc: "",
      },
      updateChapterData: {
        id: null,
        name: "",
        desc: "",
      },
      chapters: [],
    };
  },
  mounted() {
    console.log("Subject ID from route:", this.subId);
    this.loadChapters();
  },
  methods: {
    async loadChapters() {
      try {
        const res = await fetch(`/api/admin/sub/${this.subId}/chap`, {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        const data = await res.json();
        this.chapters = data || [];
      } catch (err) {
        console.error("Failed to fetch chapters:", err);
      }
    },
    async addChap() {
      try {
        const res = await fetch(`/api/admin/sub/${this.subId}/chap`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({
            name: this.newChapter.name,
            description: this.newChapter.desc,
          }),
        });
        const data = await res.json();
        if (res.ok) {
          alert(data.msg || "Chapter added.");
          this.newChapter.name = "";
          this.newChapter.desc = "";
          await this.loadChapters();
        } else {
          alert(data.msg || "Failed to add chapter.");
          await this.loadChapters();
        }
      } catch (err) {
        console.error("Add chapter failed:", err);
      }
    },
    populateUpdateForm(chapter) {
      this.updateChapterData = {
        id: chapter.id,
        name: chapter.name,
        desc: chapter.description,
      };

      // Show the Bootstrap modal
      const modalEl = document.getElementById("editChapterModal");
      const modal = new bootstrap.Modal(modalEl);
      modal.show();
    },
    clearUpdateForm() {
      this.updateChapterData = {
        id: null,
        name: "",
        desc: "",
      };
    },
    async updateChapter() {
      try {
        const res = await fetch(
          `/api/admin/sub/${this.subId}/chap/${this.updateChapterData.id}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
            body: JSON.stringify({
              name: this.updateChapterData.name,
              description: this.updateChapterData.desc,
            }),
          }
        );
        const data = await res.json();
        if (res.ok) {
          alert(data.msg || "Chapter updated.");
          this.clearUpdateForm();
          await this.loadChapters();

          // Close the modal
          const modalEl = document.getElementById("editChapterModal");
          const modal = bootstrap.Modal.getInstance(modalEl);
          modal.hide();
        } else {
          alert(data.msg || "Failed to update chapter.");
        }
      } catch (err) {
        console.error("Update chapter failed:", err);
      }
    },
    async deleteChapter(chapId) {
      try {
        const res = await fetch(`/api/admin/sub/${this.subId}/chap/${chapId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        });
        const data = await res.json();
        if (res.ok) {
          alert(data.msg || "Chapter deleted.");
          await this.loadChapters();
        } else {
          alert(data.msg || "Failed to delete chapter.");
        }
      } catch (err) {
        console.error("Delete chapter failed:", err);
      }
    },
  },
};
</script>
