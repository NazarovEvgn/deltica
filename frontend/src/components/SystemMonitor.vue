<script setup>
import { ref, computed } from 'vue'
import { NButton, NModal, NSpace, NCard, NTabs, NTabPane, NStatistic, useMessage } from 'naive-ui'
import axios from 'axios'
import { API_ENDPOINTS } from '../config/api.js'

const message = useMessage()

// Состояние модального окна
const showModal = ref(false)

// Данные
const systemInfo = ref(null)
const logs = ref([])
const loadingSystem = ref(false)
const loadingLogs = ref(false)

// Загрузка информации о системе
const loadSystemInfo = async () => {
  loadingSystem.value = true
  try {
    const response = await axios.get(API_ENDPOINTS.healthSystem)
    systemInfo.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке информации о системе:', error)
    message.error('Ошибка при загрузке информации о системе')
  } finally {
    loadingSystem.value = false
  }
}

// Загрузка логов
const loadLogs = async (limit = 100) => {
  loadingLogs.value = true
  try {
    const response = await axios.get(API_ENDPOINTS.healthLogs(limit))
    logs.value = response.data.logs || []
  } catch (error) {
    console.error('Ошибка при загрузке логов:', error)
    message.error('Ошибка при загрузке логов')
  } finally {
    loadingLogs.value = false
  }
}

// Форматирование даты
const formatDate = (dateString) => {
  const date = new Date(dateString)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${day}.${month}.${year} ${hours}:${minutes}:${seconds}`
}

// Парсинг JSON лога для отображения
const parseLogLine = (logLine) => {
  try {
    const logData = JSON.parse(logLine)
    return {
      timestamp: logData.timestamp ? formatDate(logData.timestamp) : '',
      level: logData.level || 'INFO',
      message: logData.message || logLine,
      user: logData.user || '',
      event: logData.event || '',
      raw: logData
    }
  } catch {
    return {
      timestamp: '',
      level: 'INFO',
      message: logLine,
      user: '',
      event: '',
      raw: null
    }
  }
}

// Цвет для уровня логирования
const getLevelColor = (level) => {
  const colors = {
    'ERROR': '#d4380d',
    'WARNING': '#fa8c16',
    'INFO': '#1890ff',
    'DEBUG': '#8c8c8c'
  }
  return colors[level] || '#8c8c8c'
}

// Цвет статуса БД
const dbStatusColor = computed(() => {
  if (!systemInfo.value) return '#8c8c8c'
  return systemInfo.value.database.status === 'ok' ? '#52c41a' : '#d4380d'
})

// Цвет общего статуса
const overallStatusColor = computed(() => {
  if (!systemInfo.value) return '#8c8c8c'
  return systemInfo.value.status === 'ok' ? '#52c41a' : '#fa8c16'
})

// Открытие модального окна
const openModal = async () => {
  showModal.value = true
  await Promise.all([loadSystemInfo(), loadLogs(100)])
}

// Закрытие модального окна
const closeModal = () => {
  showModal.value = false
}

// Обновление данных
const refreshData = async () => {
  await Promise.all([loadSystemInfo(), loadLogs(100)])
  message.success('Данные обновлены')
}

defineExpose({
  openModal
})
</script>

<template>
  <div>
    <!-- Модальное окно с мониторингом -->
    <n-modal
      v-model:show="showModal"
      preset="card"
      title="Мониторинг системы"
      :style="{ width: '900px' }"
      :segmented="{ content: 'soft' }"
    >
      <n-space vertical :size="16">
        <!-- Кнопка обновления -->
        <n-button
          type="primary"
          @click="refreshData"
          :loading="loadingSystem || loadingLogs"
        >
          Обновить
        </n-button>

        <!-- Вкладки -->
        <n-tabs type="line" animated>
          <!-- Вкладка: Состояние системы -->
          <n-tab-pane name="system" tab="Состояние системы">
            <div v-if="loadingSystem" style="text-align: center; padding: 20px; color: #666;">
              Загрузка...
            </div>

            <n-space v-else-if="systemInfo" vertical :size="16">
              <!-- Общий статус -->
              <n-card title="Общий статус" size="small">
                <n-space>
                  <n-statistic label="Статус">
                    <template #default>
                      <span :style="{ color: overallStatusColor }">
                        {{ systemInfo.status.toUpperCase() }}
                      </span>
                    </template>
                  </n-statistic>
                  <n-statistic label="Время проверки" :value="formatDate(systemInfo.timestamp)" />
                </n-space>
              </n-card>

              <!-- База данных -->
              <n-card title="База данных" size="small">
                <n-space>
                  <n-statistic label="Статус БД">
                    <template #default>
                      <span :style="{ color: dbStatusColor }">
                        {{ systemInfo.database.status.toUpperCase() }}
                      </span>
                    </template>
                  </n-statistic>
                  <n-statistic
                    v-if="systemInfo.database.error"
                    label="Ошибка"
                    :value="systemInfo.database.error"
                  />
                </n-space>
              </n-card>

              <!-- Ресурсы системы -->
              <n-card title="Ресурсы" size="small">
                <n-space>
                  <n-statistic label="CPU" :value="`${systemInfo.system.cpu_percent}%`" />
                  <n-statistic label="Память" :value="`${systemInfo.system.memory_percent}%`" />
                  <n-statistic
                    label="Свободная память"
                    :value="`${systemInfo.system.memory_available_gb} GB`"
                  />
                  <n-statistic label="Диск" :value="`${systemInfo.system.disk_percent}%`" />
                  <n-statistic
                    label="Свободно на диске"
                    :value="`${systemInfo.system.disk_free_gb} GB`"
                  />
                </n-space>
              </n-card>

              <!-- Логи -->
              <n-card title="Файлы логов" size="small">
                <n-space>
                  <n-statistic label="Количество файлов" :value="systemInfo.logs.count" />
                  <n-statistic
                    label="Общий размер"
                    :value="`${systemInfo.logs.total_size_mb} MB`"
                  />
                </n-space>
              </n-card>
            </n-space>
          </n-tab-pane>

          <!-- Вкладка: Логи -->
          <n-tab-pane name="logs" tab="Логи">
            <div v-if="loadingLogs" style="text-align: center; padding: 20px; color: #666;">
              Загрузка...
            </div>

            <div v-else-if="logs.length === 0" style="text-align: center; padding: 20px; color: #999;">
              Нет логов
            </div>

            <div v-else style="font-family: monospace; font-size: 12px; max-height: 500px; overflow-y: auto; background: #fafafa; padding: 12px; border-radius: 4px;">
              <div
                v-for="(log, index) in logs"
                :key="index"
                style="padding: 4px 0; border-bottom: 1px solid #e8e8e8;"
              >
                <template v-if="parseLogLine(log).raw">
                  <div>
                    <span style="color: #8c8c8c;">{{ parseLogLine(log).timestamp }}</span>
                    <span
                      :style="{
                        color: getLevelColor(parseLogLine(log).level),
                        marginLeft: '8px',
                        fontWeight: 'bold'
                      }"
                    >
                      [{{ parseLogLine(log).level }}]
                    </span>
                    <span v-if="parseLogLine(log).user" style="color: #1890ff; margin-left: 8px;">
                      @{{ parseLogLine(log).user }}
                    </span>
                    <span v-if="parseLogLine(log).event" style="color: #722ed1; margin-left: 8px;">
                      ({{ parseLogLine(log).event }})
                    </span>
                  </div>
                  <div style="margin-left: 16px; color: #262626; margin-top: 2px;">
                    {{ parseLogLine(log).message }}
                  </div>
                </template>
                <template v-else>
                  <span style="color: #595959;">{{ log }}</span>
                </template>
              </div>
            </div>
          </n-tab-pane>
        </n-tabs>
      </n-space>

      <template #footer>
        <n-space justify="end">
          <n-button @click="closeModal">Закрыть</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<style scoped>
/* Стили для скроллбара */
div::-webkit-scrollbar {
  width: 8px;
}

div::-webkit-scrollbar-track {
  background: #f1f1f1;
}

div::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

div::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>
