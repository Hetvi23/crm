<template>
  <button
    class="flex h-9 cursor-pointer items-center rounded-lg text-[#050505] duration-200 ease-in-out focus:outline-none transition-colors"
    :class="isActive ? 'bg-[#E7F3FF] font-semibold' : 'hover:bg-[#F2F3F5]'"
    style="font-size: 15px;"
    @click="handleClick"
  >
    <div
      class="flex w-full items-center justify-between duration-300 ease-in-out"
      :class="isCollapsed ? 'ml-[3px] p-1.5' : 'px-3 py-1.5'"
    >
      <div class="flex items-center truncate">
        <Tooltip :text="label" placement="right" :disabled="!isCollapsed">
          <slot name="icon">
            <span class="grid flex-shrink-0 place-items-center">
              <FeatherIcon
                v-if="typeof icon == 'string'"
                :name="icon"
                :class="['size-5', isActive ? 'text-[#1877F2]' : 'text-[#65676B]']"
              />
              <component 
                v-else 
                :is="icon" 
                :class="['size-5', isActive ? 'text-[#1877F2]' : 'text-[#65676B]']" 
              />
            </span>
          </slot>
        </Tooltip>
        <Tooltip
          :text="label"
          placement="right"
          :disabled="isCollapsed"
          :hoverDelay="1.5"
        >
          <span
            class="flex-1 flex-shrink-0 truncate duration-300 ease-in-out"
            :class="[
              isCollapsed
                ? 'ml-0 w-0 overflow-hidden opacity-0'
                : 'ml-3 w-auto opacity-100',
              isActive ? 'text-[#1877F2]' : 'text-[#050505]'
            ]"
            style="font-size: 15px; font-weight: 500;"
          >
            {{ label }}
          </span>
        </Tooltip>
      </div>
      <slot name="right" />
    </div>
  </button>
</template>

<script setup>
import { Tooltip } from 'frappe-ui'
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { isMobileView, mobileSidebarOpened } from '@/composables/settings'

const router = useRouter()
const route = useRoute()

const props = defineProps({
  icon: {
    type: [Object, String, Function],
  },
  label: {
    type: String,
    default: '',
  },
  to: {
    type: [Object, String],
    default: '',
  },
  isCollapsed: {
    type: Boolean,
    default: false,
  },
})

function handleClick() {
  if (!props.to) return
  if (typeof props.to === 'object') {
    router.push(props.to)
  } else {
    router.push({ name: props.to })
  }
  if (isMobileView.value) {
    mobileSidebarOpened.value = false
  }
}

let isActive = computed(() => {
  if (route.query.view) {
    return route.query.view == props.to?.query?.view
  }
  return route.name === props.to
})
</script>
