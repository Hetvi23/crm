<template>
  <Teleport to="#app-header" v-if="showHeader">
    <slot>
      <header class="flex h-14 items-center justify-between py-2 sm:pl-5 pl-3" style="background-color: #FFFFFF; border-bottom: 1px solid #DADDE1;">
        <div class="flex items-center gap-2">
          <slot name="left-header" />
        </div>
        <div class="flex items-center gap-2">
          <slot name="right-header" class="flex items-center gap-2" />
        </div>
      </header>
    </slot>
  </Teleport>
</template>
<script setup>
import { ref, nextTick } from 'vue'

const showHeader = ref(false)

nextTick(() => {
  showHeader.value = true
})
</script>
