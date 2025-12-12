<template>
  <div class="model-relation">
    <a-button @click="handleCreate" type="primary" style="margin-bottom: 15px;" icon="plus">{{
      $t('cmdb.ciType.addRelation')
    }}</a-button>
    <model-relation-table ref="table"></model-relation-table>
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
          <CMDBTypeSelectAntd
            v-decorator="[
              'source_ci_type_id',
              { rules: [{ required: true, message: $t('cmdb.ciType.sourceCITypeTips') }] },
            ]"
            name="source_ci_type_id"
            :CITypeGroup="CITypeGroups"
            @change="handleSourceTypeChange"
          />
        </a-form-item>
        <a-form-item :label="$t('cmdb.ciType.dstCIType')">
          <CMDBTypeSelectAntd
            v-decorator="[
              'ci_type_id',
              { rules: [{ required: true, message: $t('cmdb.ciType.dstCITypeTips') }] },
            ]"
            name="ci_type_id"
            :CITypeGroup="CITypeGroups"
            @change="handleTargetTypeChange"
          />
        </a-form-item>

        <a-form-item :label="$t('cmdb.ciType.relationType')">
          <a-select
            name="relation_type_id"
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
                      <a-select-option v-for="attr in filterAttributes(modalParentAttributes)" :key="attr.id" :title="attr.alias || attr.name">
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
                        <a-select-option value="contains">Contains (parent contains child)</a-select-option>
                        <a-select-option value="contains_parent">Contains Parent (child contains parent)</a-select-option>
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
  </div>
</template>

<script>
import { searchResourceType } from '@/modules/acl/api/resource'
import { getCITypeGroupsConfig } from '@/modules/cmdb/api/ciTypeGroup'
import { getCITypes } from '@/modules/cmdb/api/CIType'
import { createRelation, deleteRelation, getRelationTypes } from '@/modules/cmdb/api/CITypeRelation'
import { getCITypeAttributesById } from '@/modules/cmdb/api/CITypeAttr'
import { v4 as uuidv4 } from 'uuid'

import ModelRelationTable from './modules/modelRelationTable.vue'
import CMDBTypeSelectAntd from '@/modules/cmdb/components/cmdbTypeSelect/cmdbTypeSelectAntd'

export default {
  name: 'Index',
  components: {
    ModelRelationTable,
    CMDBTypeSelectAntd
  },
  data() {
    return {
      resource_type: {},
      CITypeGroups: [],
      currentId: null,

      form: this.$form.createForm(this),

      visible: false,

      drawerTitle: '',
      CITypes: [],
      relationTypes: [],

      sourceCITypeId: undefined,
      targetCITypeId: undefined,

      modalParentAttributes: [],
      modalChildAttributes: [],
      modalAttrList: [],
    }
  },
  computed: {
    currentCId() {
      if (this.currentId) {
        if (this.currentId.split('%')[1] !== 'null') {
          return Number(this.currentId.split('%')[1])
        }
        return null
      }
      return null
    },
    displayCITypes() {
      return this.CITypes
      // return this.CITypes.filter((c) => c.id !== this.targetCITypeId)
    },
    displayTargetCITypes() {
      return this.CITypes
      // return this.CITypes.filter((c) => c.id !== this.sourceCITypeId)
    },
    CITypeId() {
      return this.currentCId
    },
    constraintMap() {
      return {
        '0': this.$t('cmdb.ciType.one2Many'),
        '1': this.$t('cmdb.ciType.one2One'),
        '2': this.$t('cmdb.ciType.many2Many'),
      }
    },
  },
  provide() {
    return {
      resource_type: () => {
        return this.resource_type
      },
    }
  },
  created() {
    this.getCITypes()
    this.getRelationTypes()
  },
  mounted() {
    const _currentId = localStorage.getItem('ops_cityps_currentId')
    if (_currentId) {
      this.currentId = _currentId
    }
    searchResourceType({ page_size: 9999, app_id: 'cmdb' }).then((res) => {
      this.resource_type = { groups: res.groups, id2perms: res.id2perms }
    })
    this.loadCITypes(!_currentId)
  },
  methods: {
    async loadCITypes(isResetCurrentId = false) {
      const groups = await getCITypeGroupsConfig({ need_other: true })
      let alreadyReset = false
      if (isResetCurrentId) {
        this.currentId = null
      }
      this.$nextTick(() => {
        groups.forEach((g) => {
          if (!g.id) {
            g.id = -1
          }
          if (isResetCurrentId && !alreadyReset && g.ci_types && g.ci_types.length) {
            this.currentId = `${g.id}%${g.ci_types[0].id}%${g.ci_types[0].name}`
            alreadyReset = true
          }
          if (!g.ci_types) {
            g.ci_types = []
          }
        })
        this.CITypeGroups = groups
        localStorage.setItem('ops_cityps_currentId', this.currentId)
      })
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
          source_ci_type_id: this.sourceCITypeId,
        })
      })
    },
    onClose() {
      this.form.resetFields()
      this.visible = false
      this.sourceCITypeId = undefined
      this.targetCITypeId = undefined
    },
    handleSubmit(e) {
      e.preventDefault()
      this.form.validateFields((err, values) => {
        if (!err) {
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
            this.handleOk()
          })
        }
      })
      this.sourceCITypeId = undefined
      this.targetCITypeId = undefined
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

    handleOk() {
      this.$refs.table.refresh()
    },
    handleDelete(record) {
      deleteRelation(record.source_ci_type_id, record.id).then((res) => {
        this.$message.success(this.$t('deleteSuccess'))

        this.handleOk()
      })
    },
    handleSourceTypeChange(value) {
      this.sourceCITypeId = value
      this.modalAttrList.forEach((item) => {
        item.parentAttrId = undefined
      })
      getCITypeAttributesById(value).then((res) => {
        this.modalParentAttributes = res?.attributes ?? []
      })
    },
    handleTargetTypeChange(value) {
      this.targetCITypeId = value
      this.modalAttrList.forEach((item) => {
        item.childAttrId = undefined
      })
      getCITypeAttributesById(value).then((res) => {
        this.modalChildAttributes = res?.attributes ?? []
      })
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
.model-relation {
  background-color: #fff;
  border-radius: @border-radius-box;
  padding: 24px;
  height: calc(100vh - 64px);
  margin-bottom: -24px;
}

.modal-attribute-action {
  margin-left: 5px;
}

.model-select-name {
  font-size: 12px;
  color: #A5A9BC;
}
</style>
