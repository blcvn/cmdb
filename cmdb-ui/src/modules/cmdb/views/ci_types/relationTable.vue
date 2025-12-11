<template>
  <div class="relation-table" :style="{ padding: '0 20px 20px' }">
    <div v-if="!isInGrantComp" class="relation-table-add">
      <a-button
        type="primary"
        @click="handleCreate"
        ghost
        class="ops-button-ghost"
      >
        <ops-icon type="veops-increase" />
        {{ $t('create') }}
      </a-button>
    </div>
    <vxe-table
      ref="xTable"
      stripe
      :data="tableData"
      size="small"
      show-overflow
      show-header-overflow
      highlight-hover-row
      keep-source
      class="ops-stripe-table"
      min-height="500"
      :row-class-name="rowClass"
      :edit-config="{ trigger: 'dblclick', mode: 'cell', showIcon: false }"
      resizable
      @edit-closed="handleEditClose"
      @edit-actived="handleEditActived"
    >
      <vxe-column field="source_ci_type_name" :title="$t('cmdb.ciType.sourceCIType')"></vxe-column>
      <vxe-column field="relation_type" :title="$t('cmdb.ciType.relationType')">
        <template #default="{row}">
          <span class="primary-color" v-if="row.isParent">{{ $t('cmdb.ciType.isParent') }}</span>
          {{ row.relation_type }}
        </template>
      </vxe-column>
      <vxe-column field="alias" :title="$t('cmdb.ciType.dstCIType')"></vxe-column>
      <vxe-column field="constraint" :title="$t('cmdb.ciType.relationConstraint')">
        <template #default="{row}">
          <span v-if="row.isParent && constraintMap[row.constraint]">{{
            constraintMap[row.constraint]
              .split(' ')
              .reverse()
              .join(' ')
          }}</span>
          <span v-else>{{ constraintMap[row.constraint] }}</span>
        </template>
      </vxe-column>
      <vxe-column :width="300" field="attributeAssociation" :edit-render="{}">
        <template #header>
          <span>
            <a-tooltip :title="$t('cmdb.ciType.attributeAssociationTip1')">
              <a><a-icon type="question-circle"/></a>
            </a-tooltip>
            {{ $t('cmdb.ciType.attributeAssociation') }}
            <span :style="{ fontSize: '10px', fontWeight: 'normal' }" class="text-color-4">{{
              $t('cmdb.ciType.attributeAssociationTip2')
            }}</span>
          </span>
        </template>
        <template #default="{row}">
          <template
            v-for="item in row.parentAndChildAttrList"
          >
            <div
              :key="item.id"
              v-if="item.parentAttrId && item.childAttrId"
              :style="{ marginBottom: '6px', padding: '4px 0', lineHeight: '1.5' }"
            >
              <span :style="{ fontWeight: '500', marginRight: '4px' }">
                {{ getAttrNameById(row.isParent ? row.attributes : attributes, item.parentAttrId) }}
              </span>
              <span :style="{ margin: '0 6px', color: '#1890ff' }">→</span>
              <span :style="{ fontWeight: '500', marginRight: '8px' }">
                {{ getAttrNameById(row.isParent ? attributes : row.attributes, item.childAttrId) }}
              </span>
              <a-tag v-if="item.operator && item.operator !== 'equals'" color="blue" size="small">
                {{ item.operator }}
              </a-tag>
            </div>
          </template>
        </template>
        <template #edit="{ row }">
          <div
            v-for="item in tableAttrList"
            :key="item.id"
            class="table-attribute-row"
          >
            <a-select
              allowClear
              size="small"
              v-model="item.parentAttrId"
              :getPopupContainer="(trigger) => trigger.parentNode"
              :style="{ width: '120px', minWidth: '120px' }"
              show-search
              optionFilterProp="title"
              :placeholder="'Parent'"
            >
              <a-select-option
                v-for="attr in filterAttributes(row.isParent ? row.attributes : attributes)"
                :key="attr.id"
                :value="attr.id"
                :title="attr.alias || attr.name"
              >
                {{ attr.alias || attr.name }}
              </a-select-option>
            </a-select>
            <span class="table-attribute-row-link" :style="{ margin: '0 6px', fontSize: '14px' }">→</span>
            <a-select
              allowClear
              size="small"
              v-model="item.childAttrId"
              :getPopupContainer="(trigger) => trigger.parentNode"
              :style="{ width: '120px', minWidth: '120px' }"
              show-search
              optionFilterProp="title"
              :placeholder="'Child'"
            >
              <a-select-option
                v-for="attr in filterAttributes(row.isParent ? attributes : row.attributes)"
                :key="attr.id"
                :value="attr.id"
                :title="attr.alias || attr.name"
              >
                {{ attr.alias || attr.name }}
              </a-select-option>
            </a-select>
            <a
              class="table-attribute-row-action"
              @click="removeTableAttr(item.id)"
            >
              <a-icon type="minus-circle" />
            </a>
            <a
              class="table-attribute-row-action"
              @click="addTableAttr"
            >
              <a-icon type="plus-circle" />
            </a>
          </div>
          <!-- Matching Rules in Table Edit -->
          <div v-if="item.parentAttrId && item.childAttrId" :style="{ marginTop: '10px', padding: '8px', backgroundColor: '#f5f5f5', borderRadius: '4px' }">
            <a-row :gutter="8" type="flex" align="middle">
              <a-col :span="7">
                <a-select
                  v-model="item.operator"
                  placeholder="Operator"
                  size="small"
                  :style="{ width: '100%' }"
                  allowClear
                >
                  <a-select-option value="equals">Equals</a-select-option>
                  <a-select-option value="contains">Contains</a-select-option>
                  <a-select-option value="in_list">In List</a-select-option>
                  <a-select-option value="has_one">Has One</a-select-option>
                  <a-select-option value="compare">Compare</a-select-option>
                </a-select>
              </a-col>
              <a-col :span="8" v-if="item.operator && ['in_list', 'has_one'].includes(item.operator)">
                <a-input
                  v-model="item.separator"
                  placeholder="Separator (multi-char OK)"
                  size="small"
                  :style="{ width: '100%' }"
                >
                  <a-tooltip slot="suffix" title="Supports multi-character separators">
                    <a-icon type="info-circle" style="color: rgba(0,0,0,.45)" />
                  </a-tooltip>
                </a-input>
              </a-col>
              <a-col :span="9" v-if="item.operator === 'in_list'">
                <a-input-group compact>
                  <a-input
                    v-model="item.parentSeparator"
                    placeholder="Parent Sep"
                    size="small"
                    :style="{ width: '50%' }"
                  />
                  <a-input
                    v-model="item.childSeparator"
                    placeholder="Child Sep"
                    size="small"
                    :style="{ width: '50%' }"
                  />
                </a-input-group>
              </a-col>
            </a-row>
          </div>
        </template>
      </vxe-column>
      <vxe-column field="operation" :title="$t('operation')" width="100">
        <template #default="{row}">
          <a-space v-if="!row.isParent && row.source_ci_type_id">
            <a @click="handleOpenGrant(row)"><a-icon type="user-add"/></a>
            <a-popconfirm v-if="!isInGrantComp" :title="$t('cmdb.ciType.confirmDelete2')" @confirm="handleDelete(row)">
              <a style="color: red;"><a-icon type="delete"/></a>
            </a-popconfirm>
          </a-space>
        </template>
      </vxe-column>
      <template #empty>
        <div>
          <img :style="{ width: '100px' }" :src="require('@/assets/data_empty.png')" />
          <div>{{ $t('noData') }}</div>
        </div>
      </template>
    </vxe-table>
    <a-modal
      :closable="false"
      :title="drawerTitle"
      :visible="visible"
      @cancel="onClose"
      @ok="handleSubmit"
      width="900px"
      :bodyStyle="{ maxHeight: '70vh', overflowY: 'auto' }"
    >
      <a-form :form="form" @submit="handleSubmit" :label-col="{ span: 6 }" :wrapper-col="{ span: 14 }">
        <a-form-item :label="$t('cmdb.ciType.sourceCIType')">
          <a-select
            name="source_ci_type_id"
            :placeholder="$t('cmdb.ciType.sourceCITypeTips')"
            v-decorator="[
              'source_ci_type_id',
              { rules: [{ required: true, message: $t('cmdb.ciType.sourceCITypeTips') }] },
            ]"
          >
            <a-select-option :value="CIType.id" :key="CIType.id" v-for="CIType in displayCITypes">{{
              CIType.alias
            }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="$t('cmdb.ciType.dstCIType')">
          <CMDBTypeSelectAntd
            v-decorator="['ci_type_id', { rules: [{ required: true, message: $t('cmdb.ciType.dstCITypeTips') }] }]"
            name="ci_type_id"
            :placeholder="$t('cmdb.ciType.dstCITypeTips')"
            @change="changeChild"
          />
        </a-form-item>

        <a-form-item :label="$t('cmdb.ciType.relationType')">
          <a-select
            name="relation_type_id"
            :placeholder="$t('cmdb.ciType.relationTypeTips')"
            v-decorator="[
              'relation_type_id',
              { rules: [{ required: true, message: $t('cmdb.ciType.relationTypeTips') }] },
            ]"
          >
            <a-select-option :value="relationType.id" :key="relationType.id" v-for="relationType in relationTypes">{{
              relationType.name
            }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="$t('cmdb.ciType.relationConstraint')">
          <a-select
            :placeholder="$t('cmdb.ciType.relationConstraintTips')"
            v-decorator="[
              'constraint',
              { rules: [{ required: true, message: $t('cmdb.ciType.relationConstraintTips') }] },
            ]"
          >
            <a-select-option value="0">{{ $t('cmdb.ciType.one2Many') }}</a-select-option>
            <a-select-option value="1">{{ $t('cmdb.ciType.one2One') }}</a-select-option>
            <a-select-option value="2">{{ $t('cmdb.ciType.many2Many') }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item :label="$t('cmdb.ciType.attributeAssociation')">
          <a-row
            v-for="item in modalAttrList"
            :key="item.id"
            :style="{ marginBottom: '15px', padding: '15px', border: '1px solid #e8e8e8', borderRadius: '4px', backgroundColor: '#fafafa' }"
          >
            <a-col :span="24">
              <a-row :gutter="12" :style="{ marginBottom: '10px' }">
                <a-col :span="9">
                  <a-form-item label="Parent Attribute" :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
                    <a-select
                      :placeholder="$t('cmdb.ciType.attributeAssociationTip4')"
                      allowClear
                      v-model="item.parentAttrId"
                      show-search
                      option-filter-prop="children"
                    >
                      <a-select-option v-for="attr in filterAttributes(attributes)" :key="attr.id" :title="attr.alias || attr.name">
                        {{ attr.alias || attr.name }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="1" :style="{ textAlign: 'center', lineHeight: '40px', fontSize: '16px', fontWeight: 'bold', color: '#1890ff' }">
                  →
                </a-col>
                <a-col :span="9">
                  <a-form-item label="Child Attribute" :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
                    <a-select
                      :placeholder="$t('cmdb.ciType.attributeAssociationTip5')"
                      allowClear
                      v-model="item.childAttrId"
                      show-search
                      option-filter-prop="children"
                    >
                      <a-select-option v-for="attr in filterAttributes(modalChildAttributes)" :key="attr.id" :title="attr.alias || attr.name">
                        {{ attr.alias || attr.name }}
                      </a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :span="5" :style="{ textAlign: 'right', paddingTop: '30px' }">
                  <a-button
                    type="danger"
                    size="small"
                    icon="minus-circle"
                    @click="removeModalAttr(item.id)"
                    :style="{ marginRight: '8px' }"
                  />
                  <a-button
                    type="primary"
                    size="small"
                    icon="plus-circle"
                    @click="addModalAttr"
                  />
                </a-col>
              </a-row>
              <!-- Matching Rules Configuration -->
              <a-divider v-if="item.parentAttrId && item.childAttrId" :style="{ margin: '10px 0' }" />
              <div v-if="item.parentAttrId && item.childAttrId" :style="{ padding: '10px', backgroundColor: '#fff', borderRadius: '4px' }">
                <a-row :gutter="12">
                  <a-col :span="8">
                    <a-form-item label="Matching Operator" :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
                      <a-select
                        v-model="item.operator"
                        placeholder="Select operator (default: equals)"
                        :style="{ width: '100%' }"
                        allowClear
                      >
                        <a-select-option value="equals">Equals (exact match)</a-select-option>
                        <a-select-option value="contains">Contains</a-select-option>
                        <a-select-option value="in_list">In List</a-select-option>
                        <a-select-option value="has_one">Has One</a-select-option>
                        <a-select-option value="compare">Compare (numeric)</a-select-option>
                      </a-select>
                    </a-form-item>
                  </a-col>
                  <a-col :span="8" v-if="item.operator && ['in_list', 'has_one'].includes(item.operator)">
                    <a-form-item label="Separator (supports multi-char)" :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
                      <a-input
                        v-model="item.separator"
                        placeholder="Default: , (supports multi-character)"
                        :style="{ width: '100%' }"
                      >
                        <a-tooltip slot="suffix" title="Supports multi-character separators, e.g., ', ' or ' || '">
                          <a-icon type="question-circle" style="color: rgba(0,0,0,.45)" />
                        </a-tooltip>
                      </a-input>
                    </a-form-item>
                  </a-col>
                  <a-col :span="8" v-if="item.operator === 'in_list'">
                    <a-row :gutter="8">
                      <a-col :span="12">
                        <a-form-item label="Parent Separator" :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
                          <a-input
                            v-model="item.parentSeparator"
                            placeholder="Default: ,"
                            :style="{ width: '100%' }"
                          />
                        </a-form-item>
                      </a-col>
                      <a-col :span="12">
                        <a-form-item label="Child Separator" :label-col="{ span: 24 }" :wrapper-col="{ span: 24 }">
                          <a-input
                            v-model="item.childSeparator"
                            placeholder="Default: ,"
                            :style="{ width: '100%' }"
                          />
                        </a-form-item>
                      </a-col>
                    </a-row>
                  </a-col>
                </a-row>
              </div>
            </a-col>
          </a-row>
        </a-form-item>
      </a-form>
    </a-modal>
    <CMDBGrant ref="cmdbGrant" resourceType="CITypeRelation" app_id="cmdb" />
  </div>
</template>

<script>
import {
  createRelation,
  deleteRelation,
  getCITypeChildren,
  getCITypeParent,
  getRelationTypes,
} from '@/modules/cmdb/api/CITypeRelation'
import { getCITypes } from '@/modules/cmdb/api/CIType'
import { getCITypeAttributesById } from '@/modules/cmdb/api/CITypeAttr'
import { v4 as uuidv4 } from 'uuid'

import CMDBGrant from '@/modules/cmdb/components/cmdbGrant'
import CMDBTypeSelectAntd from '@/modules/cmdb/components/cmdbTypeSelect/cmdbTypeSelectAntd'

export default {
  name: 'RelationTable',
  components: {
    CMDBGrant,
    CMDBTypeSelectAntd
  },
  props: {
    CITypeId: {
      type: Number,
      default: null,
    },
    CITypeName: {
      type: String,
      default: '',
    },
    isInGrantComp: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      form: this.$form.createForm(this),
      visible: false,
      drawerTitle: '',
      CITypes: [],
      relationTypes: [],
      tableData: [],
      parentTableData: [],
      attributes: [],
      tableAttrList: [],
      modalAttrList: [],
      modalChildAttributes: [],
      currentEditData: null,
      isContinueCloseEdit: false,
    }
  },
  computed: {
    displayCITypes() {
      return this.CITypes.filter((c) => c.id === this.CITypeId)
    },
    windowHeight() {
      return this.$store.state.windowHeight
    },
    constraintMap() {
      return {
        '0': this.$t('cmdb.ciType.one2Many'),
        '1': this.$t('cmdb.ciType.one2One'),
        '2': this.$t('cmdb.ciType.many2Many'),
      }
    },
  },
  async mounted() {
    getCITypeAttributesById(this.CITypeId).then((res) => {
      this.attributes = res?.attributes ?? []
    })
    this.getCITypes()
    this.getRelationTypes()
    this.getData()
  },
  methods: {
    async getData() {
      if (!this.isInGrantComp) {
        await this.getCITypeParent()
      }
      await this.getCITypeChildren()
    },
    async getCITypeParent() {
      await getCITypeParent(this.CITypeId).then((res) => {
        this.parentTableData = res.parents.map((item) => {
          const parentAndChildAttrList = this.handleAttrList(item)

          return {
            ...item,
            parentAndChildAttrList,
            source_ci_type_name: this.CITypeName,
            source_ci_type_id: this.CITypeId,
            isParent: true,
          }
        })
      })
    },
    async getCITypeChildren() {
      await getCITypeChildren(this.CITypeId).then((res) => {
        const data = res.children.map((obj) => {
          const parentAndChildAttrList = this.handleAttrList(obj)

          return {
            ...obj,
            parentAndChildAttrList,
            source_ci_type_name: this.CITypeName,
            source_ci_type_id: this.CITypeId,
          }
        })
        if (this.parentTableData && this.parentTableData.length) {
          this.tableData = [...data, { isDivider: true }, ...this.parentTableData]
        } else {
          this.tableData = data
        }
      })
    },

    handleAttrList(data) {
      const length = Math.min(data?.parent_attr_ids?.length || 0, data.child_attr_ids?.length || 0)
      const parentAndChildAttrList = []
      const matching_rules = data?.matching_rules || []

      for (let i = 0; i < length; i++) {
        const parentAttrId = data?.parent_attr_ids?.[i]
        const childAttrId = data?.child_attr_ids?.[i]

        // Find matching rule for this attribute pair
        const rule = matching_rules.find(r =>
          r.parent_attr_id === parentAttrId && r.child_attr_id === childAttrId
        )

        parentAndChildAttrList.push({
          id: uuidv4(),
          parentAttrId: parentAttrId ?? '',
          childAttrId: childAttrId ?? '',
          operator: rule?.operator || undefined,
          separator: rule?.separator || ',',
          parentSeparator: rule?.parent_separator || undefined,
          childSeparator: rule?.child_separator || undefined
        })
      }
      return parentAndChildAttrList
    },

    getCITypes() {
      getCITypes().then((res) => {
        this.CITypes = res.ci_types
      })
    },
    getRelationTypes() {
      getRelationTypes().then((res) => {
        this.relationTypes = res
      })
    },
    handleDelete(record) {
      deleteRelation(record.source_ci_type_id, record.id).then((res) => {
        this.$message.success(this.$t('deleteSuccess'))
        this.getData()
      })
    },

    handleCreate() {
      this.drawerTitle = this.$t('cmdb.ciType.addRelation')
      this.visible = true
      this.$set(this, 'modalAttrList', [
        {
          id: uuidv4(),
          parentAttrId: undefined,
          childAttrId: undefined,
          operator: undefined,
          separator: ',',
          parentSeparator: undefined,
          childSeparator: undefined
        }
      ])
      this.$nextTick(() => {
        this.form.setFieldsValue({
          source_ci_type_id: this.CITypeId,
        })
      })
    },

    onClose() {
      this.form.resetFields()
      this.visible = false
    },

    handleSubmit(e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
          // eslint-disable-next-line no-console
          console.log('Received values of form: ', values)
          const {
            source_ci_type_id,
            ci_type_id,
            relation_type_id,
            constraint,
          } = values

          const {
            parent_attr_ids,
            child_attr_ids,
            matching_rules,
            validate
          } = this.handleValidateAttrList(this.modalAttrList)
          if (!validate) {
            return
          }

          const payload = {
            relation_type_id,
            constraint,
            parent_attr_ids,
            child_attr_ids,
          }
          if (matching_rules && matching_rules.length > 0) {
            payload.matching_rules = matching_rules
          }

          createRelation(source_ci_type_id, ci_type_id, payload).then((res) => {
            this.$message.success(this.$t('addSuccess'))
            this.onClose()
            this.getData()
          })
        }
      })
    },

    /**
     * 校验属性列表
     * @param {*} attrList
     */
     handleValidateAttrList(attrList) {
      const parent_attr_ids = []
      const child_attr_ids = []
      const matching_rules = []

      attrList.map((attr) => {
        if (attr.parentAttrId && attr.childAttrId) {
          parent_attr_ids.push(attr.parentAttrId)
          child_attr_ids.push(attr.childAttrId)

          // Build matching rule if operator is specified
          if (attr.operator && attr.operator !== 'equals') {
            const rule = {
              parent_attr_id: attr.parentAttrId,
              child_attr_id: attr.childAttrId,
              operator: attr.operator
            }

            // Add separator if needed
            if (['in_list', 'has_one'].includes(attr.operator)) {
              if (attr.separator) {
                rule.separator = attr.separator
              }
            }

            // Add parent/child separators for in_list
            if (attr.operator === 'in_list') {
              if (attr.parentSeparator) {
                rule.parent_separator = attr.parentSeparator
              }
              if (attr.childSeparator) {
                rule.child_separator = attr.childSeparator
              }
            }

            matching_rules.push(rule)
          }
        }
      })

      if (parent_attr_ids.length !== child_attr_ids.length) {
        this.$message.warning(this.$t('cmdb.ciType.attributeAssociationTip3'))
        return {
          validate: false
        }
      }

      return {
        validate: true,
        parent_attr_ids,
        child_attr_ids,
        matching_rules: matching_rules.length > 0 ? matching_rules : undefined
      }
    },

    handleOpenGrant(record) {
      this.$refs.cmdbGrant.open({
        name: `${record.source_ci_type_name} -> ${record.name}`,
        typeRelationIds: [record.source_ci_type_id, record.id],
        cmdbGrantType: 'type_relation',
      })
    },
    rowClass({ row }) {
      if (row.isDivider) return 'relation-table-divider'
      if (row.isParent) return 'relation-table-parent'
    },
    handleEditActived({ row }) {
      this.$nextTick(async () => {
        if (this.isContinueCloseEdit) {
          const editRecord = this.$refs.xTable.getEditRecord()
          const { row: editRow, column } = editRecord
          this.currentEditData = {
            row: editRow,
            column
          }
          return
        }
        const tableAttrList = []

        const length = Math.min(row?.parent_attr_ids?.length || 0, row.child_attr_ids?.length || 0)
        const matching_rules = row?.matching_rules || []

        if (length) {
          for (let i = 0; i < length; i++) {
            const parentAttrId = row?.parent_attr_ids?.[i]
            const childAttrId = row?.child_attr_ids?.[i]

            // Find matching rule for this attribute pair
            const rule = matching_rules.find(r =>
              r.parent_attr_id === parentAttrId && r.child_attr_id === childAttrId
            )

            tableAttrList.push({
              id: uuidv4(),
              parentAttrId: parentAttrId ?? undefined,
              childAttrId: childAttrId ?? undefined,
              operator: rule?.operator || undefined,
              separator: rule?.separator || ',',
              parentSeparator: rule?.parent_separator || undefined,
              childSeparator: rule?.child_separator || undefined
            })
          }
        } else {
          tableAttrList.push({
            id: uuidv4(),
            parentAttrId: undefined,
            childAttrId: undefined,
            operator: undefined,
            separator: ',',
            parentSeparator: undefined,
            childSeparator: undefined
          })
        }
        this.$set(this, 'tableAttrList', tableAttrList)
      })
    },
    async handleEditClose({ row }) {
      if (this.currentEditData) {
        this.currentEditData = null
        return
      }

      this.isContinueCloseEdit = true

      const { source_ci_type_id: parentId, id: childrenId, constraint, relation_type } = row
      const _find = this.relationTypes.find((item) => item.name === relation_type)
      const relation_type_id = _find?.id

      const {
        parent_attr_ids,
        child_attr_ids,
        matching_rules,
        validate
      } = this.handleValidateAttrList(this.tableAttrList)
      if (!validate) {
        this.isContinueCloseEdit = false
        return
      }

      const payload = {
        relation_type_id,
        constraint,
        parent_attr_ids,
        child_attr_ids,
      }
      if (matching_rules && matching_rules.length > 0) {
        payload.matching_rules = matching_rules
      }

      await createRelation(row.isParent ? childrenId : parentId, row.isParent ? parentId : childrenId, payload).finally(async () => {
        await this.getData()
        this.isContinueCloseEdit = false

        if (this.currentEditData) {
          setTimeout(async () => {
            const { fullData } = this.$refs.xTable.getTableData()
            const findEdit = fullData.find((item) => item.id === this?.currentEditData?.row?.id)
            await this.$refs.xTable.setEditRow(findEdit, 'attributeAssociation')
          })
        }
      })
    },
    getAttrNameById(attributes, id) {
      const _find = attributes.find((attr) => attr.id === id)
      return _find?.alias ?? _find?.name ?? id
    },
    changeChild(value) {
      this.modalAttrList.forEach((item) => {
        item.childAttrId = undefined
      })
      if (value) {
        getCITypeAttributesById(value).then((res) => {
          this.modalChildAttributes = res?.attributes ?? []
        })
      }
    },
    filterAttributes(attributes) {
      // filter password/json/is_list/longText/bool/reference
      return attributes.filter((attr) => {
        if (attr.value_type === '2' && !attr.is_index) {
          return false
        }

        return !attr.is_password && !attr.is_list && attr.value_type !== '6' && !attr.is_bool && !attr.is_reference
      })
    },
    addTableAttr() {
      this.tableAttrList.push({
        id: uuidv4(),
        parentAttrId: undefined,
        childAttrId: undefined,
        operator: undefined,
        separator: ',',
        parentSeparator: undefined,
        childSeparator: undefined
      })
    },
    removeTableAttr(id) {
      if (this.tableAttrList.length <= 1) {
        this.$message.error(this.$t('cmdb.ciType.attributeAssociationTip6'))
        return
      }
      const index = this.tableAttrList.findIndex((item) => item.id === id)
      if (index !== -1) {
        this.tableAttrList.splice(index, 1)
      }
    },

    addModalAttr() {
      this.modalAttrList.push({
        id: uuidv4(),
        parentAttrId: undefined,
        childAttrId: undefined,
        operator: undefined,
        separator: ',',
        parentSeparator: undefined,
        childSeparator: undefined
      })
    },

    removeModalAttr(id) {
      if (this.modalAttrList.length <= 1) {
        this.$message.error(this.$t('cmdb.ciType.attributeAssociationTip6'))
        return
      }
      const index = this.modalAttrList.findIndex((item) => item.id === id)
      if (index !== -1) {
        this.modalAttrList.splice(index, 1)
      }
    }
  },
}
</script>

<style lang="less" scoped>
.relation-table {
  /deep/ .vxe-cell {
    max-height: max-content !important;
  }

  &-add {
    margin-bottom: 10px;
    display: flex;
    justify-content: flex-end;
  }
}
.table-attribute-row {
  display: inline-flex;
  align-items: center;
  margin-top: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
  gap: 8px;

  &:last-child {
    margin-bottom: 8px;
  }

  &-link {
    margin: 0 6px;
    font-size: 14px;
    color: #1890ff;
    font-weight: 500;
  }

  &-action {
    margin-left: 8px;
    cursor: pointer;
    color: #1890ff;
    font-size: 16px;
    transition: color 0.3s;

    &:hover {
      color: #40a9ff;
    }
  }
}

.modal-attribute-action {
  margin-left: 5px;
}

.model-select-name {
  font-size: 12px;
  color: #A5A9BC;
}

.ops-stripe-table {
  /deep/ .relation-table-divider {
    background-color: #b1b8d3 !important;

    td {
      height: 2px !important;
      line-height: 2px !important;
    }
  }

  /deep/ .relation-table-parent {
    background-color: @primary-color_5 !important;
  }
}
</style>
