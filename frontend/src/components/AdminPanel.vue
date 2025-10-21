<script setup>
import { h } from 'vue'
import { NButton, NDropdown, NIcon } from 'naive-ui'
import {
  SettingsOutline as SettingsIcon,
  AddCircleOutline as AddIcon,
  ArchiveOutline as ArchiveIcon,
  CloudDownloadOutline as BackupIcon,
  StatsChartOutline as MonitorIcon
} from '@vicons/ionicons5'

const emit = defineEmits(['add-equipment', 'show-archive', 'show-backup', 'show-monitor'])

// Опции выпадающего меню
const dropdownOptions = [
  {
    label: 'Добавить оборудование',
    key: 'add',
    icon: () => h(NIcon, { component: AddIcon })
  },
  {
    type: 'divider',
    key: 'd1'
  },
  {
    label: 'Архив',
    key: 'archive',
    icon: () => h(NIcon, { component: ArchiveIcon })
  },
  {
    label: 'Backup БД',
    key: 'backup',
    icon: () => h(NIcon, { component: BackupIcon })
  },
  {
    label: 'Мониторинг',
    key: 'monitor',
    icon: () => h(NIcon, { component: MonitorIcon })
  }
]

// Обработчик выбора пункта меню
const handleSelect = (key) => {
  switch (key) {
    case 'add':
      emit('add-equipment')
      break
    case 'archive':
      emit('show-archive')
      break
    case 'backup':
      emit('show-backup')
      break
    case 'monitor':
      emit('show-monitor')
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
        <n-icon :component="SettingsIcon" />
      </template>
      Панель управления
    </n-button>
  </n-dropdown>
</template>

<style scoped>
/* Дополнительные стили при необходимости */
</style>
