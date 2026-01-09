<template>
  <Dialog
    v-model="show"
    :options="{
      title: leadData?.lead_name || __('Lead Details'),
      size: '3xl',
    }"
  >
    <template #body-content>
      <div v-if="loading" class="flex items-center justify-center py-8">
        <LoadingIndicator class="w-6 h-6" />
      </div>
      
      <div v-else-if="leadData" class="flex flex-col gap-6">
        <!-- Person Details -->
        <div>
          <h3 class="text-lg font-semibold mb-3 text-ink-gray-9">{{ __('Person Details') }}</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Name') }}
              </label>
              <div class="text-base">{{ leadData.lead_name || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Organization') }}
              </label>
              <div class="text-base">{{ leadData.organization || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Email') }}
              </label>
              <div class="text-base">{{ leadData.email || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Mobile') }}
              </label>
              <div class="text-base">{{ leadData.mobile_no || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Phone') }}
              </label>
              <div class="text-base">{{ leadData.phone || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Job Title') }}
              </label>
              <div class="text-base">{{ leadData.job_title || leadData.custom_designation || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('City') }}
              </label>
              <div class="text-base flex items-center gap-1.5">
                <FeatherIcon name="map-pin" class="h-4 w-4 text-blue-primary" />
                <span>{{ leadData.city || '-' }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Status & Source -->
        <div>
          <h3 class="text-lg font-semibold mb-3 text-ink-gray-9">{{ __('Lead Information') }}</h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Status') }}
              </label>
              <Badge
                :label="leadData.status"
                variant="subtle"
                theme="blue"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Source') }}
              </label>
              <div class="text-base">{{ leadData.source || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Lead Owner') }}
              </label>
              <div class="text-base">{{ leadData.lead_owner || '-' }}</div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-ink-gray-7 mb-1">
                {{ __('Created On') }}
              </label>
              <div class="text-base">{{ formatDateTime(leadData.creation) }}</div>
            </div>
          </div>
        </div>
        
        <!-- Notes (if any) -->
        <div v-if="leadData.notes">
          <h3 class="text-lg font-semibold mb-3 text-ink-gray-9">{{ __('Notes') }}</h3>
          <div class="text-base whitespace-pre-wrap bg-surface-gray-1 p-3 rounded">
            {{ leadData.notes }}
          </div>
        </div>
      </div>
    </template>
    
    <template #actions>
      <div class="flex gap-2">
        <Button
          variant="outline"
          :label="__('View Full Details')"
          @click="openFullDetails"
        />
        <Button
          variant="solid"
          :label="__('Close')"
          @click="show = false"
        />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Dialog, Badge, Button, LoadingIndicator, call, FeatherIcon } from 'frappe-ui'
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
    }
  },
  { immediate: true }
)

watch(show, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    leadData.value = null
  }
})

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
  show.value = false
  router.push({
    name: 'Lead',
    params: { leadId: props.leadId },
    query: { view: route.query.view, viewType: route.params.viewType },
  })
}
</script>

