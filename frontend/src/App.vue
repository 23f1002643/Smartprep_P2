<!-- App.vue -->
<template>
  <div id="app" :style="gradientStyle">
    <NavBar v-if="showNavBar" />
    <router-view />
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue';

export default {
  name: 'SmartPrep',
  components: {
    NavBar,
  },
  computed: {
    showNavBar() {
      const hiddenRoutes = ['/login'];
      return !hiddenRoutes.includes(this.$route.path);
    },
    gradientStyle() {
      return {
        background: 'linear-gradient(to right, #A5FECB, #20BDFF, #5433FF)',
        minHeight: '100vh',
      };
    },
  },
};
</script>
