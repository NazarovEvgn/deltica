<script setup>
import { ref, onMounted, computed } from 'vue'
import { NButton, NSpace, NEmpty, useMessage, useDialog } from 'naive-ui'
import { VGrid } from '@revolist/vue3-datagrid'
import axios from 'axios'
import AppLogo from './AppLogo.vue'
import EquipmentModal from './EquipmentModal.vue'
import SearchBar from './SearchBar.vue'
import { API_ENDPOINTS } from '../config/api.js'
import { useEquipmentFilters } from '../composables/useEquipmentFilters.js'

const emit = defineEmits(['back-to-main', 'restored'])
const message = useMessage()
const dialog = useDialog()

// Props для режима просмотра и фильтрации
const props = defineProps({
  readOnly: {
    type: Boolean,
    default: false
  },
  departmentFilter: {
    type: String,
    default: null
  }
})

// Данные архивной таблицы
const source = ref([])
const loading = ref(false)

// Поиск и фильтрация
const { searchQuery, filteredData, filterStats } = useEquipmentFilters(source)

// Состояние для модального окна просмотра
const showViewModal = ref(false)
const viewArchiveId = ref(null)

// Функция форматирования даты в dd.mm.yyyy
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

// Маппинг для подразделений
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
  'tsz': 'ЦСЗ'
}

// Определение колонок для RevoGrid (динамическое на основе props)
const columns = computed(() => {
  const baseColumns = [
    { prop: 'equipment_name', name: 'Наименование', size: 300, readonly: true, sortable: true, filter: 'string' },
    { prop: 'equipment_model', name: 'Модель', size: 220, readonly: true, sortable: true, filter: 'string' },
    { prop: 'factory_number', name: 'Зав. №', size: 150, readonly: true, sortable: true, filter: 'string' },
    { prop: 'inventory_number', name: 'Инв. №', size: 150, readonly: true, sortable: true, filter: 'string' },
    {
      prop: 'department',
      name: 'Подразделение',
      size: 120,
      readonly: true,
      sortable: true,
      filter: 'string',
      cellTemplate: (createElement, cellProps) => {
        const currentValue = cellProps.model[cellProps.prop] || ''
        return createElement('span', {
          textContent: departmentMap[currentValue] || currentValue,
          style: { padding: '0 4px' }
        })
      }
    },
    {
      prop: 'archived_at',
      name: 'Дата архивирования',
      size: 180,
      readonly: true,
      sortable: true,
      filter: 'string',
      cellTemplate: (createElement, cellProps) => {
        const dateStr = cellProps.model[cellProps.prop]
        if (!dateStr) return createElement('span', { textContent: '' })
        const date = new Date(dateStr)
        const formatted = `${formatDate(dateStr)} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
        return createElement('span', {
          textContent: formatted,
          style: { padding: '0 4px' }
        })
      }
    },
    {
      prop: 'archive_reason',
      name: 'Причина списания',
      size: 200,
      readonly: props.readOnly, // Динамически зависит от режима
      sortable: true,
      filter: 'string'
    }
  ]

  // Добавляем колонку действий только если не режим просмотра
  if (!props.readOnly) {
    baseColumns.push({
      prop: 'actions',
      name: 'Действия',
      size: 270,
      readonly: true,
      sortable: false,
      cellTemplate: (createElement, cellProps) => {
        const archivedId = cellProps.model.id
        return createElement('div', {
          style: { display: 'flex', gap: '8px', padding: '4px 8px 4px 4px' }
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
            onClick: () => viewArchive(archivedId)
          }),
          createElement('button', {
            textContent: 'Восстановить',
            style: {
              padding: '4px 12px',
              cursor: 'pointer',
              border: '1px solid #8c8c8c',
              borderRadius: '3px',
              background: '#8c8c8c',
              color: 'white',
              fontSize: '12px'
            },
            onClick: () => restoreEquipment(archivedId)
          }),
          createElement('button', {
            textContent: 'Удалить навсегда',
            style: {
              padding: '4px 12px',
              cursor: 'pointer',
              border: '1px solid #8c8c8c',
              borderRadius: '3px',
              background: '#8c8c8c',
              color: 'white',
              fontSize: '12px'
            },
            onClick: () => deleteForever(archivedId)
          })
        ])
      }
    })
  } else {
    // В режиме просмотра добавляем только кнопку просмотра
    baseColumns.push({
      prop: 'actions',
      name: 'Действия',
      size: 120,
      readonly: true,
      sortable: false,
      cellTemplate: (createElement, cellProps) => {
        const archivedId = cellProps.model.id
        return createElement('div', {
          style: { display: 'flex', gap: '8px', padding: '4px 8px 4px 4px' }
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
            onClick: () => viewArchive(archivedId)
          })
        ])
      }
    })
  }

  return baseColumns
})

// Загрузка данных архива с бэкенда
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get(API_ENDPOINTS.archive)
    let data = response.data

    // Фильтрация по подразделению если задан departmentFilter
    if (props.departmentFilter) {
      data = data.filter(item => item.department === props.departmentFilter)
    }

    source.value = data
  } catch (error) {
    console.error('Ошибка при загрузке архива:', error)
    message.error('Ошибка при загрузке архивных данных')
  } finally {
    loading.value = false
  }
}

// Просмотр архивного оборудования
const viewArchive = (archivedId) => {
  viewArchiveId.value = archivedId
  showViewModal.value = true
}

// Восстановление оборудования из архива
const restoreEquipment = async (archivedId) => {
  const archived = source.value.find(item => item.id === archivedId)
  if (!archived) return

  dialog.info({
    title: 'Подтверждение восстановления',
    content: `Вы уверены, что хотите восстановить оборудование "${archived.equipment_name}" из архива? Оно будет возвращено в основную таблицу.`,
    positiveText: 'Восстановить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.post(API_ENDPOINTS.archiveRestore(archivedId))
        message.success('Оборудование успешно восстановлено из архива')
        await loadData()
        emit('restored')
      } catch (error) {
        console.error('Ошибка при восстановлении:', error)
        message.error(error.response?.data?.detail || 'Ошибка при восстановлении оборудования')
      }
    }
  })
}

// Удаление оборудования из архива навсегда
const deleteForever = async (archivedId) => {
  const archived = source.value.find(item => item.id === archivedId)
  if (!archived) return

  dialog.error({
    title: 'Подтверждение удаления',
    content: `ВНИМАНИЕ! Вы собираетесь НАВСЕГДА удалить оборудование "${archived.equipment_name}" из архива. Это действие НЕОБРАТИМО. Продолжить?`,
    positiveText: 'Удалить навсегда',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.delete(API_ENDPOINTS.archiveDelete(archivedId))
        message.success('Оборудование удалено из архива навсегда')
        await loadData()
      } catch (error) {
        console.error('Ошибка при удалении:', error)
        message.error('Ошибка при удалении из архива')
      }
    }
  })
}

// Обработчик редактирования ячейки (не работает в режиме readOnly)
const handleAfterEdit = async (event) => {
  // В режиме просмотра редактирование запрещено
  if (props.readOnly) return

  const { prop, model, val } = event.detail

  // Обрабатываем только редактирование причины списания
  if (prop !== 'archive_reason') return

  const archivedId = model.id
  const newReason = val

  try {
    // Отправляем запрос на обновление причины
    await axios.patch(`${API_ENDPOINTS.archive}/${archivedId}/reason`, {
      archive_reason: newReason
    })

    // Обновляем локальные данные
    const itemIndex = source.value.findIndex(item => item.id === archivedId)
    if (itemIndex !== -1) {
      source.value[itemIndex].archive_reason = newReason
    }

    message.success('Причина списания обновлена')
  } catch (error) {
    console.error('Ошибка при обновлении причины списания:', error)
    message.error('Ошибка при сохранении изменений')

    // Перезагружаем данные при ошибке
    await loadData()
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="archive-table-container">
    <div class="action-panel">
      <div class="header">
        <div class="logo-title-section">
          <AppLogo @click="$emit('back-to-main')" />
          <h2 style="color: #333333; font-weight: bold; margin: 0; font-family: 'PT Astra Sans', sans-serif;">
            {{ readOnly ? 'Архив оборудования (просмотр)' : 'Архив оборудования' }}
          </h2>
        </div>
        <n-space>
          <n-button type="primary" @click="$emit('back-to-main')">
            {{ readOnly ? '← Назад' : '← Вернуться к основной таблице' }}
          </n-button>
        </n-space>
      </div>

      <!-- Поиск -->
      <div class="search-section">
        <SearchBar
          v-model="searchQuery"
          :total-count="filterStats.total"
          :filtered-count="filterStats.filtered"
          placeholder="Поиск по всем полям архива..."
        />
      </div>
    </div>

    <div class="table-wrapper" v-if="filteredData.length > 0">
      <v-grid
        ref="grid"
        :source="filteredData"
        :columns="columns"
        theme="material"
        :resize="true"
        :filter="true"
        :row-headers="true"
        @afteredit="handleAfterEdit"
      />
    </div>

    <n-empty
      v-else-if="source.length === 0"
      description="Архив пуст"
      style="margin-top: 100px;"
    >
      <template #extra>
        <n-button @click="$emit('back-to-main')">
          Вернуться к основной таблице
        </n-button>
      </template>
    </n-empty>

    <n-empty
      v-else
      description="Ничего не найдено"
      style="margin-top: 100px;"
    >
      <template #extra>
        <n-button @click="searchQuery = ''">
          Сбросить поиск
        </n-button>
      </template>
    </n-empty>

    <!-- Модальное окно для просмотра архивного оборудования -->
    <EquipmentModal
      :show="showViewModal"
      @update:show="showViewModal = $event"
      :equipment-id="viewArchiveId"
      :read-only="true"
      :is-archive="true"
    />
  </div>
</template>

<style scoped>
.archive-table-container {
  width: 100%;
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 20px;
  box-sizing: border-box;
  background: #ececec;
}

.action-panel {
  margin-bottom: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.search-section {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
}

.logo-title-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-start;
}

.header h2 {
  margin: 0;
  font-size: 20px;
  color: #333333;
  font-weight: bold;
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
  background: white;
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

/* Убрать серую заливку ячеек */
.table-wrapper :deep(revogr-data .rgCell),
.table-wrapper :deep(.rgCell) {
  background-color: #ffffff !important;
  border-bottom: 1px solid #e0e0e0;
}

.table-wrapper :deep(revogr-data .rgRow:hover .rgCell) {
  background-color: #f5f5f5 !important;
}
</style>
