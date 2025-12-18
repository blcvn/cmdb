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
        <a-tag
          v-for="layer in availableLayers"
          :key="layer"
          :color="selectedLayers.includes(layer) ? getLayerColor(layer) : 'default'"
          :class="{ 'layer-tag': true, 'layer-tag-inactive': !selectedLayers.includes(layer) }"
          @click="toggleLayer(layer)"
          style="cursor: pointer"
        >
          <a-icon v-if="selectedLayers.includes(layer)" type="check" />
          {{ layer }}
        </a-tag>
        <a-divider type="vertical" />
        <a-tag
          v-for="site in availableSites"
          :key="site"
          :color="selectedSites.includes(site) ? getSiteColor(site) : 'default'"
          :class="{ 'site-tag': true, 'site-tag-inactive': !selectedSites.includes(site) }"
          @click="toggleSite(site)"
          style="cursor: pointer"
        >
          <a-icon v-if="selectedSites.includes(site)" type="check" />
          {{ site }}
        </a-tag>
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
              <span class="node-icon">{{ getNodeIcon(node) }}</span>
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
  </div>
</template>

<script>
import SeeksRelationGraph from '@/modules/cmdb/3rd/relation-graph'
import { getTopologyGraph } from '@/modules/cmdb/api/topology_graph'
import { searchCI } from '@/modules/cmdb/api/ci'
import SplitPane from '@/components/SplitPane'
import emptyImage from '@/assets/data_empty.png'
import mockAppsData from './mock.apps.json'

export default {
  name: 'GraphView',
  components: {
    SeeksRelationGraph,
    SplitPane
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
      graphJsonData: {},
      detailModalVisible: false,
      selectedNode: null,
      mockData: null,
      selectedLayers: ['Application', 'Middleware', 'System', 'Infrastructure', 'Network'],
      availableLayers: ['Application', 'Middleware', 'System', 'Infrastructure', 'Network'],
      selectedSites: ['VNPAY', 'GDS', 'CMC'],
      availableSites: ['VNPAY', 'GDS', 'CMC'],
      layerColors: {
        'Application': '#1890ff',
        'Middleware': '#52c41a',
        'System': '#fa8c16',
        'Infrastructure': '#f5222d',
        'Network': '#722ed1'
      }
    }
  },
  watch: {
    currentPage: function(newVal, oldVal) {
      this.loadApplications(newVal, this.searchValue)
    }
  },
  mounted() {
    // Load applications from API instead of mock data
    this.loadApplications()
  },
  methods: {
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

    toggleLayer(layer) {
      const index = this.selectedLayers.indexOf(layer)
      if (index > -1) {
        // Remove layer (hide it)
        this.selectedLayers.splice(index, 1)
      } else {
        // Add layer (show it)
        this.selectedLayers.push(layer)
      }
      this.updateGraphWithFilteredData()
    },

    toggleSite(site) {
      const index = this.selectedSites.indexOf(site)
      if (index > -1) {
        // Remove site (hide it)
        this.selectedSites.splice(index, 1)
      } else {
        // Add site (show it)
        this.selectedSites.push(site)
      }
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
        .map(node => ({
          id: node.alias,
          text: node.name,
          borderColor: this.layerColors[node.layer] || '#cccccc',
          fontColor: '#333333',
          color: '#ffffff',
          data: {
            layer: node.layer,
            site: node.site,
            metadata: node.metadata,
            ci_type: node.ci_type
          }
        }))

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

    getNodeIcon(node) {
      const iconMap = {
        'Application': '📱',
        'Middleware': '⚙️',
        'System': '🖥️',
        'Infrastructure': '🌐',
        'Network': '🔗'
      }
      return iconMap[node.data.layer] || '📦'
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
    gap: 8px;
    align-items: center;
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

      .layer-tag {
        transition: all 0.3s ease;
        user-select: none;

        &:hover {
          transform: scale(1.05);
        }

        &.layer-tag-inactive {
          opacity: 0.4;
          text-decoration: line-through;
        }
      }

      .site-tag {
        transition: all 0.3s ease;
        user-select: none;

        &:hover {
          transform: scale(1.05);
        }

        &.site-tag-inactive {
          opacity: 0.4;
          text-decoration: line-through;
        }
      }
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
</style>
