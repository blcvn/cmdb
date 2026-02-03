<template>
  <a-card :bordered="false">
    <div class="relation-type-description" style="margin-bottom: 15px; padding: 12px; background-color: #f5f5f5; border-radius: 4px;">
      <div style="font-weight: 500; margin-bottom: 8px;">{{ $t('cmdb.relation_type.functionDescription') }}</div>
      <div style="color: #666; line-height: 1.6;">
        {{ $t('cmdb.relation_type.functionDetail') }}
      </div>
      <div style="margin-top: 8px; color: #666;">
        <strong>{{ $t('cmdb.relation_type.impactScale') }}:</strong>
        <ul style="margin: 4px 0 0 20px; padding: 0;">
          <li>{{ $t('cmdb.relation_type.impactNone') }} = 0 {{ $t('cmdb.relation_type.points') }}</li>
          <li>{{ $t('cmdb.relation_type.impactLow') }} = 2 {{ $t('cmdb.relation_type.points') }}</li>
          <li>{{ $t('cmdb.relation_type.impactMedium') }} = 5 {{ $t('cmdb.relation_type.points') }}</li>
          <li>{{ $t('cmdb.relation_type.impactHigh') }} = 7 {{ $t('cmdb.relation_type.points') }}</li>
          <li>{{ $t('cmdb.relation_type.impactCritical') }} = 10 {{ $t('cmdb.relation_type.points') }}</li>
        </ul>
      </div>
    </div>
    <div class="action-btn">
      <a-button @click="handleCreate" type="primary" style="margin-bottom: 15px;">{{ $t('cmdb.relation_type.addRelationType') }}</a-button>
    </div>
    <vxe-table
      ref="relationTypeTable"
      :data="tableData"
      keep-source
      highlight-hover-row
      :edit-config="{ trigger: 'manual', mode: 'row' }"
      @edit-closed="handleEditClose"
      stripe
      class="ops-stripe-table"
      bordered
    >
      <vxe-table-column
        field="name"
        :title="$t('name')"
        :edit-render="{ name: 'input', attrs: { type: 'text' }, events: { keyup: customCloseEdit } }"
      ></vxe-table-column>
      <vxe-table-column
        field="description"
        :title="$t('cmdb.relation_type.description')"
        :edit-render="{ name: 'input', attrs: { type: 'text', placeholder: $t('cmdb.relation_type.descriptionPlaceholder') } }"
        show-overflow
      >
        <template #default="{row}">
          {{ row.description || '-' }}
        </template>
      </vxe-table-column>
      <vxe-table-column
        field="first_ci_to_second_ci_impact"
        :title="$t('cmdb.relation_type.firstToSecondImpact')"
        :edit-render="{}"
      >
        <template #default="{row}">
          {{ getImpactLabel(row.first_ci_to_second_ci_impact) }}
        </template>
        <template #edit="{ row }">
          <vxe-select v-model="row.first_ci_to_second_ci_impact" transfer>
            <vxe-option
              v-for="option in impactOptions"
              :key="option.value"
              :value="option.value"
              :label="option.label"
            ></vxe-option>
          </vxe-select>
        </template>
      </vxe-table-column>
      <vxe-table-column
        field="second_ci_to_first_ci_impact"
        :title="$t('cmdb.relation_type.secondToFirstImpact')"
        :edit-render="{}"
      >
        <template #default="{row}">
          {{ getImpactLabel(row.second_ci_to_first_ci_impact) }}
        </template>
        <template #edit="{ row }">
          <vxe-select v-model="row.second_ci_to_first_ci_impact" transfer>
            <vxe-option
              v-for="option in impactOptions"
              :key="option.value"
              :value="option.value"
              :label="option.label"
            ></vxe-option>
          </vxe-select>
        </template>
      </vxe-table-column>
      <vxe-table-column field="updateTime" :title="$t('updated_at')">
        <template #default="{row}">
          {{ row.updated_at || row.created_at }}
        </template>
      </vxe-table-column>
      <vxe-table-column field="operation" :title="$t('operation')" align="center">
        <template #default="{row}">
          <template>
            <a><a-icon type="edit" @click="handleEdit(row)"/></a>
            <a-divider type="vertical" />
            <a-popconfirm :title="$t('confirmDelete')" @confirm="handleDelete(row)" :okText="$t('yes')" :cancelText="$t('no')">
              <a :style="{ color: 'red' }"><a-icon type="delete"/></a>
            </a-popconfirm>
          </template>
        </template>
      </vxe-table-column>
    </vxe-table>
  </a-card>
</template>

<script>
import moment from 'moment'
import {
  getRelationTypes,
  deleteRelationType,
  addRelationType,
  updateRelationType,
} from '@/modules/cmdb/api/relationType'

export default {
  name: 'RelationType',
  components: {},
  data() {
    return {
      tableData: [],
    }
  },

  computed: {
    impactOptions() {
      return [
        { label: this.$t('cmdb.relation_type.impactNone'), value: 0 },
        { label: this.$t('cmdb.relation_type.impactLow'), value: 2 },
        { label: this.$t('cmdb.relation_type.impactMedium'), value: 5 },
        { label: this.$t('cmdb.relation_type.impactHigh'), value: 7 },
        { label: this.$t('cmdb.relation_type.impactCritical'), value: 10 },
      ]
    },
  },
  mounted() {
    this.loadData()
  },

  methods: {
    loadData() {
      getRelationTypes().then((res) => {
        this.tableData = res
      })
    },
    handleEdit(row) {
      const $table = this.$refs.relationTypeTable
      $table.setActiveRow(row)
    },
    handleCreate() {
      const $table = this.$refs.relationTypeTable
      const newRow = {
        name: '',
        description: '',
        first_ci_to_second_ci_impact: 0,
        second_ci_to_first_ci_impact: 0,
        created_at: moment().format('YYYY-MM-DD hh:mm:ss'),
      }
      $table.insert(newRow).then(({ row }) => $table.setActiveRow(row))
    },
    handleEditClose({ row, rowIndex, column }) {
      const $table = this.$refs.relationTypeTable
      if (row.id) {
        // Update existing relation type
        const updateData = {}
        let hasChanges = false

        if (row.name && $table.isUpdateByRow(row, 'name')) {
          updateData.name = row.name
          hasChanges = true
        }
        if ($table.isUpdateByRow(row, 'description')) {
          updateData.description = row.description || null
          hasChanges = true
        }
        if ($table.isUpdateByRow(row, 'first_ci_to_second_ci_impact')) {
          updateData.first_ci_to_second_ci_impact = row.first_ci_to_second_ci_impact !== undefined ? row.first_ci_to_second_ci_impact : 0
          hasChanges = true
        }
        if ($table.isUpdateByRow(row, 'second_ci_to_first_ci_impact')) {
          updateData.second_ci_to_first_ci_impact = row.second_ci_to_first_ci_impact !== undefined ? row.second_ci_to_first_ci_impact : 0
          hasChanges = true
        }

        if (hasChanges) {
          this.updateRelationType(row.id, updateData)
        } else {
          $table.revertData(row)
        }
      } else {
        // Create new relation type
        if (row.name) {
          this.createRelationType({
            name: row.name,
            description: row.description || null,
            first_ci_to_second_ci_impact: row.first_ci_to_second_ci_impact !== undefined ? row.first_ci_to_second_ci_impact : 0,
            second_ci_to_first_ci_impact: row.second_ci_to_first_ci_impact !== undefined ? row.second_ci_to_first_ci_impact : 0,
          })
        } else {
          this.loadData()
        }
      }
    },
    getImpactLabel(value) {
      const impact = this.impactOptions.find(opt => opt.value === value)
      return impact ? impact.label : this.$t('cmdb.relation_type.impactNone')
    },
    updateRelationType(id, data) {
      updateRelationType(id, data).then((res) => {
        this.$message.success(this.$t('updateSuccess'))
        this.loadData()
      })
    },

    createRelationType(data) {
      addRelationType(data).then((res) => {
        this.$message.success(this.$t('addSuccess'))
        this.loadData()
      })
    },
    handleDelete(record) {
      this.deleteRelationType(record.id)
    },
    deleteRelationType(id) {
      deleteRelationType(id).then((res) => {
        this.$message.success(this.$t('deleteSuccess'))
        this.loadData()
      })
    },
    customCloseEdit(value, $event) {
      // enter, close edit
      if ($event.keyCode === 13) {
        const $table = this.$refs.relationTypeTable
        $table.clearActived()
      }
    },
  },
  watch: {},
}
</script>

<style lang="less" scoped></style>
