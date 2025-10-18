import { createApp } from 'vue'
import App from './App.vue'

// Импорт шрифтов и глобальных стилей
import './assets/styles/fonts.css'
import './assets/styles/global.css'
import './assets/styles/colors.css'

const app = createApp(App)

app.mount('#app')
