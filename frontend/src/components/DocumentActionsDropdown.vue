<script setup>
import { h, computed } from 'vue'
import { NButton, NDropdown, NIcon } from 'naive-ui'
import {
  DocumentTextOutline as LabelIcon,
  DocumentAttachOutline as ActIcon
} from '@vicons/ionicons5'

const props = defineProps({
  selectedCount: {
    type: Number,
    default: 0
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['print-labels', 'print-conservation-act'])

// Опции выпадающего меню
const dropdownOptions = computed(() => [
  {
    label: `Печать этикетки${props.selectedCount > 0 ? ` (${props.selectedCount})` : ''}`,
    key: 'labels',
    icon: () => h(NIcon, { component: LabelIcon }),
    disabled: props.disabled
  },
  {
    label: `Акт консервации${props.selectedCount > 0 ? ` (${props.selectedCount})` : ''}`,
    key: 'conservation-act',
    icon: () => h(NIcon, { component: ActIcon }),
    disabled: props.disabled
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
  }
}
</script>

<template>
  <n-dropdown
    trigger="hover"
    :options="dropdownOptions"
    @select="handleSelect"
  >
    <n-button
      type="primary"
      :disabled="disabled"
    >
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
