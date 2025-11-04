<template>
  <!-- Встроенная форма (без модального окна) -->
  <div v-if="embedded" class="embedded-form">
    <n-form
      ref="formRef"
      :model="formValue"
      :rules="rules"
      size="large"
      label-placement="top"
    >
      <n-form-item label="Логин" path="username">
        <n-input
          v-model:value="formValue.username"
          placeholder="Введите логин"
          :disabled="isLoading"
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <n-icon :component="PersonOutline" />
          </template>
        </n-input>
      </n-form-item>

      <n-form-item label="Пароль" path="password">
        <n-input
          v-model:value="formValue.password"
          type="password"
          show-password-on="click"
          placeholder="Введите пароль"
          :disabled="isLoading"
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <n-icon :component="LockClosedOutline" />
          </template>
        </n-input>
      </n-form-item>

      <!-- Отображение ошибки -->
      <n-alert
        v-if="authError"
        type="error"
        :title="authError"
        closable
        @close="clearError"
        style="margin-bottom: 16px"
      />

      <!-- Кнопка входа -->
      <n-button
        block
        size="large"
        @click="handleLogin"
        :loading="isLoading"
        :disabled="!formValue.username || !formValue.password"
        style="background-color: #333; color: white; border: 1px solid #333; margin-bottom: 12px;"
      >
        Войти
      </n-button>

      <!-- Разделитель -->
      <n-divider style="margin: 12px 0;">или</n-divider>

      <!-- Кнопка Windows SSO -->
      <n-button
        block
        size="large"
        @click="handleWindowsLogin"
        :loading="isLoading"
        type="info"
      >
        Войти через Windows
      </n-button>
    </n-form>
  </div>

  <!-- Модальное окно (стандартный режим) -->
  <n-modal
    v-else
    v-model:show="visible"
    preset="card"
    title="Вход в систему"
    :mask-closable="false"
    style="width: 450px"
  >
    <n-form
      ref="formRef"
      :model="formValue"
      :rules="rules"
      size="large"
      label-placement="top"
    >
      <n-form-item label="Логин" path="username">
        <n-input
          v-model:value="formValue.username"
          placeholder="Введите логин"
          :disabled="isLoading"
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <n-icon :component="PersonOutline" />
          </template>
        </n-input>
      </n-form-item>

      <n-form-item label="Пароль" path="password">
        <n-input
          v-model:value="formValue.password"
          type="password"
          show-password-on="click"
          placeholder="Введите пароль"
          :disabled="isLoading"
          @keyup.enter="handleLogin"
        >
          <template #prefix>
            <n-icon :component="LockClosedOutline" />
          </template>
        </n-input>
      </n-form-item>

      <!-- Отображение ошибки -->
      <n-alert
        v-if="authError"
        type="error"
        :title="authError"
        closable
        @close="clearError"
        style="margin-bottom: 16px"
      />

      <!-- Информационное сообщение -->
      <n-alert
        type="info"
        title="Информация"
        style="margin-bottom: 16px"
      >
        Для входа используйте логин и пароль, выданные администратором.
      </n-alert>
    </n-form>

    <template #footer>
      <n-space vertical style="width: 100%;">
        <!-- Кнопка входа -->
        <n-button
          block
          @click="handleLogin"
          :loading="isLoading"
          :disabled="!formValue.username || !formValue.password"
          style="background-color: #333; color: white; border: 1px solid #333;"
        >
          Войти
        </n-button>

        <!-- Разделитель -->
        <n-divider style="margin: 8px 0;">или</n-divider>

        <!-- Кнопка Windows SSO -->
        <n-button
          block
          @click="handleWindowsLogin"
          :loading="isLoading"
          type="info"
        >
          Войти через Windows
        </n-button>

        <!-- Кнопка отмены -->
        <n-button block @click="handleCancel" :disabled="isLoading">
          Отмена
        </n-button>
      </n-space>
    </template>
  </n-modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import { NModal, NForm, NFormItem, NInput, NButton, NSpace, NIcon, NAlert, NDivider, useMessage } from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { useAuth } from '../composables/useAuth'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  embedded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:show', 'login-success'])

const message = useMessage()
const { login, loginWithWindows, isLoading, authError, clearError } = useAuth()

// Видимость модального окна
const visible = ref(props.show)

// Синхронизация с prop
watch(() => props.show, (newVal) => {
  visible.value = newVal
})

watch(visible, (newVal) => {
  emit('update:show', newVal)
  if (!newVal) {
    // При закрытии очищаем форму и ошибки
    resetForm()
  }
})

// Форма
const formRef = ref(null)
const formValue = ref({
  username: '',
  password: ''
})

// Правила валидации
const rules = {
  username: [
    {
      required: true,
      message: 'Введите логин',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: 'Введите пароль',
      trigger: 'blur'
    }
  ]
}

// Обработчик логина
const handleLogin = async () => {
  try {
    // Валидация формы
    await formRef.value?.validate()

    // Попытка входа
    const result = await login(formValue.value.username, formValue.value.password)

    if (result.success) {
      message.success('Вход выполнен успешно')
      visible.value = false
      emit('login-success')
      resetForm()
    } else {
      // Ошибка уже установлена в composable
      message.error(result.error || 'Ошибка входа')
    }
  } catch (error) {
    // Ошибка валидации формы
    console.error('Ошибка валидации:', error)
  }
}

// Обработчик Windows логина
const handleWindowsLogin = async () => {
  try {
    // Попытка входа через Windows SSO
    const result = await loginWithWindows()

    if (result.success) {
      message.success('Вход через Windows выполнен успешно')
      visible.value = false
      emit('login-success')
      resetForm()
    } else {
      // Ошибка уже установлена в composable
      message.error(result.error || 'Ошибка входа через Windows')
    }
  } catch (error) {
    console.error('Ошибка Windows логина:', error)
  }
}

// Обработчик отмены
const handleCancel = () => {
  visible.value = false
  resetForm()
}

// Сброс формы
const resetForm = () => {
  formValue.value = {
    username: '',
    password: ''
  }
  clearError()
}
</script>

<style scoped>
/* Дополнительные стили при необходимости */
</style>
