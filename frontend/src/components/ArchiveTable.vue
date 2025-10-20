<script setup>
import { ref, onMounted } from 'vue'
import { NButton, NSpace, NEmpty, useMessage, useDialog } from 'naive-ui'
import { VGrid } from '@revolist/vue3-datagrid'
import axios from 'axios'
import AppLogo from './AppLogo.vue'

const emit = defineEmits(['back-to-main', 'restored'])
const message = useMessage()
const dialog = useDialog()

// Данные архивной таблицы
const source = ref([])
const loading = ref(false)

// Функция форматирования даты в dd.mm.yyyy
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

// Определение колонок для RevoGrid
const columns = ref([
  { prop: 'equipment_name', name: 'Наименование', size: 200, readonly: true, sortable: true, filter: 'string' },
  { prop: 'equipment_model', name: 'Модель', size: 150, readonly: true, sortable: true, filter: 'string' },
  { prop: 'factory_number', name: 'Заводской номер', size: 150, readonly: true, sortable: true, filter: 'string' },
  { prop: 'inventory_number', name: 'Инвентарный номер', size: 150, readonly: true, sortable: true, filter: 'string' },
  {
    prop: 'equipment_type',
    name: 'Тип',
    size: 100,
    readonly: true,
    sortable: true,
    filter: 'string',
    cellTemplate: (createElement, props) => {
      const typeMap = { 'SI': 'СИ', 'IO': 'ИО' }
      const currentValue = props.model[props.prop] || ''
      return createElement('span', {
        textContent: typeMap[currentValue] || currentValue,
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
    cellTemplate: (createElement, props) => {
      const dateStr = props.model[props.prop]
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
    readonly: true,
    sortable: true,
    filter: 'string',
    cellTemplate: (createElement, props) => {
      return createElement('span', {
        textContent: props.model[props.prop] || '—',
        style: { padding: '0 4px', color: props.model[props.prop] ? 'inherit' : '#999' }
      })
    }
  },
  {
    prop: 'actions',
    name: 'Действия',
    size: 260,
    readonly: true,
    sortable: false,
    cellTemplate: (createElement, props) => {
      const archivedId = props.model.id
      return createElement('div', {
        style: { display: 'flex', gap: '8px', padding: '4px 8px 4px 4px' }
      }, [
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
  }
])

// Загрузка данных архива с бэкенда
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/archive/')
    source.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке архива:', error)
    message.error('Ошибка при загрузке архивных данных')
  } finally {
    loading.value = false
  }
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
        await axios.post(`http://localhost:8000/archive/restore/${archivedId}`)
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
        await axios.delete(`http://localhost:8000/archive/${archivedId}`)
        message.success('Оборудование удалено из архива навсегда')
        await loadData()
      } catch (error) {
        console.error('Ошибка при удалении:', error)
        message.error('Ошибка при удалении из архива')
      }
    }
  })
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
          <AppLogo />
          <h2 style="color: #333333; font-weight: bold; margin: 0;">Архив оборудования</h2>
        </div>
        <n-space>
          <n-button type="primary" @click="$emit('back-to-main')">
            ← Вернуться к основной таблице
          </n-button>
        </n-space>
      </div>
    </div>

    <div class="table-wrapper" v-if="source.length > 0">
      <v-grid
        ref="grid"
        :source="source"
        :columns="columns"
        theme="compact"
        :resize="true"
        :filter="true"
        :readonly="true"
        :row-headers="true"
      />
    </div>

    <n-empty
      v-else
      description="Архив пуст"
      style="margin-top: 100px;"
    >
      <template #extra>
        <n-button @click="$emit('back-to-main')">
          Вернуться к основной таблице
        </n-button>
      </template>
    </n-empty>
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
  background: #f5f5f5;
}

.action-panel {
  margin-bottom: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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
</style>
