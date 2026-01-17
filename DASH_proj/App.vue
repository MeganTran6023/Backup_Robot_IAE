<template>
  <div class="container">
    <h2>Python Camera Stream</h2>
    <img
      :src="streamUrl"
      alt="Camera Stream"
      class="camera"
    />
  </div>
</template>

<script setup lang="ts">
const streamUrl = 'http://192.168.1.209:5000/video'
</script>

<style scoped>
.camera {
  width: 100%;
  max-width: 640px;
  border-radius: 8px;
  border: 1px solid #ccc;
}
</style>
