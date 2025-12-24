<template>
  <div class="graph-view-container">
    <SplitPane
      :min="180"
      :max="300"
      :paneLengthPixel.sync="paneLengthPixel"
      appName="cmdb-graph-view"
      :triggerLength="18"
      calcBasedParent
    >
      <template #one>
        <div class="graph-left-input-container">
          <a-button
            type="primary"
            icon="setting"
            @click="handleOpenDrawer"
            class="graph-left-config-btn"
            style="margin-bottom: 8px; width: 100%"
          >
            Configure Graph
          </a-button>
          <a-input
            v-model="searchValue"
            :placeholder="'Search applications...'"
            class="graph-left-input"
            @pressEnter="handleSearch"
          >
            <a-icon
              slot="suffix"
              type="search"
              :class="['graph-search-icon', searchValue ? 'graph-search-icon-focus' : '']"
              @click="handleSearch"
            />
          </a-input>
          <a-button @click="handleReset" class="graph-left-reset-btn">{{ $t('reset') }}</a-button>
        </div>
        <div class="graph-left">
          <a-spin :spinning="loadingApps">
            <div class="graph-left-content">
              <div
                v-for="app in applications"
                :key="app.app_code"
                :class="`${selectedAppCode === app.app_code ? 'selected' : ''} graph-left-detail`"
                @click="handleSelectApplication(app)"
              >
                <span class="graph-left-detail-icon">
                  <span class="primary-color">{{ app.app_code[0].toUpperCase() }}</span>
                </span>
                <span class="graph-left-detail-title">{{ app.app_code }}</span>
              </div>
            </div>
            <div v-if="!searchValue" class="pagination-container">
              <a-pagination
                :showSizeChanger="true"
                :current="currentPage"
                size="small"
                :total="totalApplications"
                show-quick-jumper
                :page-size="pageSize"
                :page-size-options="pageSizeOptions"
                @showSizeChange="onShowSizeChange"
                :show-total="
                  (total, range) =>
                    $t('pagination.total', {
                      range0: range[0],
                      range1: range[1],
                      total,
                    })
                "
                @change="
                  (page) => {
                    currentPage = page
                  }
                "
              >
                <template slot="buildOptionText" slot-scope="props">
                  <span v-if="props.value !== '1000'">{{ props.value }}{{ $t('itemsPerPage') }}</span>
                  <span v-if="props.value === '1000'">{{ $t('cmdb.ci.all') }}</span>
                </template>
              </a-pagination>
            </div>
          </a-spin>
        </div>
      </template>
      <template #two>
        <div v-if="selectedAppCode" class="graph-right">
          <div class="graph-toolbar">
            <a-space>
              <a-button @click="refreshGraph" icon="reload">Refresh</a-button>
              <a-select v-model="selectedLayout" @change="changeLayout" style="width: 150px">
                <a-select-option value="tree">Tree Layout</a-select-option>
                <a-select-option value="center">Center Layout</a-select-option>
              </a-select>
              <a-button @click="zoomIn" icon="zoom-in">Zoom In</a-button>
              <a-button @click="zoomOut" icon="zoom-out">Zoom Out</a-button>
              <a-button @click="fitView" icon="fullscreen">Fit View</a-button>
            </a-space>
            <div class="legend">
              <a-select
                v-model="selectedLayers"
                mode="multiple"
                placeholder="Select Layers"
                style="width: 200px; margin-right: 8px"
                @change="handleLayerChange"
              >
                <a-select-option v-for="layer in availableLayers" :key="layer" :value="layer">
                  {{ layer }}
                </a-select-option>
              </a-select>
              <a-select
                v-model="selectedSites"
                mode="multiple"
                placeholder="Select Sites"
                style="width: 200px"
                @change="handleSiteChange"
              >
                <a-select-option v-for="site in availableSites" :key="site" :value="site">
                  {{ site }}
                </a-select-option>
              </a-select>
            </div>
          </div>
          <div class="graph-content" v-loading="loading">
            <SeeksRelationGraph
              ref="graphRef"
              :options="graphOptions"
              @on-node-click="handleNodeClick"
              @on-line-click="handleLineClick"
            >
              <template v-slot:node="{ node }">
                <div class="custom-node">
                  <div class="node-header" :style="getNodeHeaderStyle(node)">
                    <template v-if="node.data.icon">
                      <img
                        v-if="node.data.icon.split('$$')[2]"
                        :src="`/api/common-setting/v1/file/${node.data.icon.split('$$')[3]}`"
                        class="node-icon-image"
                      />
                      <ops-icon
                        v-else
                        :style="{ color: node.data.icon.split('$$')[1] }"
                        :type="node.data.icon.split('$$')[0]"
                        class="node-icon"
                      />
                    </template>
                    <span v-else class="node-icon-fallback">{{ node.text[0].toUpperCase() }}</span>
                    <span class="node-name">{{ node.text }}</span>
                  </div>
                  <div v-if="node.data.site" class="node-badge" :class="`site-${node.data.site.toLowerCase()}`">
                    {{ node.data.site }}
                  </div>
                  <div class="node-layer">{{ node.data.layer }}</div>
                </div>
              </template>
            </SeeksRelationGraph>
          </div>

          <!-- Node Detail Modal -->
          <a-modal
            v-model="detailModalVisible"
            :title="selectedNode ? selectedNode.text : 'Node Details'"
            :footer="null"
            width="600px"
          >
            <div v-if="selectedNode" class="node-details">
              <a-descriptions bordered size="small" :column="1">
                <a-descriptions-item label="Name">{{ selectedNode.text }}</a-descriptions-item>
                <a-descriptions-item label="Alias">{{ selectedNode.id }}</a-descriptions-item>
                <a-descriptions-item label="Layer">
                  <a-tag :color="getLayerColor(selectedNode.data.layer)">{{ selectedNode.data.layer }}</a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="Site">
                  <a-tag v-if="selectedNode.data.site" :color="selectedNode.data.site === 'VNPAY' ? 'purple' : 'cyan'">
                    {{ selectedNode.data.site }}
                  </a-tag>
                  <span v-else>-</span>
                </a-descriptions-item>
                <a-descriptions-item label="CI Type">{{ selectedNode.data.ci_type.ci_name }}</a-descriptions-item>
                <a-descriptions-item label="Metadata" v-if="Object.keys(selectedNode.data.metadata || {}).length > 0">
                  <pre>{{ JSON.stringify(selectedNode.data.metadata, null, 2) }}</pre>
                </a-descriptions-item>
              </a-descriptions>
            </div>
          </a-modal>
        </div>
        <div v-else class="graph-right-empty">
          <a-empty :image="emptyImage" description="">
            <span slot="description">Please select an application from the list</span>
          </a-empty>
        </div>
      </template>
    </SplitPane>
    <CustomDrawer
      :closable="false"
      :title="drawerTitle"
      :visible="drawerVisible"
      @close="onClose"
      placement="right"
      width="900px"
      :destroyOnClose="true"
      :bodyStyle="{ height: 'calc(100vh - 108px)' }"
    >
      <a-form
        :form="form"
        :layout="formLayout"
        :label-col="formItemLayout.labelCol"
        :wrapper-col="formItemLayout.wrapperCol"
      >
        <a-form-item :label="$t('cmdb.topo.path')" prop="path">
          <div :style="{ height: '250px', border: '1px solid #e4e7ed' }">
            <SeeksRelationGraph ref="ciTypeRelationGraph" :options="ciTypeRelationGraphOptions">
              <div slot="node" slot-scope="{ node }" :style="{ lineHeight: '20px' }">
                <a-checkbox
                  :checked="checkedNodes.includes(node.id)"
                  @change="(e) => checked(e, node)"
                ></a-checkbox>
                <span :style="{ marginLeft: '5px' }">{{ node.text }}</span>
              </div>
            </SeeksRelationGraph>
          </div>
        </a-form-item>
        <div class="custom-drawer-bottom-action">
          <a-button @click="handleApplyFilter" :loading="loading" type="primary" style="margin-right: 1rem">{{
            $t('apply')
          }}</a-button>
          <a-button @click="onClose">{{ $t('cancel') }}</a-button>
        </div>
      </a-form>
    </CustomDrawer>
  </div>
</template>

<script>
import SeeksRelationGraph from '@/modules/cmdb/3rd/relation-graph'
import { getTopologyGraph } from '@/modules/cmdb/api/topology_graph'
import { searchCI } from '@/modules/cmdb/api/ci'
import SplitPane from '@/components/SplitPane'
import CustomDrawer from '@/components/CustomDrawer'
import CMDBExprDrawer from '@/components/CMDBExprDrawer'
import CMDBTypeSelectAntd from '@/modules/cmdb/components/cmdbTypeSelect/cmdbTypeSelectAntd'
import { getRelationsByTypeId } from '@/modules/cmdb/api/topology'
import { getCITypeGroups } from '@/modules/cmdb/api/ciTypeGroup'
import emptyImage from '@/assets/data_empty.png'
import mockAppsData from './mock.apps.json'

export default {
  name: 'GraphView',
  components: {
    SeeksRelationGraph,
    SplitPane,
    CustomDrawer,
    CMDBExprDrawer,
    CMDBTypeSelectAntd
  },
  data() {
    return {
      loading: false,
      loadingApps: false,
      selectedLayout: 'tree',
      emptyImage,
      paneLengthPixel: 250,
      applications: [],
      selectedAppCode: null,
      searchValue: '',
      currentPage: 1,
      pageSizeOptions: ['20', '50', '100', '1000'],
      pageSize: 50,
      totalApplications: 0,
      graphOptions: {
        debug: false,
        allowShowMiniToolBar: false,
        allowShowMiniNameFilter: false,
        defaultFocusRootNode: false,
        defaultNodeShape: 1,
        defaultLineShape: 4,
        defaultNodeBorderWidth: 2,
        defaultNodeWidth: 200,
        defaultNodeHeight: 80,
        defaultNodeColor: '#ffffff',
        defaultNodeFontColor: '#333333',
        defaultLineColor: '#999999',
        defaultNodeBorderColor: '#cccccc',
        layouts: [
          {
            layoutName: 'tree',
            from: 'top',
            layoutClassName: 'seeks-layout-center',
            min_per_width: 250,
            min_per_height: 150
          }
        ]
      },
      ciTypeRelationGraphOptions: {
        debug: false,
        allowShowMiniToolBar: false,
        allowShowMiniNameFilter: false,
        defaultFocusRootNode: false,
        defaultNodeColor: 'rgba(230, 247, 255, 1)',
        defaultNodeFontColor: 'rgba(33, 32, 32, 1)',
        layouts: [
          {
            layoutName: 'tree',
            layoutClassName: 'seeks-layout-center',
          },
        ],
      },
      graphJsonData: {},
      detailModalVisible: false,
      selectedNode: null,
      mockData: null,
      type2meta: {}, // Mapping from ci_alias to icon (similar to topology_view)
      selectedLayers: [],
      availableLayers: [],
      selectedSites: ['VNPAY', 'GDS', 'CMC'],
      availableSites: ['VNPAY', 'GDS', 'CMC'],
      layerColors: {
        'Application': '#1890ff',
        'Middleware': '#52c41a',
        'System': '#fa8c16',
        'Infrastructure': '#f5222d',
        'Network': '#722ed1'
      },
      // Drawer state
      drawerVisible: false,
      drawerTitle: 'Configure Graph',
      form: this.$form.createForm(this),
      formLayout: 'horizontal',
      selectedCIType: null,
      selectedInstances: '',
      selectedPath: {},
      CITypeId: null,
      checkedNodes: [],
      nodes: [],
      ciTypeRelationGraphData: null
    }
  },
  computed: {
    formItemLayout() {
      const { formLayout } = this
      return formLayout === 'horizontal'
        ? {
            labelCol: { span: 5 },
            wrapperCol: { span: 16 },
          }
        : {}
    },
  },
  watch: {
    currentPage: function(newVal, oldVal) {
      this.loadApplications(newVal, this.searchValue)
    }
  },
  mounted() {
    // Load layers from API first, then load applications
    this.loadLayersFromAPI().then(() => {
      this.loadApplications()
    })
  },
  methods: {
    async loadLayersFromAPI() {
      try {
        // Use getCITypeGroups to get all groups regardless of subscription
        const response = await getCITypeGroups({ need_other: true })
        if (response && Array.isArray(response)) {
          // Extract layer names from group[].name
          const layers = response
            .map(group => group.name)
            .filter(name => name) // Filter out empty names

          this.availableLayers = layers

          // Set selectedLayers to all layers by default
          this.selectedLayers = [...layers]

          // Extend layerColors for new layers that don't have colors yet
          const defaultColors = ['#1890ff', '#52c41a', '#fa8c16', '#f5222d', '#722ed1', '#13c2c2', '#eb2f96', '#faad14']
          layers.forEach((layer, index) => {
            if (!this.layerColors[layer]) {
              // Assign a color from defaultColors, cycling if needed
              this.layerColors[layer] = defaultColors[index % defaultColors.length]
            }
          })
        }
      } catch (error) {
        console.error('Error loading layers from API:', error)
        // Fallback to default layers if API fails
        this.availableLayers = ['Application', 'Middleware', 'System', 'Infrastructure', 'Network']
        this.selectedLayers = ['Application', 'Middleware', 'System', 'Infrastructure', 'Network']
      }
    },

    handleSelectApplication(app) {
      this.selectedAppCode = app.app_code
      this.loadGraphData(app.app_code)
    },

    handleSearch() {
      // Reset to page 1 when searching
      this.$nextTick(() => {
        if (this.currentPage === 1) {
          this.loadApplications(1, this.searchValue)
        } else {
          this.currentPage = 1
        }
      })
    },

    handleReset() {
      this.searchValue = ''
      this.$nextTick(() => {
        if (this.currentPage === 1) {
          this.loadApplications(1, '')
        } else {
          this.currentPage = 1
        }
      })
    },

    async loadApplications(page = 1, searchValue = null) {
      this.loadingApps = true
      try {
        // Build query with optional search value
        const searchValueToUse = searchValue !== null ? searchValue : this.searchValue
        let query = '_type:3'
        if (searchValueToUse && searchValueToUse.trim()) {
          query += `,*${searchValueToUse.trim()}*`
        }

        // Call API to get CIs with type 3 (Application)
        const response = await searchCI({
          q: query,
          count: this.pageSize,
          page: page
        })

        // Transform response to match expected format
        // Expected: [{ app_code: 'xxx', ... }, ...]
        if (response && response.result) {
          this.applications = response.result.map(ci => ({
            app_code: ci.app_code || ci.name || ci.unique_name,
            _id: ci._id,
            ...ci
          }))

          // Store total count for pagination
          this.totalApplications = response.numfound || response.total || 0
        }
      } catch (error) {
        console.error('Error loading applications:', error)
        this.$message.error('Failed to load applications')
        // Fallback to mock data on error
        this.applications = mockAppsData.result || []
        this.totalApplications = 0
      } finally {
        this.loadingApps = false
      }
    },

    onShowSizeChange(current, pageSize) {
      this.pageSize = pageSize
      if (this.currentPage === 1) {
        this.loadApplications(1, this.searchValue)
      } else {
        this.currentPage = 1
      }
    },

    async loadGraphData(app_code) {
      this.loading = true
      try {
        // Fetch data from API with app_code parameter
        const response = await getTopologyGraph(app_code)
        this.mockData = response

        // Build type2meta mapping from nodes (similar to topology_view)
        // Use ci_alias as key since type_id is not available in the response
        this.type2meta = {}
        if (response && response.node && Array.isArray(response.node)) {
          response.node.forEach(node => {
            if (node.ci_type && node.ci_type.ci_alias && node.ci_type.ci_icon) {
              // Only include valid icons (exclude "caise-default" and empty strings)
              const icon = node.ci_type.ci_icon
              if (icon && icon !== 'caise-default' && icon.trim() !== '') {
                this.type2meta[node.ci_type.ci_alias] = icon
              }
            }
          })
        }

        // Now use this.mockData instead of imported mockData
        this.updateGraphWithFilteredData()

        this.$nextTick(() => {
          this.loading = false
          this.$message.success('Graph loaded successfully')
        })
      } catch (error) {
        this.loading = false
        this.$message.error('Failed to load graph data')
        console.error('Error loading graph:', error)
      }
    },

    refreshGraph() {
      if (this.selectedAppCode) {
        this.loadGraphData(this.selectedAppCode)
      }
    },

    handleLayerChange(value) {
      this.selectedLayers = value
      this.updateGraphWithFilteredData()
    },

    handleSiteChange(value) {
      this.selectedSites = value
      this.updateGraphWithFilteredData()
    },

    updateGraphWithFilteredData() {
      // Check if data is loaded
      if (!this.mockData) {
        return
      }

      // Filter nodes by selected layers AND selected sites
      const filteredNodes = this.mockData.node
        .filter(node => {
          // Check layer filter
          const layerMatch = this.selectedLayers.includes(node.layer)

          // Check site filter: always show null sites, otherwise check if selected
          const siteMatch = node.site === null || this.selectedSites.includes(node.site)

          // AND logic: must match both filters
          return layerMatch && siteMatch
        })
        .map(node => {
          // Look up icon from type2meta using ci_alias (similar to topology_view)
          const ci_alias = node.ci_type?.ci_alias
          const icon = ci_alias ? (this.type2meta[ci_alias] || '') : ''
          return {
            id: node.alias,
            text: node.name,
            borderColor: this.layerColors[node.layer] || '#cccccc',
            fontColor: '#333333',
            color: '#ffffff',
            data: {
              layer: node.layer,
              site: node.site,
              metadata: node.metadata,
              ci_type: node.ci_type,
              icon: icon
            }
          }
        })

      // Create set of visible node IDs for fast lookup
      const visibleNodeIds = new Set(filteredNodes.map(n => n.id))

      // Filter edges: only show if both nodes are visible
      const filteredLinks = this.mockData.edges
        .filter(edge => visibleNodeIds.has(edge.from) && visibleNodeIds.has(edge.to))
        .map(edge => ({
          from: edge.from,
          to: edge.to,
          text: edge.text,
          color: '#999999',
          fontColor: '#666666'
        }))

      this.graphJsonData = {
        nodes: filteredNodes,
        links: filteredLinks
      }

      // Update graph
      this.$nextTick(() => {
        if (this.$refs.graphRef) {
          this.$refs.graphRef.setJsonData(this.graphJsonData)
        }
      })
    },

    changeLayout(value) {
      const layoutConfig = {
        tree: {
          layoutName: 'tree',
          from: 'top',
          layoutClassName: 'seeks-layout-center',
          min_per_width: 250,
          min_per_height: 150
        },
        center: {
          layoutName: 'center',
          layoutClassName: 'seeks-layout-center',
          centerOffset_x: 0,
          centerOffset_y: 0
        }
      }

      this.graphOptions = {
        ...this.graphOptions,
        layouts: [layoutConfig[value]]
      }

      this.$nextTick(() => {
        if (this.$refs.graphRef) {
          this.$refs.graphRef.setJsonData(this.graphJsonData)
        }
      })
    },

    zoomIn() {
      if (this.$refs.graphRef) {
        this.$refs.graphRef.zoom(0.2)
      }
    },

    zoomOut() {
      if (this.$refs.graphRef) {
        this.$refs.graphRef.zoom(-0.2)
      }
    },

    fitView() {
      if (this.$refs.graphRef) {
        this.$refs.graphRef.refresh()
      }
    },

    handleNodeClick(nodeObject, $event) {
      this.selectedNode = nodeObject
      this.detailModalVisible = true
    },

    handleLineClick(lineObject, $event) {
      this.$message.info(`Edge: ${lineObject.text || 'No label'}`)
    },

    getNodeHeaderStyle(node) {
      return {
        borderLeft: `4px solid ${this.layerColors[node.data.layer] || '#cccccc'}`
      }
    },

    getLayerColor(layer) {
      const colorMap = {
        'Application': 'blue',
        'Middleware': 'green',
        'System': 'orange',
        'Infrastructure': 'red',
        'Network': 'purple'
      }
      return colorMap[layer] || 'default'
    },

    getSiteColor(site) {
      const colorMap = {
        'VNPAY': 'purple',
        'GDS': 'cyan',
        'CMC': 'geekblue'
      }
      return colorMap[site] || 'default'
    },
    // Drawer methods
    handleOpenDrawer() {
      if (!this.selectedAppCode) {
        this.$message.warning('Please select an application first')
        return
      }
      this.drawerTitle = 'Configure Graph'
      this.drawerVisible = true

      // Set default values: Application type (3) and selected app_code
      this.selectedCIType = 3 // Application type
      this.selectedInstances = this.selectedAppCode
      this.CITypeId = 3

      // Reset form and set default values
      this.form.resetFields()
      this.$nextTick(() => {
        this.form.setFieldsValue({
          central_node_type: 3,
          central_node_instances: this.selectedAppCode
        })
        // Load relations for Application type
        this.checkedNodes = ['3'] // Application type ID
        this.getRelationsByTypeId(3)
      })

      this.selectedPath = {}
    },
    onClose() {
      this.form.resetFields()
      this.drawerVisible = false
      this.checkedNodes = []
      this.nodes = []
      this.CITypeId = null
    },
    handleOpenCmdb() {
      this.$refs.cmdbDrawer.open()
    },
    copySuccess(text) {
      this.form.setFieldsValue({ 'central_node_instances': `${text}` })
    },
    async CITypeChange(value) {
      this.CITypeId = value
      this.selectedCIType = value
      this.form.setFieldsValue({
        central_node_instances: ''
      })
      this.checkedNodes = [String(value)]
      await this.getRelationsByTypeId(value)
      if (this.$refs.cmdbDrawer.$refs.resourceSearch) {
        this.$refs.cmdbDrawer.$refs.resourceSearch.typeId = value
        await this.$refs.cmdbDrawer.$refs.resourceSearch.getCIType(value)
        await this.$refs.cmdbDrawer.$refs.resourceSearch.getAttrsByType(value)
        this.$refs.cmdbDrawer.$refs.resourceSearch.$refs['search'].currenCiType = [value]
        this.$refs.cmdbDrawer.$refs.resourceSearch.loadInstance()
      }
    },
    async getRelationsByTypeId(typeId) {
      try {
        const res = await getRelationsByTypeId(typeId)
        const nodes = []
        const links = []
        this.nodes = res.nodes
        res.edges.forEach(item => {
          links.push({
            from: `${item.from_id}`,
            to: `${item.to_id}`,
            text: `${item.text}`,
            disableDefaultClickEffect: true,
          })
        })
        res.nodes.forEach(item => {
          nodes.push({
            id: `${item.id}`,
            name: item.alias || item.name,
            text: item.alias || item.name,
            nodeShape: 1,
            borderWidth: -1,
            disableDefaultClickEffect: true,
          })
        })
        const _graphJsonData = {
          rootId: `${typeId}`,
          nodes,
          links,
        }
        this.ciTypeRelationGraphData = _graphJsonData
        if (!nodes.length) {
          this.$message.error(this.$t('cmdb.topo.noData'))
          return
        }
        this.$nextTick(() => {
          if (this.$refs.ciTypeRelationGraph) {
            this.$refs.ciTypeRelationGraph.setJsonData(_graphJsonData, (res) => {
            })
          }
        })
      } catch (error) {
        console.error('Error loading relations:', error)
        this.$message.error('Failed to load CI type relations')
      }
    },
    checked(e, node) {
      if (e.target.checked) {
        if (this.checkedNodes.findIndex(i => i === node.id) === -1) {
          this.checkedNodes.push(node.id)
        }
      } else {
        this.checkedNodes.splice(this.checkedNodes.findIndex(i => i === node.id), 1)
      }
    },
    wrapPath() {
      const path = {}
      this.checkedNodes.forEach(nodeId => {
        const _nodes = this.nodes.filter(i => String(i.id) === nodeId)
        _nodes.forEach(_node => {
          const levels = _node.level || [0]
          levels.forEach(level => {
            if (level in path) {
              path[level].push(nodeId)
            } else {
              path[level] = [nodeId]
            }
          })
        })
      })
      return path
    },
    async handleApplyFilter() {
      // Use default values: Application type (3) and selected app_code
      this.selectedCIType = 3 // Application type
      this.selectedInstances = this.selectedAppCode
      this.selectedPath = this.wrapPath()

      // Close drawer
      this.drawerVisible = false

      // Load graph with new filters
      await this.loadGraphDataWithFilters()
    },
    async loadGraphDataWithFilters() {
      this.loading = true
      try {
        // If we have CI type and instances, use them to load graph
        // Otherwise, fall back to app_code method
        if (this.selectedCIType && this.selectedInstances) {
          // TODO: Update API call to support CI type and instances filtering
          // For now, we'll use the existing API but with modified parameters
          // Use selectedInstances (which contains app_code) or fallback to selectedAppCode
          const appCodeToUse = this.selectedInstances || this.selectedAppCode
          const response = await getTopologyGraph(appCodeToUse, null, null)
          this.mockData = response

          // Build type2meta mapping from nodes (similar to loadGraphData)
          this.type2meta = {}
          if (response && response.node && Array.isArray(response.node)) {
            response.node.forEach(node => {
              if (node.ci_type && node.ci_type.ci_alias && node.ci_type.ci_icon) {
                // Only include valid icons (exclude "caise-default" and empty strings)
                const icon = node.ci_type.ci_icon
                if (icon && icon !== 'caise-default' && icon.trim() !== '') {
                  this.type2meta[node.ci_type.ci_alias] = icon
                }
              }
            })
          }

          this.updateGraphWithFilteredData()
        } else if (this.selectedAppCode) {
          // Fall back to app_code method
          await this.loadGraphData(this.selectedAppCode)
          return
        } else {
          this.$message.warning('Please configure graph filters or select an application')
          this.loading = false
          return
        }

        this.$nextTick(() => {
          this.loading = false
          this.$message.success('Graph loaded successfully')
        })
      } catch (error) {
        this.loading = false
        this.$message.error('Failed to load graph data')
        console.error('Error loading graph:', error)
      }
    }
  }
}
</script>

<style lang="less" scoped>
.graph-view-container {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background: #f0f2f5;

  .graph-left-input-container {
    margin: 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }

  .graph-left-input {
    flex: 1;
    input {
      background-color: transparent;
    }
    /deep/ .ant-input:focus {
      box-shadow: none;
    }
  }

  .graph-left-reset-btn {
    flex-shrink: 0;
  }

  .graph-left {
    width: 100%;
    height: calc(100% - 64px);
    overflow: auto;
    background: #ffffff;

    .graph-left-content {
      max-height: 100%;
      overflow: hidden;
      &:hover {
        overflow: auto;
      }
    }

    .graph-left-detail {
      padding: 8px 16px;
      cursor: pointer;
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      align-items: center;
      margin-bottom: 4px;
      height: 40px;
      line-height: 40px;
      transition: background-color 0.3s;

      .graph-left-detail-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        box-shadow: 0px 1px 2px rgba(47, 84, 235, 0.2);
        margin-right: 8px;
        background-color: #e6f7ff;
        font-weight: 600;
      }

      .graph-left-detail-title {
        overflow: hidden;
        white-space: nowrap;
        text-overflow: ellipsis;
        font-size: 14px;
      }

      &:hover {
        background-color: #e6f7ff;
      }

      &.selected {
        background-color: #bae7ff;
        .graph-left-detail-title {
          font-weight: 600;
          color: #1890ff;
        }
      }
    }

    .pagination-container {
      padding: 12px 16px;
      text-align: center;
      border-top: 1px solid #f0f0f0;
      background: #fafafa;
    }
  }

  .graph-right {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: #f0f2f5;
  }

  .graph-right-empty {
    position: absolute;
    text-align: center;
    left: 50%;
    top: 50%;
    transform: translate(-50%, -50%);
  }

  .graph-toolbar {
    padding: 16px;
    background: #ffffff;
    border-bottom: 1px solid #e8e8e8;
    display: flex;
    justify-content: space-between;
    align-items: center;

    .legend {
      display: flex;
      align-items: center;
      gap: 8px;

    }
  }

  .graph-content {
    flex: 1;
    position: relative;
    background: #ffffff;
    overflow: hidden;
  }
}

.custom-node {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  .node-header {
    flex: 1;
    padding: 8px 12px;
    display: flex;
    align-items: center;
    gap: 8px;
    background: #fafafa;

    .node-icon {
      font-size: 20px;
    }

    .node-icon-image {
      max-height: 20px;
      max-width: 20px;
      object-fit: contain;
    }

    .node-icon-fallback {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      border-radius: 4px;
      box-shadow: 0px 1px 2px rgba(47, 84, 235, 0.2);
      background-color: #e6f7ff;
      font-weight: 600;
      font-size: 14px;
      color: #1890ff;
    }

    .node-name {
      flex: 1;
      font-weight: 500;
      font-size: 14px;
      color: #333333;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
  }

  .node-badge {
    padding: 2px 8px;
    font-size: 11px;
    text-align: center;
    font-weight: 500;
    &.site-vnpay {
      background: #722ed1;
      color: #ffffff;
    }

    &.site-gds {
      background: #13c2c2;
      color: #ffffff;
    }
  }

  .node-layer {
    padding: 4px 8px;
    font-size: 11px;
    text-align: center;
    color: #666666;
    background: #f5f5f5;
    border-top: 1px solid #e8e8e8;
  }
}

.node-details {
  pre {
    background: #f5f5f5;
    padding: 8px;
    border-radius: 4px;
    font-size: 12px;
    margin: 0;
  }
}

::v-deep {
  .rel-map {
    width: 100% !important;
    height: 100% !important;
  }

  .rel-node-text {
    display: none !important;
  }
  .rel-node-shape {
    cursor: pointer;
    &:hover {
      filter: brightness(0.95);
    }
  }
}

.custom-drawer-bottom-action {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px 24px;
  background: #fff;
  border-top: 1px solid #e8e8e8;
  text-align: right;
}
</style>
