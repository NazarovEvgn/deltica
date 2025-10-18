<template>
  <n-space align="center" :size="12">
    <!-- Информация о пользователе -->
    <n-dropdown
      v-if="isAuthenticated"
      trigger="hover"
      :options="dropdownOptions"
      @select="handleSelect"
    >
      <n-button text style="font-size: 14px">
        <n-space :size="8" align="center">
          <span style="color: #999; font-size: 13px">{{ formattedDepartment }}</span>
          <span style="font-weight: 500">{{ formattedName }}</span>
          <n-icon :component="PersonCircleOutline" size="24" />
        </n-space>
      </n-button>
    </n-dropdown>

    <!-- Кнопка входа (если не авторизован) -->
    <n-button
      v-else
      type="primary"
      @click="$emit('show-login')"
      :loading="isLoading"
    >
      <template #icon>
        <n-icon :component="LogInOutline" />
      </template>
      Войти
    </n-button>
  </n-space>
</template>

<script setup>
import { computed, h } from 'vue'
import { NButton, NSpace, NIcon, NTag, NDropdown, useDialog, useMessage } from 'naive-ui'
import { PersonCircleOutline, LogInOutline, LogOutOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth'

defineEmits(['show-login'])

const dialog = useDialog()
const message = useMessage()
const { currentUser, isAuthenticated, isLoading, logout } = useAuth()

// Форматирование ФИО в формат "Фамилия И."
const formattedName = computed(() => {
  if (!currentUser.value?.full_name) return ''

  const nameParts = currentUser.value.full_name.trim().split(' ')
  if (nameParts.length === 0) return ''

  const lastName = nameParts[0]
  const firstName = nameParts[1]

  if (!firstName) return lastName

  return `${lastName} ${firstName.charAt(0)}.`
})

// Форматирование department (техническое значение -> красивое название)
const formattedDepartment = computed(() => {
  const departmentMap = {
    'gruppa_sm': 'Группа СМ',
    'gtl': 'ГТЛ',
    'lbr': 'ЛБР',
    'ltr': 'ЛТР',
    'lhaiei': 'ЛХАиЭИ',
    'ogmk': 'ОГМК',
    'oii': 'ОИИ',
    'smtsik': 'СМТСиК',
    'soii': 'СОИИ',
    'to': 'ТО',
    'ts': 'ТС',
    'es': 'ЭС'
  }
  const dept = currentUser.value?.department || ''
  return departmentMap[dept] || dept
})

// Название роли
const roleLabel = computed(() => {
  return currentUser.value?.role === 'admin' ? 'Администратор' : 'Лаборант'
})

// Опции выпадающего меню
const dropdownOptions = computed(() => [
  {
    label: 'Выйти',
    key: 'logout',
    icon: () => h(NIcon, { component: LogOutOutline })
  }
])

// Обработчик выбора пункта меню
const handleSelect = (key) => {
  if (key === 'logout') {
    handleLogout()
  }
}

// Выход из системы
const handleLogout = () => {
  dialog.warning({
    title: 'Выход из системы',
    content: 'Вы уверены, что хотите выйти?',
    positiveText: 'Выйти',
    negativeText: 'Отмена',
    onPositiveClick: () => {
      logout()
      message.info('Вы вышли из системы')
    }
  })
}
</script>

<style scoped>
/* Дополнительные стили при необходимости */
</style>
