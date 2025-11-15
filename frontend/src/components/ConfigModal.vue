<script setup>
import { ref } from 'vue'
import { NModal, NCard, NForm, NFormItem, NInput, NButton, NSpace } from 'naive-ui'

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
})

const emit = defineEmits(['update:show', 'config-saved'])

const serverUrl = ref('http://localhost:8000')
const isSaving = ref(false)

// Обработка сохранения конфигурации
const handleSave = async () => {
  if (!serverUrl.value) {
    return
  }

  // Убираем trailing slash если есть
  let url = serverUrl.value.trim()
  if (url.endsWith('/')) {
    url = url.slice(0, -1)
  }

  // Добавляем http:// если протокол не указан
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = `http://${url}`
  }

  isSaving.value = true

  try {
    // Сохраняем конфигурацию через Electron IPC
    if (window.electron) {
      await window.electron.saveConfig({
        serverUrl: url
      })
    }

    emit('config-saved', url)
  } catch (error) {
    console.error('Ошибка сохранения конфигурации:', error)
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <n-modal
    :show="show"
    :mask-closable="false"
    :close-on-esc="false"
    :on-update:show="(val) => emit('update:show', val)"
  >
    <n-card
      style="width: 500px"
      title="Настройка подключения к серверу"
      :bordered="false"
      size="large"
    >
      <div style="margin-bottom: 24px; color: #666; font-size: 14px;">
        <p style="margin: 0 0 12px 0;">
          Укажите адрес сервера Deltica для подключения.
        </p>
        <p style="margin: 0; font-weight: 500;">
          Примеры:
        </p>
        <ul style="margin: 8px 0 0 20px; padding: 0;">
          <li>localhost или 127.0.0.1 (если сервер на этом же ПК)</li>
          <li>192.168.1.10 (если сервер в локальной сети)</li>
          <li>http://192.168.1.10:8000 (с указанием протокола и порта)</li>
        </ul>
      </div>

      <n-form>
        <n-form-item label="Адрес сервера" required>
          <n-input
            v-model:value="serverUrl"
            placeholder="localhost или 192.168.1.10"
            size="large"
            :disabled="isSaving"
            @keyup.enter="handleSave"
          />
        </n-form-item>
      </n-form>

      <template #footer>
        <n-space justify="end">
          <n-button
            type="primary"
            size="large"
            :loading="isSaving"
            :disabled="!serverUrl"
            @click="handleSave"
          >
            Сохранить и продолжить
          </n-button>
        </n-space>
      </template>
    </n-card>
  </n-modal>
</template>
