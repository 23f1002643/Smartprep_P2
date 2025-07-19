import { createApp } from 'vue';
import SmartPrep from './App.vue';
import router from './router';
import { createPinia } from 'pinia';

const pinia = createPinia();

const app = createApp(SmartPrep);

app.use(router);

app.use(pinia);

app.mount('#app');
