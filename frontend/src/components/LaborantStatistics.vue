<script setup>
import { ref, computed, watch } from 'vue'
import {
  NButton,
  NModal,
  NCard,
  NSpace,
  NDatePicker,
  NText,
  NDivider,
  useMessage
} from 'naive-ui'
import axios from 'axios'
import { API_ENDPOINTS } from '../config/api.js'
import { useAuth } from '../composables/useAuth'

const message = useMessage()
const { currentUser } = useAuth()

const showModal = ref(false)
const dateRange = ref(null)
const archiveData = ref([])
const isLoading = ref(false)

// Props - данные основной таблицы
const props = defineProps({
  equipmentData: {
    type: Array,
    required: true
  }
})

// Открытие модального окна
const openModal = () => {
  showModal.value = true
  // Устанавливаем текущий год по умолчанию
  const startOfYear = new Date(new Date().getFullYear(), 0, 1).getTime()
  const endOfYear = new Date(new Date().getFullYear(), 11, 31).getTime()
  dateRange.value = [startOfYear, endOfYear]
}

// Закрытие модального окна
const closeModal = () => {
  showModal.value = false
}

// Загрузка данных из архива
const loadArchiveData = async () => {
  try {
    isLoading.value = true
    const response = await axios.get(API_ENDPOINTS.archive, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    archiveData.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке архива:', error)
    message.error('Ошибка при загрузке данных архива')
  } finally {
    isLoading.value = false
  }
}

// Загружаем архив при открытии
watch(showModal, (newValue) => {
  if (newValue) {
    loadArchiveData()
  }
})

// Статистика по выбранному диапазону дат
const statistics = computed(() => {
  if (!dateRange.value || !Array.isArray(dateRange.value) || dateRange.value.length !== 2) {
    return {
      totalVerified: 0,
      verifications: 0,
      calibrations: 0,
      certifications: 0,
      failed: 0,
      fit: 0,
      inStorage: 0
    }
  }

  const [startTimestamp, endTimestamp] = dateRange.value
  const startDate = new Date(startTimestamp)
  const endDate = new Date(endTimestamp)

  // Фильтруем оборудование по дате верификации
  const verifiedInRange = props.equipmentData.filter(item => {
    if (!item.verification_date) return false

    const verificationDate = new Date(item.verification_date)
    return verificationDate >= startDate && verificationDate <= endDate
  })

  // Подсчет по типам верификации
  const verifications = verifiedInRange.filter(item => item.verification_type === 'verification').length
  const calibrations = verifiedInRange.filter(item => item.verification_type === 'calibration').length
  const certifications = verifiedInRange.filter(item => item.verification_type === 'certification').length

  // Подсчет по статусам (только из отфильтрованных по дате)
  const fit = verifiedInRange.filter(item => item.status === 'status_fit').length
  const inStorage = verifiedInRange.filter(item => item.status === 'status_storage').length

  // Подсчет не прошедших поверку из архива
  // Фильтруем архив по подразделению текущего пользователя и причине "Извещение о непригодности"
  const userDepartment = currentUser.value?.department
  const failed = archiveData.value.filter(item => {
    if (!item.archive_reason || !item.department) return false

    // Проверяем подразделение и причину архивации
    const matchesDepartment = item.department === userDepartment
    const matchesReason = item.archive_reason.includes('Извещение о непригодности') ||
                          item.archive_reason.includes('непригодност')

    // Проверяем, что дата верификации попадает в диапазон (если указана)
    if (item.verification_date) {
      const verificationDate = new Date(item.verification_date)
      return matchesDepartment && matchesReason &&
             verificationDate >= startDate && verificationDate <= endDate
    }

    return matchesDepartment && matchesReason
  }).length

  return {
    totalVerified: verifiedInRange.length,
    verifications,
    calibrations,
    certifications,
    failed,
    fit,
    inStorage
  }
})

// Emit для событий
const emit = defineEmits(['show-archive-for-failed'])

// Обработчик клика на метрику "Списано"
const handleFailedClick = () => {
  console.log('[LaborantStatistics] Клик на метрику Списано')
  console.log('[LaborantStatistics] Подразделение:', currentUser.value?.department)
  console.log('[LaborantStatistics] Кол-во списанного:', statistics.value.failed)

  // Закрываем модальное окно статистики
  showModal.value = false

  // Отправляем событие родителю с подразделением лаборанта
  emit('show-archive-for-failed', currentUser.value?.department)
  console.log('[LaborantStatistics] Событие show-archive-for-failed отправлено')
}

// Экспортируем метод открытия для родительского компонента
defineExpose({
  openModal
})
</script>

<template>
  <n-modal
    v-model:show="showModal"
    preset="card"
    title="Статистика верификации"
    :style="{ width: '800px' }"
    @after-leave="closeModal"
  >
    <n-space vertical :size="20">
      <!-- Селектор периода -->
      <div>
        <n-text strong style="display: block; margin-bottom: 8px; font-size: 14px;">
          Период верификации
        </n-text>
        <n-date-picker
          v-model:value="dateRange"
          type="daterange"
          clearable
          :style="{ width: '100%' }"
          placeholder="Выберите период"
          start-placeholder="Дата от"
          end-placeholder="Дата до"
        />
      </div>

      <n-divider style="margin: 8px 0;" />

      <!-- Блок: Общая статистика -->
      <n-card title="Общая статистика" size="small">
        <n-space vertical :size="12">
          <div class="stat-row">
            <n-text depth="3">Всего прошло верификацию:</n-text>
            <n-text strong style="font-size: 16px; color: #333;">{{ statistics.totalVerified }}</n-text>
          </div>
        </n-space>
      </n-card>

      <!-- Блок: По типам верификации -->
      <n-card title="По типам верификации" size="small">
        <n-space vertical :size="12">
          <div class="stat-row">
            <n-text depth="3">Поверка:</n-text>
            <n-text strong style="font-size: 16px; color: #333;">{{ statistics.verifications }}</n-text>
          </div>
          <div class="stat-row">
            <n-text depth="3">Калибровка:</n-text>
            <n-text strong style="font-size: 16px; color: #333;">{{ statistics.calibrations }}</n-text>
          </div>
          <div class="stat-row">
            <n-text depth="3">Аттестация:</n-text>
            <n-text strong style="font-size: 16px; color: #333;">{{ statistics.certifications }}</n-text>
          </div>
        </n-space>
      </n-card>

      <!-- Блок: Не прошедшие поверку -->
      <n-card title="Не прошедшие поверку (из архива)" size="small">
        <n-space vertical :size="12">
          <div class="stat-row clickable" @click="handleFailedClick">
            <n-text depth="3">Извещение о непригодности:</n-text>
            <n-text strong style="font-size: 16px; color: #d03050;">{{ statistics.failed }}</n-text>
          </div>
        </n-space>
      </n-card>

      <!-- Блок: По статусам -->
      <n-card title="По статусам" size="small">
        <n-space vertical :size="12">
          <div class="stat-row">
            <n-text depth="3">Годных:</n-text>
            <n-text strong style="font-size: 16px; color: #18a058;">{{ statistics.fit }}</n-text>
          </div>
          <div class="stat-row">
            <n-text depth="3">На консервации:</n-text>
            <n-text strong style="font-size: 16px; color: #333;">{{ statistics.inStorage }}</n-text>
          </div>
        </n-space>
      </n-card>
    </n-space>
  </n-modal>
</template>

<style scoped>
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
}

.stat-row.clickable {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.stat-row.clickable:hover {
  background-color: rgba(0, 113, 188, 0.1);
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .stat-row {
    background-color: rgba(255, 255, 255, 0.05);
  }

  .stat-row.clickable:hover {
    background-color: rgba(0, 113, 188, 0.2);
  }
}
</style>
