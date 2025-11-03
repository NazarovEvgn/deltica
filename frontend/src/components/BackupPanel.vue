<script setup>
import { ref } from 'vue'
import { NButton, NModal, NSpace, NCard, useMessage } from 'naive-ui'
import axios from 'axios'

const message = useMessage()

// Состояние модального окна
const showModal = ref(false)

// Данные
const backupHistory = ref([])
const loading = ref(false)
const creating = ref(false)
const exporting = ref(false)

// Загрузка истории backup
const loadBackupHistory = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/backup/history?limit=20')
    backupHistory.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке истории backup:', error)
    message.error('Ошибка при загрузке истории')
  } finally {
    loading.value = false
  }
}

// Создание backup
const createBackup = async () => {
  creating.value = true
  try {
    const response = await axios.post('http://localhost:8000/backup/create')
    message.success('Резервная копия создана')
    await loadBackupHistory()
  } catch (error) {
    console.error('Ошибка при создании backup:', error)
    const errorMsg = error.response?.data?.detail || 'Ошибка создания резервной копии'
    message.error(errorMsg)
  } finally {
    creating.value = false
  }
}

// Форматирование даты
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${day}.${month}.${year} ${hours}:${minutes}`
}

// Форматирование размера
const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// Экспорт в Excel
const exportToExcel = async () => {
  exporting.value = true
  try {
    const response = await axios.get('http://localhost:8000/backup/export-excel', {
      responseType: 'blob'
    })

    // Создаем blob и ссылку для скачивания
    const blob = new Blob([response.data], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url

    // Извлекаем имя файла из заголовка Content-Disposition
    const contentDisposition = response.headers['content-disposition']
    let fileName = 'deltica_export.xlsx'
    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename\*=UTF-8''(.+)/)
      if (fileNameMatch && fileNameMatch[1]) {
        fileName = decodeURIComponent(fileNameMatch[1])
      }
    }

    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    message.success('Данные экспортированы в Excel')
  } catch (error) {
    console.error('Ошибка при экспорте в Excel:', error)
    const errorMsg = error.response?.data?.detail || 'Ошибка экспорта данных'
    message.error(errorMsg)
  } finally {
    exporting.value = false
  }
}

// Открытие модального окна
const openModal = async () => {
  showModal.value = true
  await loadBackupHistory()
}

// Закрытие модального окна
const closeModal = () => {
  showModal.value = false
}

defineExpose({
  openModal
})
</script>

<template>
  <div>
    <!-- Модальное окно с управлением backup -->
    <n-modal
      v-model:show="showModal"
      preset="card"
      title="Резервное копирование БД"
      :style="{ width: '800px' }"
      :segmented="{ content: 'soft' }"
    >
      <n-space vertical :size="16">
        <!-- Кнопки создания и экспорта -->
        <n-card size="small">
          <n-space :size="12">
            <n-button
              type="primary"
              :loading="creating"
              :disabled="creating || exporting"
              @click="createBackup"
            >
              {{ creating ? 'Создание резервной копии...' : 'Создать резервную копию' }}
            </n-button>
            <n-button
              type="primary"
              :loading="exporting"
              :disabled="creating || exporting"
              @click="exportToExcel"
            >
              {{ exporting ? 'Экспорт в Excel...' : 'Экспорт в Excel' }}
            </n-button>
          </n-space>
        </n-card>

        <!-- История в виде логов -->
        <n-card title="История резервных копий" size="small">
          <div v-if="loading" style="text-align: center; padding: 20px; color: #666;">
            Загрузка...
          </div>

          <div v-else-if="backupHistory.length === 0" style="text-align: center; padding: 20px; color: #999;">
            Нет резервных копий
          </div>

          <div v-else style="font-family: monospace; font-size: 13px; max-height: 400px; overflow-y: auto;">
            <div
              v-for="backup in backupHistory"
              :key="backup.id"
              style="padding: 8px; border-bottom: 1px solid #f0f0f0;"
              :style="{
                backgroundColor: backup.status === 'success' ? '#f6ffed' : '#fff2e8'
              }"
            >
              <div>
                <strong style="color: #666;">[{{ formatDate(backup.created_at) }}]</strong>
                <span
                  :style="{
                    color: backup.status === 'success' ? '#52c41a' : '#fa8c16',
                    marginLeft: '8px'
                  }"
                >
                  {{ backup.status === 'success' ? '✓ УСПЕХ' : '✗ ОШИБКА' }}
                </span>
              </div>
              <div style="margin-top: 4px; color: #595959;">
                Файл: {{ backup.file_name }}
              </div>
              <div v-if="backup.status === 'success'" style="margin-top: 2px; color: #8c8c8c; font-size: 12px;">
                Размер: {{ formatSize(backup.file_size) }} | Создал: {{ backup.created_by }}
              </div>
              <div v-if="backup.error_message" style="margin-top: 4px; color: #d4380d; font-size: 12px;">
                Ошибка: {{ backup.error_message }}
              </div>
            </div>
          </div>
        </n-card>
      </n-space>

      <template #footer>
        <n-space justify="end">
          <n-button @click="closeModal">Закрыть</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
/* Стили для скроллбара */
div::-webkit-scrollbar {
  width: 8px;
}

div::-webkit-scrollbar-track {
  background: #f1f1f1;
}

div::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

div::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
