<script setup>
import { ref, onMounted, h, computed, watch } from 'vue'
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
import { useEquipmentFilters } from '../composables/useEquipmentFilters'
import { useEquipmentMetrics } from '../composables/useEquipmentMetrics'
import { useAuth } from '../composables/useAuth'

const emit = defineEmits(['add-equipment', 'edit-equipment', 'show-archive', 'show-login'])

// Аутентификация
const { currentUser, isAuthenticated, isAdmin, isLaborant } = useAuth()

// Данные таблицы
const source = ref([])
const loading = ref(false)

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
} = useEquipmentFilters(source)

// Инициализация метрик (на основе данных из БД, уже отфильтрованных по department для лаборанта)
const { metrics } = useEquipmentMetrics(source)

// Состояние drawer для фильтров
const showFilterDrawer = ref(false)

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

// Динамические колонки на основе видимых полей
const dynamicColumns = computed(() => {
  return visibleColumns.value.map(fieldKey => {
    const fieldDef = fieldDefinitions[fieldKey]

    // Базовая конфигурация колонки
    const columnConfig = {
      prop: fieldKey,
      name: fieldDef?.label || fieldKey,
      size: 150,
      readonly: fieldDef?.computed || false
    }

    // Добавляем cellTemplate для форматирования
    if (fieldKey === 'verification_date' || fieldKey === 'verification_due' || fieldKey === 'payment_date') {
      columnConfig.cellTemplate = (createElement, props) => {
        return createElement('span', {
          textContent: formatDate(props.model[props.prop]),
          style: { padding: '0 4px' }
        })
      }
    } else if (fieldKey === 'verification_plan') {
      columnConfig.cellTemplate = (createElement, props) => {
        return createElement('span', {
          textContent: formatMonthYear(props.model[props.prop]),
          style: { padding: '0 4px' }
        })
      }
    } else if (fieldKey === 'verification_type') {
      columnConfig.readonly = true
      columnConfig.cellTemplate = (createElement, props) => {
        const verificationTypeMap = {
          'calibration': 'Калибровка',
          'verification': 'Поверка',
          'certification': 'Аттестация'
        }
        const currentValue = props.model[props.prop] || ''
        const displayValue = verificationTypeMap[currentValue] || currentValue

        return createElement('span', {
          textContent: displayValue,
          style: { padding: '0 4px' }
        })
      }
    } else if (fieldKey === 'status') {
      columnConfig.readonly = true
      columnConfig.cellTemplate = (createElement, props) => {
        const statusMap = {
          'status_fit': 'Годен',
          'status_expired': 'Просрочен',
          'status_expiring': 'Истекает',
          'status_storage': 'На хранении',
          'status_verification': 'На верификации',
          'status_repair': 'На ремонте'
        }
        const currentValue = props.model[props.prop] || ''
        const displayValue = statusMap[currentValue] || currentValue

        return createElement('span', {
          textContent: displayValue,
          style: { padding: '0 4px' }
        })
      }
    }

    return columnConfig
  })
})

// Добавляем колонку действий в конец (только для администратора)
const columnsWithActions = computed(() => {
  const columns = [...dynamicColumns.value]

  // Колонка действий только для администратора
  if (isAdmin.value) {
    columns.push({
      prop: 'actions',
      name: 'Действия',
      size: 200,
      readonly: true,
      cellTemplate: (createElement, props) => {
        const equipmentId = props.model.equipment_id
        return createElement('div', {
          style: { display: 'flex', gap: '8px', padding: '4px' }
        }, [
          createElement('button', {
            textContent: 'Редактировать',
            style: {
              padding: '4px 12px',
              cursor: 'pointer',
              border: '1px solid #18a058',
              borderRadius: '3px',
              background: '#18a058',
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
              border: '1px solid #d03050',
              borderRadius: '3px',
              background: '#d03050',
              color: 'white',
              fontSize: '12px'
            },
            onClick: () => deleteEquipment(equipmentId)
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
    console.log('Row index:', rowIndex, 'Source:', source.value)

    if (rowIndex !== undefined && source.value[rowIndex]) {
      const row = source.value[rowIndex]
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
const saveCellToServer = async (equipmentId, prop, val) => {
  try {
    // Получаем полные данные для обновления
    const fullDataResponse = await axios.get(`http://localhost:8000/main-table/${equipmentId}/full`)
    const fullData = fullDataResponse.data

    // Обновляем измененное поле
    fullData[prop] = val

    // Отправляем обновление на сервер
    await axios.put(`http://localhost:8000/main-table/${equipmentId}`, fullData)

    console.log(`Successfully saved ${prop} = ${val} for equipment ${equipmentId}`)
    return true
  } catch (error) {
    console.error('Ошибка при сохранении изменений:', error)
    throw error
  }
}

// Обработчик после редактирования ячейки
const handleAfterEdit = async (event) => {
  console.log('After edit event:', event)

  if (event.detail) {
    const { rowIndex, prop, val } = event.detail
    const row = source.value[rowIndex]

    if (row && row.equipment_id) {
      console.log(`Cell edited: row ${rowIndex}, field ${prop}, new value: ${val}`)

      // Обновляем локальные данные
      row[prop] = val

      // Автосохранение на сервер
      try {
        await saveCellToServer(row.equipment_id, prop, val)
      } catch (error) {
        alert(`Ошибка при сохранении: ${error.response?.data?.detail || error.message}`)
        // Откатываем изменения при ошибке
        await loadData()
      }
    }
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

              // Сохраняем на сервер
              try {
                await saveCellToServer(rowModel.equipment_id, prop, newValue)
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

onMounted(() => {
  loadData()
  loadSavedSettings()
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
      <!-- Первая строка: кнопки, метрики, поиск и профиль -->
      <n-space :size="16" align="center" justify="space-between" style="width: 100%">
        <n-space :size="16" align="center">
          <!-- Кнопки управления -->
          <n-space v-if="isAdmin">
            <n-button type="primary" @click="$emit('add-equipment')">
              Добавить оборудование
            </n-button>
            <n-button @click="loadData">
              Обновить
            </n-button>
            <n-button type="warning" @click="$emit('show-archive')">
              Архив
            </n-button>
            <BackupPanel />
            <SystemMonitor />
            <n-button secondary @click="showFilterDrawer = true">
              Фильтры и колонки
            </n-button>
          </n-space>

          <n-space v-else-if="isAuthenticated">
            <n-button @click="loadData">
              Обновить
            </n-button>
            <n-button secondary @click="showFilterDrawer = true">
              Фильтры и колонки
            </n-button>
          </n-space>

          <!-- Дашборд с метриками -->
          <MetricsDashboard :metrics="metrics" />

          <!-- Поиск -->
          <SearchBar
            v-model="searchQuery"
            :total-count="filterStats.total"
            :filtered-count="filterStats.filtered"
          />
        </n-space>

        <!-- DocumentsPanel и UserProfile компоненты справа -->
        <n-space :size="12" align="center">
          <DocumentsPanel />
          <UserProfile @show-login="$emit('show-login')" />
        </n-space>
      </n-space>

      <div class="hint-text" v-if="isAdmin">
        Двойной клик по строке для редактирования. Можно копировать данные (Ctrl+C / Ctrl+V)
      </div>
      <div class="hint-text" v-else-if="isLaborant">
        Отображается оборудование подразделения: {{ currentUser?.department }}
      </div>
    </div>

    <!-- Таблица с данными -->
    <div class="table-wrapper">
      <v-grid
        ref="grid"
        :source="filteredData"
        :columns="columnsWithActions"
        theme="compact"
        :resize="true"
        :range="true"
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
          @update:visible-columns="visibleColumns = $event"
          @update:active-filters="activeFilters = $event"
          @reset="resetFilters"
          @apply-quick-filter="applyQuickFilter"
        />
      </n-drawer-content>
    </n-drawer>
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

.hint-text {
  color: #888;
  font-size: 13px;
  font-style: italic;
}

.table-wrapper {
  flex: 1;
  min-height: 0;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

/* RevoGrid стили */
.table-wrapper :deep(revo-grid) {
  height: 100%;
  width: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>
