<script setup>
import { computed } from 'vue'
import { NModal, NButton, NCard, NSpace, NDataTable } from 'naive-ui'
import { useAnalytics } from '../composables/useAnalytics'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  equipmentData: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:show'])

// Преобразуем массив в ref для composable
const equipmentDataRef = computed(() => props.equipmentData)

// Используем composable для расчетов
const {
  verificationCalendar,
  monthlyTotals,
  monthNames,
  currentYear,
  totalVerifications,
  totalCalibrations,
  totalCertifications,
  totalWorks
} = useAnalytics(equipmentDataRef)

// Конфигурация колонок таблицы
const columns = [
  {
    title: 'Подразделение',
    key: 'department',
    width: 180,
    fixed: 'left',
    align: 'left'
  },
  ...monthNames.map((month, index) => ({
    title: month,
    key: `month_${index}`,
    width: 90,
    align: 'center',
    render: (row) => row.monthCounts[index] || 0
  }))
]

// Данные для таблицы (календарь верификаций)
const tableData = verificationCalendar

// Данные для итоговой строки
const summaryRow = () => {
  const row = { department: 'ИТОГО' }
  monthlyTotals.value.forEach((total, index) => {
    row[`month_${index}`] = total
  })
  return row
}

// Закрытие модального окна
const handleClose = () => {
  emit('update:show', false)
}
</script>

<template>
  <n-modal
    :show="show"
    @update:show="(value) => emit('update:show', value)"
    preset="card"
    title="Аналитика"
    style="width: 95%; max-width: 1600px;"
    :bordered="false"
    :segmented="{ content: true }"
  >
    <template #header-extra>
      <n-button @click="handleClose">
        Закрыть
      </n-button>
    </template>

    <div class="analytics-container">
      <!-- Статистические показатели -->
      <n-space :vertical="false" :size="16" style="margin-bottom: 24px;">
        <n-card
          class="stat-card"
          :bordered="true"
          size="small"
          hoverable
        >
          <div class="stat-value">{{ totalVerifications }}</div>
          <div class="stat-label">Поверок в текущем году</div>
        </n-card>

        <n-card
          class="stat-card"
          :bordered="true"
          size="small"
          hoverable
        >
          <div class="stat-value">{{ totalCalibrations }}</div>
          <div class="stat-label">Калибровок в текущем году</div>
        </n-card>

        <n-card
          class="stat-card"
          :bordered="true"
          size="small"
          hoverable
        >
          <div class="stat-value">{{ totalCertifications }}</div>
          <div class="stat-label">Аттестаций в текущем году</div>
        </n-card>

        <n-card
          class="stat-card primary"
          :bordered="true"
          size="small"
          hoverable
        >
          <div class="stat-value">{{ totalWorks }}</div>
          <div class="stat-label">Всего работ по верификации</div>
        </n-card>
      </n-space>

      <!-- Календарь верификаций -->
      <div class="calendar-section">
        <h3 style="margin: 0 0 16px 0; font-size: 16px; font-weight: 600;">
          Календарь верификаций
        </h3>

        <n-data-table
          :columns="columns"
          :data="tableData"
          :bordered="true"
          :single-line="false"
          :scroll-x="1400"
          size="small"
          :summary="() => summaryRow()"
          style="background-color: white;"
        />
      </div>
    </div>
  </n-modal>
</template>

<style scoped>
.analytics-container {
  font-family: 'PT Astra Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Карточки статистики */
.stat-card {
  flex: 1;
  min-width: 200px;
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 13px;
  color: #666;
  line-height: 1.4;
}

/* Секция календаря */
.calendar-section {
  margin-top: 24px;
}

/* Стили для таблицы */
.calendar-section :deep(.n-data-table) {
  border-radius: 6px;
}

.calendar-section :deep(.n-data-table-th) {
  background-color: #f5f5f5;
  font-weight: 600;
  text-align: center;
}

.calendar-section :deep(.n-data-table-td) {
  text-align: center;
}

/* Стиль итоговой строки */
.calendar-section :deep(.n-data-table__summary tr) {
  background-color: #f0f7ff;
  font-weight: 600;
}

.calendar-section :deep(.n-data-table__summary td) {
  text-align: center;
  color: #0071BC;
}
</style>
