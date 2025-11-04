// frontend/src/composables/useAuth.js
// Composable для управления аутентификацией пользователей

import { ref, computed } from 'vue'
import axios from 'axios'

// API URL загружается из config.json (можно изменить без пересборки)
let API_URL = 'http://localhost:8000' // Fallback значение

// Загрузка конфигурации при старте
async function loadConfig() {
  try {
    const response = await fetch('/config.json')
    const config = await response.json()
    if (config.apiUrl) {
      API_URL = config.apiUrl
      console.log('API URL загружен из конфигурации:', API_URL)
    }
  } catch (error) {
    console.warn('Не удалось загрузить config.json, используется localhost:', error)
  }
}

// Загружаем конфигурацию сразу
await loadConfig()

// Глобальное состояние (shared state)
const currentUser = ref(null)
const isAuthenticated = ref(false)
const isLoading = ref(false)
const isInitializing = ref(false)  // Состояние первичной инициализации
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
  try {
    isInitializing.value = true

    const token = getToken()
    if (token) {
      // Есть сохраненный токен - проверяем его валидность
      await fetchCurrentUser()

      // Если токен валиден - пользователь вошел
      if (isAuthenticated.value) {
        console.log('Восстановлена сессия из сохраненного токена')
        return
      }
    }

    // Токена нет или он невалиден - пробуем автоматический Windows SSO
    console.log('Попытка автоматического входа через Windows SSO...')
    const result = await tryAutoLogin()

    if (result.success) {
      console.log('Автоматический вход выполнен успешно')
    } else {
      console.log('Требуется ручной вход')
    }
  } finally {
    isInitializing.value = false
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

// Windows SSO логин
const loginWithWindows = async () => {
  try {
    isLoading.value = true
    authError.value = null

    const response = await axios.post(`${API_URL}/auth/windows-login`)

    const { access_token, user } = response.data

    // Сохраняем токен и данные пользователя
    saveToken(access_token)
    currentUser.value = user
    isAuthenticated.value = true

    return { success: true }
  } catch (error) {
    console.error('Ошибка Windows логина:', error)

    // Обработка ошибок
    if (error.response?.status === 401) {
      authError.value = 'Пользователь не найден в системе. Обратитесь к администратору.'
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

// Тихая попытка Windows SSO (без показа ошибок пользователю)
const tryAutoLogin = async () => {
  try {
    const response = await axios.post(`${API_URL}/auth/windows-login`)
    const { access_token, user } = response.data

    // Сохраняем токен и данные пользователя
    saveToken(access_token)
    currentUser.value = user
    isAuthenticated.value = true

    console.log('Автоматический вход через Windows SSO успешен:', user.username)
    return { success: true }
  } catch (error) {
    // Тихая ошибка - не устанавливаем authError
    console.log('Автоматический Windows SSO не удался, требуется ручной вход')
    return { success: false }
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
    isInitializing,
    authError,
    isAdmin,
    isLaborant,

    // Actions
    initialize,
    login,
    loginWithWindows,
    tryAutoLogin,
    logout,
    clearError,
    fetchCurrentUser
  }
}
