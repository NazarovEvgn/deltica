<script setup>
import { ref, onMounted, computed } from 'vue'
import { NModal, NButton, NSpace, NEmpty, useMessage, useDialog } from 'naive-ui'
import { VGrid } from '@revolist/vue3-datagrid'
import axios from 'axios'
import { API_ENDPOINTS } from '../config/api.js'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:show'])

const message = useMessage()
const dialog = useDialog()

// Данные таблицы
const source = ref([])
const loading = ref(false)

// Определение колонок для RevoGrid
const columns = ref([
  {
    prop: 'executor_name',
    name: 'Исполнитель',
    size: 250,
    sortable: true,
    filter: 'string'
  },
  {
    prop: 'contract_number',
    name: 'Номер договора',
    size: 180,
    sortable: true,
    filter: 'string'
  },
  {
    prop: 'valid_until',
    name: 'Действует до',
    size: 150,
    sortable: true,
    filter: 'string',
    cellTemplate: (createElement, props) => {
      const dateStr = props.model[props.prop]
      if (!dateStr) return createElement('span', { textContent: '' })
      const formatted = formatDate(dateStr)
      return createElement('span', {
        textContent: formatted,
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'contract_amount',
    name: 'Сумма по договору',
    size: 180,
    sortable: true,
    cellTemplate: (createElement, props) => {
      const value = props.model[props.prop]
      return createElement('span', {
        textContent: formatMoney(value),
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'spent_amount',
    name: 'Израсходовано',
    size: 180,
    sortable: true,
    cellTemplate: (createElement, props) => {
      const value = props.model[props.prop]
      return createElement('span', {
        textContent: formatMoney(value),
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'balance',
    name: 'Остаток',
    size: 160,
    readonly: true,
    sortable: true,
    cellTemplate: (createElement, props) => {
      const value = props.model[props.prop] || 0
      const color = value < 0 ? '#d03050' : '#18a058'
      return createElement('span', {
        textContent: formatMoney(value),
        style: { padding: '0 4px', color, fontWeight: '500' }
      })
    }
  },
  {
    prop: 'current_balance',
    name: 'Текущий баланс',
    size: 180,
    sortable: true,
    cellTemplate: (createElement, props) => {
      const value = props.model[props.prop]
      return createElement('span', {
        textContent: value ? formatMoney(value) : '—',
        style: { padding: '0 4px' }
      })
    }
  },
  {
    prop: 'actions',
    name: 'Действия',
    size: 100,
    readonly: true,
    cellTemplate: (createElement, props) => {
      const contractId = props.model.id
      return createElement('button', {
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
        onClick: () => deleteContract(contractId)
      })
    }
  }
])

// Форматирование даты
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

// Форматирование денежных сумм
const formatMoney = (value) => {
  if (!value && value !== 0) return '0 ₽'
  return new Intl.NumberFormat('ru-RU', {
    style: 'currency',
    currency: 'RUB',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

// Загрузка данных с сервера
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get(API_ENDPOINTS.contracts)
    source.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке договоров:', error)
    message.error('Ошибка при загрузке данных')
  } finally {
    loading.value = false
  }
}

// Обработка редактирования ячейки
const handleAfterEdit = async (event) => {
  const { prop, model } = event.detail

  // Пропускаем readonly колонки
  if (prop === 'balance' || prop === 'actions') return

  try {
    // Получаем полные данные контракта
    const contract = source.value.find(c => c.id === model.id)
    if (!contract) return

    // Обновляем данные на сервере
    await axios.put(API_ENDPOINTS.contractById(contract.id), {
      executor_name: contract.executor_name,
      contract_number: contract.contract_number,
      valid_until: contract.valid_until,
      contract_amount: parseFloat(contract.contract_amount) || 0,
      spent_amount: parseFloat(contract.spent_amount) || 0,
      current_balance: contract.current_balance ? parseFloat(contract.current_balance) : null
    })

    // Перезагружаем данные чтобы получить обновленный balance
    await loadData()
    message.success('Данные обновлены')
  } catch (error) {
    console.error('Ошибка при обновлении договора:', error)
    message.error('Ошибка при сохранении данных')
    await loadData() // Откатываем изменения
  }
}

// Добавление нового договора
const addContract = async () => {
  try {
    const newContract = {
      executor_name: 'Новый исполнитель',
      contract_number: '№',
      valid_until: new Date().toISOString().split('T')[0],
      contract_amount: 0,
      spent_amount: 0,
      current_balance: null
    }

    await axios.post(API_ENDPOINTS.contracts, newContract)
    await loadData()
    message.success('Договор добавлен')
  } catch (error) {
    console.error('Ошибка при создании договора:', error)
    message.error('Ошибка при добавлении договора')
  }
}

// Удаление договора
const deleteContract = async (contractId) => {
  const contract = source.value.find(c => c.id === contractId)
  if (!contract) return

  dialog.error({
    title: 'Подтверждение удаления',
    content: `Вы уверены, что хотите удалить договор "${contract.contract_number}" с исполнителем "${contract.executor_name}"?`,
    positiveText: 'Удалить',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.delete(API_ENDPOINTS.contractById(contractId))
        await loadData()
        message.success('Договор удален')
      } catch (error) {
        console.error('Ошибка при удалении договора:', error)
        message.error('Ошибка при удалении договора')
      }
    }
  })
}

// Закрытие модального окна
const handleClose = () => {
  emit('update:show', false)
}

onMounted(() => {
  if (props.show) {
    loadData()
  }
})

// Загружаем данные при открытии модального окна
const handleUpdateShow = (value) => {
  if (value) {
    loadData()
  }
}
</script>

<template>
  <n-modal
    :show="show"
    @update:show="handleUpdateShow"
    preset="card"
    title="Баланс по договорам"
    style="width: 90%; max-width: 1400px;"
    :bordered="false"
    :segmented="{ content: true }"
  >
    <template #header-extra>
      <n-space>
        <n-button type="primary" @click="addContract">
          + Добавить договор
        </n-button>
        <n-button @click="handleClose">
          Закрыть
        </n-button>
      </n-space>
    </template>

    <div class="contracts-table-wrapper">
      <v-grid
        v-if="source.length > 0"
        :source="source"
        :columns="columns"
        theme="compact"
        :resize="true"
        :filter="true"
        :row-headers="true"
        @afteredit="handleAfterEdit"
      />
      <n-empty
        v-else
        description="Нет договоров"
        style="margin: 60px 0;"
      >
        <template #extra>
          <n-button type="primary" @click="addContract">
            + Добавить первый договор
          </n-button>
        </template>
      </n-empty>
    </div>
  </n-modal>
</template>

<style scoped>
.contracts-table-wrapper {
  min-height: 400px;
  max-height: 600px;
  overflow: auto;
}

.contracts-table-wrapper :deep(revo-grid) {
  height: 100%;
  width: 100%;
  font-family: 'PT Astra Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #ffffff;
}

/* Показывать иконки сортировки и фильтрации при наведении */
.contracts-table-wrapper :deep(.header-sortable),
.contracts-table-wrapper :deep(.header-filter) {
  opacity: 0.3;
  transition: opacity 0.2s;
}

.contracts-table-wrapper :deep(revogr-header-cell:hover .header-sortable),
.contracts-table-wrapper :deep(revogr-header-cell:hover .header-filter) {
  opacity: 1;
}

/* Всегда показывать активные иконки */
.contracts-table-wrapper :deep(.header-sortable.active),
.contracts-table-wrapper :deep(.header-filter.active) {
  opacity: 1;
}
</style>
