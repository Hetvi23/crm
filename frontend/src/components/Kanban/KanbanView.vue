<template>
  <!-- Kanban Board Container - Meta Style -->
  <div class="kanban-board-container flex overflow-x-auto h-full" style="padding: 16px; background-color: #F0F2F5; gap: 16px;">
    <Draggable
      v-if="columns"
      :list="columns"
      item-key="column"
      @end="updateColumn"
      :delay="isTouchScreenDevice() ? 200 : 0"
      class="flex pb-3.5 h-full"
      style="gap: 16px; align-items: flex-start;"
    >
      <template #item="{ element: column }">
        <div
          v-if="!column.column.delete"
          :class="['flex flex-col min-w-[272px] w-[272px] rounded-lg kanban-column', parseColorBg(column.column.color || colors[0])]"
          style="background-color: #FFFFFF; border: 1px solid #E4E6EA; flex-shrink: 0; padding: 12px; max-height: calc(100vh - 200px); box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);"
        >
          <!-- Column Header - Meta Style -->
          <div class="flex gap-2 items-center group justify-between mb-3">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <Popover>
                <template #target="{ togglePopover }">
                  <Button
                    variant="ghost"
                    size="sm"
                    class="hover:!bg-surface-gray-2 p-1"
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
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <h3 class="kanban-column-header truncate">
                  {{ column.column.name }}
                </h3>
                <div class="kanban-column-count flex items-center justify-center rounded-full px-1.5 py-0.5 flex-shrink-0" style="min-width: 20px; height: 20px;">
                  {{ getColumnCount(column) }}
                </div>
              </div>
            </div>
            <div class="flex items-center gap-1 flex-shrink-0">
              <Dropdown :options="actions(column)">
                <template #default>
                  <Button
                    class="hidden group-hover:flex opacity-60 hover:opacity-100 transition-opacity hover:bg-[#F0F2F5]"
                    icon="more-horizontal"
                    variant="ghost"
                    size="sm"
                    style="padding: 6px; font-size: 15px; color: #65676B; border-radius: 6px;"
                  />
                </template>
              </Dropdown>
              <Button
                icon="plus"
                variant="ghost"
                size="sm"
                @click="options.onNewClick(column)"
                class="opacity-60 hover:opacity-100 transition-opacity hover:bg-[#F0F2F5]"
                style="padding: 6px; font-size: 15px; color: #65676B; border-radius: 6px;"
              />
            </div>
          </div>
          <!-- Column Content Area - Meta Style -->
          <div 
            class="overflow-y-auto flex flex-col flex-1 min-h-0 relative"
            :ref="el => setColumnScrollRef(el, column.column.name)"
            style="scroll-behavior: smooth;"
          >
            <!-- Empty State for Column - Meta Style (shown only when truly empty) -->
            <div
              v-if="(!column.data || column.data.length === 0) && (getColumnCount(column) === 0 || column.column.count === 0)"
              class="absolute inset-0 flex flex-col items-center justify-center py-12 px-4 pointer-events-none z-0"
              style="min-height: 200px;"
            >
              <div class="flex flex-col items-center gap-4 max-w-[240px] text-center">
                <!-- Placeholder illustration - Meta Style (3 stacked cards) -->
                <div class="flex gap-1.5 opacity-30 mb-2">
                  <div class="w-14 h-18 rounded-lg" style="background-color: #E4E6EA; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);"></div>
                  <div class="w-14 h-18 rounded-lg mt-1" style="background-color: #E4E6EA; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);"></div>
                  <div class="w-14 h-18 rounded-lg mt-2" style="background-color: #E4E6EA; box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);"></div>
                </div>
                <div class="flex flex-col gap-2 px-2">
                  <div class="kanban-empty-state-title">
                    {{ __('No {0} leads', [column.column.name]) }}
                  </div>
                  <div class="kanban-empty-state-description">
                    {{ __('Move leads to this stage if they have a strong interest in your products or services and are probably a good fit for your business.') }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Cards List - Meta Style (Always rendered to enable drop zone, even when empty) -->
            <div 
              class="flex-1 min-h-[200px] relative z-10"
              :data-column="column.column.name"
            >
              <Draggable
                :list="column.data || []"
                group="fields"
                item-key="name"
                class="flex flex-col w-full h-full"
                style="gap: 12px; min-height: 200px;"
                @end="updateColumn"
                :delay="isTouchScreenDevice() ? 200 : 0"
                :data-column="column.column.name"
                :force-fallback="false"
                :fallback-on-body="false"
                :empty-insert-threshold="50"
              >
              <template #item="{ element: fields }">
                <component
                  :is="options.onClick ? 'div' : (options.getRoute ? 'router-link' : 'div')"
                  class="kanban-card rounded-lg border flex flex-col cursor-pointer transition-all hover:shadow-sm active:scale-[0.98]"
                  style="background-color: #FFFFFF; border-color: #E4E6EA; padding: 12px; margin-bottom: 0;"
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
                  <!-- Title Section - Meta Style -->
                  <div class="mb-2">
                    <slot
                      name="title"
                      v-bind="{ fields, titleField, itemName: fields.name }"
                    >
                      <div class="flex items-center gap-2">
                        <div 
                          v-if="fields[titleField]" 
                          class="kanban-card-title truncate"
                          style="color: #050505; font-size: 15px; font-weight: 600; line-height: 1.3333; letter-spacing: -0.01em;"
                        >
                          {{ typeof fields[titleField] === 'object' ? fields[titleField].label : fields[titleField] }}
                        </div>
                        <div 
                          v-else 
                          class="truncate kanban-card-field-secondary"
                          style="color: #65676B; font-size: 15px; font-weight: 400; line-height: 1.3333;"
                        >
                          {{ __('No Title') }}
                        </div>
                      </div>
                    </slot>
                  </div>

                  <!-- Fields Section - Meta Style with consistent typography -->
                  <div class="flex flex-col mb-2" style="gap: 8px;">
                    <template v-for="value in column.fields" :key="value">
                      <slot
                        name="fields"
                        v-bind="{
                          fields,
                          fieldName: value,
                          itemName: fields.name,
                        }"
                      >
                        <!-- Default display for fields not handled by slot -->
                        <div 
                          v-if="fields[value] && value !== titleField" 
                          class="flex items-start gap-2"
                        >
                          <div 
                            class="flex-1 min-w-0 kanban-card-field"
                            style="color: #050505; font-size: 15px; font-weight: 400; line-height: 1.3333; word-wrap: break-word;"
                          >
                            {{ typeof fields[value] === 'object' ? (fields[value].label || fields[value]) : fields[value] }}
                          </div>
                        </div>
                      </slot>
                    </template>
                  </div>

                  <!-- Actions Section - Meta Style -->
                  <div class="border-t pt-2.5 mt-auto" style="border-color: #E4E6EA; margin-top: 8px;">
                    <slot name="actions" v-bind="{ itemName: fields.name, currentColumn: column.column.name }">
                      <div class="flex gap-2 items-center justify-between">
                        <div></div>
                        <Button 
                          icon="plus" 
                          variant="ghost" 
                          size="sm"
                          @click.stop.prevent 
                          class="opacity-60 hover:opacity-100 transition-opacity"
                          style="padding: 4px; font-size: 15px; color: #65676B;"
                        />
                      </div>
                    </slot>
                  </div>
                </component>
              </template>
              </Draggable>
            </div>
            
            <!-- Infinite Scroll Sentinel and Loading Indicator -->
            <div class="flex flex-col items-center justify-center py-3 pt-2 gap-2">
              <!-- Loading indicator when loading more -->
              <div
                v-if="loadingColumns[column.column.name]"
                class="flex flex-col items-center gap-2"
              >
                <LoadingIndicator size="sm" />
                <div
                  class="text-center"
                  style="color: #65676B; font-size: 13px; font-weight: 400; line-height: 1.3846;"
                >
                  {{ __('Loading...') }}
                </div>
              </div>

              <!-- Show count information when not loading and has more items -->
              <div
                v-else-if="column.column.all_count && (column.column.count || column.data?.length || 0) < column.column.all_count"
                class="text-center"
                style="color: #65676B; font-size: 13px; font-weight: 400; line-height: 1.3846;"
              >
                {{ __('Showing {0} of {1}', [
                  column.column.count || column.data?.length || 0,
                  column.column.all_count || 0
                ]) }}
              </div>

              <!-- Show message when all items are loaded -->
              <div
                v-else-if="column.column.all_count && (column.column.count || column.data?.length || 0) >= column.column.all_count && column.column.all_count > 0"
                class="text-center"
                style="color: #65676B; font-size: 13px; font-weight: 400; line-height: 1.3846;"
              >
                {{ __('All {0} items loaded', [column.column.all_count]) }}
              </div>

              <!-- Infinite Scroll Sentinel - invisible element at bottom to trigger loading -->
              <div
                v-if="column.column.all_count && (column.column.count || column.data?.length || 0) < column.column.all_count && !loadingColumns[column.column.name]"
                :ref="el => setSentinelRef(el, column.column.name)"
                class="h-1 w-full"
                style="min-height: 1px;"
              ></div>
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
import { Dropdown, Popover, FeatherIcon, LoadingIndicator, Button } from 'frappe-ui'
import { computed, ref, watch, onUnmounted, nextTick } from 'vue'

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

  // Ensure each column has a data array initialized (even if empty) for drag and drop to work
  _columns.forEach((column) => {
    if (!column.data || !Array.isArray(column.data)) {
      column.data = []
    }
  })

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
    // Ensure data exists and is an array before mapping
    col.column['order'] = (col.data && Array.isArray(col.data)) ? col.data.map((d) => d.name) : []
    if (col.column.page_length) {
      delete col.column.page_length
    }
    _columns.push(col.column)
  })

  let data = { kanban_columns: _columns }

  if (toColumn != fromColumn && itemName) {
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

// Infinite Scroll implementation
const loadingColumns = ref({})
const previousColumnData = ref({})
const loadingTimeouts = ref({})
const columnScrollRefs = ref({})
const savedScrollPositions = ref({})
const mutationObservers = ref({})
const scrollRestoreIntervals = ref({})
const sentinelRefs = ref({})
const intersectionObservers = ref({})

function setColumnScrollRef(el, columnName) {
  if (el) {
    columnScrollRefs.value[columnName] = el
    // Set up intersection observer for infinite scroll once the scroll container is available
    nextTick(() => {
      setupIntersectionObserver(columnName)
    })
  } else {
    // Clean up observers when element is removed
    if (mutationObservers.value[columnName]) {
      mutationObservers.value[columnName].disconnect()
      delete mutationObservers.value[columnName]
    }
    if (intersectionObservers.value[columnName]) {
      intersectionObservers.value[columnName].disconnect()
      delete intersectionObservers.value[columnName]
    }
  }
}

function setSentinelRef(el, columnName) {
  if (el) {
    sentinelRefs.value[columnName] = el
    // Set up intersection observer once sentinel is available
    nextTick(() => {
      setupIntersectionObserver(columnName)
    })
  } else {
    // Clean up observer when element is removed
    if (intersectionObservers.value[columnName]) {
      intersectionObservers.value[columnName].disconnect()
      delete intersectionObservers.value[columnName]
    }
    delete sentinelRefs.value[columnName]
  }
}

function setupIntersectionObserver(columnName) {
  // Don't set up if already exists or if currently loading
  if (intersectionObservers.value[columnName] || loadingColumns.value[columnName]) {
    return
  }

  const sentinel = sentinelRefs.value[columnName]
  const scrollContainer = columnScrollRefs.value[columnName]

  if (!sentinel || !scrollContainer) {
    return
  }

  // Check if there are more items to load
  const column = columns.value.find((col) => col.column.name === columnName)
  if (!column) {
    return
  }

  const hasMoreItems = column.column.all_count && 
    (column.column.count || column.data?.length || 0) < column.column.all_count

  // If no more items, clean up any existing observer
  if (!hasMoreItems) {
    if (intersectionObservers.value[columnName]) {
      intersectionObservers.value[columnName].disconnect()
      delete intersectionObservers.value[columnName]
    }
    return
  }

  // Create intersection observer
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        // When sentinel comes into view (user scrolled near bottom)
        if (entry.isIntersecting && !loadingColumns.value[columnName]) {
          handleLoadMore(columnName)
        }
      })
    },
    {
      // Trigger when sentinel is within 100px of viewport to start loading before user reaches bottom
      root: scrollContainer,
      rootMargin: '100px',
      threshold: 0.1,
    }
  )

  observer.observe(sentinel)
  intersectionObservers.value[columnName] = observer
}

function handleLoadMore(columnName) {
  // Prevent multiple simultaneous loads for the same column
  if (loadingColumns.value[columnName]) return
  
  // Save current scroll position and reference item before loading
  const scrollContainer = columnScrollRefs.value[columnName]
  
  if (scrollContainer) {
    // Find the first visible card to use as a stable reference point
    const containerRect = scrollContainer.getBoundingClientRect()
    const currentScrollTop = scrollContainer.scrollTop
    const cards = Array.from(scrollContainer.querySelectorAll('[data-name]'))
    
    let referenceItemName = null
    let referenceItemTopInScroll = null
    let referenceItemTopRelativeToViewport = null
    
    // Find the card that's currently visible at or near the top of the viewport
    // This card will be our anchor point for scroll restoration
    for (const card of cards) {
      const cardRect = card.getBoundingClientRect()
      const cardTopRelativeToViewport = cardRect.top - containerRect.top
      
      // If this card is visible at or near the top of the viewport (within 100px), use it as reference
      if (cardTopRelativeToViewport >= -50 && cardTopRelativeToViewport <= 150) {
        referenceItemName = card.getAttribute('data-name')
        // Position of card's top in the scrollable content = viewport offset + scrollTop
        referenceItemTopInScroll = cardTopRelativeToViewport + currentScrollTop
        // How far the card is from the top of the viewport
        referenceItemTopRelativeToViewport = cardTopRelativeToViewport
        break
      }
    }
    
    // If no reference found, use the first card as fallback
    if (!referenceItemName && cards.length > 0) {
      const firstCard = cards[0]
      referenceItemName = firstCard.getAttribute('data-name')
      const cardRect = firstCard.getBoundingClientRect()
      referenceItemTopInScroll = cardRect.top - containerRect.top + currentScrollTop
      referenceItemTopRelativeToViewport = cardRect.top - containerRect.top
    }
    
    savedScrollPositions.value[columnName] = {
      scrollTop: currentScrollTop,
      scrollHeight: scrollContainer.scrollHeight,
      itemCount: cards.length,
      referenceItemName: referenceItemName,
      referenceItemTopInScroll: referenceItemTopInScroll, // Absolute position in scrollable content
      referenceItemTopRelativeToViewport: referenceItemTopRelativeToViewport, // Position relative to viewport
    }
  }
  
  // Store current data count for comparison
  const column = columns.value.find((col) => col.column.name === columnName)
  if (column) {
    previousColumnData.value[columnName] = {
      count: column.column.count || 0,
      dataLength: column.data?.length || 0,
      allCount: column.column.all_count || 0,
      timestamp: Date.now()
    }
  }
  
  // Clear any existing timeout for this column
  if (loadingTimeouts.value[columnName]) {
    clearTimeout(loadingTimeouts.value[columnName])
  }
  
  // Temporarily disconnect intersection observer to prevent multiple triggers during loading
  if (intersectionObservers.value[columnName]) {
    intersectionObservers.value[columnName].disconnect()
    delete intersectionObservers.value[columnName]
  }
  
  // Set loading state
  loadingColumns.value[columnName] = true
  
  // Set up MutationObserver to watch for DOM changes and restore scroll
  // This will catch when new items are added and restore scroll position
  if (scrollContainer && savedScrollPositions.value[columnName]) {
    // Clean up existing observer and interval for this column
    if (mutationObservers.value[columnName]) {
      mutationObservers.value[columnName].disconnect()
    }
    if (scrollRestoreIntervals.value[columnName]) {
      clearInterval(scrollRestoreIntervals.value[columnName])
    }
    
    // Create observer to watch for DOM changes (new items being added)
    const observer = new MutationObserver((mutations) => {
      // Check if any new nodes were added (new lead cards)
      const hasNewNodes = mutations.some(mutation => 
        mutation.addedNodes.length > 0 && 
        Array.from(mutation.addedNodes).some(node => 
          node.nodeType === 1 && (node.hasAttribute('data-name') || node.querySelector('[data-name]'))
        )
      )
      
      if (hasNewNodes && savedScrollPositions.value[columnName]) {
        // Debounce to avoid too many restorations
        setTimeout(() => {
          if (savedScrollPositions.value[columnName] && columnScrollRefs.value[columnName]) {
            restoreScrollPosition(columnName)
          }
        }, 100)
      }
    })
    
    observer.observe(scrollContainer, {
      childList: true, // Watch for added/removed children
      subtree: true, // Watch all descendants
    })
    
    mutationObservers.value[columnName] = observer
    
    // Also set up an interval to continuously check and restore scroll position
    // This handles cases where scroll gets reset after we restore it
    let attempts = 0
    const maxAttempts = 20 // Check for 2 seconds (20 * 100ms)
    scrollRestoreIntervals.value[columnName] = setInterval(() => {
      attempts++
      
      const currentContainer = columnScrollRefs.value[columnName]
      const savedPos = savedScrollPositions.value[columnName]
      
      if (!currentContainer || !savedPos || attempts >= maxAttempts) {
        // Clean up interval
        if (scrollRestoreIntervals.value[columnName]) {
          clearInterval(scrollRestoreIntervals.value[columnName])
          delete scrollRestoreIntervals.value[columnName]
        }
        // Clean up observer and saved position after max attempts
        if (attempts >= maxAttempts) {
          if (mutationObservers.value[columnName]) {
            mutationObservers.value[columnName].disconnect()
            delete mutationObservers.value[columnName]
          }
          delete savedScrollPositions.value[columnName]
        }
        return
      }
      
      // Check if scroll was reset (should be at saved position, but is near top)
      const currentScroll = currentContainer.scrollTop
      const targetScroll = Math.min(savedPos.scrollTop, currentContainer.scrollHeight - currentContainer.clientHeight)
      
      // If scroll was reset (is near 0 but should be at target), restore it
      if (currentScroll < 100 && targetScroll > 100) {
        currentContainer.scrollTop = Math.max(0, targetScroll)
      }
    }, 100) // Check every 100ms
  }
  
  // Set fallback timeout to reset loading state if it takes too long (10 seconds)
  loadingTimeouts.value[columnName] = setTimeout(() => {
    if (loadingColumns.value[columnName]) {
      loadingColumns.value[columnName] = false
      delete previousColumnData.value[columnName]
      delete savedScrollPositions.value[columnName]
      delete loadingTimeouts.value[columnName]
      // Clean up observer and interval
      if (mutationObservers.value[columnName]) {
        mutationObservers.value[columnName].disconnect()
        delete mutationObservers.value[columnName]
      }
      if (scrollRestoreIntervals.value[columnName]) {
        clearInterval(scrollRestoreIntervals.value[columnName])
        delete scrollRestoreIntervals.value[columnName]
      }
    }
  }, 10000)
  
  // Emit loadMore event to parent - parent will handle the actual loading
  emit('loadMore', columnName)
}

function restoreScrollPosition(columnName) {
  const savedPosition = savedScrollPositions.value[columnName]
  const scrollContainer = columnScrollRefs.value[columnName]
  
  if (!savedPosition || !scrollContainer) return false
  
  // Simple and reliable approach: Since new items are added at the bottom,
  // existing items don't move, so we can restore the exact same scrollTop value
  const maxScrollTop = Math.max(0, scrollContainer.scrollHeight - scrollContainer.clientHeight)
  const targetScrollTop = Math.min(savedPosition.scrollTop, maxScrollTop)
  
  // Restore scroll position immediately
  const currentScroll = scrollContainer.scrollTop
  scrollContainer.scrollTop = Math.max(0, targetScrollTop)
  
  // If scroll position was significantly different (likely reset), log for debugging
  if (Math.abs(currentScroll - targetScrollTop) > 50) {
    console.log(`Restoring scroll for ${columnName}: was ${currentScroll}, restoring to ${targetScrollTop}`)
  }
  
  // Double-check after a brief delay in case Vue or another process resets it
  setTimeout(() => {
    if (scrollContainer && savedScrollPositions.value && savedScrollPositions.value[columnName]) {
      const currentScrollCheck = scrollContainer.scrollTop
      const maxScroll = Math.max(0, scrollContainer.scrollHeight - scrollContainer.clientHeight)
      const targetScroll = Math.min(savedPosition.scrollTop, maxScroll)
      
      // If scroll was reset (near top when it shouldn't be), restore again
      if (Math.abs(currentScrollCheck - targetScroll) > 50 && currentScrollCheck < 100) {
        scrollContainer.scrollTop = Math.max(0, targetScroll)
      }
    }
  }, 100)
  
  return true
}

// Watch for column data changes to automatically reset loading state when data actually loads
watch(
  () => kanban.value?.data?.data,
  (newData, oldData) => {
    if (!newData) return
    
    // When new data arrives, check each column to see if data has changed
    columns.value.forEach((column) => {
      const columnName = column.column.name
      
      if (loadingColumns.value[columnName]) {
        const previous = previousColumnData.value[columnName]
        if (!previous) {
          // No previous data, clear loading state
          loadingColumns.value[columnName] = false
          if (loadingTimeouts.value[columnName]) {
            clearTimeout(loadingTimeouts.value[columnName])
            delete loadingTimeouts.value[columnName]
          }
          return
        }
        
        const currentCount = column.column.count || 0
        const currentDataLength = column.data?.length || 0
        const currentAllCount = column.column.all_count || 0
        
        // Check if data has changed:
        // 1. Data count has increased (new items loaded)
        // 2. Data length has increased (new items in the array)
        // 3. We've reached the end (count >= all_count)
        // 4. All count has changed (which means data was refreshed)
        const dataHasChanged = (
          currentCount > previous.count ||
          currentDataLength > previous.dataLength ||
          currentCount >= currentAllCount ||
          (currentAllCount > 0 && previous.allCount !== currentAllCount)
        )
        
        if (dataHasChanged) {
          // Data has loaded successfully - clear loading state
          loadingColumns.value[columnName] = false
          delete previousColumnData.value[columnName]
          
          // Clear timeout
          if (loadingTimeouts.value[columnName]) {
            clearTimeout(loadingTimeouts.value[columnName])
            delete loadingTimeouts.value[columnName]
          }
          
          // Restore scroll position to where user was before loading
          // Use multiple attempts with delays to ensure DOM is fully updated
          // Since new items are added at bottom, existing items don't move, so we restore the same scroll position
          
          // Immediate attempt after nextTick
          nextTick(() => {
            restoreScrollPosition(columnName)
            
            // Re-setup intersection observer for infinite scroll after data loads
            // Clean up existing observer first
            if (intersectionObservers.value[columnName]) {
              intersectionObservers.value[columnName].disconnect()
              delete intersectionObservers.value[columnName]
            }
            // Re-setup observer after a short delay to ensure DOM is updated
            setTimeout(() => {
              setupIntersectionObserver(columnName)
            }, 300)
            
            // Multiple attempts with increasing delays to catch any scroll resets
            // This ensures scroll position is restored even if Vue or other code resets it
            const restoreAttempts = [50, 150, 300, 500, 800]
            restoreAttempts.forEach((delay) => {
              setTimeout(() => {
                restoreScrollPosition(columnName)
                
                // After the final attempt, clean up saved position and observer
                if (delay === restoreAttempts[restoreAttempts.length - 1]) {
                  setTimeout(() => {
                    if (savedScrollPositions.value && savedScrollPositions.value[columnName]) {
                      delete savedScrollPositions.value[columnName]
                        // Disconnect mutation observer and interval after restoration is complete
                        if (mutationObservers.value[columnName]) {
                          mutationObservers.value[columnName].disconnect()
                          delete mutationObservers.value[columnName]
                        }
                        if (scrollRestoreIntervals.value[columnName]) {
                          clearInterval(scrollRestoreIntervals.value[columnName])
                          delete scrollRestoreIntervals.value[columnName]
                        }
                    }
                  }, 300)
                }
              }, delay)
            })
          })
        }
      }
    })
  },
  { deep: true, flush: 'post' }
)

// Watch columns to set up intersection observers when columns are first loaded or changed
watch(
  () => columns.value,
  () => {
    // Set up intersection observers for all columns after a short delay
    // to ensure DOM is ready
    nextTick(() => {
      setTimeout(() => {
        columns.value.forEach((column) => {
          const columnName = column.column.name
          if (!intersectionObservers.value[columnName]) {
            setupIntersectionObserver(columnName)
          }
        })
      }, 100)
    })
  },
  { immediate: true, deep: true }
)

// Cleanup on unmount
onUnmounted(() => {
  // Clear all timeouts
  Object.values(loadingTimeouts.value).forEach((timeout) => {
    if (timeout) clearTimeout(timeout)
  })
  
  // Clear all intervals
  Object.values(scrollRestoreIntervals.value).forEach((interval) => {
    if (interval) clearInterval(interval)
  })
  
  // Disconnect all mutation observers
  Object.values(mutationObservers.value).forEach((observer) => {
    if (observer) observer.disconnect()
  })
  
  // Disconnect all intersection observers
  Object.values(intersectionObservers.value).forEach((observer) => {
    if (observer) observer.disconnect()
  })
  
  loadingTimeouts.value = {}
  loadingColumns.value = {}
  previousColumnData.value = {}
  savedScrollPositions.value = {}
  columnScrollRefs.value = {}
  mutationObservers.value = {}
  scrollRestoreIntervals.value = {}
  sentinelRefs.value = {}
  intersectionObservers.value = {}
})
</script>
