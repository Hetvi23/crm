<template>
  <div class="flex overflow-x-auto h-full" style="padding: 0 16px;">
    <Draggable
      v-if="columns"
      :list="columns"
      item-key="column"
      @end="updateColumn"
      :delay="isTouchScreenDevice() ? 200 : 0"
      class="flex pb-3.5"
      style="gap: 16px;"
    >
      <template #item="{ element: column }">
        <div
          v-if="!column.column.delete"
          :class="['flex flex-col gap-2.5 min-w-72 w-72 rounded-lg p-3', parseColorBg(column.column.color || colors[0])]"
          style="border: 1px solid #DADDE1; flex-shrink: 0;"
        >
          <div class="flex gap-2 items-center group justify-between">
            <div class="flex items-center text-base">
              <Popover>
                <template #target="{ togglePopover }">
                  <Button
                    variant="ghost"
                    size="sm"
                    class="hover:!bg-surface-gray-2"
                    @click="togglePopover"
                  >
                    <IndicatorIcon :class="parseColor(column.column.color)" />
                  </Button>
                </template>
                <template #body>
                  <div
                    class="flex flex-col gap-3 px-3 py-2.5 min-w-40 rounded-lg bg-surface-modal shadow-2xl ring-1 ring-black ring-opacity-5 focus:outline-none"
                  >
                    <div class="flex gap-1">
                      <Button
                        variant="ghost"
                        v-for="color in colors"
                        :key="color"
                        @click="() => (column.column.color = color)"
                      >
                        <IndicatorIcon :class="parseColor(color)" />
                      </Button>
                    </div>
                    <div class="flex flex-row-reverse">
                      <Button
                        variant="solid"
                        :label="__('Apply')"
                        @click="updateColumn"
                      />
                    </div>
                  </div>
                </template>
              </Popover>
              <div class="flex items-center gap-2">
                <div style="color: #050505; font-size: 15px; font-weight: 600;">{{ column.column.name }}</div>
                <div 
                  class="flex items-center justify-center rounded-full px-2 py-0.5"
                  style="background-color: #E4E6EA; color: #65676B; font-size: 12px; font-weight: 600; min-width: 20px; height: 20px;"
                >
                  {{ getColumnCount(column) }}
                </div>
              </div>
            </div>
            <div class="flex">
              <Dropdown :options="actions(column)">
                <template #default>
                  <Button
                    class="hidden group-hover:flex"
                    icon="more-horizontal"
                    variant="ghost"
                  />
                </template>
              </Dropdown>
              <Button
                icon="plus"
                variant="ghost"
                @click="options.onNewClick(column)"
              />
            </div>
          </div>
          <div 
            class="overflow-y-auto flex flex-col gap-2 h-full"
            :ref="el => setColumnScrollRef(el, column.column.name)"
            @scroll="handleColumnScroll($event, column.column.name, column)"
            style="scroll-behavior: smooth;"
          >
            <Draggable
              :list="column.data"
              group="fields"
              item-key="name"
              class="flex flex-col gap-3.5 flex-1"
              @end="updateColumn"
              :delay="isTouchScreenDevice() ? 200 : 0"
              :data-column="column.column.name"
            >
              <template #item="{ element: fields }">
                <component
                  :is="options.onClick ? 'div' : (options.getRoute ? 'router-link' : 'div')"
                  class="rounded-lg border flex flex-col cursor-pointer hover:shadow-md transition-all"
                  style="background-color: #FFFFFF; border-color: #DADDE1; padding: 12px; margin-bottom: 8px;"
                  :data-name="fields.name"
                  v-bind="{
                    to: options.onClick ? undefined : (options.getRoute ? options.getRoute(fields) : undefined),
                    onClick: options.onClick
                      ? (e) => {
                          e.preventDefault()
                          e.stopPropagation()
                          options.onClick(fields)
                        }
                      : undefined,
                  }"
                >
                  <!-- Title Section - Better formatted like Meta -->
                  <div class="mb-3">
                    <slot
                      name="title"
                      v-bind="{ fields, titleField, itemName: fields.name }"
                    >
                      <div class="flex items-center gap-2">
                        <div v-if="fields[titleField]" class="font-semibold" style="color: #050505; font-size: 15px; line-height: 1.4;">
                          {{ typeof fields[titleField] === 'object' ? fields[titleField].label : fields[titleField] }}
                        </div>
                        <div v-else style="color: #65676B; font-size: 15px;">
                          {{ __('No Title') }}
                        </div>
                      </div>
                    </slot>
                  </div>

                  <!-- Fields Section - Better formatted with icons and spacing like Meta -->
                  <div class="flex flex-col gap-2.5 mb-3">
                    <template v-for="value in column.fields" :key="value">
                      <slot
                        name="fields"
                        v-bind="{
                          fields,
                          fieldName: value,
                          itemName: fields.name,
                        }"
                      >
                        <!-- Skip city in regular fields loop - we'll show it separately with icon -->
                        <div v-if="fields[value] && value !== titleField && value !== 'city'" class="flex items-start gap-2">
                          <div class="text-sm leading-5" style="color: #050505; min-width: 0; flex: 1; word-wrap: break-word;">
                            {{ typeof fields[value] === 'object' ? (fields[value].label || fields[value]) : fields[value] }}
                          </div>
                        </div>
                      </slot>
                    </template>
                    <!-- Always show city if available, with map-pin icon -->
                    <div v-if="getCityValue(fields.city) && titleField !== 'city'" class="flex items-center gap-1.5 pt-1">
                      <slot
                        name="fields"
                        v-bind="{
                          fields,
                          fieldName: 'city',
                          itemName: fields.name,
                        }"
                      >
                        <FeatherIcon name="map-pin" class="h-3.5 w-3.5 flex-shrink-0" style="color: #1877F2;" />
                        <span class="text-sm leading-5" style="color: #65676B; font-weight: 500;">
                          {{ getCityValue(fields.city) }}
                        </span>
                      </slot>
                    </div>
                  </div>

                  <!-- Actions Section -->
                  <div class="border-t pt-2.5 mt-2" style="border-color: #E4E6EA;">
                    <slot name="actions" v-bind="{ itemName: fields.name, currentColumn: column.column.name }">
                      <div class="flex gap-2 items-center justify-between">
                        <div></div>
                        <Button icon="plus" variant="ghost" @click.stop.prevent />
                      </div>
                    </slot>
                  </div>
                </component>
              </template>
            </Draggable>
            <!-- Infinite scroll trigger element - hidden but used for intersection observer -->
            <div
              v-if="column.column.count < column.column.all_count"
              :ref="el => setLoadMoreRef(el, column.column.name)"
              class="h-1"
              style="min-height: 1px;"
            ></div>
            <!-- Loading indicator -->
            <div
              v-if="loadingColumns[column.column.name] && column.column.count < column.column.all_count"
              class="flex items-center justify-center py-3"
            >
              <LoadingIndicator class="w-4 h-4 text-ink-gray-6" />
            </div>
          </div>
        </div>
      </template>
    </Draggable>
    <div v-if="deletedColumns.length" class="shrink-0 min-w-64">
      <Autocomplete
        value=""
        :options="deletedColumns"
        @change="(e) => addColumn(e)"
      >
        <template #target="{ togglePopover }">
          <Button
            class="w-full mt-2.5 mb-1 mr-5"
            :label="__('Add Column')"
            iconLeft="plus"
            @click="togglePopover()"
          />
        </template>
      </Autocomplete>
    </div>
  </div>
</template>
<script setup>
import Autocomplete from '@/components/frappe-ui/Autocomplete.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import { isTouchScreenDevice, colors, parseColor, parseColorBg } from '@/utils'
import Draggable from 'vuedraggable'
import { Dropdown, Popover, FeatherIcon, LoadingIndicator } from 'frappe-ui'
import { computed, ref, onMounted, onUnmounted, nextTick, watch } from 'vue'

const props = defineProps({
  options: {
    type: Object,
    default: () => ({
      getRoute: null,
      onClick: null,
      onNewClick: null,
    }),
  },
})

const emit = defineEmits(['update', 'loadMore'])

const kanban = defineModel()

const titleField = computed(() => {
  return kanban.value?.data?.title_field
})

const columns = computed(() => {
  if (!kanban.value?.data?.data || kanban.value.data.view_type != 'kanban')
    return []
  let _columns = kanban.value.data.data

  let has_color = _columns.some((column) => column.column?.color)
  if (!has_color) {
    _columns.forEach((column, i) => {
      column.column['color'] = colors[i % colors.length]
    })
  }
  return _columns
})

const deletedColumns = computed(() => {
  return columns.value
    .filter((col) => col.column['delete'])
    .map((col) => {
      return { label: col.column.name, value: col.column.name }
    })
})

function actions(column) {
  return [
    {
      group: __('Options'),
      hideLabel: true,
      items: [
        {
          label: __('Delete'),
          icon: 'trash-2',
          onClick: () => {
            column.column['delete'] = true
            updateColumn()
          },
        },
      ],
    },
  ]
}

function addColumn(e) {
  let column = columns.value.find((col) => col.column.name == e.value)
  column.column['delete'] = false
  updateColumn()
}

function updateColumn(d) {
  let toColumn = d?.to?.dataset.column
  let fromColumn = d?.from?.dataset.column
  let itemName = d?.item?.dataset.name

  let _columns = []
  columns.value.forEach((col) => {
    col.column['order'] = col.data.map((d) => d.name)
    if (col.column.page_length) {
      delete col.column.page_length
    }
    _columns.push(col.column)
  })

  let data = { kanban_columns: _columns }

  if (toColumn != fromColumn) {
    data = { item: itemName, to: toColumn, kanban_columns: _columns }
  }

  emit('update', data)
}

function getCityValue(city) {
  if (!city) return ''
  if (typeof city === 'object') {
    const value = city.label || city.value || city
    return value && String(value).trim() ? String(value).trim() : ''
  }
  return city && String(city).trim() ? String(city).trim() : ''
}

function getColumnCount(column) {
  // Return the total count of leads in this column
  // Prefer all_count (total leads in this status), fallback to count (currently loaded), then data length
  if (column.column.all_count !== undefined && column.column.all_count !== null) {
    return column.column.all_count
  }
  if (column.column.count !== undefined && column.column.count !== null) {
    return column.column.count
  }
  return column.data?.length || 0
}

// Infinite scroll implementation
const loadingColumns = ref({})
const columnScrollRefs = ref({})
const loadMoreRefs = ref({})
const intersectionObservers = ref({})
const loadingStates = ref({})
const checkIntervals = ref({})

function setColumnScrollRef(el, columnName) {
  if (el) {
    columnScrollRefs.value[columnName] = el
  }
}

function setLoadMoreRef(el, columnName) {
  if (el) {
    loadMoreRefs.value[columnName] = el
    // Setup intersection observer for this column
    nextTick(() => {
      setupIntersectionObserver(columnName)
    })
  }
}

function setupIntersectionObserver(columnName) {
  // Clean up existing observer
  if (intersectionObservers.value[columnName]) {
    intersectionObservers.value[columnName].disconnect()
    delete intersectionObservers.value[columnName]
  }

  const loadMoreElement = loadMoreRefs.value[columnName]
  const scrollContainer = columnScrollRefs.value[columnName]
  
  if (!loadMoreElement || !scrollContainer) return

  // Create new intersection observer with document as root for better reliability
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !loadingStates.value[columnName]) {
          const column = columns.value.find((col) => col.column.name === columnName)
          if (column && column.column.count < column.column.all_count) {
            loadMore(columnName)
          }
        }
      })
    },
    {
      root: scrollContainer,
      rootMargin: '200px', // Start loading 200px before reaching the bottom
      threshold: 0.01,
    }
  )

  observer.observe(loadMoreElement)
  intersectionObservers.value[columnName] = observer
}

const scrollTimeouts = ref({})
const lastScrollPositions = ref({})

function handleColumnScroll(event, columnName, column) {
  // Throttle scroll events
  if (scrollTimeouts.value[columnName]) {
    clearTimeout(scrollTimeouts.value[columnName])
  }
  
  scrollTimeouts.value[columnName] = setTimeout(() => {
    // Primary scroll detection - more reliable than intersection observer
    const scrollElement = event.target
    const scrollTop = scrollElement.scrollTop
    const scrollHeight = scrollElement.scrollHeight
    const clientHeight = scrollElement.clientHeight
    const scrollBottom = scrollHeight - scrollTop - clientHeight
    
    // Only trigger if scrolling down and near bottom
    const lastPosition = lastScrollPositions.value[columnName] || 0
    const isScrollingDown = scrollTop > lastPosition
    lastScrollPositions.value[columnName] = scrollTop
    
    // Load more when within 400px of bottom and scrolling down
    if (isScrollingDown && scrollBottom < 400 && !loadingStates.value[columnName]) {
      if (column.column.count < column.column.all_count) {
        loadMore(columnName)
      }
    }
  }, 200)
}

function loadMore(columnName) {
  if (loadingStates.value[columnName]) return
  
  // Clear any existing interval for this column
  if (checkIntervals.value[columnName]) {
    clearInterval(checkIntervals.value[columnName])
  }
  
  loadingStates.value[columnName] = true
  loadingColumns.value[columnName] = true
  
  // Store the current count before loading
  const column = columns.value.find((col) => col.column.name === columnName)
  const beforeCount = column?.data?.length || 0
  
  emit('loadMore', columnName)
  
  // Reset loading state after data loads (check every 500ms)
  checkIntervals.value[columnName] = setInterval(() => {
    const updatedColumn = columns.value.find((col) => col.column.name === columnName)
    const afterCount = updatedColumn?.data?.length || 0
    
    if (afterCount > beforeCount || !updatedColumn || updatedColumn.column.count >= updatedColumn.column.all_count) {
      loadingStates.value[columnName] = false
      loadingColumns.value[columnName] = false
      if (checkIntervals.value[columnName]) {
        clearInterval(checkIntervals.value[columnName])
        delete checkIntervals.value[columnName]
      }
      
      // Re-setup observer after data loads
      nextTick(() => {
        setupIntersectionObserver(columnName)
      })
    }
  }, 500)
  
  // Fallback: Reset loading state after 10 seconds
  setTimeout(() => {
    if (loadingStates.value[columnName]) {
      loadingStates.value[columnName] = false
      loadingColumns.value[columnName] = false
      if (checkIntervals.value[columnName]) {
        clearInterval(checkIntervals.value[columnName])
        delete checkIntervals.value[columnName]
      }
    }
  }, 10000)
}

// Watch for column data changes to reset loading state
const previousColumnCounts = ref({})

// Simplified watch - just track data for reference
watch(
  () => kanban.value?.data?.data,
  (newData) => {
    if (!newData) return
    // Data changes are handled in loadMore function via interval checking
  },
  { deep: true }
)

onMounted(() => {
  // Setup observers for all columns after mount
  nextTick(() => {
    columns.value.forEach((column) => {
      if (loadMoreRefs.value[column.column.name]) {
        setupIntersectionObserver(column.column.name)
      }
    })
  })
})

onUnmounted(() => {
  // Clean up all observers
  Object.values(intersectionObservers.value).forEach((observer) => {
    if (observer) observer.disconnect()
  })
  // Clean up all intervals
  Object.values(checkIntervals.value).forEach((interval) => {
    if (interval) clearInterval(interval)
  })
})
</script>
