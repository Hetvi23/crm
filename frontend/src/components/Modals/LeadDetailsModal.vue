<template>
  <!-- Right Side Sidebar -->
  <Transition name="slide-right">
    <div
      v-if="show"
      class="fixed top-0 right-0 h-full w-full max-w-[360px] bg-white shadow-xl z-50 flex flex-col overflow-hidden"
      style="background-color: #FFFFFF; border-left: 1px solid #DADDE1;"
    >
      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-3 border-b flex-shrink-0" style="border-color: #DADDE1; background-color: #FFFFFF;">
        <h2 class="text-2xl font-semibold text-ink-gray-9 truncate pr-2">
          {{ leadData?.lead_name || __('Lead Details') }}
        </h2>
        <button
          @click="closeSidebar"
          class="p-1.5 hover:bg-surface-gray-2 rounded transition-colors flex-shrink-0"
          aria-label="Close"
        >
          <FeatherIcon name="x" class="h-5 w-5 text-ink-gray-7" />
        </button>
      </div>

      <!-- Content -->
      <div class="flex-1 overflow-y-auto px-4 py-3">
        <div v-if="loading" class="flex items-center justify-center py-8">
          <LoadingIndicator class="w-5 h-5" />
        </div>
        
        <div v-else-if="leadData" class="flex flex-col gap-4">
          <!-- Person Details -->
          <div>
            <h3 class="text-xl font-semibold mb-2 text-ink-gray-9">{{ __('Person Details') }}</h3>
            <div class="flex flex-col gap-3">
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Name') }}
                </label>
                <div class="text-lg text-ink-gray-9">{{ leadData.lead_name || '-' }}</div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Organization') }}
                </label>
                <div class="text-lg text-ink-gray-9">{{ leadData.organization || '-' }}</div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Email') }}
                </label>
                <div class="text-lg text-ink-gray-9 flex items-center gap-1.5">
                  <FeatherIcon v-if="leadData.email" name="mail" class="h-4 w-4 text-ink-gray-5 flex-shrink-0" />
                  <span class="truncate">{{ leadData.email || '-' }}</span>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Mobile') }}
                </label>
                <div class="text-lg text-ink-gray-9 flex items-center gap-1.5">
                  <FeatherIcon v-if="leadData.mobile_no" name="phone" class="h-4 w-4 text-ink-gray-5 flex-shrink-0" />
                  <span class="truncate">{{ leadData.mobile_no || '-' }}</span>
                </div>
              </div>
              
              <div v-if="leadData.phone">
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Phone') }}
                </label>
                <div class="text-lg text-ink-gray-9 flex items-center gap-1.5">
                  <FeatherIcon name="phone" class="h-4 w-4 text-ink-gray-5 flex-shrink-0" />
                  <span class="truncate">{{ leadData.phone }}</span>
                </div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Job Title') }}
                </label>
                <div class="text-lg text-ink-gray-9">{{ leadData.job_title || leadData.custom_designation || '-' }}</div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('City') }}
                </label>
                <div class="text-lg text-ink-gray-9 flex items-center gap-1.5">
                  <FeatherIcon v-if="leadData.city" name="map-pin" class="h-4 w-4 text-blue-primary flex-shrink-0" />
                  <span>{{ leadData.city || '-' }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Status & Source -->
          <div>
            <h3 class="text-xl font-semibold mb-2 text-ink-gray-9">{{ __('Lead Information') }}</h3>
            <div class="flex flex-col gap-3">
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Status') }}
                </label>
                <Badge
                  :label="leadData.status"
                  variant="subtle"
                  theme="blue"
                  size="sm"
                />
              </div>
              
              <div v-if="leadData.source">
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Source') }}
                </label>
                <div class="text-lg text-ink-gray-9">{{ leadData.source }}</div>
              </div>
              
              <div v-if="leadData.lead_owner">
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Lead Owner') }}
                </label>
                <div class="text-lg text-ink-gray-9">{{ leadData.lead_owner }}</div>
              </div>
              
              <div>
                <label class="block text-sm font-medium text-ink-gray-6 mb-0.5">
                  {{ __('Created On') }}
                </label>
                <div class="text-lg text-ink-gray-9">{{ formatDateTime(leadData.creation) }}</div>
              </div>
            </div>
          </div>
          
          <!-- Notes (if any) -->
          <div v-if="leadData.notes">
            <h3 class="text-xl font-semibold mb-2 text-ink-gray-9">{{ __('Notes') }}</h3>
            <div class="text-lg whitespace-pre-wrap bg-surface-gray-1 p-2.5 rounded text-ink-gray-9">
              {{ leadData.notes }}
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="flex items-center justify-between gap-2 px-4 py-3 border-t flex-shrink-0" style="border-color: #DADDE1; background-color: #FFFFFF;">
        <Button
          variant="outline"
          :label="__('View Full Details')"
          @click="openFullDetails"
          class="flex-1"
        />
        <Button
          variant="solid"
          :label="__('Close')"
          @click="closeSidebar"
          class="flex-1"
        />
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { Badge, Button, LoadingIndicator, call, FeatherIcon } from 'frappe-ui'
import { useRouter, useRoute } from 'vue-router'

const props = defineProps({
  leadId: {
    type: String,
    required: true,
  },
  modelValue: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const router = useRouter()
const route = useRoute()
const show = ref(props.modelValue)
const loading = ref(false)
const leadData = ref(null)

watch(
  () => props.modelValue,
  (val) => {
    show.value = val
    if (val) {
      loadLeadData()
      // Don't prevent body scroll - allow main content to remain accessible
      // document.body.style.overflow = 'hidden'
    }
  },
  { immediate: true }
)

// Watch for leadId changes - reload data when a different lead is selected
watch(
  () => props.leadId,
  (newLeadId, oldLeadId) => {
    // Only reload if leadId actually changed and sidebar is open
    if (newLeadId && newLeadId !== oldLeadId && show.value) {
      // Clear old data immediately to show loading state
      leadData.value = null
      // Load new lead data
      loadLeadData()
    }
  },
  { immediate: false }
)

watch(show, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    leadData.value = null
  }
})

// Handle ESC key to close sidebar
function handleEscapeKey(event) {
  if (event.key === 'Escape' && show.value) {
    closeSidebar()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscapeKey)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscapeKey)
})

function closeSidebar() {
  show.value = false
}

async function loadLeadData() {
  loading.value = true
  try {
    const data = await call('frappe.client.get', {
      doctype: 'CRM Lead',
      name: props.leadId,
    })
    leadData.value = data
  } catch (error) {
    console.error('Error loading lead data:', error)
    window.frappe?.show_alert({
      message: __('Failed to load lead details'),
      indicator: 'red',
    })
  } finally {
    loading.value = false
  }
}

function formatDateTime(dateTime) {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function openFullDetails() {
  closeSidebar()
  router.push({
    name: 'Lead',
    params: { leadId: props.leadId },
    query: { view: route.query.view, viewType: route.params.viewType },
  })
}
</script>

<style scoped>
/* Slide in from right animation */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease-in-out;
}

.slide-right-enter-from {
  transform: translateX(100%);
}

.slide-right-enter-to {
  transform: translateX(0);
}

.slide-right-leave-from {
  transform: translateX(0);
}

.slide-right-leave-to {
  transform: translateX(100%);
}

</style>

