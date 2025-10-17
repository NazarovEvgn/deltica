<script setup>
import { ref, onMounted } from 'vue'
import {
  NButton,
  NModal,
  NCard,
  NList,
  NListItem,
  NThing,
  NIcon,
  NSpace,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  useMessage,
  useDialog
} from 'naive-ui'
import {
  DocumentTextOutline as DocumentIcon,
  CloudUploadOutline as CloudUploadIcon,
  TrashOutline as TrashIcon,
  FolderOpenOutline as FolderIcon
} from '@vicons/ionicons5'
import axios from 'axios'
import { useAuth } from '../composables/useAuth'

const message = useMessage()
const dialog = useDialog()
const { isAdmin } = useAuth()

const showModal = ref(false)
const documents = ref([])
const isLoading = ref(false)

// Загрузка списка документов
const loadDocuments = async () => {
  try {
    isLoading.value = true
    const response = await axios.get('http://localhost:8000/pinned-documents/')
    documents.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке документов:', error)
    message.error(error.response?.data?.detail || 'Ошибка при загрузке документов')
  } finally {
    isLoading.value = false
  }
}

// Открытие панели
const handleOpen = () => {
  showModal.value = true
  loadDocuments()
}

// Закрытие панели
const handleClose = () => {
  showModal.value = false
}

// Обработчик загрузки файла (только для админа)
const handleFileUpload = async ({ file }) => {
  if (!isAdmin.value) {
    message.warning('Загрузка документов доступна только администратору')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file.file)

    await axios.post(
      'http://localhost:8000/pinned-documents/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    message.success('Документ успешно загружен')
    await loadDocuments()
  } catch (error) {
    console.error('Ошибка при загрузке документа:', error)
    message.error(error.response?.data?.detail || 'Ошибка при загрузке документа')
  }

  return false  // Предотвращаем стандартное поведение
}

// Открытие документа для просмотра в новой вкладке
const openDocument = async (documentId) => {
  try {
    const response = await axios.get(`http://localhost:8000/pinned-documents/view/${documentId}`, {
      responseType: 'blob'
    })

    // Создаем blob URL
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)

    // Открываем в новой вкладке
    window.open(url, '_blank')

    // Освобождаем память через некоторое время
    setTimeout(() => window.URL.revokeObjectURL(url), 100)
  } catch (error) {
    console.error('Ошибка при открытии документа:', error)
    message.error(error.response?.data?.detail || 'Ошибка при открытии документа')
  }
}

// Скачивание документа
const downloadDocument = async (documentId, fileName) => {
  try {
    const response = await axios.get(`http://localhost:8000/pinned-documents/download/${documentId}`, {
      responseType: 'blob'
    })

    // Создаем blob URL
    const blob = new Blob([response.data], { type: 'application/pdf' })
    const url = window.URL.createObjectURL(blob)

    // Создаем временную ссылку для скачивания
    const link = document.createElement('a')
    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()

    // Очистка
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Ошибка при скачивании документа:', error)
    message.error(error.response?.data?.detail || 'Ошибка при скачивании документа')
  }
}

// Удаление документа (только для админа)
const deleteDocument = async (documentId, documentName) => {
  if (!isAdmin.value) {
    message.warning('Удаление документов доступно только администратору')
    return
  }

  dialog.warning({
    title: 'Подтверждение удаления',
    content: `Вы уверены, что хотите удалить документ "${documentName}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.delete(`http://localhost:8000/pinned-documents/${documentId}`)
        message.success('Документ успешно удален')
        await loadDocuments()
      } catch (error) {
        console.error('Ошибка при удалении документа:', error)
        message.error(error.response?.data?.detail || 'Ошибка при удалении документа')
      }
    }
  })
}

// Форматирование размера файла
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// Форматирование даты загрузки
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<template>
  <div>
    <!-- Кнопка для открытия панели -->
    <n-button @click="handleOpen" type="info">
      <template #icon>
        <n-icon :component="FolderIcon" />
      </template>
      Документы
    </n-button>

    <!-- Модальное окно с документами -->
    <n-modal
      v-model:show="showModal"
      preset="card"
      title="Закрепленные документы"
      style="width: 800px;"
      :segmented="{ content: 'soft', footer: 'soft' }"
    >
      <!-- Загрузчик файлов (только для админа) -->
      <template v-if="isAdmin">
        <n-space vertical style="margin-bottom: 24px;">
          <n-upload
            :custom-request="handleFileUpload"
            :show-file-list="false"
            accept=".pdf"
          >
            <n-upload-dragger>
              <div style="margin-bottom: 12px">
                <n-icon size="48" :depth="3">
                  <cloud-upload-icon />
                </n-icon>
              </div>
              <n-text style="font-size: 16px">
                Перетащите PDF документ сюда или нажмите для загрузки
              </n-text>
              <n-p depth="3" style="margin: 8px 0 0 0">
                Допустимые форматы: только PDF<br />
                Максимальный размер: 50 МБ
              </n-p>
            </n-upload-dragger>
          </n-upload>
        </n-space>
      </template>

      <!-- Список документов -->
      <n-list v-if="documents.length > 0" bordered>
        <n-list-item v-for="doc in documents" :key="doc.id">
          <n-thing>
            <template #avatar>
              <n-icon size="24" :component="DocumentIcon" />
            </template>
            <template #header>
              <a
                href="#"
                @click.prevent="openDocument(doc.id)"
                style="color: #18a058; text-decoration: none; cursor: pointer; font-weight: 500;"
                @mouseover="$event.target.style.textDecoration = 'underline'"
                @mouseleave="$event.target.style.textDecoration = 'none'"
              >
                {{ doc.file_name }}
              </a>
            </template>
            <template #description>
              {{ formatFileSize(doc.file_size) }} • Загружен: {{ formatDate(doc.uploaded_at) }}
              <span v-if="doc.uploaded_by"> • {{ doc.uploaded_by }}</span>
            </template>
            <template #action>
              <n-space>
                <n-button size="small" @click="downloadDocument(doc.id, doc.file_name)">
                  Скачать
                </n-button>
                <n-button
                  v-if="isAdmin"
                  size="small"
                  type="error"
                  @click="deleteDocument(doc.id, doc.file_name)"
                >
                  <template #icon>
                    <n-icon :component="TrashIcon" />
                  </template>
                  Удалить
                </n-button>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>
      <n-text v-else depth="3" style="display: block; text-align: center; padding: 40px 0;">
        Документы не загружены
      </n-text>

      <template #footer>
        <n-space justify="end">
          <n-button @click="handleClose">Закрыть</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
/* Дополнительные стили если нужно */
</style>
