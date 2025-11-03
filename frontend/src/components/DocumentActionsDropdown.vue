<script setup>
import { h, computed } from 'vue'
import { NButton, NDropdown, NIcon } from 'naive-ui'
import {
  DocumentTextOutline as LabelIcon,
  DocumentAttachOutline as ActIcon,
  CloseCircleOutline as ClearIcon
} from '@vicons/ionicons5'

const props = defineProps({
  selectedCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['print-labels', 'print-conservation-act', 'download-commissioning-template', 'clear-selection'])

// Опции выпадающего меню
const dropdownOptions = computed(() => [
  {
    label: `Печать этикетки${props.selectedCount > 0 ? ` (${props.selectedCount})` : ''}`,
    key: 'labels',
    icon: () => h(NIcon, { component: LabelIcon }),
    disabled: props.selectedCount === 0  // Доступно только если выбрано оборудование
  },
  {
    label: `Акт консервации${props.selectedCount > 0 ? ` (${props.selectedCount})` : ''}`,
    key: 'conservation-act',
    icon: () => h(NIcon, { component: ActIcon }),
    disabled: props.selectedCount === 0  // Доступно только если выбрано оборудование
  },
  {
    type: 'divider',
    key: 'd1'
  },
  {
    label: 'Снять выделение',
    key: 'clear-selection',
    icon: () => h(NIcon, { component: ClearIcon }),
    disabled: props.selectedCount === 0  // Доступно только если выбрано оборудование
  },
  {
    type: 'divider',
    key: 'd2'
  },
  {
    label: 'Акт ввода в эксплуатацию',
    key: 'commissioning-template',
    icon: () => h(NIcon, { component: ActIcon }),
    disabled: false  // Всегда доступен, не зависит от выбранного оборудования
  }
])

// Обработчик выбора пункта меню
const handleSelect = (key) => {
  switch (key) {
    case 'labels':
      emit('print-labels')
      break
    case 'conservation-act':
      emit('print-conservation-act')
      break
    case 'clear-selection':
      emit('clear-selection')
      break
    case 'commissioning-template':
      emit('download-commissioning-template')
      break
  }
}
</script>

<template>
  <n-dropdown
    trigger="hover"
    :options="dropdownOptions"
    @select="handleSelect"
  >
    <n-button type="primary">
      <template #icon>
        <n-icon :component="LabelIcon" />
      </template>
      Этикетки и акты{{ selectedCount > 0 ? ` (${selectedCount})` : '' }}
    </n-button>
  </n-dropdown>
</template>

<style scoped>
/* Дополнительные стили при необходимости */
</style>
