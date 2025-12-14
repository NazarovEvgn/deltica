<script setup>
import { ref, onMounted } from 'vue'
import { NMessageProvider, NDialogProvider, NConfigProvider, NSpin } from 'naive-ui'
import MainTable from './components/MainTable.vue'
import ArchiveTable from './components/ArchiveTable.vue'
import EquipmentModal from './components/EquipmentModal.vue'
import LoginModal from './components/LoginModal.vue'
import ConfigModal from './components/ConfigModal.vue'
import { useAuth } from './composables/useAuth'
import { updateApiBaseUrl } from './config/api.js'

// Настройка темы Naive UI для использования PT Astra Sans и корпоративных цветов
const themeOverrides = {
  common: {
    fontFamily: 'PT Astra Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif',
    borderRadius: '6px',               // Увеличен радиус скругления до 6px (одинаково с таблицей)
    primaryColor: '#0071BC',           // Основной синий Газпром Нефти
    primaryColorHover: '#005a9c',      // Темнее при наведении
    primaryColorPressed: '#004a7c',    // Темнее при нажатии
    infoColor: '#00A6E4',              // Светло-голубой
    infoColorHover: '#0086b8',
    infoColorPressed: '#006890',
    warningColor: '#F7941D',           // Оранжевый
    warningColorHover: '#d77a16',
    warningColorPressed: '#b76512',
    successColor: '#8BC53F',           // Зеленый
    successColorHover: '#76a835',
    successColorPressed: '#5f8829'
  }
}

const showModal = ref(false)
const editingEquipmentId = ref(null)
const isViewMode = ref(false)
const mainTableRef = ref(null)
const showArchive = ref(false)
const showLoginModal = ref(false)
const showConfigModal = ref(false)

// Параметры для архива (режим просмотра для лаборанта)
const archiveReadOnly = ref(false)
const archiveDepartmentFilter = ref(null)

// Инициализация аутентификации
const { initialize, isAuthenticated, isInitializing } = useAuth()

onMounted(async () => {
  // В Electron режиме сначала проверяем конфигурацию
  if (window.electron) {
    const config = await window.electron.getConfig()

    // Если конфигурации нет - показываем диалог настройки
    if (!config || !config.serverUrl) {
      showConfigModal.value = true
      return
    }

    // Если конфигурация есть - обновляем API URL
    updateApiBaseUrl(config.serverUrl)
  }

  // Попытка автоматического входа:
  // 1. Проверка сохраненного токена
  // 2. Если токена нет - попытка Windows SSO
  // 3. Если не получилось - показ формы логина
  await initialize()
})

// Обработка сохранения конфигурации
const handleConfigSaved = async (serverUrl) => {
  showConfigModal.value = false

  // Обновляем API URL
  updateApiBaseUrl(serverUrl)

  // Продолжаем инициализацию
  await initialize()
}

// Открыть модальное окно для добавления
const handleAddEquipment = () => {
  editingEquipmentId.value = null
  isViewMode.value = false
  showModal.value = true
}

// Открыть модальное окно для редактирования
const handleEditEquipment = (equipmentId) => {
  editingEquipmentId.value = equipmentId
  isViewMode.value = false
  showModal.value = true
}

// Открыть модальное окно для просмотра (для лаборанта)
const handleViewEquipment = (equipmentId) => {
  editingEquipmentId.value = equipmentId
  isViewMode.value = true
  showModal.value = true
}

// Обработка сохранения (после создания или обновления)
const handleSaved = () => {
  mainTableRef.value?.loadData()
}

// Переключение отображения архива
const toggleArchive = (options = {}) => {
  console.log('[App.vue] toggleArchive вызван с параметрами:', options)
  console.log('[App.vue] Текущее состояние showArchive:', showArchive.value)

  // Если переданы параметры (например, из метрики "Списано"), всегда открываем архив
  if (options.readOnly !== undefined || options.departmentFilter !== undefined) {
    console.log('[App.vue] Открываем архив с параметрами (режим метрики Списано)')
    showArchive.value = true
    archiveReadOnly.value = options.readOnly || false
    archiveDepartmentFilter.value = options.departmentFilter || null
  } else if (showArchive.value) {
    // Если параметры не переданы и архив уже открыт - закрываем
    console.log('[App.vue] Закрываем архив (переключатель)')
    showArchive.value = false
    archiveReadOnly.value = false
    archiveDepartmentFilter.value = null
  } else {
    // Открываем архив без параметров (обычный режим)
    console.log('[App.vue] Открываем архив в обычном режиме')
    showArchive.value = true
    archiveReadOnly.value = false
    archiveDepartmentFilter.value = null
  }

  console.log('[App.vue] Новое состояние:', {
    showArchive: showArchive.value,
    readOnly: archiveReadOnly.value,
    departmentFilter: archiveDepartmentFilter.value
  })
}

// Показать окно логина
const showLogin = () => {
  showLoginModal.value = true
}

// Обработка успешного входа
const handleLoginSuccess = () => {
  // После входа перезагружаем данные таблицы
  mainTableRef.value?.loadData()
}
</script>

<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-dialog-provider>
        <!-- Диалог настройки сервера (первый запуск в Electron) -->
        <ConfigModal
          v-model:show="showConfigModal"
          @config-saved="handleConfigSaved"
        />

        <div id="app">
          <!-- Индикатор загрузки при инициализации -->
          <div v-if="isInitializing" class="loading-page">
            <div class="loading-container">
              <img src="/favicon.png" alt="Deltica" class="loading-logo" />
              <h1 class="loading-title">Deltica</h1>
              <n-spin size="large" style="margin-top: 32px" />
              <p class="loading-text">Вход в систему...</p>
            </div>
          </div>

          <!-- Страница авторизации (если пользователь не авторизован после инициализации) -->
          <div v-else-if="!isAuthenticated" class="login-page">
            <div class="login-container">
              <!-- Логотип и название -->
              <div class="login-header">
                <img src="/favicon.png" alt="Deltica" class="login-logo" />
                <h1 class="login-title">Deltica</h1>
              </div>
              <!-- Форма входа -->
              <LoginModal
                :show="true"
                :embedded="true"
                @login-success="handleLoginSuccess"
              />
            </div>
          </div>

          <!-- Основное приложение (если пользователь авторизован) -->
          <template v-else>
            <MainTable
              v-if="!showArchive"
              ref="mainTableRef"
              @add-equipment="handleAddEquipment"
              @edit-equipment="handleEditEquipment"
              @view-equipment="handleViewEquipment"
              @show-archive="toggleArchive"
              @show-login="showLogin"
            />
            <ArchiveTable
              v-else
              :read-only="archiveReadOnly"
              :department-filter="archiveDepartmentFilter"
              @back-to-main="toggleArchive"
              @restored="handleSaved"
            />
            <EquipmentModal
              v-model:show="showModal"
              :equipment-id="editingEquipmentId"
              :read-only="isViewMode"
              @saved="handleSaved"
            />
          </template>
        </div>
      </n-dialog-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<style>
#app {
  height: 100vh;
  overflow: hidden;
}

/* Страница загрузки при инициализации */
.loading-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #ececec;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.loading-logo {
  width: 48px;
  height: 48px;
  margin-bottom: 16px;
}

.loading-title {
  font-size: 36px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
}

.loading-text {
  font-size: 14px;
  color: #666;
  margin-top: 16px;
}

/* Страница авторизации */
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #ececec;
}

.login-container {
  background: white;
  padding: 48px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 400px;
}

.login-header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 32px;
}

.login-logo {
  width: 32px;
  height: 32px;
}

.login-title {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin: 0;
}
</style>
