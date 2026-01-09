<template>
  <div class="flex items-center">
    <router-link
      :to="{ name: routeName }"
      class="px-0.5 py-1 font-semibold focus:outline-none transition-colors"
      style="font-size: 20px; color: #050505;"
      :class="[
        viewControls
          ? 'hover:text-[#1877F2]'
          : '',
      ]"
    >
      {{ __(routeName) }}
    </router-link>
    <span
      v-if="viewControls"
      class="mx-1 text-base"
      style="color: #65676B;"
      aria-hidden="true"
    >
      /
    </span>
    <Dropdown
      v-if="viewControls"
      :options="viewControls.viewsDropdownOptions"
    >
      <template #default="{ open }">
        <Button
          variant="ghost"
          class="text-lg font-medium text-nowrap"
          :label="__(viewControls.currentView.label)"
          :iconRight="open ? 'chevron-up' : 'chevron-down'"
        >
          <template #prefix>
            <Icon :icon="viewControls.currentView.icon" class="h-4" />
          </template>
        </Button>
      </template>
      <template #item="{ item, close }">
        <button
          class="group flex text-ink-gray-6 gap-4 h-7 w-full justify-between items-center rounded px-2 text-base hover:bg-surface-gray-3"
          @click="item.onClick"
        >
          <div class="flex items-center">
            <FeatherIcon
              v-if="item.icon && typeof item.icon === 'string'"
              :name="item.icon"
              class="mr-2 h-4 w-4 flex-shrink-0 text-ink-gray-7"
              aria-hidden="true"
            />
            <component
              class="mr-2 h-4 w-4 flex-shrink-0 text-ink-gray-7"
              v-else-if="item.icon"
              :is="item.icon"
            />
            <span class="whitespace-nowrap">
              {{ item.label }}
            </span>
          </div>
          <div
            v-if="item.name"
            class="flex flex-row-reverse gap-2 items-center min-w-11"
          >
            <Dropdown
              placement="right-start"
              :options="viewControls.viewActions(item, close)"
            >
              <template #default>
                <Button
                  variant="ghost"
                  class="!size-5 hidden group-hover:block"
                  icon="more-horizontal"
                  @click.stop
                />
              </template>
            </Dropdown>
            <FeatherIcon
              v-if="isCurrentView(item)"
              name="check"
              class="size-4 text-ink-gray-7"
            />
          </div>
        </button>
      </template>
    </Dropdown>
  </div>
</template>
<script setup>
import Icon from '@/components/Icon.vue'
import { Dropdown } from 'frappe-ui'

const props = defineProps({
  routeName: {
    type: String,
    required: true,
  },
})

const viewControls = defineModel()

const isCurrentView = (item) => {
  return item.name === viewControls.value.currentView.name
}
</script>
