<script setup>
import { ref, watch, onMounted } from 'vue'
import {
  NModal,
  NCard,
  NForm,
  NFormItem,
  NInput,
  NSelect,
  NRadioGroup,
  NRadio,
  NDatePicker,
  NInputNumber,
  NButton,
  NSpace,
  NGrid,
  NGridItem,
  NUpload,
  NUploadDragger,
  NText,
  NP,
  NIcon,
  NList,
  NListItem,
  NThing,
  useMessage,
  useDialog,
  NDialogProvider
} from 'naive-ui'
import { CloudUploadOutline as CloudUploadIcon, DocumentTextOutline as DocumentIcon, TrashOutline as TrashIcon, ArchiveOutline as ArchiveIcon } from '@vicons/ionicons5'
import axios from 'axios'
import { useAuth } from '@/composables/useAuth'

const message = useMessage()
const dialog = useDialog()

// Аутентификация
const { isAdmin } = useAuth()

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  equipmentId: {
    type: Number,
    default: null
  },
  readOnly: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'saved'])

// Модель формы
const formValue = ref({
  // Equipment
  equipment_name: '',
  equipment_model: '',
  equipment_type: 'SI',
  equipment_specs: '',
  factory_number: '',
  inventory_number: '',
  equipment_year: new Date().getFullYear(),

  // Verification
  verification_type: 'verification',
  registry_number: '',
  verification_interval: 12,
  verification_date: Date.now(),
  verification_due: Date.now(),
  verification_plan: Date.now(),
  verification_state: 'state_work',
  status: 'status_fit',

  // Responsibility
  department: '',
  responsible_person: '',
  verifier_org: '',

  // Finance
  budget_item: '',
  code_rate: '',
  cost_rate: null,
  quantity: 1,
  coefficient: 1.0,
  total_cost: null,
  invoice_number: '',
  paid_amount: null,
  payment_date: null
})

// Опции для select-ов
const equipmentTypeOptions = [
  { label: 'СИ (Средства Измерения)', value: 'SI' },
  { label: 'ИО (Испытательное Оборудование)', value: 'IO' }
]

const verificationTypeOptions = [
  { label: 'Калибровка', value: 'calibration' },
  { label: 'Поверка', value: 'verification' },
  { label: 'Аттестация', value: 'certification' }
]

const verificationStateOptions = [
  { label: 'В работе', value: 'state_work' },
  { label: 'На консервации', value: 'state_storage' },
  { label: 'На верификации', value: 'state_verification' },
  { label: 'В ремонте', value: 'state_repair' },
  { label: 'В архиве', value: 'state_archived' }
]

const statusOptions = [
  { label: 'Годен', value: 'status_fit' },
  { label: 'Просрочен', value: 'status_expired' },
  { label: 'Истекает', value: 'status_expiring' },
  { label: 'На консервации', value: 'status_storage' },
  { label: 'На верификации', value: 'status_verification' },
  { label: 'В ремонте', value: 'status_repair' }
]

const departmentOptions = [
  { label: 'Группа СМ', value: 'gruppa_sm' },
  { label: 'ГТЛ', value: 'gtl' },
  { label: 'ЛБР', value: 'lbr' },
  { label: 'ЛТР', value: 'ltr' },
  { label: 'ЛХАиЭИ', value: 'lhaiei' },
  { label: 'ОГМК', value: 'ogmk' },
  { label: 'ОИИ', value: 'oii' },
  { label: 'СМТСиК', value: 'smtsik' },
  { label: 'СОИИ', value: 'soii' },
  { label: 'ТО', value: 'to' },
  { label: 'ТС', value: 'ts' },
  { label: 'ЭС', value: 'es' }
]

const responsiblePersonOptions = [
  { label: 'Аббасов И.', value: 'iabbasov' },
  { label: 'Абрамов А.', value: 'aabramov' },
  { label: 'Антипенский Е.', value: 'eantipensky' },
  { label: 'Бикиняев Р.', value: 'rbikinyaev' },
  { label: 'Горбачев Д.', value: 'dgorbachev' },
  { label: 'Дубинский И.', value: 'idubinsky' },
  { label: 'Забора И.', value: 'izabora' },
  { label: 'Калашников С.', value: 'skalashnikov' },
  { label: 'Кобякова Н.', value: 'nkobyakova' },
  { label: 'Кулинич Г.', value: 'gkulinich' },
  { label: 'Макаров В.', value: 'vmakarov' },
  { label: 'Матуся С.', value: 'smatusya' },
  { label: 'Медведев А.', value: 'amedvedev' },
  { label: 'Назаров Е.', value: 'enazarov' },
  { label: 'Пальянов В.', value: 'vpalyanov' },
  { label: 'Радионов А.', value: 'aradionov' },
  { label: 'Солодовниченко И.', value: 'isolodovnichenko' },
  { label: 'Фещенко Р.', value: 'rfeschenko' },
  { label: 'Черкашин А.', value: 'acherkashin' }
]

const isEdit = ref(false)

// Состояние файлов
const equipmentFiles = ref([])

// Загрузка списка файлов оборудования
const loadEquipmentFiles = async () => {
  if (!props.equipmentId) return

  try {
    const response = await axios.get(`http://localhost:8000/files/equipment/${props.equipmentId}`)
    equipmentFiles.value = response.data
  } catch (error) {
    console.error('Ошибка при загрузке файлов:', error)
  }
}

// Обработчик загрузки файла
const handleFileUpload = async ({ file }) => {
  if (!isEdit.value || !props.equipmentId) {
    message.warning('Сначала сохраните оборудование')
    return
  }

  try {
    const formData = new FormData()
    formData.append('file', file.file)
    formData.append('file_type', 'other')

    await axios.post(
      `http://localhost:8000/files/upload/${props.equipmentId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    message.success('Файл успешно загружен')
    await loadEquipmentFiles()
  } catch (error) {
    console.error('Ошибка при загрузке файла:', error)
    message.error(error.response?.data?.detail || 'Ошибка при загрузке файла')
  }

  return false  // Предотвращаем стандартное поведение
}

// Открытие файла для просмотра
const openFile = (fileId, fileName) => {
  // Открываем файл в новой вкладке для просмотра
  window.open(`http://localhost:8000/files/view/${fileId}`, '_blank')
}

// Скачивание файла (принудительное скачивание)
const downloadFile = (fileId, fileName) => {
  // Используем endpoint для скачивания
  window.location.href = `http://localhost:8000/files/download/${fileId}`
}

// Удаление файла
const deleteFile = async (fileId) => {
  try {
    await axios.delete(`http://localhost:8000/files/${fileId}`)
    message.success('Файл успешно удален')
    await loadEquipmentFiles()
  } catch (error) {
    console.error('Ошибка при удалении файла:', error)
    message.error('Ошибка при удалении файла')
  }
}

// Форматирование размера файла
const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}


// Загрузка данных для редактирования
const loadEquipmentData = async () => {
  if (!props.equipmentId) return

  try {
    const response = await axios.get(`http://localhost:8000/main-table/${props.equipmentId}/full`)
    const data = response.data

    // Заполняем форму данными
    formValue.value = {
      equipment_name: data.equipment_name,
      equipment_model: data.equipment_model,
      equipment_type: data.equipment_type || 'SI',
      equipment_specs: data.equipment_specs || '',
      factory_number: data.factory_number,
      inventory_number: data.inventory_number,
      equipment_year: data.equipment_year,

      verification_type: data.verification_type,
      registry_number: data.registry_number || '',
      verification_interval: data.verification_interval,
      verification_date: data.verification_date ? new Date(data.verification_date).getTime() : Date.now(),
      verification_due: data.verification_due ? new Date(data.verification_due).getTime() : Date.now(),
      verification_plan: data.verification_plan ? new Date(data.verification_plan).getTime() : Date.now(),
      verification_state: data.verification_state,
      status: data.status,

      department: data.department || '',
      responsible_person: data.responsible_person || '',
      verifier_org: data.verifier_org || '',

      budget_item: data.budget_item || '',
      code_rate: data.code_rate || '',
      cost_rate: data.cost_rate,
      quantity: data.quantity || 1,
      coefficient: data.coefficient || 1.0,
      total_cost: data.total_cost,
      invoice_number: data.invoice_number || '',
      paid_amount: data.paid_amount,
      payment_date: data.payment_date ? new Date(data.payment_date).getTime() : null
    }
  } catch (error) {
    console.error('Ошибка при загрузке данных оборудования:', error)
  }
}

// Сброс формы
const resetForm = () => {
  formValue.value = {
    equipment_name: '',
    equipment_model: '',
    equipment_type: 'SI',
    equipment_specs: '',
    factory_number: '',
    inventory_number: '',
    equipment_year: new Date().getFullYear(),

    verification_type: 'verification',
    registry_number: '',
    verification_interval: 12,
    verification_date: Date.now(),
    verification_due: Date.now(),
    verification_plan: Date.now(),
    verification_state: 'state_work',
    status: 'status_fit',

    department: '',
    responsible_person: '',
    verifier_org: '',

    budget_item: '',
    code_rate: null,
    cost_rate: null,
    quantity: 1,
    coefficient: 1.0,
    total_cost: null,
    invoice_number: '',
    paid_amount: null,
    payment_date: null
  }
}

// Функция для конвертации timestamp в локальную дату YYYY-MM-DD
const formatDateToLocal = (timestamp) => {
  const date = new Date(timestamp)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// Валидация verification_interval (должен быть кратен 12)
const validateVerificationInterval = (value) => {
  if (value && value % 12 !== 0) {
    message.error('Интервал верификации должен быть кратен 12 месяцам (12, 24, 36, 48 и т.д.)')
    return false
  }
  return true
}

// Обработчик изменения verification_interval
const handleIntervalChange = (value) => {
  if (!validateVerificationInterval(value)) {
    // Округляем до ближайшего кратного 12
    const rounded = Math.round(value / 12) * 12
    formValue.value.verification_interval = rounded || 12
  }
}

// Сохранение данных
const handleSave = async () => {
  // Валидация перед сохранением
  if (!validateVerificationInterval(formValue.value.verification_interval)) {
    return
  }
  try {
    // Подготовка данных для отправки
    const payload = {
      ...formValue.value,
      verification_date: formatDateToLocal(formValue.value.verification_date),
      verification_due: formatDateToLocal(formValue.value.verification_due),
      verification_plan: formatDateToLocal(formValue.value.verification_plan),
      payment_date: formValue.value.payment_date
        ? formatDateToLocal(formValue.value.payment_date)
        : null
    }

    if (isEdit.value) {
      // Обновление
      await axios.put(`http://localhost:8000/main-table/${props.equipmentId}`, payload)
    } else {
      // Создание
      await axios.post('http://localhost:8000/main-table/', payload)
    }

    message.success(isEdit.value ? 'Данные успешно обновлены' : 'Оборудование успешно добавлено')
    emit('saved')
    handleClose()
  } catch (error) {
    console.error('Ошибка при сохранении:', error)
    console.error('Полный ответ ошибки:', error.response)

    let errorMessage = 'Ошибка при сохранении данных'

    if (error.response?.data?.detail) {
      // Если detail - это массив (validation errors от Pydantic)
      if (Array.isArray(error.response.data.detail)) {
        const errors = error.response.data.detail.map(err => {
          const field = err.loc?.[err.loc.length - 1] || 'field'
          return `${field}: ${err.msg}`
        }).join('; ')
        errorMessage = `Ошибки валидации: ${errors}`
      } else {
        errorMessage = error.response.data.detail
      }
    } else if (error.message) {
      errorMessage = error.message
    }

    message.error(errorMessage)
  }
}

// Закрытие модального окна
const handleClose = () => {
  emit('update:show', false)
  resetForm()
}

// Архивирование оборудования
const handleArchive = async () => {
  dialog.warning({
    title: 'Подтверждение архивирования',
    content: `Вы уверены, что хотите архивировать оборудование "${formValue.value.equipment_name}"? Оно будет перемещено в архив и удалено из основной таблицы.`,
    positiveText: 'Архивировать',
    negativeText: 'Отмена',
    onPositiveClick: async () => {
      try {
        await axios.post(`http://localhost:8000/archive/equipment/${props.equipmentId}`, {
          archive_reason: null  // Можно добавить поле для ввода причины
        })
        message.success('Оборудование успешно архивировано')
        emit('saved')
        handleClose()
      } catch (error) {
        console.error('Ошибка при архивировании:', error)
        message.error(error.response?.data?.detail || 'Ошибка при архивировании оборудования')
      }
    }
  })
}

// Автоматическое обновление verification_plan при изменении verification_date или verification_interval
watch([() => formValue.value.verification_date, () => formValue.value.verification_interval], ([newDate, newInterval]) => {
  if (newDate && newInterval) {
    // Вычисляем verification_due (date + interval месяцев - 1 день)
    const date = new Date(newDate)
    date.setMonth(date.getMonth() + newInterval)
    date.setDate(date.getDate() - 1)

    // Устанавливаем verification_plan на первое число месяца verification_due
    const planDate = new Date(date.getFullYear(), date.getMonth(), 1)
    formValue.value.verification_plan = planDate.getTime()
  }
})

// Автоматический расчет total_cost: cost_rate * quantity * coefficient
watch([() => formValue.value.cost_rate, () => formValue.value.quantity, () => formValue.value.coefficient],
  ([costRate, quantity, coefficient]) => {
    if (costRate && quantity && coefficient) {
      formValue.value.total_cost = costRate * quantity * coefficient
    } else if (costRate && quantity) {
      formValue.value.total_cost = costRate * quantity
    } else {
      formValue.value.total_cost = null
    }
  }
)

// Функции для получения меток из options
const getEquipmentTypeLabel = (value) => {
  const option = equipmentTypeOptions.find(opt => opt.value === value)
  return option ? option.label : value
}

const getVerificationTypeLabel = (value) => {
  const option = verificationTypeOptions.find(opt => opt.value === value)
  return option ? option.label : value
}

const getVerificationStateLabel = (value) => {
  const option = verificationStateOptions.find(opt => opt.value === value)
  return option ? option.label : value
}

const getStatusLabel = (value) => {
  const option = statusOptions.find(opt => opt.value === value)
  return option ? option.label : value
}

const getDepartmentLabel = (value) => {
  const option = departmentOptions.find(opt => opt.value === value)
  return option ? option.label : value
}

const getResponsiblePersonLabel = (value) => {
  const option = responsiblePersonOptions.find(opt => opt.value === value)
  return option ? option.label : value
}

// Функции для форматирования дат
const formatDisplayDate = (timestamp) => {
  if (!timestamp) return 'Не указано'
  const date = new Date(timestamp)
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}.${month}.${year}`
}

const formatDisplayMonth = (timestamp) => {
  if (!timestamp) return 'Не указано'
  const date = new Date(timestamp)
  const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек']
  return `${months[date.getMonth()]} ${date.getFullYear()}`
}

// Наблюдение за изменением show и equipmentId
watch(() => props.show, (newValue) => {
  if (newValue) {
    isEdit.value = !!props.equipmentId
    if (isEdit.value) {
      loadEquipmentData()
      loadEquipmentFiles()
    } else {
      resetForm()
      equipmentFiles.value = []
    }
  }
})
</script>

<template>
  <n-modal
    :show="show"
    @update:show="handleClose"
    preset="card"
    :title="readOnly ? 'Полная информация по оборудованию и закрепленные файлы' : (isEdit ? 'Редактировать оборудование' : 'Добавить оборудование')"
    style="width: 90%; max-width: 1200px;"
    :segmented="{ content: 'soft', footer: 'soft' }"
  >
    <!-- Текстовый вид для readOnly режима -->
    <div v-if="readOnly" class="info-view">
      <!-- Секция: Оборудование -->
      <div class="info-section">
        <h3>Оборудование</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Наименование:</span>
            <span class="info-value">{{ formValue.equipment_name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Модель:</span>
            <span class="info-value">{{ formValue.equipment_model }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Тип оборудования:</span>
            <span class="info-value">{{ getEquipmentTypeLabel(formValue.equipment_type) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Заводской номер:</span>
            <span class="info-value">{{ formValue.factory_number }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Инвентарный номер:</span>
            <span class="info-value">{{ formValue.inventory_number }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Год выпуска:</span>
            <span class="info-value">{{ formValue.equipment_year }}</span>
          </div>
          <div class="info-item" v-if="formValue.equipment_specs">
            <span class="info-label">Спецификация:</span>
            <span class="info-value">{{ formValue.equipment_specs }}</span>
          </div>
        </div>
      </div>

      <!-- Секция: Верификация -->
      <div class="info-section">
        <h3>Верификация</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Тип верификации:</span>
            <span class="info-value">{{ getVerificationTypeLabel(formValue.verification_type) }}</span>
          </div>
          <div class="info-item" v-if="formValue.registry_number">
            <span class="info-label">Номер в реестре:</span>
            <span class="info-value">{{ formValue.registry_number }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Интервал (месяцы):</span>
            <span class="info-value">{{ formValue.verification_interval }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Дата верификации:</span>
            <span class="info-value">{{ formatDisplayDate(formValue.verification_date) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Действует до:</span>
            <span class="info-value">{{ formatDisplayDate(formValue.verification_due) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">План верификации:</span>
            <span class="info-value">{{ formatDisplayMonth(formValue.verification_plan) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Состояние:</span>
            <span class="info-value">{{ getVerificationStateLabel(formValue.verification_state) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Статус:</span>
            <span class="info-value">{{ getStatusLabel(formValue.status) }}</span>
          </div>
        </div>
      </div>

      <!-- Секция: Ответственные лица -->
      <div class="info-section">
        <h3>Ответственные лица</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Подразделение:</span>
            <span class="info-value">{{ getDepartmentLabel(formValue.department) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Ответственное лицо:</span>
            <span class="info-value">{{ getResponsiblePersonLabel(formValue.responsible_person) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Организация-поверитель:</span>
            <span class="info-value">{{ formValue.verifier_org }}</span>
          </div>
        </div>
      </div>

      <!-- Секция: Финансы (только для админов) -->
      <div class="info-section" v-if="isAdmin">
        <h3>Финансы</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Статья бюджета:</span>
            <span class="info-value">{{ formValue.budget_item || 'Не указано' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Тариф:</span>
            <span class="info-value">{{ formValue.code_rate || 'Не указано' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Стоимость по тарифу (без НДС):</span>
            <span class="info-value">{{ formValue.cost_rate ? formValue.cost_rate.toFixed(2) + ' ₽' : 'Не указано' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Кол-во:</span>
            <span class="info-value">{{ formValue.quantity }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Доп. коэффициент:</span>
            <span class="info-value">{{ formValue.coefficient }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Итоговая стоимость (без НДС):</span>
            <span class="info-value">{{ formValue.total_cost ? formValue.total_cost.toFixed(2) + ' ₽' : 'Не указано' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Номер счета:</span>
            <span class="info-value">{{ formValue.invoice_number || 'Не указано' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Факт оплаты:</span>
            <span class="info-value">{{ formValue.paid_amount ? formValue.paid_amount.toFixed(2) + ' ₽' : 'Не указано' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Дата оплаты:</span>
            <span class="info-value">{{ formatDisplayDate(formValue.payment_date) }}</span>
          </div>
        </div>
      </div>

      <!-- Секция: Прикрепленные файлы -->
      <div class="info-section" v-if="isEdit">
        <h3>Прикрепленные файлы</h3>
        <n-list v-if="equipmentFiles.length > 0" bordered>
          <n-list-item v-for="file in equipmentFiles" :key="file.id">
            <n-thing>
              <template #avatar>
                <n-icon size="24" :component="DocumentIcon" />
              </template>
              <template #header>
                <a
                  href="#"
                  @click.prevent="openFile(file.id, file.file_name)"
                  style="color: #0071BC; text-decoration: none; cursor: pointer;"
                  @mouseover="$event.target.style.textDecoration = 'underline'"
                  @mouseleave="$event.target.style.textDecoration = 'none'"
                >
                  {{ file.file_name }}
                </a>
              </template>
              <template #description>
                {{ formatFileSize(file.file_size) }}
              </template>
              <template #action>
                <n-button size="small" @click="downloadFile(file.id, file.file_name)">
                  Скачать
                </n-button>
              </template>
            </n-thing>
          </n-list-item>
        </n-list>
        <n-text v-else depth="3" style="display: block;">
          Файлы не загружены
        </n-text>
      </div>
    </div>

    <!-- Форма для редактирования (не readOnly) -->
    <n-form v-else :model="formValue" label-placement="top">
      <n-grid :cols="3" :x-gap="24">
        <!-- Секция: Оборудование -->
        <n-grid-item :span="3">
          <h3>Оборудование</h3>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Наименование" required>
            <n-input v-model:value="formValue.equipment_name" placeholder="Введите наименование" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Модель" required>
            <n-input v-model:value="formValue.equipment_model" placeholder="Введите модель" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Тип оборудования" required>
            <n-select v-model:value="formValue.equipment_type" :options="equipmentTypeOptions" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Заводской номер" required>
            <n-input v-model:value="formValue.factory_number" placeholder="Введите заводской номер" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Инвентарный номер" required>
            <n-input v-model:value="formValue.inventory_number" placeholder="Введите инвентарный номер" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Год выпуска" required>
            <n-input-number v-model:value="formValue.equipment_year" :min="1900" :max="2100" style="width: 100%" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item :span="3">
          <n-form-item label="Спецификация">
            <n-input v-model:value="formValue.equipment_specs" type="textarea" placeholder="Введите спецификацию" />
          </n-form-item>
        </n-grid-item>

        <!-- Секция: Верификация -->
        <n-grid-item :span="3">
          <h3>Верификация</h3>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Тип верификации" required>
            <n-select v-model:value="formValue.verification_type" :options="verificationTypeOptions" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Номер в реестре">
            <n-input v-model:value="formValue.registry_number" placeholder="Введите номер" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Интервал (месяцы)" required>
            <n-input-number
              v-model:value="formValue.verification_interval"
              :min="12"
              :step="12"
              @blur="handleIntervalChange(formValue.verification_interval)"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Дата верификации" required>
            <n-date-picker
              v-model:value="formValue.verification_date"
              type="date"
              format="dd/MM/yyyy"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Действует до" required>
            <n-date-picker
              v-model:value="formValue.verification_due"
              type="date"
              format="dd/MM/yyyy"
              disabled
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="План верификации" required>
            <n-date-picker
              v-model:value="formValue.verification_plan"
              type="month"
              format="MMM yyyy"
              style="width: 100%"
            />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Состояние" required>
            <n-select v-model:value="formValue.verification_state" :options="verificationStateOptions" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Статус" required>
            <n-select v-model:value="formValue.status" :options="statusOptions" disabled />
          </n-form-item>
        </n-grid-item>

        <!-- Секция: Ответственность -->
        <n-grid-item :span="3">
          <h3>Ответственные лица</h3>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Подразделение" required>
            <n-select v-model:value="formValue.department" :options="departmentOptions" placeholder="Выберите подразделение" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Ответственное лицо" required>
            <n-select v-model:value="formValue.responsible_person" :options="responsiblePersonOptions" placeholder="Выберите ответственное лицо" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Организация-поверитель" required>
            <n-input v-model:value="formValue.verifier_org" placeholder="Введите организацию" />
          </n-form-item>
        </n-grid-item>

        <!-- Секция: Финансы -->
        <n-grid-item :span="3">
          <h3>Финансы</h3>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Статья бюджета" required>
            <n-input v-model:value="formValue.budget_item" placeholder="Например: 11.03.02.1." />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Тариф">
            <n-input v-model:value="formValue.code_rate" placeholder="Например: 23ПВ0341" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Стоимость по тарифу (без НДС)">
            <n-input-number v-model:value="formValue.cost_rate" :precision="2" :min="0" style="width: 100%" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Кол-во" required>
            <n-input-number v-model:value="formValue.quantity" :min="1" style="width: 100%" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Доп. коэффициент">
            <n-input-number v-model:value="formValue.coefficient" :precision="2" :min="0" style="width: 100%" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Итоговая стоимость (без НДС)">
            <n-input-number
              v-model:value="formValue.total_cost"
              :precision="2"
              :min="0"
              style="width: 100%"
              disabled
              :input-props="{ style: 'background-color: white; color: black;' }"
            />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Номер счета">
            <n-input v-model:value="formValue.invoice_number" placeholder="Введите номер счета" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Факт оплаты">
            <n-input-number v-model:value="formValue.paid_amount" :precision="2" :min="0" style="width: 100%" />
          </n-form-item>
        </n-grid-item>

        <n-grid-item>
          <n-form-item label="Дата оплаты">
            <n-date-picker v-model:value="formValue.payment_date" type="date" style="width: 100%" clearable />
          </n-form-item>
        </n-grid-item>

        <!-- Секция: Файлы (только при редактировании) -->
        <template v-if="isEdit">
          <n-grid-item :span="3">
            <h3>Прикрепленные файлы</h3>
          </n-grid-item>

          <n-grid-item :span="3">
            <!-- Список загруженных файлов -->
            <n-list v-if="equipmentFiles.length > 0" bordered style="margin-bottom: 16px;">
              <n-list-item v-for="file in equipmentFiles" :key="file.id">
                <n-thing>
                  <template #avatar>
                    <n-icon size="24" :component="DocumentIcon" />
                  </template>
                  <template #header>
                    <a
                      href="#"
                      @click.prevent="openFile(file.id, file.file_name)"
                      style="color: #18a058; text-decoration: none; cursor: pointer;"
                      @mouseover="$event.target.style.textDecoration = 'underline'"
                      @mouseleave="$event.target.style.textDecoration = 'none'"
                    >
                      {{ file.file_name }}
                    </a>
                  </template>
                  <template #description>
                    {{ formatFileSize(file.file_size) }}
                  </template>
                  <template #action>
                    <n-space>
                      <n-button size="small" @click="downloadFile(file.id, file.file_name)">
                        Скачать
                      </n-button>
                      <n-button v-if="!readOnly" size="small" type="error" @click="deleteFile(file.id)">
                        <template #icon>
                          <n-icon :component="TrashIcon" />
                        </template>
                        Удалить
                      </n-button>
                    </n-space>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
            <n-text v-else depth="3" style="display: block; margin-bottom: 16px;">
              Файлы не загружены
            </n-text>

            <!-- Загрузчик файлов (скрыт в режиме readOnly) -->
            <n-space v-if="!readOnly" vertical>
              <n-upload
                :custom-request="handleFileUpload"
                :show-file-list="false"
                accept=".pdf,.doc,.docx,.jpg,.jpeg,.png,.xls,.xlsx"
              >
                <n-upload-dragger>
                  <div style="margin-bottom: 12px">
                    <n-icon size="48" :depth="3">
                      <cloud-upload-icon />
                    </n-icon>
                  </div>
                  <n-text style="font-size: 16px">
                    Перетащите файл сюда или нажмите для загрузки
                  </n-text>
                  <n-p depth="3" style="margin: 8px 0 0 0">
                    Допустимые форматы: PDF, DOC, DOCX, JPG, PNG, XLS, XLSX<br />
                    Максимальный размер: 50 МБ
                  </n-p>
                </n-upload-dragger>
              </n-upload>
            </n-space>
          </n-grid-item>
        </template>
      </n-grid>
    </n-form>

    <template #footer>
      <n-space v-if="readOnly" justify="end">
        <n-button @click="handleClose">Закрыть</n-button>
      </n-space>
      <n-space v-else justify="space-between">
        <n-button
          v-if="isEdit"
          type="warning"
          @click="handleArchive"
        >
          <template #icon>
            <n-icon :component="ArchiveIcon" />
          </template>
          В архив
        </n-button>
        <span v-else></span>

        <n-space>
          <n-button @click="handleClose">Отмена</n-button>
          <n-button type="primary" @click="handleSave">
            {{ isEdit ? 'Сохранить' : 'Создать' }}
          </n-button>
        </n-space>
      </n-space>
    </template>
  </n-modal>
</template>

<style scoped>
h3 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid var(--gpn-blue-primary, #0071BC);
  padding-bottom: 8px;
}

/* Стили для текстового вида информации (readOnly режим) */
.info-view {
  font-family: 'PT Astra Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.info-section {
  margin-bottom: 24px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px 24px;
}

.info-item {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-label {
  font-weight: 600;
  color: #666;
  min-width: 200px;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  word-break: break-word;
}
</style>
