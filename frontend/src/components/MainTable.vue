<script setup>
import { ref, onMounted, onUnmounted, h, computed, watch } from 'vue'
import { NButton, NSpace, NDrawer, NDrawerContent } from 'naive-ui'
import { VGrid } from '@revolist/vue3-datagrid'
import axios from 'axios'
import SearchBar from './SearchBar.vue'
import FilterPanel from './FilterPanel.vue'
import UserProfile from './UserProfile.vue'
import DocumentsPanel from './DocumentsPanel.vue'
import MetricsDashboard from './MetricsDashboard.vue'
import BackupPanel from './BackupPanel.vue'
import SystemMonitor from './SystemMonitor.vue'
import ContractsNotebook from './ContractsNotebook.vue'
import AnalyticsDashboard from './AnalyticsDashboard.vue'
import LaborantStatistics from './LaborantStatistics.vue'
import AppLogo from './AppLogo.vue'
import AdminPanel from './AdminPanel.vue'
import DocumentActionsDropdown from './DocumentActionsDropdown.vue'
import { useEquipmentFilters } from '../composables/useEquipmentFilters'
import { useEquipmentMetrics } from '../composables/useEquipmentMetrics'
import { useAuth } from '../composables/useAuth'

const emit = defineEmits(['add-equipment', 'edit-equipment', 'view-equipment', 'show-archive', 'show-login'])

// Аутентификация
const { currentUser, isAuthenticated, isAdmin, isLaborant } = useAuth()

// Данные таблицы
const source = ref([])
const loading = ref(false)

// Архивные данные для метрики "Списано"
const archiveData = ref([])

// История изменений для undo функциональности (последние 10 операций)
const editHistory = ref([])
const MAX_HISTORY_SIZE = 10
const isUndoing = ref(false) // Флаг для предотвращения добавления в историю во время undo

// Выбранные строки для печати этикеток
const selectedIds = ref(new Set())
// Счетчик для принудительного обновления чекбоксов
const checkboxUpdateTrigger = ref(0)

// Инициализация фильтров
const {
  searchQuery,
  visibleColumns,
  activeFilters,
  fieldDefinitions,
  fieldGroups,
  filteredData,
  filterStats,
  resetFilters,
  applyQuickFilter,
  loadSavedSettings
} = useEquipmentFilters(source, isLaborant)

// Инициализация метрик (на основе данных из БД, уже отфильтрованных по department для лаборанта)
const { metrics } = useEquipmentMetrics(source, archiveData, currentUser)

// Состояние drawer для фильтров
const showFilterDrawer = ref(false)

// Refs для BackupPanel, SystemMonitor, ContractsNotebook, AnalyticsDashboard и LaborantStatistics
const backupPanelRef = ref(null)
const systemMonitorRef = ref(null)
const statisticsRef = ref(null)
const showContractsNotebook = ref(false)
const showAnalyticsDashboard = ref(false)

// Функция форматирования даты в dd.mm.yyyy
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

// Функция форматирования месяца и года (например: Октябрь 2025)
const formatMonthYear = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ]
  const month = monthNames[date.getMonth()]
  const year = date.getFullYear()
  return `${month} ${year}`
}

// Маппинги для преобразования технических значений в человекочитаемые
const departmentMap = {
  'gruppa_sm': 'Группа СМ',
  'gtl': 'ГТЛ',
  'lbr': 'ЛБР',
  'ltr': 'ЛТР',
  'lhaiei': 'ЛХАиЭИ',
  'ogmk': 'ОГМК',
  'oii': 'ОИИ',
  'ooops': 'ОООПС',
  'smtsik': 'СМТСиК',
  'soii': 'СОИИ',
  'to': 'ТО',
  'ts': 'ТС',
  'es': 'ЭС'
}

const verificationStateMap = {
  'state_work': 'В работе',
  'state_storage': 'На консервации',
  'state_verification': 'На верификации',
  'state_repair': 'В ремонте',
  'state_archived': 'В архиве'
}

const verificationTypeMap = {
  'calibration': 'Калибровка',
  'verification': 'Поверка',
  'certification': 'Аттестация'
}

const equipmentTypeMap = {
  'SI': 'СИ',
  'IO': 'ИО'
}

const statusMap = {
  'status_fit': 'Годен',
  'status_expired': 'Просрочен',
  'status_expiring': 'Истекает',
  'status_storage': 'На консервации',
  'status_verification': 'На верификации',
  'status_repair': 'На ремонте'
}

// Загрузка данных с бэкенда
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/main-table/')
    let data = response.data

    // Фильтрация данных для лаборанта (показываем только оборудование его подразделения)
    if (isLaborant.value && currentUser.value?.department) {
      data = data.filter(item => item.department === currentUser.value.department)
    }

    source.value = data
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  } finally {
    loading.value = false
  }
}

// Загрузка архивных данных для метрики "Списано"
const loadArchiveData = async () => {
  try {
    const response = await axios.get('http://localhost:8000/archive/', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    archiveData.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке архивных данных:', error)
    // Не показываем ошибку пользователю, так как это не критично
    archiveData.value = []
  }
}

// Обратные маппинги (для преобразования обратно в технические значения)
const reverseDepartmentMap = Object.fromEntries(
  Object.entries(departmentMap).map(([key, value]) => [value, key])
)

const reverseVerificationStateMap = Object.fromEntries(
  Object.entries(verificationStateMap).map(([key, value]) => [value, key])
)

const reverseVerificationTypeMap = Object.fromEntries(
  Object.entries(verificationTypeMap).map(([key, value]) => [value, key])
)

const reverseEquipmentTypeMap = Object.fromEntries(
  Object.entries(equipmentTypeMap).map(([key, value]) => [value, key])
)

// Функция для преобразования даты из dd.mm.yyyy в yyyy-mm-dd
const parseDateFromDisplay = (dateString) => {
  if (!dateString || dateString === '') return null

  // Если уже в формате yyyy-mm-dd
  if (dateString.match(/^\d{4}-\d{2}-\d{2}$/)) return dateString

  // Если в формате dd.mm.yyyy
  const match = dateString.match(/^(\d{2})\.(\d{2})\.(\d{4})$/)
  if (match) {
    const [, day, month, year] = match
    return `${year}-${month}-${day}`
  }

  return dateString
}

// Функция для преобразования месяца из "Октябрь 2025" в yyyy-mm-dd
const parseMonthYearFromDisplay = (monthYearString) => {
  if (!monthYearString || monthYearString === '') return null

  const monthNames = [
    'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
    'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
  ]

  const parts = monthYearString.split(' ')
  if (parts.length === 2) {
    const monthIndex = monthNames.indexOf(parts[0])
    if (monthIndex !== -1) {
      const year = parts[1]
      const month = String(monthIndex + 1).padStart(2, '0')
      return `${year}-${month}-01`
    }
  }

  return monthYearString
}

// Функция для преобразования человекочитаемого значения обратно в техническое
const reverseTransformValue = (prop, value) => {
  if (prop === 'department') return reverseDepartmentMap[value] || value
  if (prop === 'verification_state') return reverseVerificationStateMap[value] || value
  if (prop === 'verification_type') return reverseVerificationTypeMap[value] || value
  if (prop === 'equipment_type') return reverseEquipmentTypeMap[value] || value

  // Обработка дат
  if (prop === 'verification_date' || prop === 'verification_due' || prop === 'payment_date') {
    return parseDateFromDisplay(value)
  }
  if (prop === 'verification_plan') {
    return parseMonthYearFromDisplay(value)
  }

  return value
}

// Трансформированные данные для RevoGrid (с человекочитаемыми значениями)
const transformedSource = computed(() => {
  return filteredData.value.map(item => ({
    ...item,
    department: departmentMap[item.department] || item.department,
    verification_state: verificationStateMap[item.verification_state] || item.verification_state,
    verification_type: verificationTypeMap[item.verification_type] || item.verification_type,
    equipment_type: equipmentTypeMap[item.equipment_type] || item.equipment_type,
    status_display: statusMap[item.status] || item.status,
    // Форматирование дат
    verification_date: formatDate(item.verification_date),
    verification_due: formatDate(item.verification_due),
    verification_plan: formatMonthYear(item.verification_plan),
    payment_date: formatDate(item.payment_date)
  }))
})

// Динамические колонки на основе видимых полей
const dynamicColumns = computed(() => {
  return visibleColumns.value.map(fieldKey => {
    const fieldDef = fieldDefinitions[fieldKey]

    // Определяем размер колонки в зависимости от поля
    let columnSize = 150 // дефолтный размер
    if (fieldKey === 'equipment_name') {
      columnSize = 300 // увеличенная ширина для наименования
    } else if (fieldKey === 'equipment_model') {
      columnSize = 220 // увеличенная ширина для модели
    } else if (fieldKey === 'equipment_type') {
      columnSize = 180 // "Тип оборудования"
    } else if (fieldKey === 'equipment_specs') {
      columnSize = 180 // "Характеристики}"
    } else if (fieldKey === 'verification_interval') {
      columnSize = 120 // уменьшенный размер для интервала
    } else if (fieldKey === 'verification_plan') {
      columnSize = 130 // ширина по содержимому
    } else if (fieldKey === 'verification_date') {
      columnSize = 180 // "Дата верификации"
    } else if (fieldKey === 'verification_due') {
      columnSize = 140 // "Действует до"
    } else if (fieldKey === 'verification_type') {
      columnSize = 170 // "Тип верификации"
    } else if (fieldKey === 'registry_number') {
      columnSize = 160 // "Номер в реестре"
    } else if (fieldKey === 'verifier_org') {
      columnSize = 220 // "Организация-поверитель"
    } else if (fieldKey === 'budget_item') {
      columnSize = 160 // "Статья бюджета"
    } else if (fieldKey === 'code_rate') {
      columnSize = 140 // "Тариф"
    } else if (fieldKey === 'cost_rate') {
      columnSize = 270 // "Стоимость по тарифу (без НДС)"
    } else if (fieldKey === 'total_cost') {
      columnSize = 270 // "Итоговая стоимость (без НДС)"
    } else if (fieldKey === 'coefficient') {
      columnSize = 190 // "Коэффициент"
    } else if (fieldKey === 'paid_amount') {
      columnSize = 140 // "Факт оплаты"
    } else if (fieldKey === 'status') {
      columnSize = 130 // ширина по содержимому (например: "На верификации")
    } else if (fieldKey === 'department') {
      columnSize = 170 // "Подразделение"
    } else if (fieldKey === 'responsible_person') {
      columnSize = 170 // "Ответственный"
    }

    // Базовая конфигурация колонки
    const columnConfig = {
      prop: fieldKey,
      name: fieldDef?.label || fieldKey,
      size: columnSize,
      sortable: true, // Включаем сортировку для всех колонок
      filter: isAdmin.value ? 'string' : false, // Фильтрация только для администратора
      // Убираем readonly для verification_due, несмотря на то что это computed поле
      readonly: (fieldKey === 'verification_due') ? false : (fieldDef?.computed || false)
    }

    // Добавляем cellTemplate для форматирования

    // Статусы с цветовым кодированием
    if (fieldKey === 'status') {
      // Изменяем prop на status_display для отображения
      columnConfig.prop = 'status_display'
      columnConfig.cellTemplate = (createElement, props) => {
        // Карта цветов для статусов (используем оригинальное значение status)
        const statusColors = {
          'status_fit': '#52c41a',           // зеленый
          'status_expired': '#f5222d',       // красный
          'status_expiring': '#fa8c16',      // оранжевый
          'status_storage': '#1890ff',       // синий
          'status_verification': '#722ed1',  // фиолетовый
          'status_repair': '#fadb14'         // желтый
        }

        const displayValue = props.model.status_display || ''
        const originalStatus = props.model.status || ''
        const color = statusColors[originalStatus] || '#000'

        return createElement('span', {
          textContent: displayValue,
          style: {
            padding: '0 4px',
            color: color,
            fontWeight: '600'
          }
        })
      }
    }

    // Финансовые поля с форматированием (разделение тысяч и 2 знака после запятой)
    if (fieldKey === 'cost_rate' || fieldKey === 'total_cost' || fieldKey === 'paid_amount') {
      columnConfig.cellTemplate = (createElement, props) => {
        const value = props.model[fieldKey]

        // Форматирование числа: разделение тысяч пробелом, 2 знака после запятой
        let formattedValue = ''
        if (value !== null && value !== undefined && value !== '') {
          const num = parseFloat(value)
          if (!isNaN(num)) {
            formattedValue = num.toLocaleString('ru-RU', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })
          } else {
            formattedValue = value
          }
        }

        return createElement('span', {
          textContent: formattedValue,
          style: {
            padding: '0 4px',
            textAlign: 'right',
            display: 'block',
            fontVariantNumeric: 'tabular-nums'
          }
        })
      }
    }

    return columnConfig
  })
})

// Добавляем колонку действий в конец
const columnsWithActions = computed(() => {
  // Добавляем зависимость от триггера для обновления чекбоксов
  const _ = checkboxUpdateTrigger.value

  const columns = []

  // Добавляем колонку с чекбоксами В НАЧАЛО
  columns.push({
    prop: 'checkbox',
    name: '',
    size: 50,
    pin: 'colPinStart',
    cellTemplate: (createElement, props) => {
      const equipmentId = props.model.equipment_id
      const isChecked = selectedIds.value.has(equipmentId)

      return createElement('input', {
        type: 'checkbox',
        checked: isChecked,
        style: {
          cursor: 'pointer',
          width: '16px',
          height: '16px',
          margin: '0 auto',
          display: 'block'
        },
        onChange: (event) => {
          if (event.target.checked) {
            selectedIds.value.add(equipmentId)
          } else {
            selectedIds.value.delete(equipmentId)
          }
          // Принудительно обновляем компонент
          selectedIds.value = new Set(selectedIds.value)
        }
      })
    }
  })

  // Добавляем остальные колонки
  columns.push(...dynamicColumns.value)

  // Колонка действий для администратора
  if (isAdmin.value) {
    columns.push({
      prop: 'actions',
      name: 'Действия',
      size: 215,
      cellTemplate: (createElement, props) => {
        const equipmentId = props.model.equipment_id
        return createElement('div', {
          style: { display: 'flex', gap: '8px', padding: '4px 8px 4px 4px' }
        }, [
          createElement('button', {
            textContent: 'Редактировать',
            style: {
              padding: '4px 12px',
              cursor: 'pointer',
              border: '1px solid #8c8c8c',
              borderRadius: '3px',
              background: '#8c8c8c',
              color: 'white',
              fontSize: '12px'
            },
            onClick: () => editEquipment(equipmentId)
          }),
          createElement('button', {
            textContent: 'Удалить',
            style: {
              padding: '4px 12px',
              cursor: 'pointer',
              border: '1px solid #8c8c8c',
              borderRadius: '3px',
              background: '#8c8c8c',
              color: 'white',
              fontSize: '12px'
            },
            onClick: () => deleteEquipment(equipmentId)
          })
        ])
      }
    })
  }
  // Колонка действий для лаборанта (только просмотр)
  else if (isLaborant.value) {
    columns.push({
      prop: 'actions',
      name: 'Действия',
      size: 130,
      cellTemplate: (createElement, props) => {
        const equipmentId = props.model.equipment_id
        return createElement('div', {
          style: { display: 'flex', gap: '8px', padding: '4px 8px 4px 4px', justifyContent: 'center' }
        }, [
          createElement('button', {
            textContent: 'Просмотр',
            style: {
              padding: '4px 12px',
              cursor: 'pointer',
              border: '1px solid #8c8c8c',
              borderRadius: '3px',
              background: '#8c8c8c',
              color: 'white',
              fontSize: '12px'
            },
            onClick: () => viewEquipment(equipmentId)
          })
        ])
      }
    })
  }

  return columns
})

// Обработчик двойного клика по ячейке
const handleCellDblClick = (event) => {
  console.log('Cell double click event:', event)

  // Попробуем разные способы получить данные строки
  if (event.detail) {
    const rowIndex = event.detail.rowIndex ?? event.detail.y
    console.log('Row index:', rowIndex, 'FilteredData:', filteredData.value)

    if (rowIndex !== undefined && filteredData.value[rowIndex]) {
      const row = filteredData.value[rowIndex]
      console.log('Row data:', row)
      const equipmentId = row.equipment_id

      if (equipmentId) {
        console.log('Opening edit for equipment:', equipmentId)
        editEquipment(equipmentId)
      }
    }
  }
}

// Функция для сохранения одной ячейки на сервер
// val должно быть уже преобразовано в техническое значение вызывающей функцией
const saveCellToServer = async (equipmentId, prop, val) => {
  try {
    console.log(`[saveCellToServer] Saving: equipmentId=${equipmentId}, prop=${prop}, val=${val}, type=${typeof val}`)

    // Получаем полные данные для обновления
    const fullDataResponse = await axios.get(`http://localhost:8000/main-table/${equipmentId}/full`)
    const fullData = fullDataResponse.data

    console.log(`[saveCellToServer] Full data received:`, fullData)

    // Обновляем измененное поле (val уже должно быть в техническом формате)
    fullData[prop] = val

    console.log(`[saveCellToServer] Sending PUT request with:`, fullData)

    // Отправляем обновление на сервер
    await axios.put(`http://localhost:8000/main-table/${equipmentId}`, fullData)

    console.log(`[saveCellToServer] Successfully saved ${prop} = ${val}`)
    return true
  } catch (error) {
    console.error('[saveCellToServer] Error:', error)
    console.error('[saveCellToServer] Error response:', error.response?.data)
    throw error
  }
}

// Обработчик после редактирования ячейки
const handleAfterEdit = async (event) => {
  console.log('After edit event:', event)

  if (event.detail) {
    const { rowIndex, prop, val } = event.detail
    const row = filteredData.value[rowIndex]

    if (row && row.equipment_id) {
      console.log(`Cell edited: row ${rowIndex}, field ${prop}, new value: ${val}`)

      // Преобразуем человекочитаемое значение обратно в техническое
      const technicalValue = reverseTransformValue(prop, val)

      // Сохраняем старое значение В ИСТОРИЮ (до изменения)
      const sourceRow = source.value.find(item => item.equipment_id === row.equipment_id)
      const oldValue = sourceRow ? sourceRow[prop] : null

      // Добавляем в историю изменений ТОЛЬКО если это НЕ undo операция
      if (!isUndoing.value) {
        editHistory.value.push({
          equipmentId: row.equipment_id,
          field: prop,
          oldValue: oldValue,
          newValue: technicalValue,
          timestamp: Date.now()
        })

        // Ограничиваем размер истории (FIFO - удаляем самые старые)
        if (editHistory.value.length > MAX_HISTORY_SIZE) {
          editHistory.value.shift()
        }

        console.log(`[History] Added to history. Total: ${editHistory.value.length}`, editHistory.value[editHistory.value.length - 1])
      } else {
        console.log(`[History] Skipped adding to history (undo in progress)`)
      }

      // Обновляем локальные данные (оригинальные данные в source)
      if (sourceRow) {
        sourceRow[prop] = technicalValue
      }

      // Автосохранение на сервер (передаем уже преобразованное техническое значение)
      try {
        await saveCellToServer(row.equipment_id, prop, technicalValue)
      } catch (error) {
        // При ошибке - удаляем из истории и откатываем (только если не undo)
        if (!isUndoing.value) {
          editHistory.value.pop()
          console.log(`[History] Removed from history due to error`)
        }
        alert(`Ошибка при сохранении: ${error.response?.data?.detail || error.message}`)
        // Откатываем изменения при ошибке
        await loadData()
      }
    }
  }
}

// Функция отмены последнего изменения (Ctrl+Z)
const undoLastEdit = async () => {
  if (editHistory.value.length === 0) {
    console.log('[Undo] No edits to undo')
    window.$message?.warning('Нет изменений для отмены')
    return
  }

  const lastEdit = editHistory.value.pop()
  console.log('[Undo] Undoing last edit:', lastEdit)
  console.log('[Undo] History size after pop:', editHistory.value.length)

  // Устанавливаем флаг undo для предотвращения добавления в историю
  isUndoing.value = true

  try {
    // Откатываем на сервере к старому значению
    await saveCellToServer(lastEdit.equipmentId, lastEdit.field, lastEdit.oldValue)

    // Обновляем локальные данные без полного loadData()
    const sourceRow = source.value.find(item => item.equipment_id === lastEdit.equipmentId)
    if (sourceRow) {
      sourceRow[lastEdit.field] = lastEdit.oldValue
    }

    // Показываем уведомление об успешной отмене
    const fieldLabel = fieldDefinitions.value?.find(f => f.key === lastEdit.field)?.label || lastEdit.field
    window.$message?.success(`Отменено изменение поля "${fieldLabel}"`)

    console.log('[Undo] Successfully undone. Remaining history:', editHistory.value.length)
  } catch (error) {
    // При ошибке возвращаем изменение обратно в историю
    editHistory.value.push(lastEdit)
    console.error('[Undo] Error while undoing:', error)
    console.log('[Undo] History restored. Size:', editHistory.value.length)
    window.$message?.error('Ошибка при отмене изменения')
  } finally {
    // Сбрасываем флаг undo
    isUndoing.value = false
  }
}

// Обработчик ПЕРЕД редактированием диапазона (протаскивание, копирование)
// RevoGrid не вызывает afterrangeedit, поэтому используем beforerangeedit
const handleBeforeRangeEdit = async (event) => {
  console.log('Before range edit event:', event)
  console.log('Event detail:', event.detail)

  if (event.detail) {
    const { data, models } = event.detail

    console.log('Range data:', data)
    console.log('Range models:', models)

    // Используем setTimeout чтобы дать RevoGrid время обновить данные
    setTimeout(async () => {
      if (data && models) {
        // Проходим по всем измененным строкам
        for (const rowKey in data) {
          const rowChanges = data[rowKey] // изменения в строке
          const rowModel = models[rowKey] // полный объект строки

          if (rowModel && rowModel.equipment_id) {
            console.log(`Row ${rowKey} changes:`, rowChanges)

            // Обновляем каждое измененное поле
            for (const prop in rowChanges) {
              const newValue = rowChanges[prop]
              console.log(`Range edit: field ${prop}, new value: ${newValue}`)

              // Преобразуем человекочитаемое значение обратно в техническое
              const technicalValue = reverseTransformValue(prop, newValue)

              // Сохраняем на сервер (передаем техническое значение)
              try {
                await saveCellToServer(rowModel.equipment_id, prop, technicalValue)
              } catch (error) {
                console.error(`Failed to save row ${rowKey}, field ${prop}:`, error)
              }
            }
          }
        }

        console.log('All changes saved, reloading data...')
        // Перезагружаем все данные после массового обновления
        await loadData()
      }
    }, 100) // Небольшая задержка для завершения редактирования в RevoGrid
  }
}

// Удаление оборудования
const deleteEquipment = async (equipmentId) => {
  if (!confirm('Вы уверены, что хотите удалить это оборудование?')) {
    return
  }

  try {
    await axios.delete(`http://localhost:8000/main-table/${equipmentId}`)
    await loadData() // Перезагрузка данных после удаления
  } catch (error) {
    console.error('Ошибка при удалении:', error)
    alert('Ошибка при удалении оборудования')
  }
}

// Редактирование оборудования
const editEquipment = (equipmentId) => {
  emit('edit-equipment', equipmentId)
}

// Просмотр оборудования (для лаборанта)
const viewEquipment = (equipmentId) => {
  emit('view-equipment', equipmentId)
}

// Вспомогательная функция для открытия или скачивания файла
const handleFileDownload = async (blob, filename) => {
  // Проверяем, запущено ли приложение в Electron
  if (window.electron && window.electron.openFile) {
    // В Electron режиме - открываем файл автоматически
    try {
      const arrayBuffer = await blob.arrayBuffer()
      const result = await window.electron.openFile(arrayBuffer, filename)

      if (!result.success) {
        console.error('Ошибка при открытии файла:', result.error)
        alert('Ошибка при открытии файла: ' + result.error)
      }
    } catch (error) {
      console.error('Ошибка при открытии файла в Electron:', error)
      alert('Ошибка при открытии файла: ' + error.message)
    }
  } else {
    // В браузере - обычное скачивание
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }
}

// Печать этикеток для выбранного оборудования
const printLabels = async () => {
  if (selectedIds.value.size === 0) {
    return
  }

  try {
    loading.value = true
    const equipmentIds = Array.from(selectedIds.value)

    const response = await axios.post(
      'http://localhost:8000/documents/labels',
      { equipment_ids: equipmentIds },
      {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    // Открываем файл в Word (Electron) или скачиваем (браузер)
    const filename = `Этикетки_${equipmentIds.length}_шт.docx`
    await handleFileDownload(new Blob([response.data]), filename)

    // Очищаем выбранные строки после успешной генерации
    selectedIds.value.clear()
    selectedIds.value = new Set(selectedIds.value)

    const message = window.electron
      ? `Этикетки для ${equipmentIds.length} ед. оборудования успешно сгенерированы и открыты в Word`
      : `Этикетки для ${equipmentIds.length} ед. оборудования успешно сгенерированы`
    alert(message)
  } catch (error) {
    console.error('Ошибка при генерации этикеток:', error)
    alert('Ошибка при генерации этикеток: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const printConservationAct = async () => {
  if (selectedIds.value.size === 0) {
    return
  }

  try {
    loading.value = true
    const equipmentIds = Array.from(selectedIds.value)

    const response = await axios.post(
      'http://localhost:8000/documents/conservation-act',
      { equipment_ids: equipmentIds },
      {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    // Открываем файл в Word (Electron) или скачиваем (браузер)
    const filename = `Акт_консервации_${equipmentIds.length}_шт.docx`
    await handleFileDownload(new Blob([response.data]), filename)

    // Очищаем выбранные строки после успешной генерации
    selectedIds.value.clear()
    selectedIds.value = new Set(selectedIds.value)

    const message = window.electron
      ? `Акт консервации для ${equipmentIds.length} ед. оборудования успешно сгенерирован и открыт в Word`
      : `Акт консервации для ${equipmentIds.length} ед. оборудования успешно сгенерирован`
    alert(message)
  } catch (error) {
    console.error('Ошибка при генерации акта консервации:', error)
    alert('Ошибка при генерации акта консервации: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Генерация заявки на поверку
const printBidPoverka = async () => {
  if (selectedIds.value.size === 0) {
    return
  }

  try {
    loading.value = true
    const equipmentIds = Array.from(selectedIds.value)

    const response = await axios.post(
      'http://localhost:8000/documents/bid-poverka',
      { equipment_ids: equipmentIds },
      {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    const filename = `Заявка_на_поверку_${equipmentIds.length}_шт.docx`
    await handleFileDownload(new Blob([response.data]), filename)

    selectedIds.value.clear()
    selectedIds.value = new Set(selectedIds.value)

    const message = window.electron
      ? `Заявка на поверку для ${equipmentIds.length} ед. оборудования успешно сгенерирована и открыта в Word`
      : `Заявка на поверку для ${equipmentIds.length} ед. оборудования успешно сгенерирована`
    alert(message)
  } catch (error) {
    console.error('Ошибка при генерации заявки на поверку:', error)
    alert('Ошибка при генерации заявки на поверку: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Генерация заявки на калибровку (только для администратора)
const printBidCalibrovka = async () => {
  if (selectedIds.value.size === 0) {
    return
  }

  try {
    loading.value = true
    const equipmentIds = Array.from(selectedIds.value)

    const response = await axios.post(
      'http://localhost:8000/documents/bid-calibrovka',
      { equipment_ids: equipmentIds },
      {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    const filename = `Заявка_на_калибровку_${equipmentIds.length}_шт.docx`
    await handleFileDownload(new Blob([response.data]), filename)

    selectedIds.value.clear()
    selectedIds.value = new Set(selectedIds.value)

    const message = window.electron
      ? `Заявка на калибровку для ${equipmentIds.length} ед. оборудования успешно сгенерирована и открыта в Word`
      : `Заявка на калибровку для ${equipmentIds.length} ед. оборудования успешно сгенерирована`
    alert(message)
  } catch (error) {
    console.error('Ошибка при генерации заявки на калибровку:', error)
    alert('Ошибка при генерации заявки на калибровку: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Генерация предписания (только для администратора)
const printRequest = async () => {
  if (selectedIds.value.size === 0) {
    return
  }

  try {
    loading.value = true
    const equipmentIds = Array.from(selectedIds.value)

    const response = await axios.post(
      'http://localhost:8000/documents/request',
      { equipment_ids: equipmentIds },
      {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    const filename = `Предписание_${equipmentIds.length}_шт.docx`
    await handleFileDownload(new Blob([response.data]), filename)

    selectedIds.value.clear()
    selectedIds.value = new Set(selectedIds.value)

    const message = window.electron
      ? `Предписание для ${equipmentIds.length} ед. оборудования успешно сгенерировано и открыто в Word`
      : `Предписание для ${equipmentIds.length} ед. оборудования успешно сгенерировано`
    alert(message)
  } catch (error) {
    console.error('Ошибка при генерации предписания:', error)
    alert('Ошибка при генерации предписания: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Сброс выделенных строк
const clearSelection = () => {
  selectedIds.value.clear()
  selectedIds.value = new Set(selectedIds.value)
  // Инкрементируем триггер для обновления чекбоксов в таблице
  checkboxUpdateTrigger.value++
}

const downloadCommissioningTemplate = async () => {
  try {
    loading.value = true

    const response = await axios.get(
      'http://localhost:8000/documents/commissioning-template',
      {
        responseType: 'blob',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      }
    )

    // Открываем файл в Word (Electron) или скачиваем (браузер)
    const filename = 'Акт_ввода_в_эксплуатацию.docx'
    await handleFileDownload(new Blob([response.data]), filename)

    if (window.electron) {
      alert('Шаблон акта ввода в эксплуатацию успешно открыт в Word')
    }
  } catch (error) {
    console.error('Ошибка при скачивании шаблона:', error)
    alert('Ошибка при скачивании шаблона: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

// Обработчик клика по логотипу - прокрутка к началу страницы
const handleLogoClick = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  loadData()
  loadArchiveData() // Загружаем архивные данные для метрики "Списано"
  loadSavedSettings()

  // Подключаем обработчик Ctrl+Z для Electron режима
  if (window.electron && window.electron.onUndo) {
    window.electron.onUndo(() => {
      console.log('[Electron] Undo action triggered via Ctrl+Z')
      undoLastEdit()
    })
  }

  // Подключаем обработчик Ctrl+Z для браузерного режима
  const handleKeyDown = (event) => {
    // Ctrl+Z (Windows/Linux) или Cmd+Z (Mac)
    if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
      // Проверяем что не в input/textarea (они должны иметь свой undo)
      const target = event.target
      if (target.tagName !== 'INPUT' && target.tagName !== 'TEXTAREA' && !target.isContentEditable) {
        event.preventDefault()
        console.log('[Browser] Undo action triggered via Ctrl+Z')
        undoLastEdit()
      }
    }
  }

  document.addEventListener('keydown', handleKeyDown)

  // Сохраняем ссылку на обработчик для очистки в onUnmounted
  window.__undoKeyHandler = handleKeyDown
})

onUnmounted(() => {
  // Отключаем обработчик Electron
  if (window.electron && window.electron.removeUndoListener) {
    window.electron.removeUndoListener()
  }

  // Отключаем обработчик браузера
  if (window.__undoKeyHandler) {
    document.removeEventListener('keydown', window.__undoKeyHandler)
    delete window.__undoKeyHandler
  }
})

// Экспорт функции для перезагрузки данных (для использования родительским компонентом)
defineExpose({
  loadData
})
</script>

<template>
  <div class="main-table-container">
    <!-- Панель действий и поиска -->
    <div class="top-panel">
      <!-- Первая строка: логотип, дашборд и профиль -->
      <div class="header-row">
        <!-- Левая часть: логотип -->
        <div class="header-left">
          <AppLogo @click="handleLogoClick" />
        </div>

        <!-- Центральная часть: Дашборд с метриками -->
        <div class="header-center">
          <MetricsDashboard :metrics="metrics" />
        </div>

        <!-- Правая часть: UserProfile -->
        <div class="header-right">
          <UserProfile @show-login="$emit('show-login')" />
        </div>
      </div>

      <!-- Вторая строка: Кнопки, поиск по центру -->
      <div class="header-row" style="margin-top: 12px;">
        <!-- Левая часть: Фильтры, Документы и AdminPanel -->
        <div class="header-left">
          <n-space :size="12" align="center">
            <n-button type="primary" @click="showFilterDrawer = true">
              Фильтры
            </n-button>
            <DocumentsPanel />
            <n-button v-if="isLaborant" type="primary" @click="statisticsRef?.openModal()">
              Статистика
            </n-button>
            <AdminPanel
              v-if="isAdmin"
              @add-equipment="$emit('add-equipment')"
              @show-archive="$emit('show-archive')"
              @show-backup="backupPanelRef?.openModal()"
              @show-monitor="systemMonitorRef?.openModal()"
              @show-contracts="showContractsNotebook = true"
              @show-analytics="showAnalyticsDashboard = true"
            />
          </n-space>
        </div>

        <!-- Центральная часть: Поиск -->
        <div class="header-center">
          <SearchBar
            v-model="searchQuery"
            :total-count="filterStats.total"
            :filtered-count="filterStats.filtered"
          />
        </div>

        <!-- Правая часть: Этикетки и акты -->
        <div class="header-right">
          <DocumentActionsDropdown
            :selected-count="selectedIds.size"
            :is-admin="isAdmin"
            @print-labels="printLabels"
            @print-conservation-act="printConservationAct"
            @print-bid-poverka="printBidPoverka"
            @print-bid-calibrovka="printBidCalibrovka"
            @print-request="printRequest"
            @clear-selection="clearSelection"
            @download-commissioning-template="downloadCommissioningTemplate"
          />
        </div>
      </div>
    </div>

    <!-- Таблица с данными -->
    <div class="table-wrapper">
      <v-grid
        ref="grid"
        :key="checkboxUpdateTrigger"
        :source="transformedSource"
        :columns="columnsWithActions"
        theme="material"
        :resize="true"
        :range="true"
        :filter="true"
        :readonly="isLaborant"
        :row-headers="true"
        :can-focus="true"
        @afteredit="handleAfterEdit"
        @beforerangeedit="handleBeforeRangeEdit"
        @celldblclick="handleCellDblClick"
      />
    </div>

    <!-- Drawer с фильтрами -->
    <n-drawer
      v-model:show="showFilterDrawer"
      :width="400"
      placement="left"
    >
      <n-drawer-content title="Фильтры и колонки" closable>
        <FilterPanel
          :field-definitions="fieldDefinitions"
          :field-groups="fieldGroups"
          :visible-columns="visibleColumns"
          :active-filters="activeFilters"
          :is-laborant="isLaborant"
          @update:visible-columns="visibleColumns = $event"
          @update:active-filters="activeFilters = $event"
          @reset="resetFilters"
          @apply-quick-filter="applyQuickFilter"
        />
      </n-drawer-content>
    </n-drawer>

    <!-- Модальные окна для BackupPanel, SystemMonitor, ContractsNotebook, AnalyticsDashboard и LaborantStatistics -->
    <BackupPanel ref="backupPanelRef" />
    <SystemMonitor ref="systemMonitorRef" />
    <LaborantStatistics ref="statisticsRef" :equipment-data="source" />
    <ContractsNotebook v-model:show="showContractsNotebook" />
    <AnalyticsDashboard v-model:show="showAnalyticsDashboard" :equipment-data="source" />
  </div>
</template>

<style scoped>
.main-table-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  gap: 16px;
}

.top-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Трёхколоночная сетка для центрирования */
.header-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  width: 100%;
  gap: 16px;
}

.header-left {
  justify-self: start;
}

.header-center {
  justify-self: center;
}

.header-right {
  justify-self: end;
}

.hint-text {
  color: #888;
  font-size: 13px;
  font-style: italic;
}

.table-wrapper {
  flex: 1;
  min-height: 0;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
  background-color: #ffffff;
}

/* RevoGrid стили */
.table-wrapper :deep(revo-grid) {
  height: 100%;
  width: 100%;
  font-family: 'PT Astra Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #ffffff;
}

/* Показывать иконки сортировки и фильтрации при наведении */
.table-wrapper :deep(.header-sortable),
.table-wrapper :deep(.header-filter) {
  opacity: 0.3;
  transition: opacity 0.2s;
}

.table-wrapper :deep(revogr-header-cell:hover .header-sortable),
.table-wrapper :deep(revogr-header-cell:hover .header-filter) {
  opacity: 1;
}

/* Всегда показывать активные иконки */
.table-wrapper :deep(.header-sortable.active),
.table-wrapper :deep(.header-filter.active) {
  opacity: 1;
}

/* Выравнивание чекбоксов по центру ячейки */
.table-wrapper :deep(revogr-data) input[type="checkbox"],
.table-wrapper :deep(revogr-header) input[type="checkbox"] {
  vertical-align: middle;
  margin: 0;
}

.table-wrapper :deep(.rgRow) {
  align-items: center;
}

.table-wrapper :deep(.rgCell) {
  display: flex;
  align-items: center;
}
</style>
