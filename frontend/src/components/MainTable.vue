<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NSpace } from 'naive-ui'
import { VGrid } from '@revolist/vue3-datagrid'
import axios from 'axios'

const emit = defineEmits(['add-equipment', 'edit-equipment', 'show-archive'])

// Данные таблицы
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

// Определение колонок для RevoGrid
const columns = ref([
  { prop: 'equipment_name', name: 'Наименование', size: 200 },
  { prop: 'equipment_model', name: 'Модель', size: 150 },
  { prop: 'factory_number', name: 'Заводской номер', size: 150 },
  { prop: 'inventory_number', name: 'Инвентарный номер', size: 150 },
  {
    prop: 'verification_type',
    name: 'Тип верификации',
    size: 150,
    readonly: true,
    cellTemplate: (createElement, props) => {
      const verificationTypeMap = {
        'calibration': 'Калибровка',
        'verification': 'Поверка',
        'certification': 'Аттестация'
      }
      const currentValue = props.model[props.prop] || ''
      const displayValue = verificationTypeMap[currentValue] || currentValue

      return createElement('span', {
        textContent: displayValue,
        style: {
          padding: '0 4px'
        }
      })
    }
  },
  { prop: 'verification_interval', name: 'Интервал (мес)', size: 120 },
  {
    prop: 'verification_date',
    name: 'Дата верификации',
    size: 150,
    cellTemplate: (createElement, props) => {
      return createElement('span', {
        textContent: formatDate(props.model[props.prop]),
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'verification_due',
    name: 'Действует до',
    size: 150,
    readonly: true,
    cellTemplate: (createElement, props) => {
      return createElement('span', {
        textContent: formatDate(props.model[props.prop]),
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'verification_plan',
    name: 'План верификации',
    size: 150,
    cellTemplate: (createElement, props) => {
      return createElement('span', {
        textContent: formatMonthYear(props.model[props.prop]),
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'status',
    name: 'Статус',
    size: 150,
    readonly: true,
    cellTemplate: (createElement, props) => {
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
        style: {
          padding: '0 4px'
        }
      })
    }
  },
  {
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
  }
])

// Загрузка данных с бэкенда
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/main-table/')
    source.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  } finally {
    loading.value = false
  }
}

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
})

// Экспорт функции для перезагрузки данных (для использования родительским компонентом)
defineExpose({
  loadData
})
</script>

<template>
  <div class="main-table-container">
    <div class="action-panel">
      <n-space>
        <n-button type="primary" @click="$emit('add-equipment')">
          Добавить оборудование
        </n-button>
        <n-button @click="loadData">
          Обновить
        </n-button>
        <n-button type="warning" @click="$emit('show-archive')">
          Архив
        </n-button>
      </n-space>
      <div class="hint-text">
        Двойной клик по строке для редактирования. Можно копировать данные (Ctrl+C / Ctrl+V)
      </div>
    </div>

    <div class="table-wrapper">
      <v-grid
        ref="grid"
        :source="source"
        :columns="columns"
        theme="compact"
        :resize="true"
        :range="true"
        :readonly="false"
        :row-headers="true"
        :can-focus="true"
        @afteredit="handleAfterEdit"
        @beforerangeedit="handleBeforeRangeEdit"
        @celldblclick="handleCellDblClick"
      />
    </div>
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
}

.action-panel {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
