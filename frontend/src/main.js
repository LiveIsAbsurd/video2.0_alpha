import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import VuePlyr from "vue-plyr"
import Antd from 'ant-design-vue';
import 'vue-plyr/dist/vue-plyr.css'

const app = createApp(App)
app.use(router)
app.use(VuePlyr, {
    plyr: {}
  })
app.use(Antd)
app.mount('#app')
