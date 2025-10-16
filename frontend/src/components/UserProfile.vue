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
        <template #icon>
          <n-icon :component="PersonCircleOutline" size="24" />
        </template>
        <n-space :size="4" align="center" style="margin-left: 8px">
          <span style="font-weight: 500">{{ currentUser?.full_name }}</span>
          <n-tag
            :type="currentUser?.role === 'admin' ? 'success' : 'info'"
            size="small"
            :bordered="false"
            round
          >
            {{ roleLabel }}
          </n-tag>
          <span style="color: #999; font-size: 13px">{{ currentUser?.department }}</span>
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
import { PersonCircleOutline, LogInOutline, LogOutOutline, InformationCircleOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth'

defineEmits(['show-login'])

const dialog = useDialog()
const message = useMessage()
const { currentUser, isAuthenticated, isLoading, logout } = useAuth()

// Название роли
const roleLabel = computed(() => {
  return currentUser.value?.role === 'admin' ? 'Администратор' : 'Лаборант'
})

// Опции выпадающего меню
const dropdownOptions = computed(() => [
  {
    label: 'Информация о профиле',
    key: 'profile',
    icon: () => h(NIcon, { component: InformationCircleOutline })
  },
  {
    type: 'divider',
    key: 'd1'
  },
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
  } else if (key === 'profile') {
    showProfileInfo()
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

// Показ информации о профиле
const showProfileInfo = () => {
  dialog.info({
    title: 'Профиль пользователя',
    content: () => {
      return h('div', { style: 'line-height: 1.8' }, [
        h('p', [h('strong', 'ФИО: '), currentUser.value?.full_name]),
        h('p', [h('strong', 'Логин: '), currentUser.value?.username]),
        h('p', [h('strong', 'Подразделение: '), currentUser.value?.department]),
        h('p', [
          h('strong', 'Роль: '),
          currentUser.value?.role === 'admin' ? 'Администратор' : 'Лаборант'
        ]),
        h('p', [
          h('strong', 'Статус: '),
          currentUser.value?.is_active ? 'Активен' : 'Деактивирован'
        ]),
        h('p', { style: 'color: #999; font-size: 13px; margin-top: 12px' }, [
          'Дата создания: ',
          new Date(currentUser.value?.created_at).toLocaleString('ru-RU')
        ])
      ])
    },
    positiveText: 'OK'
  })
}
</script>

<style scoped>
/* Дополнительные стили при необходимости */
</style>
