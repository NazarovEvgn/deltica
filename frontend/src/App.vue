<script setup>
import { ref, onMounted } from 'vue'
import { NMessageProvider, NDialogProvider, NConfigProvider } from 'naive-ui'
import MainTable from './components/MainTable.vue'
import ArchiveTable from './components/ArchiveTable.vue'
import EquipmentModal from './components/EquipmentModal.vue'
import LoginModal from './components/LoginModal.vue'
import { useAuth } from './composables/useAuth'

// Настройка темы Naive UI для использования PT Astra Sans
const themeOverrides = {
  common: {
    fontFamily: 'PT Astra Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif'
  }
}

const showModal = ref(false)
const editingEquipmentId = ref(null)
const mainTableRef = ref(null)
const showArchive = ref(false)
const showLoginModal = ref(false)

// Инициализация аутентификации
const { initialize } = useAuth()

onMounted(async () => {
  // Проверяем наличие сохраненного токена и восстанавливаем сессию
  await initialize()
})

// Открыть модальное окно для добавления
const handleAddEquipment = () => {
  editingEquipmentId.value = null
  showModal.value = true
}

// Открыть модальное окно для редактирования
const handleEditEquipment = (equipmentId) => {
  editingEquipmentId.value = equipmentId
  showModal.value = true
}

// Обработка сохранения (после создания или обновления)
const handleSaved = () => {
  mainTableRef.value?.loadData()
}

// Переключение отображения архива
const toggleArchive = () => {
  showArchive.value = !showArchive.value
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
        <div id="app">
          <MainTable
            v-if="!showArchive"
            ref="mainTableRef"
            @add-equipment="handleAddEquipment"
            @edit-equipment="handleEditEquipment"
            @show-archive="toggleArchive"
            @show-login="showLogin"
          />
          <ArchiveTable
            v-else
            @back-to-main="toggleArchive"
            @restored="handleSaved"
          />
          <EquipmentModal
            v-model:show="showModal"
            :equipment-id="editingEquipmentId"
            @saved="handleSaved"
          />
          <LoginModal
            v-model:show="showLoginModal"
            @login-success="handleLoginSuccess"
          />
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
</style>
