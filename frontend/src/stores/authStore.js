import { defineStore } from 'pinia';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
    userInfo: JSON.parse(localStorage.getItem('user_info')) || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(credentials) {
      try {
        const response = await fetch('/api/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(credentials),
        });

        const data = await response.json();

        if (!response.ok) {
          console.error('Login failed:', data.msg);
          return false;
        }

        this.token = data.access_token;
        this.userInfo = data.user;
        this.role = data.user.role;

        localStorage.setItem('token', this.token);
        localStorage.setItem('user_info', JSON.stringify(this.userInfo));
        localStorage.setItem('role', this.role);

        alert(`Welcome, ${data.user.name}! You are now logged in.`);
        
        return true;

      } catch (error) {
        console.error('An error occurred during login:', error);
        return false;
      }
    },

    async logout() {
      const currentToken = this.token;
      const currentUserName = this.userInfo?.name;

      this.token = null;
      this.userInfo = null;
      this.role = null;

      localStorage.removeItem('token');
      localStorage.removeItem('user_info');
      localStorage.removeItem('role');

      const message = `Goodbye, ${currentUserName || 'User'}! You are now logged out.`;
      const symbol = currentToken ? '✔️' : '❌';

      alert(`${symbol} ${message}`);

      if (currentToken) {
        try {
          await fetch('/api/logout', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${currentToken}`
            }
          });
        } catch (error) {
          console.error('API call to logout endpoint failed:', error);
        }
      }
    },
  },
});
