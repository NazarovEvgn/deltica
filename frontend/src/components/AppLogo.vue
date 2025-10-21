<template>
  <div class="app-logo">
    <img src="/favicon.png" alt="Deltica Logo" class="logo-image" />
    <span class="app-name">Deltica</span>
  </div>
</template>

<script setup>
// Компонент логотипа приложения
</script>

<style scoped>
.app-logo {
  display: flex;
  align-items: center;
  gap: 6px;
}

.logo-image {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.app-name {
  font-size: 20px;
  font-weight: 700;
  color: #333333;
  letter-spacing: 0.5px;
}
</style>
