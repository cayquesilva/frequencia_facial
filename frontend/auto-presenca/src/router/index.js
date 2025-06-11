import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue'; // Vamos criar um componente HomeView
import AdminView from '../views/AdminView.vue';
import RecognitionView from '../views/RecognitionView.vue';
import LogsView from '../views/LogsView.vue';
import SchoolUnitsView from '../views/SchoolUnitsView.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminView
  },
  {
    path: '/recognition',
    name: 'recognition',
    component: RecognitionView
  },
  {
    path: '/logs',
    name: 'logs',
    component: LogsView
  },
  {
    path: '/school-units',
    name: 'school-units',
    component: SchoolUnitsView
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL || '/'),
  routes
});

export default router;