import { createRouter, createWebHistory } from 'vue-router';
import Header from '../components/Header/Header.vue';
import List from '../components/List/List.vue';
import File from '../components/File/File.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    components: {
        default: Header,
        list: List
    }
  },
  {
    path: '/list/:id',
    name: 'list',
    components: {
        default: Header,
        file: File
    },
    props: true
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
