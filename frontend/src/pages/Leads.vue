<template>
  <LayoutHeader>
    <template #left-header>
      <ViewBreadcrumbs v-model="viewControls" routeName="Leads" />
    </template>
    <template #right-header>
      <CustomActions
        v-if="leadsListView?.customListActions"
        :actions="leadsListView.customListActions"
      />
      <Button
        variant="outline"
        :label="__('Sync Meta Leads')"
        iconLeft="refresh"
        :loading="syncing"
        @click="syncMetaLeads"
      />
      <Button
        variant="solid"
        :label="__('Create')"
        iconLeft="plus"
        @click="showLeadModal = true"
      />
    </template>
  </LayoutHeader>
  <!-- Search Bar and Controls - Meta Style -->
  <div class="px-5 py-3" style="background-color: #FFFFFF; border-bottom: 1px solid #E4E6EA;">
    <div class="flex items-center gap-3 flex-wrap">
      <TextInput
        v-model="searchQuery"
        :placeholder="__('Search leads by name, email, mobile number, or company...')"
        class="flex-1 min-w-[300px] max-w-md search-input-leads"
        style="font-size: 15px; font-weight: 400; line-height: 1.3333; border-radius: 20px; background-color: #F0F2F5; border: none; padding: 8px 16px; outline: none; box-shadow: none;"
        @input="handleSearch"
      >
        <template #prefix>
          <FeatherIcon name="search" class="h-4 w-4" style="color: #65676B;" />
        </template>
      </TextInput>
      <Button
        v-if="searchQuery"
        variant="ghost"
        icon="x"
        size="sm"
        @click="clearSearch"
        style="padding: 6px; font-size: 15px;"
        class="hover:bg-surface-gray-2"
      />
      
      <!-- Filter, Refresh, and Settings Buttons -->
      <div class="flex items-center gap-2">
        <Button
          :tooltip="__('Refresh')"
          :icon="RefreshIcon"
          :loading="viewControlsList?.loading"
          @click="viewControls?.reload()"
          variant="ghost"
          size="sm"
          style="padding: 6px; font-size: 15px;"
          class="hover:bg-surface-gray-2"
        />
        <Filter
          v-if="viewControlsList"
          v-model="viewControlsList"
          :doctype="'CRM Lead'"
          :default_filters="{ converted: 0 }"
          @update="viewControls?.updateFilter"
        />
        <KanbanSettings
          v-if="viewControlsList && route.params.viewType === 'kanban'"
          v-model="viewControlsList"
          doctype="CRM Lead"
          @update="viewControls?.updateKanbanSettings"
        />
        
        <!-- Toggle buttons for kanban view only -->
        <template v-if="route.params.viewType === 'kanban'">
          <div class="flex items-center gap-2 px-2 border-l" style="border-color: #E4E6EA;">
            <Button
              :variant="showNotQualified ? 'solid' : 'outline'"
              size="sm"
              :label="__('Show Not Qualified')"
              @click="showNotQualified = !showNotQualified"
              style="font-size: 13px; padding: 6px 12px; height: 32px; border-radius: 6px; font-weight: 500;"
              :class="showNotQualified ? 'bg-[#1877F2] text-white hover:bg-[#166FE5]' : 'border-[#E4E6EA] text-[#050505] hover:bg-[#F0F2F5]'"
            />
            <Button
              :variant="showLostLeads ? 'solid' : 'outline'"
              size="sm"
              :label="__('Show Lost Leads')"
              @click="showLostLeads = !showLostLeads"
              style="font-size: 13px; padding: 6px 12px; height: 32px; border-radius: 6px; font-weight: 500;"
              :class="showLostLeads ? 'bg-[#1877F2] text-white hover:bg-[#166FE5]' : 'border-[#E4E6EA] text-[#050505] hover:bg-[#F0F2F5]'"
            />
          </div>
        </template>
      </div>
    </div>
  </div>
  <ViewControls
    ref="viewControls"
    v-model="leads"
    v-model:loadMore="loadMore"
    v-model:resizeColumn="triggerResize"
    v-model:updatedPageCount="updatedPageCount"
    doctype="CRM Lead"
    :filters="{ converted: 0 }"
    :options="{
      allowedViews: ['list', 'group_by', 'kanban'],
      hideActionButtons: true,
    }"
  />
  <KanbanView
    v-if="route.params.viewType == 'kanban'"
    v-model="filteredLeads"
    :options="{
      onClick: (row) => showLeadDetails(row.name),
      onNewClick: (column) => onNewClick(column),
    }"
    @update="(data) => viewControls.updateKanbanSettings(data)"
    @loadMore="(columnName) => viewControls.loadMoreKanban(columnName)"
  >
    <template #title="{ titleField, itemName }">
      <div class="flex items-center gap-2">
        <div v-if="titleField === 'status'">
          <IndicatorIcon :class="getRow(itemName, titleField).color" />
        </div>
        <div
          v-else-if="
            titleField === 'organization' && getRow(itemName, titleField).label
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).logo"
            :label="getRow(itemName, titleField).label"
            size="sm"
          />
        </div>
        <div
          v-else-if="
            titleField === 'lead_name' && getRow(itemName, titleField).label
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).image"
            :label="getRow(itemName, titleField).image_label"
            size="sm"
          />
        </div>
        <div
          v-else-if="
            titleField === 'lead_owner' &&
            getRow(itemName, titleField).full_name
          "
        >
          <Avatar
            class="flex items-center"
            :image="getRow(itemName, titleField).user_image"
            :label="getRow(itemName, titleField).full_name"
            size="sm"
          />
        </div>
        <div v-else-if="titleField === 'mobile_no'">
          <PhoneIcon class="h-4 w-4" style="color: #65676B;" />
        </div>
        <div
          v-if="
            [
              'modified',
              'creation',
              'first_response_time',
              'first_responded_on',
              'response_by',
            ].includes(titleField)
          "
          class="truncate"
          style="color: #050505; font-size: 15px; font-weight: 600; line-height: 1.3333;"
        >
          <Tooltip :text="getRow(itemName, titleField).label">
            <div>{{ getRow(itemName, titleField).timeAgo }}</div>
          </Tooltip>
        </div>
        <div v-else-if="titleField === 'sla_status'" class="truncate">
          <Badge
            v-if="getRow(itemName, titleField).value"
            :variant="'subtle'"
            :theme="getRow(itemName, titleField).color"
            size="md"
            :label="getRow(itemName, titleField).value"
          />
        </div>
        <div
          v-else-if="getRow(itemName, titleField).label"
          class="truncate font-semibold"
          style="color: #050505; font-size: 15px; font-weight: 600; line-height: 1.3333; letter-spacing: -0.01em;"
        >
          {{ getRow(itemName, titleField).label }}
        </div>
        <div 
          class="truncate" 
          v-else
          style="color: #65676B; font-size: 15px; font-weight: 400; line-height: 1.3333;"
        >
          {{ __('No Title') }}
        </div>
      </div>
    </template>
    <template #fields="{ fieldName, itemName }">
      <div
        v-if="getRow(itemName, fieldName).label || getRow(itemName, fieldName).value || (fieldName === 'organization' && getRow(itemName, fieldName)) || (fieldName === 'mobile_no' && getRow(itemName, fieldName)) || (fieldName === 'city' && getRow(itemName, fieldName))"
        class="flex items-center gap-2 min-w-0"
      >
        <div v-if="fieldName === 'status'">
          <IndicatorIcon :class="getRow(itemName, fieldName).color" />
        </div>
        <!-- Organization - show with icon if available, otherwise as text - Meta Style (No Border) -->
        <div v-else-if="fieldName === 'organization'" class="flex items-center gap-1.5 min-w-0 flex-1">
          <div v-if="getRow(itemName, fieldName).logo" class="flex items-center flex-shrink-0">
            <Avatar
              class="flex items-center"
              :image="getRow(itemName, fieldName).logo"
              :label="getRow(itemName, fieldName).label || getRow(itemName, fieldName)"
              size="xs"
            />
          </div>
          <span 
            v-else 
            class="truncate kanban-card-field"
            style="color: #050505; font-size: 15px; font-weight: 400; line-height: 1.3333; border: none; outline: none; background: transparent; padding: 0; box-shadow: none;"
          >
            {{ getRow(itemName, fieldName).label || getRow(itemName, fieldName) }}
          </span>
        </div>
        <!-- Phone (mobile_no) - show with phone icon - Meta Style (No Border) -->
        <div v-else-if="fieldName === 'mobile_no'" class="flex items-center gap-1.5 min-w-0 flex-1">
          <FeatherIcon name="phone" class="h-4 w-4 flex-shrink-0" style="color: #65676B;" />
          <span 
            class="truncate kanban-card-field"
            style="color: #050505; font-size: 15px; font-weight: 400; line-height: 1.3333; border: none; outline: none; background: transparent; padding: 0; box-shadow: none;"
          >
            {{ getRow(itemName, fieldName).label || getRow(itemName, fieldName) }}
          </span>
        </div>
        <!-- City - show with map-pin icon - Meta Style (No Border) -->
        <div v-else-if="fieldName === 'city'" class="flex items-center gap-1.5 min-w-0 flex-1">
          <FeatherIcon name="map-pin" class="h-4 w-4 flex-shrink-0" style="color: #65676B;" />
          <span 
            class="truncate kanban-card-field-secondary"
            style="color: #65676B; font-size: 15px; font-weight: 400; line-height: 1.3333; border: none; outline: none; background: transparent; padding: 0; box-shadow: none;"
          >
            {{ getRow(itemName, fieldName).label || getRow(itemName, fieldName) }}
          </span>
        </div>
        <div v-else-if="fieldName === 'lead_name'">
          <Avatar
            v-if="getRow(itemName, fieldName).label"
            class="flex items-center"
            :image="getRow(itemName, fieldName).image"
            :label="getRow(itemName, fieldName).image_label"
            size="xs"
          />
        </div>
        <div v-else-if="fieldName === 'lead_owner'">
          <Avatar
            v-if="getRow(itemName, fieldName).full_name"
            class="flex items-center"
            :image="getRow(itemName, fieldName).user_image"
            :label="getRow(itemName, fieldName).full_name"
            size="xs"
          />
        </div>
        <div
          v-else-if="
            [
              'modified',
              'creation',
              'first_response_time',
              'first_responded_on',
              'response_by',
            ].includes(fieldName)
          "
          class="truncate"
          style="color: #65676B; font-size: 15px; font-weight: 400; line-height: 1.3333;"
        >
          <Tooltip :text="getRow(itemName, fieldName).label">
            <div>{{ getRow(itemName, fieldName).timeAgo }}</div>
          </Tooltip>
        </div>
        <div v-else-if="fieldName === 'sla_status'" class="truncate">
          <Badge
            v-if="getRow(itemName, fieldName).value"
            :variant="'subtle'"
            :theme="getRow(itemName, fieldName).color"
            size="md"
            :label="getRow(itemName, fieldName).value"
          />
        </div>
        <div v-else-if="fieldName === '_assign'" class="flex items-center">
          <MultipleAvatar
            :avatars="getRow(itemName, fieldName).label"
            size="xs"
          />
        </div>
        <div v-else-if="fieldName === 'email'" class="flex items-center gap-1.5 min-w-0 flex-1">
          <FeatherIcon name="mail" class="h-4 w-4 flex-shrink-0" style="color: #65676B;" />
          <span 
            class="truncate kanban-card-field"
            style="color: #050505; font-size: 15px; font-weight: 400; line-height: 1.3333; border: none; outline: none; background: transparent; padding: 0; box-shadow: none;"
          >
            {{ getRow(itemName, fieldName).label || getRow(itemName, fieldName) }}
          </span>
        </div>
        <div 
          v-else 
          class="truncate kanban-card-field"
          style="color: #050505; font-size: 15px; font-weight: 400; line-height: 1.3333; border: none; outline: none; background: transparent; padding: 0; box-shadow: none;"
        >
          {{ getRow(itemName, fieldName).label || getRow(itemName, fieldName) }}
        </div>
      </div>
    </template>
    <template #actions="{ itemName, currentColumn }">
      <div class="flex gap-2 items-center justify-between w-full" @click.stop.prevent>
        <Dropdown :options="getMoveToOptions(itemName, currentColumn)" placement="top-start">
          <template #default>
            <Button
              variant="ghost" 
              size="sm"
              :label="__('Move to')"
              iconLeft="arrow-right"
              @click.stop.prevent
              style="font-size: 15px; padding: 6px 12px; color: #1877F2; font-weight: 600; height: 32px; border-radius: 6px;"
              class="hover:bg-[#E7F3FF] transition-colors"
            />
          </template>
        </Dropdown>
        <div class="flex gap-2">
          <Button
            variant="solid"
            size="sm"
            :label="__('Reminder')"
            @click.stop.prevent="openReminderModal(itemName)"
            style="font-size: 15px; padding: 6px 16px; background-color: #1877F2; font-weight: 600; height: 32px; border-radius: 6px;"
            class="transition-colors hover:bg-[#166FE5]"
          />
        </div>
      </div>
    </template>
  </KanbanView>
  <LeadsListView
    ref="leadsListView"
    v-else-if="leads.data && rows.length"
    v-model="leads.data.page_length_count"
    v-model:list="leads"
    :rows="rows"
    :columns="leads.data.columns"
    :options="{
      showTooltip: false,
      resizeColumn: true,
      rowCount: leads.data.row_count,
      totalCount: leads.data.total_count,
    }"
    @loadMore="() => loadMore++"
    @columnWidthUpdated="() => triggerResize++"
    @updatePageCount="(count) => (updatedPageCount = count)"
    @applyFilter="(data) => viewControls.applyFilter(data)"
    @applyLikeFilter="(data) => viewControls.applyLikeFilter(data)"
    @likeDoc="(data) => viewControls.likeDoc(data)"
    @selectionsChanged="
      (selections) => viewControls.updateSelections(selections)
    "
  />
  <div v-else-if="leads.data" class="flex h-full items-center justify-center">
    <div
      class="flex flex-col items-center gap-3 text-xl font-medium text-ink-gray-4"
    >
      <LeadsIcon class="h-10 w-10" />
      <span>{{ __('No {0} Found', [__('Leads')]) }}</span>
      <Button
        :label="__('Create')"
        iconLeft="plus"
        @click="showLeadModal = true"
      />
    </div>
  </div>
  <LeadModal
    v-if="showLeadModal"
    v-model="showLeadModal"
    :defaults="defaults"
  />
  <NoteModal
    v-if="showNoteModal"
    v-model="showNoteModal"
    :note="note"
    doctype="CRM Lead"
    :doc="docname"
  />
  <TaskModal
    v-if="showTaskModal"
    v-model="showTaskModal"
    :task="task"
    doctype="CRM Lead"
    :doc="docname"
  />
  <ReminderModal
    v-if="showReminderModal"
    v-model="showReminderModal"
    :leadId="selectedLeadId"
    :leadName="selectedLeadName"
  />
  <LeadDetailsModal
    v-if="showLeadDetailsModal"
    v-model="showLeadDetailsModal"
    :leadId="selectedLeadId"
  />
</template>

<script setup>
import ViewBreadcrumbs from '@/components/ViewBreadcrumbs.vue'
import MultipleAvatar from '@/components/MultipleAvatar.vue'
import CustomActions from '@/components/CustomActions.vue'
import EmailAtIcon from '@/components/Icons/EmailAtIcon.vue'
import PhoneIcon from '@/components/Icons/PhoneIcon.vue'
import NoteIcon from '@/components/Icons/NoteIcon.vue'
import TaskIcon from '@/components/Icons/TaskIcon.vue'
import CommentIcon from '@/components/Icons/CommentIcon.vue'
import IndicatorIcon from '@/components/Icons/IndicatorIcon.vue'
import LeadsIcon from '@/components/Icons/LeadsIcon.vue'
import LayoutHeader from '@/components/LayoutHeader.vue'
import LeadsListView from '@/components/ListViews/LeadsListView.vue'
import KanbanView from '@/components/Kanban/KanbanView.vue'
import LeadModal from '@/components/Modals/LeadModal.vue'
import NoteModal from '@/components/Modals/NoteModal.vue'
import TaskModal from '@/components/Modals/TaskModal.vue'
import ReminderModal from '@/components/Modals/ReminderModal.vue'
import LeadDetailsModal from '@/components/Modals/LeadDetailsModal.vue'
import ViewControls from '@/components/ViewControls.vue'
import Filter from '@/components/Filter.vue'
import KanbanSettings from '@/components/Kanban/KanbanSettings.vue'
import RefreshIcon from '@/components/Icons/RefreshIcon.vue'
import { getMeta } from '@/stores/meta'
import { globalStore } from '@/stores/global'
import { usersStore } from '@/stores/users'
import { statusesStore } from '@/stores/statuses'
import { callEnabled } from '@/composables/settings'
import { formatDate, timeAgo, website, formatTime } from '@/utils'
import { Avatar, Tooltip, Dropdown, Button, call, toast, TextInput, FeatherIcon } from 'frappe-ui'
import { useRoute, useRouter } from 'vue-router'
import { ref, computed, reactive, h } from 'vue'

const { getFormattedPercent, getFormattedFloat, getFormattedCurrency } =
  getMeta('CRM Lead')
const { makeCall } = globalStore()
const { getUser } = usersStore()
const { getLeadStatus } = statusesStore()

const route = useRoute()
const router = useRouter()

const leadsListView = ref(null)
const showLeadModal = ref(false)
const searchQuery = ref('')
const showNotQualified = ref(false)
const showLostLeads = ref(false)

const defaults = reactive({})

// leads data is loaded in the ViewControls component
const leads = ref({})
const loadMore = ref(1)
const triggerResize = ref(1)
const updatedPageCount = ref(20)
const viewControls = ref(null)

// Computed property to access the list from viewControls
const viewControlsList = computed(() => {
  return viewControls.value?.list
})

// Filtered leads for kanban view based on toggle states
const filteredLeads = computed(() => {
  if (!leads.value?.data || route.params.viewType !== 'kanban') {
    return leads.value
  }

  // Create a deep copy to avoid mutating the original
  const filtered = JSON.parse(JSON.stringify(leads.value))
  
  if (!filtered.data?.data) {
    return filtered
  }

  // Filter columns based on toggle states
  filtered.data.data = filtered.data.data.filter((column) => {
    const columnName = column.column?.name
    
    if (!columnName) return true
    
    // Normalize column name for comparison (case-insensitive)
    const normalizedName = columnName.toLowerCase().trim()
    
    // Hide "Not qualified" column unless toggle is on
    if (normalizedName === 'not qualified' || normalizedName === 'notqualified') {
      return showNotQualified.value
    }
    
    // Hide "Lost" column unless toggle is on
    if (normalizedName === 'lost') {
      return showLostLeads.value
    }
    
    // Show all other columns
    return true
  })

  return filtered
})

function getRow(name, field) {
  function getValue(value) {
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      return value
    }
    return { label: value }
  }
  return getValue(rows.value?.find((row) => row.name == name)[field])
}

// Rows
const rows = computed(() => {
  if (!leads.value?.data?.data) return []
  if (leads.value.data.view_type === 'group_by') {
    if (!leads.value?.data.group_by_field?.fieldname) return []
    return getGroupedByRows(
      leads.value?.data.data,
      leads.value?.data.group_by_field,
      leads.value.data.columns,
    )
  } else if (leads.value.data.view_type === 'kanban') {
    return getKanbanRows(leads.value.data.data, leads.value.data.fields)
  } else {
    return parseRows(leads.value?.data.data, leads.value.data.columns)
  }
})

function getGroupedByRows(listRows, groupByField, columns) {
  let groupedRows = []

  groupByField.options?.forEach((option) => {
    let filteredRows = []

    if (!option) {
      filteredRows = listRows.filter((row) => !row[groupByField.fieldname])
    } else {
      filteredRows = listRows.filter(
        (row) => row[groupByField.fieldname] == option,
      )
    }

    let groupDetail = {
      label: groupByField.label,
      group: option || __(' '),
      collapsed: false,
      rows: parseRows(filteredRows, columns),
    }
    if (groupByField.fieldname == 'status') {
      groupDetail.icon = () =>
        h(IndicatorIcon, {
          class: getLeadStatus(option)?.color,
        })
    }
    groupedRows.push(groupDetail)
  })

  return groupedRows || listRows
}

function getKanbanRows(data, columns) {
  let _rows = []
  data.forEach((column) => {
    column.data?.forEach((row) => {
      // Ensure city is always included in the row data
      if (!row.hasOwnProperty('city') && row.city === undefined) {
        // Try to get city from the lead document if available
        // This ensures city is always available for display
      }
      _rows.push(row)
    })
  })
  return parseRows(_rows, columns)
}

function parseRows(rows, columns = []) {
  let view_type = leads.value.data.view_type
  let key = view_type === 'kanban' ? 'fieldname' : 'key'
  let type = view_type === 'kanban' ? 'fieldtype' : 'type'

  return rows.map((lead) => {
    let _rows = {}
    // Get base rows and always add required fields for kanban view
    const baseRows = leads.value?.data.rows || []
    // Ensure required fields for kanban cards are included: organization, mobile_no, city
    const requiredKanbanFields = ['organization', 'mobile_no', 'city']
    const allRows = [...baseRows, ...requiredKanbanFields].filter((v, i, a) => a.indexOf(v) === i)
    
    allRows.forEach((row) => {
      _rows[row] = lead[row]

      let fieldType = columns?.find((col) => (col[key] || col.value) == row)?.[
        type
      ]

      if (
        fieldType &&
        ['Date', 'Datetime'].includes(fieldType) &&
        !['modified', 'creation'].includes(row)
      ) {
        _rows[row] = formatDate(lead[row], '', true, fieldType == 'Datetime')
      }

      if (fieldType && fieldType == 'Currency') {
        _rows[row] = getFormattedCurrency(row, lead)
      }

      if (fieldType && fieldType == 'Float') {
        _rows[row] = getFormattedFloat(row, lead)
      }

      if (fieldType && fieldType == 'Percent') {
        _rows[row] = getFormattedPercent(row, lead)
      }

      if (row == 'lead_name') {
        _rows[row] = {
          label: lead.lead_name,
          image: lead.image,
          image_label: lead.first_name,
        }
      } else if (row == 'organization') {
        _rows[row] = lead.organization
      } else if (row === 'website') {
        _rows[row] = website(lead.website)
      } else if (row == 'city') {
        _rows[row] = {
          label: lead.city || '',
        }
      } else if (row == 'status') {
        _rows[row] = {
          label: lead.status,
          color: getLeadStatus(lead.status)?.color,
        }
      } else if (row == 'sla_status') {
        let value = lead.sla_status
        let tooltipText = value
        let color =
          lead.sla_status == 'Failed'
            ? 'red'
            : lead.sla_status == 'Fulfilled'
              ? 'green'
              : 'orange'
        if (value == 'First Response Due') {
          value = __(timeAgo(lead.response_by))
          tooltipText = formatDate(lead.response_by)
          if (new Date(lead.response_by) < new Date()) {
            color = 'red'
          }
        }
        _rows[row] = {
          label: tooltipText,
          value: value,
          color: color,
        }
      } else if (row == 'lead_owner') {
        _rows[row] = {
          label: lead.lead_owner && getUser(lead.lead_owner).full_name,
          ...(lead.lead_owner && getUser(lead.lead_owner)),
        }
      } else if (row == '_assign') {
        let assignees = JSON.parse(lead._assign || '[]')
        _rows[row] = assignees.map((user) => ({
          name: user,
          image: getUser(user).user_image,
          label: getUser(user).full_name,
        }))
      } else if (['modified', 'creation'].includes(row)) {
        _rows[row] = {
          label: formatDate(lead[row]),
          timeAgo: __(timeAgo(lead[row])),
        }
      } else if (
        ['first_response_time', 'first_responded_on', 'response_by'].includes(
          row,
        )
      ) {
        let field = row == 'response_by' ? 'response_by' : 'first_responded_on'
        _rows[row] = {
          label: lead[field] ? formatDate(lead[field]) : '',
          timeAgo: lead[row]
            ? row == 'first_response_time'
              ? formatTime(lead[row])
              : __(timeAgo(lead[row]))
            : '',
        }
      }
    })
    _rows['_email_count'] = lead._email_count
    _rows['_note_count'] = lead._note_count
    _rows['_task_count'] = lead._task_count
    _rows['_comment_count'] = lead._comment_count
    return _rows
  })
}

function onNewClick(column) {
  let column_field = leads.value.params.column_field

  if (column_field) {
    defaults[column_field] = column.column.name
  }

  showLeadModal.value = true
}

function getMoveToOptions(itemName, currentColumn) {
  if (!leads.value?.data?.data) return []
  
  const allColumns = leads.value.data.data
    .filter((col) => col.column.name !== currentColumn && !col.column.delete)
    .map((colData) => {
      const targetColumnName = colData.column.name
      return {
        label: targetColumnName,
        onClick: () => {
          // Move the card to the selected column using viewControls
          if (viewControls.value && viewControls.value.updateKanbanSettings) {
            const kanban_columns = leads.value.data.kanban_columns || []
            
            // Update kanban columns with the move
            const updated_columns = kanban_columns.map((kc) => {
              const kcName = kc.name
              const order = kc.order || []
              
              // Remove from all columns first
              const filteredOrder = order.filter((name) => name !== itemName)
              
              // Add to target column
              if (kcName === targetColumnName) {
                if (!filteredOrder.includes(itemName)) {
                  filteredOrder.push(itemName)
                }
              }
              
              return {
                ...kc,
                order: filteredOrder,
              }
            })
            
            // Use viewControls to update kanban settings
            viewControls.value.updateKanbanSettings({
              item: itemName,
              to: targetColumnName,
              kanban_columns: updated_columns,
            })
          }
        },
      }
    })
  
  return [
    {
      group: __('Move to'),
      hideLabel: true,
      items: allColumns,
    },
  ]
}

function actions(itemName) {
  let mobile_no = getRow(itemName, 'mobile_no')?.label || ''
  let actions = [
    {
      icon: h(PhoneIcon, { class: 'h-4 w-4' }),
      label: __('Make a Call'),
      onClick: () => makeCall(mobile_no),
      condition: () => mobile_no && callEnabled.value,
    },
    {
      icon: h(NoteIcon, { class: 'h-4 w-4' }),
      label: __('New Note'),
      onClick: () => showNote(itemName),
    },
    {
      icon: h(TaskIcon, { class: 'h-4 w-4' }),
      label: __('New Task'),
      onClick: () => showTask(itemName),
    },
  ]
  return actions.filter((action) =>
    action.condition ? action.condition() : true,
  )
}

const docname = ref('')
const showNoteModal = ref(false)
const note = ref({
  title: '',
  content: '',
})

function showNote(name) {
  docname.value = name
  showNoteModal.value = true
}

const showTaskModal = ref(false)
const task = ref({
  title: '',
  description: '',
  assigned_to: '',
  due_date: '',
  priority: 'Low',
  status: 'Backlog',
})

function showTask(name) {
  docname.value = name
  showTaskModal.value = true
}

// Reminder Modal
const showReminderModal = ref(false)
const selectedLeadId = ref('')
const selectedLeadName = ref('')

function openReminderModal(itemName) {
  selectedLeadId.value = itemName
  selectedLeadName.value = getRow(itemName, 'lead_name')?.label || itemName
  showReminderModal.value = true
}

// Lead Details Modal
const showLeadDetailsModal = ref(false)

function showLeadDetails(itemName) {
  // Update the selected lead ID
  selectedLeadId.value = itemName
  // If sidebar is already open, just update the lead ID (will trigger reload)
  // If sidebar is closed, open it
  if (!showLeadDetailsModal.value) {
    showLeadDetailsModal.value = true
  }
  // Note: If sidebar is already open, the LeadDetailsModal component's watch on leadId
  // will automatically reload the data for the new lead
}

// Meta Leads Sync
const syncing = ref(false)

async function syncMetaLeads() {
  syncing.value = true
  try {
    const result = await call('crm_essenceerp.crm_for_meta_leads.doctype.meta_config.meta_config.sync_meta_leads_now')
    
    // The call function returns the message directly
    if (result && result.success) {
      const leadsCreated = result.leads_created || 0
      // Refresh the leads list
      if (viewControls.value && viewControls.value.refresh) {
        viewControls.value.refresh()
      } else {
        // Trigger a reload by updating loadMore
        loadMore.value++
      }
      // Show success toast notification
      if (leadsCreated > 0) {
        toast.success(__('Successfully created {0} new lead(s) from Meta API.', [leadsCreated]))
      } else {
        toast.success(__('Sync completed. No new leads found. All leads are up to date.'))
      }
    } else if (result && result.error) {
      // Show error toast notification
      toast.error(result.error || __('An error occurred during sync. Please check Error Log.'))
    }
  } catch (error) {
    // Show error toast notification
    toast.error(error.message || __('An unexpected error occurred. Please check Error Log.'))
  } finally {
    syncing.value = false
  }
}

// Search functionality
let searchTimeout = null
const currentSearchTerm = ref('')

function handleSearch() {
  // Debounce search to avoid too many API calls
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  searchTimeout = setTimeout(() => {
    if (!searchQuery.value.trim()) {
      clearSearch()
      return
    }
    
    // Apply search using txt parameter - backend handles OR search across multiple fields
    const searchTerm = searchQuery.value.trim()
    if (viewControls.value && viewControls.value.list) {
      console.log('Applying search for:', searchTerm)
      
      // Store search term
      currentSearchTerm.value = searchTerm
      
      // Set txt parameter on the resource params - getParams() will preserve it
      // The backend API will handle OR search across lead_name, first_name, last_name, email, mobile_no, phone, organization, name
      if (!viewControls.value.list.params) {
        viewControls.value.list.params = {}
      }
      
      viewControls.value.list.params.txt = searchTerm
      
      // Reload using ViewControls reload - it will preserve txt via getParams()
      console.log('Reloading with search txt:', searchTerm)
      viewControls.value.reload()
    } else {
      console.error('ViewControls or list not available')
    }
  }, 300) // 300ms debounce
}

function clearSearch() {
  searchQuery.value = ''
  currentSearchTerm.value = ''
  
  // Clear search and reload
  if (viewControls.value && viewControls.value.list) {
    console.log('Clearing search')
    
    // Remove txt parameter - getParams() won't include it anymore
    if (viewControls.value.list.params) {
      delete viewControls.value.list.params.txt
    }
    
    // Reload using ViewControls reload
    console.log('Reloading without search')
    viewControls.value.reload()
  } else {
    console.error('ViewControls or list not available for clear')
  }
}
</script>
