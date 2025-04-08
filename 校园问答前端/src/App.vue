<script setup lang="ts">
import { RouterView } from 'vue-router'
import LoginPage from './views/LoginPage.vue'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const router = useRouter()

onMounted(() => {
  if (router.currentRoute.value.name === 'empty') {
    router.push('/login')
  }
})
</script>

<template>
    <RouterView v-if="router.currentRoute.value.name !== 'login'" />
    <LoginPage v-else />
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
}

#app {
  padding: 0;
  height: 100%;
  width: 100%;
}
</style>
