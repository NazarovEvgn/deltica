<template>
  <div class="app-logo" @click="handleClick">
    <img src="/favicon.png" alt="Deltica Logo" class="logo-image" />
    <span class="app-name">Deltica</span>
  </div>
</template>

<script setup>
// Компонент логотипа приложения
const emit = defineEmits(['click'])

const handleClick = () => {
  emit('click')
}
</script>

<style scoped>
.app-logo {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
}

.app-logo:hover {
  opacity: 0.8;
}

.logo-image {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.app-name {
  font-size: 20px;
  font-weight: 900;
  color: #333333;
  letter-spacing: 0.5px;
}
</style>
