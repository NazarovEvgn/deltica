<script setup>
import { ref, computed, h } from 'vue'
import {
  NCard,
  NSpace,
  NButton,
  NCollapse,
  NCollapseItem,
  NCheckbox,
  NCheckboxGroup,
  NSelect,
  NTag,
  NIcon,
  NText,
  NDivider,
  NBadge
} from 'naive-ui'
import {
  ConstructOutline,
  CheckmarkCircleOutline,
  PeopleOutline,
  CashOutline,
  FunnelOutline,
  RefreshOutline
} from '@vicons/ionicons5'

const props = defineProps({
  fieldDefinitions: {
    type: Object,
    required: true
  },
  fieldGroups: {
    type: Object,
    required: true
  },
  visibleColumns: {
    type: Array,
    required: true
  },
  activeFilters: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:visibleColumns', 'update:activeFilters', 'reset', 'applyQuickFilter'])

// ==================== ИКОНКИ ====================

const groupIcons = {
  'construct-outline': ConstructOutline,
  'checkmark-circle-outline': CheckmarkCircleOutline,
  'people-outline': PeopleOutline,
  'cash-outline': CashOutline
}

// ==================== ГРУППИРОВКА ПОЛЕЙ ====================

const fieldsByGroup = computed(() => {
  const grouped = {}

  for (const [groupKey, groupInfo] of Object.entries(props.fieldGroups)) {
    grouped[groupKey] = {
      ...groupInfo,
      fields: []
    }
  }

  for (const [fieldKey, fieldInfo] of Object.entries(props.fieldDefinitions)) {
    const group = fieldInfo.group
    if (grouped[group]) {
      grouped[group].fields.push({
        key: fieldKey,
        ...fieldInfo
      })
    }
  }

  return grouped
})

// ==================== ВИДИМОСТЬ КОЛОНОК ====================

const isColumnVisible = (fieldKey) => {
  return props.visibleColumns.includes(fieldKey)
}

const toggleColumnVisibility = (fieldKey) => {
  const newVisible = [...props.visibleColumns]
  const index = newVisible.indexOf(fieldKey)

  if (index > -1) {
    newVisible.splice(index, 1)
  } else {
    newVisible.push(fieldKey)
  }

  emit('update:visibleColumns', newVisible)
}

// ==================== АКТИВНЫЕ ФИЛЬТРЫ ====================

const getFilterValue = (fieldKey) => {
  return props.activeFilters[fieldKey] || null
}

const setFilterValue = (fieldKey, value) => {
  const newFilters = { ...props.activeFilters }

  if (!value || (Array.isArray(value) && value.length === 0)) {
    delete newFilters[fieldKey]
  } else {
    newFilters[fieldKey] = value
  }

  emit('update:activeFilters', newFilters)
}

// ==================== СТАТИСТИКА ФИЛЬТРОВ ====================

const activeFilterCount = computed(() => {
  return Object.keys(props.activeFilters).length
})

const visibleColumnCount = computed(() => {
  return props.visibleColumns.length
})

// ==================== БЫСТРЫЕ ФИЛЬТРЫ ====================

const quickFilters = ref([
  { label: 'Просроченные', value: 'expired', color: 'error' },
  { label: 'Истекают', value: 'expiring', color: 'warning' },
  { label: 'Годные', value: 'fit', color: 'success' },
  { label: 'На верификации', value: 'on_verification', color: 'info' },
  { label: 'На хранении', value: 'in_storage', color: 'default' },
  { label: 'В ремонте', value: 'in_repair', color: 'default' }
])

const applyQuickFilter = (filterValue) => {
  emit('applyQuickFilter', filterValue)
}

// ==================== СБРОС ====================

const handleReset = () => {
  emit('reset')
}

// ==================== РЕНДЕР ФИЛЬТРА ДЛЯ ПОЛЯ ====================

const renderFieldFilter = (field) => {
  const filterValue = getFilterValue(field.key)

  // Для enum-полей - мультиселект
  if (field.type === 'enum' && field.options) {
    return h(NSelect, {
      value: filterValue,
      options: field.options,
      multiple: true,
      clearable: true,
      placeholder: `Выберите ${field.label.toLowerCase()}`,
      size: 'small',
      onUpdateValue: (value) => setFilterValue(field.key, value)
    })
  }

  // Для остальных типов пока не добавляем фильтры (можно расширить в будущем)
  return h(NText, { depth: 3, style: { fontSize: '12px' } }, 'Фильтр не доступен')
}
</script>

<template>
  <n-card
    title="Фильтры и колонки"
    size="small"
    :segmented="{
      content: true,
      footer: 'soft'
    }"
    class="filter-panel"
  >
    <template #header-extra>
      <n-space :size="8">
        <n-badge :value="activeFilterCount" :max="99" show-zero>
          <n-icon :component="FunnelOutline" :size="18" />
        </n-badge>
      </n-space>
    </template>

    <n-space vertical :size="16">
      <!-- Быстрые фильтры -->
      <div class="quick-filters-section">
        <n-text strong style="font-size: 14px; margin-bottom: 8px; display: block">
          Быстрые фильтры
        </n-text>
        <n-space :size="8" :wrap="true">
          <n-tag
            v-for="filter in quickFilters"
            :key="filter.value"
            :type="filter.color"
            :bordered="false"
            style="cursor: pointer"
            @click="applyQuickFilter(filter.value)"
          >
            {{ filter.label }}
          </n-tag>
        </n-space>
      </div>

      <n-divider style="margin: 8px 0" />

      <!-- Динамические фильтры по группам -->
      <n-collapse accordion default-expanded-names="equipment">
        <n-collapse-item
          v-for="(groupData, groupKey) in fieldsByGroup"
          :key="groupKey"
          :name="groupKey"
        >
          <template #header>
            <n-space :size="8" align="center">
              <n-icon
                :component="groupIcons[groupData.icon]"
                :size="18"
              />
              <n-text strong>{{ groupData.label }}</n-text>
              <n-badge
                :value="groupData.fields.filter(f => visibleColumns.includes(f.key)).length"
                :max="99"
                type="success"
                show-zero
              />
            </n-space>
          </template>

          <n-space vertical :size="12">
            <div
              v-for="field in groupData.fields"
              :key="field.key"
              class="field-filter-item"
            >
              <!-- Чекбокс для видимости колонки -->
              <n-checkbox
                :checked="isColumnVisible(field.key)"
                @update:checked="toggleColumnVisibility(field.key)"
              >
                <n-text :depth="isColumnVisible(field.key) ? 1 : 3">
                  {{ field.label }}
                </n-text>
              </n-checkbox>

              <!-- Фильтр для поля (если колонка видима и поле поддерживает фильтрацию) -->
              <div
                v-if="isColumnVisible(field.key) && field.type === 'enum'"
                class="field-filter-control"
              >
                <component :is="renderFieldFilter(field)" />
              </div>
            </div>
          </n-space>
        </n-collapse-item>
      </n-collapse>

      <n-divider style="margin: 8px 0" />

      <!-- Статистика и кнопка сброса -->
      <n-space justify="space-between" align="center">
        <n-space vertical :size="4">
          <n-text depth="3" style="font-size: 12px">
            Колонок: {{ visibleColumnCount }}
          </n-text>
          <n-text depth="3" style="font-size: 12px">
            Фильтров: {{ activeFilterCount }}
          </n-text>
        </n-space>

        <n-button
          secondary
          type="warning"
          size="small"
          @click="handleReset"
        >
          <template #icon>
            <n-icon :component="RefreshOutline" />
          </template>
          Сбросить всё
        </n-button>
      </n-space>
    </n-space>
  </n-card>
</template>

<style scoped>
.filter-panel {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.quick-filters-section {
  padding: 4px 0;
}

.field-filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  border-radius: 4px;
  background-color: rgba(0, 0, 0, 0.02);
}

.field-filter-control {
  margin-left: 24px;
}

/* Стили для dark mode (опционально) */
@media (prefers-color-scheme: dark) {
  .field-filter-item {
    background-color: rgba(255, 255, 255, 0.05);
  }
}
</style>
