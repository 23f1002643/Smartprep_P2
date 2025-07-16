<template>   
  <div class="container mt-5">     
    <div class="row justify-content-center">       
      <div class="col-md-6">         
        <div class="card">           
          <div class="card-header text-center">             
            <h2>Login Page</h2>           
          </div>           
          <div class="card-body">             
            <form @submit.prevent="login">               
              <div class="form-group mb-3">
                <div v-if="msg" class="alert alert-danger text-center">{{ msg }}</div>
                <label for="username">Username</label>                 
                <input type="text" class="form-control" id="username" placeholder="Username" v-model="username" required>               
              </div>               
              <div class="form-group mb-3">                 
                <label for="password">Password</label>                 
                <input type="password" class="form-control" id="password" placeholder="Password" v-model="password" required>               
              </div>               
              <button type="submit" class="btn btn-primary w-100">Login</button>             
            </form>             
            <div class="text-center mt-3">               
              <p>Don't have an account? <router-link to="/register" class="text-primary">Sign up</router-link></p>             
            </div>           
          </div>         
        </div>       
      </div>     
    </div>   
  </div> 
</template>  

<script> 
export default {
  data(){
    return {
      username: '',
      password: '',
      msg: null,
    };
  },
  methods: {
    async login() {
      this.msg = null;
      const payload = {
        username: this.username,
        password: this.password,
      };
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        });

        let data;
        try {
          data = await response.json();
        } catch (e) {
          this.msg = 'Server did not return valid JSON.';
          return;
        }

        if (response.ok) {
          localStorage.setItem('token', data.access_token);
          localStorage.setItem('user_info', JSON.stringify(data.user));
          localStorage.setItem('role', data.user.role);
          if(data.user.role === 'admin'){
            alert('Admin login successful');
            this.$router.push('/admin/dashboard');
          } else {
            alert(`${data.user.name} login successful`);
            this.$router.push('/user/dashboard');
          }
        } else {
          this.msg = data.msg || 'Ohh no! Login failed';
        }
      } catch (error) {
        console.error(error);
        this.msg = 'Something went wrong';
      }
    },
  },
};
</script>

