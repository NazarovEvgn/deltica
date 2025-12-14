<script setup>
import { ref, watch, h } from 'vue'
import { NInput, NSpace, NBadge, NText, NIcon } from 'naive-ui'
import { SearchOutline } from '@vicons/ionicons5'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Поиск...'
  },
  totalCount: {
    type: Number,
    default: 0
  },
  filteredCount: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue'])

// Локальное значение с debounce
const localValue = ref(props.modelValue)
let debounceTimer = null

// Debounce для поиска (300ms)
watch(localValue, (newValue) => {
  if (debounceTimer) {
    clearTimeout(debounceTimer)
  }

  debounceTimer = setTimeout(() => {
    emit('update:modelValue', newValue)
  }, 300)
})

// Синхронизация с внешним значением
watch(() => props.modelValue, (newValue) => {
  if (newValue !== localValue.value) {
    localValue.value = newValue
  }
})

// Очистка поиска
const clearSearch = () => {
  localValue.value = ''
  emit('update:modelValue', '')
}
</script>

<template>
  <div class="search-bar-container">
    <n-space vertical :size="8">
      <n-input
        v-model:value="localValue"
        :placeholder="placeholder"
        clearable
        size="medium"
        @clear="clearSearch"
      >
        <template #prefix>
          <n-icon :component="SearchOutline" />
        </template>
      </n-input>

      <!-- Статистика поиска -->
      <div v-if="filteredCount !== totalCount || localValue" class="search-stats">
        <n-space :size="12" align="center">
          <n-text depth="3" style="font-size: 13px">
            Найдено:
          </n-text>
          <n-badge
            :value="filteredCount"
            :max="9999"
            :color="filteredCount === 0 ? '#d03050' : '#18a058'"
            show-zero
          >
            <n-text strong style="margin-right: 8px">
              {{ filteredCount }}
            </n-text>
          </n-badge>
          <n-text depth="3" style="font-size: 13px">
            из {{ totalCount }}
          </n-text>
        </n-space>
      </div>
    </n-space>
  </div>
</template>

<style scoped>
.search-bar-container {
  width: 600px;
}

.search-stats {
  padding-left: 4px;
}
</style>
