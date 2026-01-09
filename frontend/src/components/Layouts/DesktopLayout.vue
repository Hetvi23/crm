<template>
  <div class="flex h-screen w-screen" style="background-color: #F0F2F5;">
    <div class="h-full border-r" style="background-color: #FFFFFF; border-color: #DADDE1;">
      <AppSidebar />
    </div>
    <div class="flex-1 flex flex-col h-full overflow-auto" style="background-color: #F0F2F5;">
      <AppHeader />
      <slot />
    </div>
    <GlobalModals />
  </div>
</template>
<script setup>
import AppSidebar from '@/components/Layouts/AppSidebar.vue'
import AppHeader from '@/components/Layouts/AppHeader.vue'
import GlobalModals from '@/components/Modals/GlobalModals.vue'
</script>
