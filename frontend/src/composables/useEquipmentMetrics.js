// composables/useEquipmentMetrics.js
// Вычисление метрик по оборудованию для дашборда

import { computed } from 'vue'

/**
 * Composable для вычисления метрик по оборудованию
 * @param {Ref} filteredData - реактивный массив отфильтрованных данных оборудования
 * @returns {Object} - объект с вычисляемыми метриками
 */
export function useEquipmentMetrics(filteredData) {
  /**
   * Общее количество оборудования (после применения фильтров)
   */
  const totalCount = computed(() => {
    return filteredData.value?.length || 0
  })

  /**
   * Количество годного оборудования (status_fit)
   */
  const fitCount = computed(() => {
    return filteredData.value?.filter(item => item.status === 'status_fit').length || 0
  })

  /**
   * Количество просроченного оборудования (status_expired)
   */
  const expiredCount = computed(() => {
    return filteredData.value?.filter(item => item.status === 'status_expired').length || 0
  })

  /**
   * Количество оборудования на верификации (status_verification)
   */
  const onVerificationCount = computed(() => {
    return filteredData.value?.filter(item => item.status === 'status_verification').length || 0
  })

  /**
   * Количество оборудования на консервации (status_storage)
   */
  const inStorageCount = computed(() => {
    return filteredData.value?.filter(item => item.status === 'status_storage').length || 0
  })

  /**
   * Количество оборудования в ремонте (status_repair)
   */
  const inRepairCount = computed(() => {
    return filteredData.value?.filter(item => item.status === 'status_repair').length || 0
  })

  /**
   * Количество оборудования с истекающим сроком (status_expiring)
   * Дополнительная метрика для более полной картины
   */
  const expiringCount = computed(() => {
    return filteredData.value?.filter(item => item.status === 'status_expiring').length || 0
  })

  /**
   * Процент годного оборудования от общего количества
   */
  const fitPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return Math.round((fitCount.value / totalCount.value) * 100)
  })

  /**
   * Процент просроченного оборудования от общего количества
   */
  const expiredPercentage = computed(() => {
    if (totalCount.value === 0) return 0
    return Math.round((expiredCount.value / totalCount.value) * 100)
  })

  /**
   * Общая статистика для быстрого доступа
   */
  const metrics = computed(() => ({
    total: totalCount.value,
    fit: fitCount.value,
    expired: expiredCount.value,
    expiring: expiringCount.value,
    onVerification: onVerificationCount.value,
    inStorage: inStorageCount.value,
    inRepair: inRepairCount.value,
    fitPercentage: fitPercentage.value,
    expiredPercentage: expiredPercentage.value
  }))

  return {
    // Счетчики
    totalCount,
    fitCount,
    expiredCount,
    expiringCount,
    onVerificationCount,
    inStorageCount,
    inRepairCount,

    // Проценты
    fitPercentage,
    expiredPercentage,

    // Общая статистика
    metrics
  }
}
