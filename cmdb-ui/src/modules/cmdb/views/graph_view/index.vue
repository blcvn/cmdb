<template>
  <div class="graph-view-container">
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
</template>

<script>
import SeeksRelationGraph from '@/modules/cmdb/3rd/relation-graph'
import mockData from './mock.json'

export default {
  name: 'GraphView',
  components: {
    SeeksRelationGraph
  },
  data() {
    return {
      loading: false,
      selectedLayout: 'tree',
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
  mounted() {
    this.loadGraphData()
  },
  methods: {
    loadGraphData() {
      this.loading = true
      try {
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
      this.loadGraphData()
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
      // Filter nodes by selected layers AND selected sites
      const filteredNodes = mockData.node
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
      const filteredLinks = mockData.edges
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
