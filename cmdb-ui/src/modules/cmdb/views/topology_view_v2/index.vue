<template>
  <div class="topo-wrap" :style="{ height: `${windowHeight - 96}px` }">
    <a-tabs v-model="activeTab" type="card">
      <a-tab-pane key="filter" tab="Filter View">
        <div class="filter-view-container" :style="{ height: `${windowHeight - 136}px` }">
          <a-card :bordered="false" size="small" style="margin-bottom: 16px">
        <a-form layout="inline" :form="filterForm">
          <a-form-item label="Root CI">
            <CMDBTypeSelectAntd
              v-model="rootCITypeId"
              placeholder="Select CI Type"
              style="width: 200px; margin-right: 8px"
              @change="handleRootCITypeChange"
            />
            <a-input-group compact style="width: 400px">
        <a-input
                v-decorator="['root_ci_id', {
                  rules: [{ required: true, message: 'Root CI is required' }],
                  initialValue: ''
                }]"
                :placeholder="rootCITypeId ? (rootCIName || 'Click button to select instance') : 'Select CI Type first'"
                :disabled="!rootCITypeId"
                readonly
                style="width: calc(100% - 100px)"
              />
            <a-button
              type="primary"
                :disabled="!rootCITypeId"
                @click="handleOpenRootCIDrawer"
                style="width: 100px"
              >
                <a-icon type="search" />
                Select
            </a-button>
            </a-input-group>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handleAddFilterRule" icon="plus">Add Filter Rule</a-button>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="handleFilterGraph" :loading="filterLoading">Filter</a-button>
          </a-form-item>
        </a-form>
        <div v-for="(rule, index) in filterRules" :key="index" style="margin-top: 16px; padding: 12px; border: 1px solid #e8e8e8; border-radius: 4px">
          <a-row :gutter="16">
            <a-col :span="6">
              <a-form-item label="CI Type">
                <CMDBTypeSelectAntd
                  v-model="rule.type_id"
                  placeholder="Select CI Type"
                  @change="(val) => handleFilterRuleCITypeChange(index, val)"
                />
              </a-form-item>
            </a-col>
            <a-col :span="16">
              <a-form-item label="Filters">
                <div v-for="(filter, fIndex) in rule.filters" :key="fIndex" style="margin-bottom: 8px">
                  <a-input-group compact>
                    <a-select
                      v-model="filter.attr"
                      placeholder="Select Attribute"
                      style="width: 40%"
                      :loading="rule.attributesLoading"
                      @change="(val) => handleFilterAttrChange(index, fIndex, val)"
                    >
                      <a-select-option v-for="attr in rule.attributes" :key="attr.id" :value="attr.name">
                        {{ attr.alias || attr.name }}
                      </a-select-option>
                    </a-select>
                    <a-select
                      v-model="filter.values"
                      mode="multiple"
                      placeholder="Select Values"
                      style="width: 50%"
                      :loading="filter.valuesLoading"
                      :disabled="!filter.attr"
                    >
                      <a-select-option v-for="value in filter.distinctValues" :key="value" :value="value">
                        {{ value }}
                      </a-select-option>
                    </a-select>
                    <a-button @click="handleRemoveFilter(index, fIndex)" icon="delete" style="width: 10%"></a-button>
                  </a-input-group>
                  </div>
                <a-button size="small" @click="handleAddFilter(index)" icon="plus">Add Filter</a-button>
              </a-form-item>
            </a-col>
            <a-col :span="2">
              <a-button @click="handleRemoveFilterRule(index)" icon="delete" type="danger"></a-button>
            </a-col>
          </a-row>
                </div>
      </a-card>
      <a-card :bordered="false" size="small">
        <div v-if="filteredNodesGrouped.length === 0" style="text-align: center; padding: 40px">
          <a-empty description="No Data"></a-empty>
            </div>
        <div v-for="(group, groupIndex) in filteredNodesGrouped" :key="groupIndex" style="margin-bottom: 24px">
          <a-card :bordered="true" size="small" :title="group.ci_type" :head-style="{ backgroundColor: '#f0f2f5', fontWeight: 'bold' }">
            <vxe-table
              :ref="`filterTable_${groupIndex}`"
              border
                      size="small"
              show-overflow="tooltip"
              :data="group.nodes"
              :max-height="`${windowHeight - 450}px`"
              resizable
            >
              <vxe-column field="_id" title="ID" width="100"></vxe-column>
              <vxe-column
                v-for="(key, index) in group.keys"
                :key="index"
                :field="key"
                :title="key"
                min-width="150"
              ></vxe-column>
            </vxe-table>
            <div style="margin-top: 8px; color: #8c8c8c; font-size: 12px">
              Total: {{ group.nodes.length }}
                  </div>
          </a-card>
            </div>
      </a-card>
          </div>
      </a-tab-pane>
      <a-tab-pane key="stats" tab="Statistics View">
        <div class="stats-view-container" :style="{ height: `${windowHeight - 136}px`, overflowY: 'auto', padding: '16px' }">
          <a-card :bordered="false" size="small" style="margin-bottom: 16px">
            <a-form layout="inline">
              <a-form-item label="Select CI Type">
          <CMDBTypeSelectAntd
                  v-model="statsTypeId"
                  placeholder="Select CI Type"
                  style="width: 300px"
          />
        </a-form-item>
              <a-form-item>
                <a-button type="primary" @click="handleLoadStats" :loading="statsLoading">Load Statistics</a-button>
        </a-form-item>
            </a-form>
          </a-card>

          <a-card v-if="statsData" :bordered="false" size="small">
            <p><strong>CI Type:</strong> {{ statsData.type_name }}</p>
            <p><strong>Total CIs:</strong> {{ statsData.total_cis }}</p>

            <a-table
              :columns="statsColumns"
              :data-source="statsData.results"
              :pagination="{
                current: statsData.page,
                pageSize: statsData.per_page,
                total: statsData.total_cis,
                showSizeChanger: true,
                showTotal: total => `Total ${total} CIs`,
                pageSizeOptions: ['10', '20', '50', '100']
              }"
              :row-key="record => record.ci_id"
              size="small"
              :scroll="{ x: true }"
              @change="handleStatsTableChange"
            >
              <template #expandedRowRender="record">
                <a-table
                  :columns="statsDetailColumns"
                  :data-source="record.stats"
                  :pagination="false"
                  :row-key="rec => rec.type_id"
                  size="small"
                    />
                  </template>
            </a-table>
          </a-card>
                </div>
      </a-tab-pane>
    </a-tabs>
    <CMDBExprDrawer ref="rootCIDrawer" type="resourceView" :typeId="rootCITypeId" @copySuccess="handleRootCISelect" @selectCI="handleRootCISelectDirect" />
  </div>
</template>
<script>
import { searchCI, getDistinctValues } from '@/modules/cmdb/api/ci'
import { getCITypeAttributesById } from '@/modules/cmdb/api/CITypeAttr'
import { getFilteredGraph, getStatsByType } from '@/modules/cmdb/api/topology'
import CMDBExprDrawer from '@/components/CMDBExprDrawer'
import CMDBTypeSelectAntd from '@/modules/cmdb/components/cmdbTypeSelect/cmdbTypeSelectAntd'

export default {
  name: 'TopologyViewV2',
  components: {
    CMDBExprDrawer,
    CMDBTypeSelectAntd
  },
  data() {
    return {
      activeTab: 'filter',
      filterForm: this.$form.createForm(this),
      filterRules: [],
      // Stats view
      statsTypeId: null,
      statsData: null,
      statsLoading: false,
      statsPage: 1,
      statsPerPage: 20,
      statsColumns: [
        {
          title: 'CI ID',
          dataIndex: 'ci_id',
          key: 'ci_id',
          width: 80
        },
        {
          title: 'CI Name',
          dataIndex: 'ci_name',
          key: 'ci_name',
          width: 200
        },
        {
          title: 'Total Related CIs',
          dataIndex: 'total_related_cis',
          key: 'total_related_cis',
          width: 150
        }
      ],
      statsDetailColumns: [
        {
          title: 'CI Type ID',
          dataIndex: 'type_id',
          key: 'type_id',
          width: 100
        },
        {
          title: 'CI Type Name',
          dataIndex: 'type_name',
          key: 'type_name',
          width: 200
        },
        {
          title: 'Count',
          dataIndex: 'count',
          key: 'count',
          width: 100
        }
      ],
      filterLoading: false,
      filteredNodes: [],
      filteredNodeKeys: [],
      filteredNodesGrouped: [],
      rootCITypeId: null,
      rootCIId: null,
      rootCIName: null,
      drawerVisible: false,
      drawerTitle: '',
    }
  },
  computed: {
    windowHeight() {
      return this.$store.state.windowHeight
    },
  },
  methods: {
    handleCloseDrawer() {
      this.drawerVisible = false
    },
    handleRootCITypeChange(value) {
      this.rootCITypeId = value
      this.filterForm.setFieldsValue({ root_ci_id: '' })
      this.rootCIId = null
      this.rootCIName = null
    },
    handleOpenRootCIDrawer() {
      if (!this.rootCITypeId) {
        this.$message.warning('Please select CI Type first')
        return
      }
      this.$refs.rootCIDrawer.open()
    },
    handleRootCISelectDirect(ci) {
      // Handle direct CI selection from row click
      if (!ci || !ci._id) {
        this.$message.error('Invalid CI selection')
        return
      }
      const ciId = String(ci._id)
      this.rootCIId = ciId
      // Try to find a name field (common fields: name, hostname, title, etc.)
      this.rootCIName = ci.name || ci.hostname || ci.title || ci._id || `CI-${ciId}`

      // Set form value
      this.$nextTick(() => {
        this.filterForm.setFieldsValue({ root_ci_id: ciId })
        this.filterForm.validateFields(['root_ci_id'], { force: true }, (errors) => {
          if (errors) {
            console.error('Validation errors:', errors)
          } else {
            console.log('Form validation passed for root_ci_id')
          }
        })
      })
    },
    async handleRootCISelect(text) {
      console.log('handleRootCISelect received:', text)
      // Parse expression from ResourceSearch (fallback for copy expression)
      // Format can be: q=_type:(123),_id:456 or q=_id:456 or _id:456
      let ciId = null

      // Extract query part if it starts with q=
      let queryPart = text
      if (text.startsWith('q=')) {
        queryPart = text.substring(2)
      }

      // Try multiple patterns to extract CI ID
      // Pattern 1: _id:123 (single ID)
      let match = queryPart.match(/_id:(\d+)(?!\d)/)
      if (match) {
        ciId = match[1]
      } else {
        // Pattern 2: _id:(123) or _id:(123;456) - take first ID
        match = queryPart.match(/_id:\((\d+)/)
        if (match) {
          ciId = match[1]
        } else {
          // Pattern 3: Just a number at the end (fallback)
          match = queryPart.match(/(\d+)$/)
          if (match && queryPart.includes('_id')) {
            ciId = match[1]
          }
        }
      }

      if (ciId) {
        console.log('Extracted CI ID:', ciId)
        this.rootCIId = ciId

        // Fetch CI details to get the name first
        try {
          const res = await searchCI({ q: `_id:${ciId}` }, false)
          if (res.result && res.result.length > 0) {
            const ci = res.result[0]
            // Try to find a name field (common fields: name, hostname, title, etc.)
            this.rootCIName = ci.name || ci.hostname || ci.title || ci._id || `CI-${ciId}`
            console.log('CI name set to:', this.rootCIName)
          } else {
            this.rootCIName = `CI-${ciId}`
          }
        } catch (error) {
          console.error('Failed to fetch CI details:', error)
          this.rootCIName = `CI-${ciId}`
        }

        // Set form value after getting name
        this.$nextTick(() => {
          this.filterForm.setFieldsValue({ root_ci_id: ciId })
          // Force validation to clear any previous errors
          this.filterForm.validateFields(['root_ci_id'], { force: true }, (errors) => {
            if (errors) {
              console.error('Validation errors:', errors)
            } else {
              console.log('Form validation passed for root_ci_id')
            }
          })
        })
      } else {
        console.error('Could not extract CI ID from:', text)
        this.$message.error('Invalid CI selection. Please click on a CI row to select it.')
      }
    },
    async handleFilterRuleCITypeChange(ruleIndex, typeId) {
      const rule = this.filterRules[ruleIndex]
      rule.type_id = typeId
      rule.attributes = []
      rule.attributesLoading = true
      rule.filters.forEach(filter => {
        filter.attr = ''
        filter.values = []
        filter.distinctValues = []
      })
      if (typeId) {
        try {
          const res = await getCITypeAttributesById(typeId)
          rule.attributes = res.attributes || []
        } catch (error) {
          this.$message.error('Failed to load attributes')
        } finally {
          rule.attributesLoading = false
        }
          } else {
        rule.attributesLoading = false
      }
    },
    async handleFilterAttrChange(ruleIndex, filterIndex, attrName) {
      const filter = this.filterRules[ruleIndex].filters[filterIndex]
      filter.attr = attrName
      filter.values = []
      filter.distinctValues = []
      filter.valuesLoading = true
      if (attrName && this.filterRules[ruleIndex].type_id) {
        try {
          // Get distinct values from backend API
          const res = await getDistinctValues(this.filterRules[ruleIndex].type_id, attrName)
          if (res.values && Array.isArray(res.values)) {
            filter.distinctValues = res.values
          }
        } catch (error) {
          console.error('Failed to load distinct values:', error)
          this.$message.error('Failed to load distinct values')
        } finally {
          filter.valuesLoading = false
        }
            } else {
        filter.valuesLoading = false
      }
    },
    handleAddFilterRule() {
      this.filterRules.push({
        type_id: null,
        attributes: [],
        attributesLoading: false,
        filters: [{
          attr: '',
          values: [],
          distinctValues: [],
          valuesLoading: false
        }]
      })
    },
    handleRemoveFilterRule(index) {
      this.filterRules.splice(index, 1)
    },
    handleAddFilter(ruleIndex) {
      this.filterRules[ruleIndex].filters.push({
        attr: '',
        values: [],
        distinctValues: [],
        valuesLoading: false
      })
    },
    handleRemoveFilter(ruleIndex, filterIndex) {
      this.filterRules[ruleIndex].filters.splice(filterIndex, 1)
    },
    async handleFilterGraph() {
      console.log('handleFilterGraph called')
      console.log('rootCIId:', this.rootCIId)
      console.log('rootCIName:', this.rootCIName)

      // Validate form first
      this.filterForm.validateFields(async (err, values) => {
        console.log('Form validation result:', { err, values })
        if (err) {
          console.error('Form validation errors:', err)
          // Show first error message
          const firstError = Object.keys(err)[0]
          if (firstError) {
            this.$message.error(err[firstError].errors[0].message)
          }
          return
        }

        // Get root CI ID from form or data
        const rootCiId = values.root_ci_id || this.rootCIId
        console.log('Using root CI ID:', rootCiId)
        if (!rootCiId) {
          this.$message.error('Root CI is required. Please select a CI instance.')
          return
        }
        // Convert to integer for API call
        const rootCiIdInt = parseInt(rootCiId, 10)
        if (isNaN(rootCiIdInt)) {
          this.$message.error('Invalid root CI ID')
        return
      }
        // Build filter rules
        const filterRules = this.filterRules.map(rule => {
          if (!rule.type_id) {
            return null
          }
          const filters = {}
          rule.filters.forEach(filter => {
            if (filter.attr && filter.values && filter.values.length) {
              const values = Array.isArray(filter.values) ? filter.values : [filter.values]
              if (values.length) {
                filters[filter.attr] = values
              }
            }
          })
          if (Object.keys(filters).length === 0) {
            return null
          }
          return {
            type_id: rule.type_id,
            filters
          }
        }).filter(rule => rule !== null)

        // Allow empty filter rules (will return all CIs from root)
        this.filterLoading = true
        try {
          const res = await getFilteredGraph(rootCiIdInt, filterRules)
          this.filteredNodes = res.nodes || []
          // Group nodes by CI Type
          const grouped = {}
          this.filteredNodes.forEach(node => {
            const ciType = node.ci_type || node._type || 'Unknown'
            if (!grouped[ciType]) {
              grouped[ciType] = {
                ci_type: ciType,
                nodes: [],
                keys: new Set()
              }
            }
            grouped[ciType].nodes.push(node)
            // Extract keys for this group
            Object.keys(node).forEach(key => {
              if (key !== '_id' && key !== '_type' && key !== 'ci_type') {
                grouped[ciType].keys.add(key)
              }
            })
          })
          // Convert to array and sort keys
          this.filteredNodesGrouped = Object.values(grouped).map(group => ({
            ...group,
            keys: Array.from(group.keys).sort()
          })).sort((a, b) => a.ci_type.localeCompare(b.ci_type))
          this.$message.success(`Filter success: ${this.filteredNodes.length} nodes found`)
        } catch (error) {
          this.$message.error(error.response?.data?.message || (this.$t('cmdb.topo.filterFailed') || 'Filter failed'))
        } finally {
          this.filterLoading = false
        }
      })
    },
    async handleLoadStats(page, perPage) {
      // Handle default values and ensure page/perPage are numbers
      const currentPage = typeof page === 'number' ? page : (this.statsPage || 1)
      const currentPerPage = typeof perPage === 'number' ? perPage : (this.statsPerPage || 20)

      if (!this.statsTypeId) {
        this.$message.warning('Please select a CI Type first')
        return
      }

      this.statsLoading = true
      try {
        const res = await getStatsByType(this.statsTypeId, currentPage, currentPerPage)
        this.statsData = res
        this.statsPage = res.page
        this.statsPerPage = res.per_page
        this.$message.success(`Loaded ${res.results.length} of ${res.total_cis} CIs (Page ${res.page}/${res.total_pages})`)
      } catch (error) {
        console.error('Error loading statistics:', error)
        this.$message.error(error.response?.data?.message || 'Failed to load statistics')
      } finally {
        this.statsLoading = false
      }
    },
    handleStatsTableChange(pagination, filters, sorter) {
      // pagination is an object with { current, pageSize, total }
      if (pagination && typeof pagination.current === 'number') {
        this.handleLoadStats(pagination.current, pagination.pageSize)
      }
    }
  },
}
</script>

<style lang="less" scoped>
.ant-message {
  z-index: 99999999 !important;
}
.topo-wrap {
  margin: 0 0 -24px 0;
  .topo-empty {
    position: absolute;
    text-align: center;
    left: 50%;
    top: 40%;
    transform: translate(-50%, -50%);
  }

  .topo-left {
    width: 100%;
    overflow: auto;
    float: left;

    .topo-left-content {
      max-height: calc(100% - 45px);
      overflow: hidden;
      &:hover {
        overflow: auto;
      }
    }
    .topo-left-title {
      padding: 10px 0;
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      color: @text-color_3;
    }
    .topo-left-group {
      position: relative;
      padding: 8px 0 8px 14px;
      color: rgb(99, 99, 99);
      cursor: pointer;
      font-size: 14px;
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      > div:nth-child(2) {
        font-size: 14px;
        display: none;
      }
      &:hover {
        background-color: @primary-color_3;
        > div:nth-child(2) {
          display: inline-flex;
        }
        svg {
          display: inline !important;
        }
      }
    }
    .topo-left-detail {
      padding: 3px 14px;
      cursor: pointer;
      position: relative;
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      align-items: center;
      margin-bottom: 4px;
      height: 32px;
      line-height: 32px;
      .topo-left-detail-action {
        display: none;
        margin-left: auto;
      }
      .topo-left-detail-title {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
      }
      .topo-left-detail-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border-radius: 2px;
        box-shadow: 0px 1px 2px rgba(47, 84, 235, 0.2);
        margin-right: 6px;
        background-color: #fff;
        img {
          max-height: 20px;
          max-width: 20px;
        }
      }
      &:hover {
        background-color: @primary-color_3;
        svg {
          display: inline !important;
        }
        .topo-left-detail-action {
          display: inline-flex;
        }
      }
    }
    .selected {
      background-color: @primary-color_3;
      .topo-left-detail-title {
        font-weight: 700;
      }
    }
  }
  .topo-right {
    width: 100%;
    position: relative;
    background-color: #fff;
    .topo-right-empty {
      position: absolute;
      text-align: center;
      left: 50%;
      top: 40%;
      transform: translate(-50%, -50%);
    }

    .relation-graph-search {
      position: absolute;
      z-index: 10;
      top: 20px;
      left: 20px;
      width: 300px;
    }
  }
  .topo-left,
  .topo-right {
    height: 100%;
  }
  .node-tips {
    z-index: 999;
    padding: 10px;
    background-color: #ffffff;
    border:#eeeeee solid 1px;
    box-shadow: 0px 0px 8px #cccccc;
    position: absolute;
    overflow: auto;
  }
}
.chart-left-preview {
  border: 1px solid #e4e7ed;
  border-radius: 2px;
  height: 280px;
  width: 92%;
  position: relative;
  padding: 12px;
  .chart-left-preview-operation {
    color: #86909c;
    position: absolute;
    top: 12px;
    right: 12px;
    cursor: pointer;
  }
  .chart-left-preview-box {
    padding: 6px 12px;
    height: 250px;
    border-radius: 8px;
  }
}

.relation-graph-node {
  padding: 6px 3px;
  border-radius: 2px;
  border-width: 2px;
  border-style: solid;
  background-color: transparent;
  position: relative !important;
  display: flex;
  justify-content: center;
  align-items: center;

  &-text {
    color: #000000;
    font-size: 12px;
    font-weight: 400;
    margin-left: 6px;
    word-break: break-all;
  }

  &-icon {
    font-size: 12px;
    color: rgba(0, 0, 0, 0.65);
  }

  &-image {
    max-height: 20px;
    max-width: 20px;
  }
}

/deep/ .relation-graph {
  background-color: #FFFFFF;

  .rel-node {
    padding: 0px;
    height: auto !important;
  }
  .rel-node-checked {
    box-shadow: none;
  }
  .c-expanded {
    background-color: rgb(64, 158, 255) !important;
  }
  .c-collapsed {
    background-color: rgb(64, 158, 255) !important;
  }
}
</style>

<style lang="less">
.cmdb-topo-left-input {
  input {
    background-color: transparent;
  }
  .ant-input:focus {
    box-shadow: none;
  }
}
.ant-message {
  z-index: 99999999 !important;
}
.filter-view-container {
  padding: 16px;
  height: 100%;
  overflow-y: auto;
}
</style>
