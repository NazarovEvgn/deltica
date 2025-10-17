<script setup>
import { computed } from 'vue'
import { NSpace, NStatistic } from 'naive-ui'

// Принимаем метрики как пропс
const props = defineProps({
  metrics: {
    type: Object,
    required: true
  }
})

// Определяем цвета для каждой метрики
const metricColors = {
  total: '#18a058', // зеленый
  fit: '#18a058', // зеленый
  expired: '#d03050', // красный
  onVerification: '#2080f0', // синий
  inStorage: '#f0a020', // оранжевый
  inRepair: '#9333ea' // фиолетовый
}

// Конфигурация отображаемых метрик
const displayMetrics = computed(() => [
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
    label: 'На хранении',
    value: props.metrics.inStorage,
    color: metricColors.inStorage,
    key: 'inStorage'
  },
  {
    label: 'В ремонте',
    value: props.metrics.inRepair,
    color: metricColors.inRepair,
    key: 'inRepair'
  }
])
</script>

<template>
  <div class="metrics-dashboard">
    <n-space :size="12" align="center" :wrap="false">
      <div
        v-for="metric in displayMetrics"
        :key="metric.key"
        class="metric-card"
        :style="{ borderLeftColor: metric.color }"
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
  padding: 8px 16px;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  border-left-width: 4px;
  border-radius: 4px;
  min-width: 90px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.metric-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  line-height: 1.2;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: #666;
  text-align: center;
  line-height: 1.3;
  white-space: nowrap;
}
</style>
