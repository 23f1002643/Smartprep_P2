import { createApp } from 'vue'
import SmartPrep from './App.vue'
import router from './router'

const app = createApp(SmartPrep)
app.use(router)
app.mount('#app')
