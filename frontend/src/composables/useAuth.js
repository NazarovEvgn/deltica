// frontend/src/composables/useAuth.js
// Composable для управления аутентификацией пользователей

import { ref, computed } from 'vue'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

// Глобальное состояние (shared state)
const currentUser = ref(null)
const isAuthenticated = ref(false)
const isLoading = ref(false)
const authError = ref(null)

// Проверка роли администратора
const isAdmin = computed(() => {
  return currentUser.value?.role === 'admin'
})

// Проверка роли лаборанта
const isLaborant = computed(() => {
  return currentUser.value?.role === 'laborant'
})

// Сохранение токена в localStorage
const saveToken = (token) => {
  localStorage.setItem('auth_token', token)
}

// Получение токена из localStorage
const getToken = () => {
  return localStorage.getItem('auth_token')
}

// Удаление токена из localStorage
const removeToken = () => {
  localStorage.removeItem('auth_token')
}

// Настройка axios interceptor для добавления токена в заголовки
const setupAxiosInterceptor = () => {
  axios.interceptors.request.use(
    (config) => {
      const token = getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // Interceptor для обработки 401 ошибок (невалидный токен)
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        // Токен невалиден - выходим
        logout()
      }
      return Promise.reject(error)
    }
  )
}

// Инициализация - запускается при загрузке приложения
const initialize = async () => {
  const token = getToken()
  if (token) {
    // Есть токен - проверяем его валидность и получаем данные пользователя
    await fetchCurrentUser()
  }
}

// Получение данных текущего пользователя
const fetchCurrentUser = async () => {
  try {
    isLoading.value = true
    authError.value = null

    const response = await axios.get(`${API_URL}/auth/me`)
    currentUser.value = response.data
    isAuthenticated.value = true
  } catch (error) {
    console.error('Ошибка получения данных пользователя:', error)
    // Если токен невалиден - очищаем состояние
    currentUser.value = null
    isAuthenticated.value = false
    removeToken()
  } finally {
    isLoading.value = false
  }
}

// Логин пользователя
const login = async (username, password) => {
  try {
    isLoading.value = true
    authError.value = null

    const response = await axios.post(`${API_URL}/auth/login`, {
      username,
      password
    })

    const { access_token, user } = response.data

    // Сохраняем токен и данные пользователя
    saveToken(access_token)
    currentUser.value = user
    isAuthenticated.value = true

    return { success: true }
  } catch (error) {
    console.error('Ошибка логина:', error)

    // Обработка ошибок
    if (error.response?.status === 401) {
      authError.value = 'Неверный логин или пароль'
    } else if (error.response?.status === 403) {
      authError.value = 'Пользователь деактивирован. Обратитесь к администратору.'
    } else {
      authError.value = 'Ошибка соединения с сервером'
    }

    return { success: false, error: authError.value }
  } finally {
    isLoading.value = false
  }
}

// Выход пользователя
const logout = () => {
  currentUser.value = null
  isAuthenticated.value = false
  removeToken()
  authError.value = null
}

// Очистка ошибок
const clearError = () => {
  authError.value = null
}

// Экспортируемый composable
export function useAuth() {
  // Настраиваем axios interceptor при первом использовании
  if (!axios.interceptors.request.handlers.length) {
    setupAxiosInterceptor()
  }

  return {
    // State
    currentUser,
    isAuthenticated,
    isLoading,
    authError,
    isAdmin,
    isLaborant,

    // Actions
    initialize,
    login,
    logout,
    clearError,
    fetchCurrentUser
  }
}
