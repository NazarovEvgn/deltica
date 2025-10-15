<script setup>
import { ref } from 'vue'
import { NMessageProvider, NDialogProvider } from 'naive-ui'
import MainTable from './components/MainTable.vue'
import EquipmentModal from './components/EquipmentModal.vue'

const showModal = ref(false)
const editingEquipmentId = ref(null)
const mainTableRef = ref(null)

// Открыть модальное окно для добавления
const handleAddEquipment = () => {
  editingEquipmentId.value = null
  showModal.value = true
}

// Открыть модальное окно для редактирования
const handleEditEquipment = (equipmentId) => {
  editingEquipmentId.value = equipmentId
  showModal.value = true
}

// Обработка сохранения (после создания или обновления)
const handleSaved = () => {
  mainTableRef.value?.loadData()
}
</script>

<template>
  <n-message-provider>
    <n-dialog-provider>
      <div id="app">
        <MainTable
          ref="mainTableRef"
          @add-equipment="handleAddEquipment"
          @edit-equipment="handleEditEquipment"
        />
        <EquipmentModal
          v-model:show="showModal"
          :equipment-id="editingEquipmentId"
          @saved="handleSaved"
        />
      </div>
    </n-dialog-provider>
  </n-message-provider>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  overflow: hidden;
}
</style>
