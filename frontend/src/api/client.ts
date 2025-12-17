import axios from 'axios';

// Важно: Убедись, что порт совпадает с бэкендом (8000)
const API_URL = 'http://127.0.0.1:8000/api/v1';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем токен (если есть) в каждый запрос
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Если сервер вернул 401 (нет доступа), выкидываем на логин
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Опционально: window.location.href = '/login';
      // Но лучше обрабатывать это в React-компонентах
    }
    return Promise.reject(error);
  }
);
