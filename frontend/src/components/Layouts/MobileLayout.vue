<template>
  <div class="flex h-screen w-screen" style="background-color: #F0F2F5;">
    <MobileSidebar />
    <div class="flex h-full flex-1 flex-col overflow-auto" style="background-color: #F0F2F5;">
      <MobileAppHeader />
      <slot />
    </div>
    <GlobalModals />
  </div>
</template>
<script setup>
import MobileSidebar from '@/components/Mobile/MobileSidebar.vue'
import MobileAppHeader from '@/components/Mobile/MobileAppHeader.vue'
import GlobalModals from '@/components/Modals/GlobalModals.vue'
</script>
