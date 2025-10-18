// composables/useEquipmentFilters.js
// Централизованная логика поиска и фильтрации оборудования

import { ref, computed, watch } from 'vue'

/**
 * Composable для управления поиском и фильтрацией данных об оборудовании
 * @param {Ref} sourceData - реактивный массив данных оборудования
 * @returns {Object} - объект с методами и реактивными свойствами фильтрации
 */
export function useEquipmentFilters(sourceData) {
  // ==================== СОСТОЯНИЕ ====================

  // Поисковый запрос
  const searchQuery = ref('')

  // Активные колонки для отображения (дефолтные из текущей таблицы)
  const visibleColumns = ref([
    'equipment_name',
    'equipment_model',
    'factory_number',
    'inventory_number',
    'verification_type',
    'verification_interval',
    'verification_due',
    'verification_plan',
    'status'
  ])

  // Динамические фильтры (используется Naive UI Data Table filter format)
  const activeFilters = ref({})

  // ==================== МЕТАДАННЫЕ ПОЛЕЙ ====================

  // Определение всех доступных полей с метаинформацией
  const fieldDefinitions = {
    // Оборудование
    equipment_name: {
      label: 'Наименование',
      group: 'equipment',
      type: 'string',
      searchable: true
    },
    equipment_model: {
      label: 'Модель',
      group: 'equipment',
      type: 'string',
      searchable: true
    },
    equipment_type: {
      label: 'Тип оборудования',
      group: 'equipment',
      type: 'enum',
      searchable: true,
      options: [
        { label: 'СИ (Средство измерения)', value: 'SI' },
        { label: 'ИО (Испытательное оборудование)', value: 'IO' }
      ]
    },
    equipment_specs: {
      label: 'Характеристики',
      group: 'equipment',
      type: 'string',
      searchable: true
    },
    factory_number: {
      label: 'Зав. №',
      group: 'equipment',
      type: 'string',
      searchable: true
    },
    inventory_number: {
      label: 'Инв. №',
      group: 'equipment',
      type: 'string',
      searchable: true
    },
    equipment_year: {
      label: 'Год выпуска',
      group: 'equipment',
      type: 'number',
      searchable: true
    },

    // Верификация
    verification_type: {
      label: 'Тип верификации',
      group: 'verification',
      type: 'enum',
      searchable: true,
      options: [
        { label: 'Калибровка', value: 'calibration' },
        { label: 'Поверка', value: 'verification' },
        { label: 'Аттестация', value: 'certification' }
      ]
    },
    registry_number: {
      label: 'Номер в реестре',
      group: 'verification',
      type: 'string',
      searchable: true
    },
    verification_interval: {
      label: 'Интервал',
      group: 'verification',
      type: 'number',
      searchable: false
    },
    verification_date: {
      label: 'Дата верификации',
      group: 'verification',
      type: 'date',
      searchable: false
    },
    verification_due: {
      label: 'Действует до',
      group: 'verification',
      type: 'date',
      searchable: false,
      computed: true
    },
    verification_plan: {
      label: 'План',
      group: 'verification',
      type: 'date',
      searchable: false
    },
    verification_state: {
      label: 'Состояние',
      group: 'verification',
      type: 'enum',
      searchable: true,
      options: [
        { label: 'В работе', value: 'state_work' },
        { label: 'На хранении', value: 'state_storage' },
        { label: 'На верификации', value: 'state_verification' },
        { label: 'В ремонте', value: 'state_repair' },
        { label: 'Архивировано', value: 'state_archived' }
      ]
    },
    status: {
      label: 'Статус',
      group: 'verification',
      type: 'enum',
      searchable: true,
      options: [
        { label: 'Годен', value: 'status_fit' },
        { label: 'Просрочен', value: 'status_expired' },
        { label: 'Истекает', value: 'status_expiring' },
        { label: 'На хранении', value: 'status_storage' },
        { label: 'На верификации', value: 'status_verification' },
        { label: 'На ремонте', value: 'status_repair' }
      ]
    },

    // Ответственность
    department: {
      label: 'Подразделение',
      group: 'responsibility',
      type: 'string',
      searchable: true
    },
    responsible_person: {
      label: 'Ответственный',
      group: 'responsibility',
      type: 'string',
      searchable: true
    },
    verifier_org: {
      label: 'Организация-поверитель',
      group: 'responsibility',
      type: 'string',
      searchable: true
    },

    // Финансы
    cost_rate: {
      label: 'Стоимость за единицу',
      group: 'finance',
      type: 'number',
      searchable: false
    },
    quantity: {
      label: 'Количество',
      group: 'finance',
      type: 'number',
      searchable: false
    },
    coefficient: {
      label: 'Коэффициент',
      group: 'finance',
      type: 'number',
      searchable: false
    },
    total_cost: {
      label: 'Общая стоимость',
      group: 'finance',
      type: 'number',
      searchable: false
    },
    invoice_number: {
      label: 'Номер счета',
      group: 'finance',
      type: 'string',
      searchable: true
    },
    paid_amount: {
      label: 'Оплачено',
      group: 'finance',
      type: 'number',
      searchable: false
    },
    payment_date: {
      label: 'Дата оплаты',
      group: 'finance',
      type: 'date',
      searchable: false
    }
  }

  // Группировка полей по категориям
  const fieldGroups = {
    equipment: { label: 'Оборудование', icon: 'construct-outline' },
    verification: { label: 'Верификация', icon: 'checkmark-circle-outline' },
    responsibility: { label: 'Ответственность', icon: 'people-outline' },
    finance: { label: 'Финансы', icon: 'cash-outline' }
  }

  // ==================== ПОИСК ====================

  /**
   * Проверяет, содержит ли значение поисковый запрос
   */
  const matchesSearch = (value, query) => {
    if (!value) return false
    const searchLower = query.toLowerCase()
    const valueLower = String(value).toLowerCase()
    return valueLower.includes(searchLower)
  }

  /**
   * Поиск по всем текстовым полям записи
   */
  const searchInRecord = (record, query) => {
    if (!query) return true

    // Поиск по всем searchable полям
    for (const [field, definition] of Object.entries(fieldDefinitions)) {
      if (definition.searchable && record[field]) {
        if (matchesSearch(record[field], query)) {
          return true
        }
      }
    }

    return false
  }

  // ==================== ФИЛЬТРАЦИЯ ====================

  /**
   * Применяет динамические фильтры к записи
   */
  const matchesFilters = (record) => {
    // Если нет активных фильтров, пропускаем запись
    if (Object.keys(activeFilters.value).length === 0) return true

    // Проверяем каждый активный фильтр
    for (const [field, filterValue] of Object.entries(activeFilters.value)) {
      if (!filterValue || filterValue.length === 0) continue

      const recordValue = record[field]
      const definition = fieldDefinitions[field]

      if (!definition) continue

      // Для enum-полей проверяем вхождение в список выбранных значений
      if (definition.type === 'enum') {
        if (Array.isArray(filterValue)) {
          if (!filterValue.includes(recordValue)) return false
        } else {
          if (filterValue !== recordValue) return false
        }
      }

      // Для строковых полей используем частичное совпадение
      if (definition.type === 'string') {
        if (Array.isArray(filterValue)) {
          // Если массив значений, проверяем вхождение
          if (!filterValue.some(v => matchesSearch(recordValue, v))) return false
        } else {
          if (!matchesSearch(recordValue, filterValue)) return false
        }
      }

      // Для числовых полей - точное совпадение или диапазон
      if (definition.type === 'number') {
        if (typeof filterValue === 'object' && filterValue.min !== undefined && filterValue.max !== undefined) {
          const numValue = Number(recordValue)
          if (numValue < filterValue.min || numValue > filterValue.max) return false
        } else if (recordValue !== filterValue) {
          return false
        }
      }

      // Для дат - диапазон
      if (definition.type === 'date' && typeof filterValue === 'object') {
        if (filterValue.start && filterValue.end) {
          const recordDate = new Date(recordValue)
          const startDate = new Date(filterValue.start)
          const endDate = new Date(filterValue.end)
          if (recordDate < startDate || recordDate > endDate) return false
        }
      }
    }

    return true
  }

  // ==================== ВЫЧИСЛЯЕМЫЕ СВОЙСТВА ====================

  /**
   * Отфильтрованные данные с применением поиска и фильтров
   */
  const filteredData = computed(() => {
    if (!sourceData.value) return []

    return sourceData.value.filter(record => {
      // Применяем поиск
      if (!searchInRecord(record, searchQuery.value)) return false

      // Применяем фильтры
      if (!matchesFilters(record)) return false

      return true
    })
  })

  /**
   * Список колонок для отображения в таблице
   */
  const displayColumns = computed(() => {
    return visibleColumns.value.map(field => ({
      prop: field,
      ...fieldDefinitions[field]
    }))
  })

  /**
   * Статистика по отфильтрованным данным
   */
  const filterStats = computed(() => {
    return {
      total: sourceData.value?.length || 0,
      filtered: filteredData.value.length,
      isFiltered: searchQuery.value || Object.keys(activeFilters.value).length > 0
    }
  })

  // ==================== МЕТОДЫ ====================

  /**
   * Сброс всех фильтров и поиска
   */
  const resetFilters = () => {
    searchQuery.value = ''
    activeFilters.value = {}
    // Возвращаем дефолтные колонки
    visibleColumns.value = [
      'equipment_name',
      'equipment_model',
      'factory_number',
      'inventory_number',
      'verification_type',
      'verification_interval',
      'verification_due',
      'verification_plan',
      'status'
    ]
  }

  /**
   * Установка фильтра для конкретного поля
   */
  const setFilter = (field, value) => {
    if (!value || (Array.isArray(value) && value.length === 0)) {
      // Удаляем фильтр если значение пустое
      const { [field]: _, ...rest } = activeFilters.value
      activeFilters.value = rest
    } else {
      activeFilters.value = {
        ...activeFilters.value,
        [field]: value
      }
    }
  }

  /**
   * Переключение видимости колонки
   */
  const toggleColumn = (field, visible) => {
    if (visible && !visibleColumns.value.includes(field)) {
      visibleColumns.value.push(field)
    } else if (!visible) {
      visibleColumns.value = visibleColumns.value.filter(f => f !== field)
    }
  }

  /**
   * Быстрые фильтры (предустановки)
   */
  const applyQuickFilter = (filterName) => {
    resetFilters()

    switch (filterName) {
      case 'expired':
        setFilter('status', ['status_expired'])
        break
      case 'expiring':
        setFilter('status', ['status_expiring'])
        break
      case 'fit':
        setFilter('status', ['status_fit'])
        break
      case 'on_verification':
        setFilter('verification_state', ['state_verification'])
        break
      case 'in_storage':
        setFilter('verification_state', ['state_storage'])
        break
      case 'in_repair':
        setFilter('verification_state', ['state_repair'])
        break
    }
  }

  // ==================== СОХРАНЕНИЕ НАСТРОЕК ====================

  // Сохраняем настройки фильтров в localStorage
  watch([visibleColumns, activeFilters], () => {
    localStorage.setItem('equipment_visible_columns', JSON.stringify(visibleColumns.value))
    localStorage.setItem('equipment_active_filters', JSON.stringify(activeFilters.value))
  }, { deep: true })

  // Загружаем сохраненные настройки при инициализации
  const loadSavedSettings = () => {
    const savedColumns = localStorage.getItem('equipment_visible_columns')
    const savedFilters = localStorage.getItem('equipment_active_filters')

    if (savedColumns) {
      try {
        const parsed = JSON.parse(savedColumns)
        // Фильтруем verification_date из сохраненных колонок
        visibleColumns.value = parsed.filter(col => col !== 'verification_date')
      } catch (e) {
        console.warn('Failed to load saved columns:', e)
      }
    }

    if (savedFilters) {
      try {
        activeFilters.value = JSON.parse(savedFilters)
      } catch (e) {
        console.warn('Failed to load saved filters:', e)
      }
    }
  }

  // ==================== ВОЗВРАТ ====================

  return {
    // Состояние
    searchQuery,
    visibleColumns,
    activeFilters,

    // Метаданные
    fieldDefinitions,
    fieldGroups,

    // Вычисляемые свойства
    filteredData,
    displayColumns,
    filterStats,

    // Методы
    resetFilters,
    setFilter,
    toggleColumn,
    applyQuickFilter,
    loadSavedSettings
  }
}
