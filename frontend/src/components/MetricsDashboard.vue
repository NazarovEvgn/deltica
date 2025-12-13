<script setup>
import { computed } from 'vue'
import { NSpace, NStatistic } from 'naive-ui'

// Принимаем метрики как пропс
const props = defineProps({
  metrics: {
    type: Object,
    required: true
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  activeFilters: {
    type: Object,
    default: () => ({})
  }
})

// Эмитим события
const emit = defineEmits(['metric-click', 'reset-filters'])

// Обработчик клика на метрику
const handleMetricClick = (metricKey) => {
  if (metricKey === 'total') {
    // Клик на "Всего" сбрасывает все фильтры
    emit('reset-filters')
  } else {
    emit('metric-click', metricKey)
  }
}

// Убираем цвета из метрик согласно плану UI/UX
const metricColors = {
  total: '#333333',
  fit: '#333333',
  expired: '#333333',
  onVerification: '#333333',
  inStorage: '#333333',
  inRepair: '#333333',
  failed: '#333333'
}

// Определяем активную метрику на основе activeFilters
const activeMetricKey = computed(() => {
  if (!props.activeFilters || Object.keys(props.activeFilters).length === 0) {
    return 'total' // Нет фильтров = показываем все
  }

  // Проверяем какой фильтр активен
  if (props.activeFilters.status) {
    const statusFilters = Array.isArray(props.activeFilters.status)
      ? props.activeFilters.status
      : [props.activeFilters.status]

    if (statusFilters.includes('status_fit')) return 'fit'
    if (statusFilters.includes('status_expired')) return 'expired'
    if (statusFilters.includes('status_expiring')) return 'expiring'
  }

  if (props.activeFilters.verification_state) {
    const stateFilters = Array.isArray(props.activeFilters.verification_state)
      ? props.activeFilters.verification_state
      : [props.activeFilters.verification_state]

    if (stateFilters.includes('state_verification')) return 'onVerification'
    if (stateFilters.includes('state_storage')) return 'inStorage'
    if (stateFilters.includes('state_repair')) return 'inRepair'
  }

  return null
})

// Конфигурация отображаемых метрик
const displayMetrics = computed(() => {
  const allMetrics = [
    {
      label: 'Всего',
      value: props.metrics.total,
      color: metricColors.total,
      key: 'total'
    },
    {
      label: 'Годных',
      value: props.metrics.fit,
      color: metricColors.fit,
      key: 'fit'
    },
    {
      label: 'Просроченных',
      value: props.metrics.expired,
      color: metricColors.expired,
      key: 'expired'
    },
    {
      label: 'На верификации',
      value: props.metrics.onVerification,
      color: metricColors.onVerification,
      key: 'onVerification'
    },
    {
      label: 'На консервации',
      value: props.metrics.inStorage,
      color: metricColors.inStorage,
      key: 'inStorage'
    },
    {
      label: 'В ремонте',
      value: props.metrics.inRepair,
      color: metricColors.inRepair,
      key: 'inRepair'
    },
    {
      label: 'Списано',
      value: props.metrics.failed,
      color: metricColors.failed,
      key: 'failed'
    }
  ]

  // Убираем метрику "Списано" для администраторов
  if (props.isAdmin) {
    return allMetrics.filter(metric => metric.key !== 'failed')
  }

  return allMetrics
})
</script>

<template>
  <div class="metrics-dashboard">
    <n-space :size="8" align="center" :wrap="false">
      <div
        v-for="metric in displayMetrics"
        :key="metric.key"
        class="metric-card clickable"
        :class="{ active: metric.key === activeMetricKey }"
        :style="{ borderLeftColor: metric.color }"
        @click="handleMetricClick(metric.key)"
      >
        <div class="metric-value" :style="{ color: metric.color }">
          {{ metric.value }}
        </div>
        <div class="metric-label">{{ metric.label }}</div>
      </div>
    </n-space>
  </div>
</template>

<style scoped>
.metrics-dashboard {
  display: flex;
  align-items: center;
}

.metric-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-radius: 3px;
  min-width: 60px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.metric-card.clickable {
  cursor: pointer;
}

.metric-card.clickable:hover {
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
  background: #f8f9fa;
}

.metric-card.clickable:active {
  transform: translateY(0);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-card.active {
  background: #e3f2fd;
  border-color: #0071BC;
  box-shadow: 0 2px 8px rgba(0, 113, 188, 0.2);
}

.metric-card.active .metric-value {
  color: #0071BC !important;
  font-weight: 700;
}

.metric-value {
  font-size: 17px;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 2px;
}

.metric-label {
  font-size: 11px;
  color: #666;
  text-align: center;
  line-height: 1.2;
  white-space: nowrap;
}
</style>
