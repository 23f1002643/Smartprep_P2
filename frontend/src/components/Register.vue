<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header text-center">
            <h2>Registeration Page</h2>
          </div>
          <div class="card-body">
            <form @submit.prevent="register">
              <div v-if="msg" class="alert alert-danger text-center mb-3">{{ msg }}</div>
              
              <div class="form-group mb-3">
                <input type="text" class="form-control" id="username" placeholder="Username" v-model="username" required>
              </div>
              <div class="form-group mb-3">
                <input type="email" class="form-control" id="email" placeholder="Email" v-model="email" required>
              </div>
              <div class="form-group mb-3">
                <input type="password" class="form-control" id="password" placeholder="Password" v-model="pwd" required>
              </div>
              <div class="form-group mb-3">
                <input type="text" class="form-control" id="f_name" placeholder="First Name" v-model="f_name" required>
              </div>
              <div class="form-group mb-3">
                <input type="text" class="form-control" id="l_name" placeholder="Last Name" v-model="l_name" required>
              </div>
              <div class="form-group mb-3">
                <select class="form-control" id="edu_qul" v-model="edu_qul" required>
                  <option disabled value="">Select Education Qualification</option>
                  <option>Graduate</option>
                  <option>Post Graduate</option>
                  <option>Senior Secondary</option>
                  <option>Secondary</option>
                  <option>Below Secondary</option>
                  <option>PhD</option>
                </select>
              </div>
              <div class="form-group mb-3">
                <input type="text" class="form-control" id="mobile_no" placeholder="Mobile Number" v-model="mobile_no" required>
              </div>
              <div class="form-group mb-3">
                <input type="date" class="form-control" id="dob" placeholder="Date of Birth" v-model="dob" required>
              </div>
              <button type="submit" class="btn btn-primary w-100">Sign Up</button>
            </form>
            <div class="text-center mt-3">
              <p>Already have an account? <router-link to="/" class="text-primary">Login</router-link></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      username: '',
      email: '',
      pwd: '',
      f_name: '',
      l_name: '',
      edu_qul: '',
      mobile_no: '',
      dob: '',
      msg: null,
    };
  },
  methods: {
    async register() {
      this.msg = null;
      const payload = {
        username: this.username,
        email: this.email,
        pwd: this.pwd,
        f_name: this.f_name,
        l_name: this.l_name,
        edu_qul: this.edu_qul,
        mobile_no: this.mobile_no,
        dob: this.dob,
      };
      try {
        const response = await fetch('/api/register', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });
        
        const data = await response.json();
        
        if (response.ok) {
          alert(data.message || 'Registration successful!'); 
          this.$router.push('/');
        } else {
          this.msg = data.message || 'Ohh no! Signup failed';
        }
      } catch (error) {
        console.error(error);
        this.msg = 'Something went wrong. Please try again.';
      }
    },
  },
};
</script>
