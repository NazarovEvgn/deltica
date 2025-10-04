<script setup>
import { NButton, NSpace } from 'naive-ui'

const props = defineProps({
  equipmentId: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['edit', 'delete'])

const handleEdit = () => {
  emit('edit', props.equipmentId)
}

const handleDelete = () => {
  if (confirm('Вы уверены, что хотите удалить это оборудование?')) {
    emit('delete', props.equipmentId)
  }
}
</script>

<template>
  <n-space>
    <n-button size="small" @click="handleEdit">
      Редактировать
    </n-button>
    <n-button size="small" type="error" @click="handleDelete">
      Удалить
    </n-button>
  </n-space>
</template>

<style scoped>
.n-space {
  padding: 4px;
}
</style>
