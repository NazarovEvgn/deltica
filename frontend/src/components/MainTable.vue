<script setup>
import { ref, onMounted, h } from 'vue'
import { NButton, NSpace, NDataTable } from 'naive-ui'
import axios from 'axios'

const emit = defineEmits(['add-equipment', 'edit-equipment'])

// Данные таблицы
const data = ref([])
const loading = ref(false)

const columns = [
  { title: 'Наименование', key: 'equipment_name', width: 200 },
  { title: 'Модель', key: 'equipment_model', width: 150 },
  { title: 'Заводской номер', key: 'factory_number', width: 150 },
  { title: 'Инвентарный номер', key: 'inventory_number', width: 150 },
  { title: 'Тип верификации', key: 'verification_type', width: 150 },
  { title: 'Интервал (мес)', key: 'verification_interval', width: 120 },
  { title: 'Дата верификации', key: 'verification_date', width: 150 },
  { title: 'Действует до', key: 'verification_due', width: 150 },
  { title: 'План верификации', key: 'verification_plan', width: 150 },
  { title: 'Состояние', key: 'verification_state', width: 150 },
  { title: 'Статус', key: 'status', width: 150 },
  {
    title: 'Действия',
    key: 'actions',
    width: 200,
    render(row) {
      return h(
        NSpace,
        {},
        {
          default: () => [
            h(
              NButton,
              {
                size: 'small',
                onClick: () => editEquipment(row.equipment_id)
              },
              { default: () => 'Редактировать' }
            ),
            h(
              NButton,
              {
                size: 'small',
                type: 'error',
                onClick: () => deleteEquipment(row.equipment_id)
              },
              { default: () => 'Удалить' }
            )
          ]
        }
      )
    }
  }
]

// Загрузка данных с бэкенда
const loadData = async () => {
  loading.value = true
  try {
    const response = await axios.get('http://localhost:8000/main-table/')
    data.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке данных:', error)
  } finally {
    loading.value = false
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
      </n-space>
    </div>

    <div class="table-wrapper">
      <n-data-table
        :columns="columns"
        :data="data"
        :loading="loading"
        :scroll-x="1800"
        striped
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
}

.action-panel {
  margin-bottom: 20px;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
}
</style>
