<template>
  <div class="network-viewer-container">
    <div class="diagram-wrapper">
      <div v-if="hasData" :id="diagramId" class="diagram"></div>
      <div v-else class="no-data-message">
        <div class="no-data-content">
          <svg class="no-data-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            ></path>
          </svg>
          <h3>No Network Data</h3>
          <p>No nodes or links provided to display the network diagram.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as go from 'gojs'

// Import icons
import cloudIcon from '@/assets/icons/cloud-server-svgrepo-com.svg'
import firewallIcon from '@/assets/icons/firewalld2-svgrepo-com.svg'
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import serverIcon from '@/assets/icons/server-svgrepo-com.svg'
import routerIcon from '@/assets/icons/router-svgrepo-com.svg'
import pcIcon from '@/assets/icons/pc-svgrepo-com.svg'

export default {
  name: 'NetworkViewer',

  props: {
    nodes: {
      type: Array,
      default: () => [],
      required: false,
    },
    links: {
      type: Array,
      default: () => [],
      required: false,
    },
  },

  data() {
    return {
      diagramId: `diagram-${this._uid}`,
      myDiagram: null,
      // Mock data for demonstration
      mockNodes: [
        { key: 0, type: 'Cloud', loc: '0 0', text: 'Internet' },
        { key: 1, type: 'Firewall', loc: '100 0', text: 'Main Firewall' },
        { key: 2, type: 'Router', loc: '200 0', text: 'Core Router' },
        { key: 3, type: 'Server', loc: '300 0', text: 'Web Server' },
        { key: 4, type: 'Switch', loc: '200 100', text: 'Main Switch' },
        { key: 5, type: 'Firewall', loc: '25 100', text: 'DMZ Firewall' },
        { key: 6, type: 'Router', loc: '25 200', text: 'Branch Router' },
        { key: 7, type: 'Switch', loc: '400 100', text: 'Access Switch' },

        // Groups
        { key: 10, isGroup: true, text: 'Office Network' },
        { key: 11, type: 'PC', loc: '150 220', group: 10, text: 'Workstation 1' },
        { key: 12, type: 'PC', loc: '250 220', group: 10, text: 'Workstation 2' },
        { key: 13, type: 'PC', loc: '150 270', group: 10, text: 'Laptop 1' },
        { key: 14, type: 'PC', loc: '250 270', group: 10, text: 'Laptop 2' },

        { key: 20, isGroup: true, text: 'Server Farm' },
        { key: 21, type: 'Server', loc: '350 220', group: 20, text: 'Database Server' },
        { key: 22, type: 'Server', loc: '450 220', group: 20, text: 'File Server' },
        { key: 23, type: 'Server', loc: '350 270', group: 20, text: 'Mail Server' },
        { key: 24, type: 'Server', loc: '450 270', group: 20, text: 'Backup Server' },

        { key: 30, isGroup: true, text: 'Guest Network' },
        { key: 31, type: 'PC', loc: '-100 172', group: 30, text: 'Guest Device 1' },
        { key: 32, type: 'PC', loc: '-100 242', group: 30, text: 'Guest Device 2' },
      ],
      mockLinks: [
        { from: 0, to: 1, startLabel: 'WAN', endLabel: 'Internet' },
        { from: 1, to: 2, startLabel: 'Filtered', endLabel: 'Clean' },
        { from: 2, to: 3, startLabel: 'HTTP', endLabel: 'Web' },
        { from: 2, to: 4, startLabel: 'LAN', endLabel: 'Switch' },
        { from: 5, to: 4, startLabel: 'DMZ', endLabel: 'Internal' },
        { from: 5, to: 6, startLabel: 'Secure', endLabel: 'Branch' },
        { from: 4, to: 7, startLabel: 'Trunk', endLabel: 'Access' },
        { from: 4, to: 10, startLabel: 'Office', endLabel: 'Users' },
        { from: 7, to: 20, startLabel: 'Data', endLabel: 'Servers' },
        { from: 6, to: 30, startLabel: 'Guest', endLabel: 'Isolated' },
      ],
    }
  },

  computed: {
    // Use provided data or fall back to mock data
    effectiveNodes() {
      return this.nodes.length > 0 ? this.nodes : this.mockNodes
    },

    effectiveLinks() {
      return this.links.length > 0 ? this.links : this.mockLinks
    },

    hasData() {
      return this.effectiveNodes.length > 0 || this.effectiveLinks.length > 0
    },
  },

  mounted() {
    if (typeof go !== 'undefined' && this.hasData) {
      this.initDiagram()
    }
  },

  beforeUnmount() {
    // Clean up the diagram when component is destroyed
    if (this.myDiagram) {
      this.myDiagram.div = null
      this.myDiagram = null
    }
  },

  watch: {
    nodes: {
      handler(newNodes) {
        if (this.myDiagram) {
          this.updateDiagram()
        } else if (this.hasData) {
          this.$nextTick(() => {
            this.initDiagram()
          })
        }
      },
      deep: true,
    },
    links: {
      handler(newLinks) {
        if (this.myDiagram) {
          this.updateDiagram()
        } else if (this.hasData) {
          this.$nextTick(() => {
            this.initDiagram()
          })
        }
      },
      deep: true,
    },
  },

  methods: {
    initDiagram() {
      // Only initialize if we have data and the div exists
      if (!this.hasData || !document.getElementById(this.diagramId)) {
        return
      }

      // Configure the diagram for view-only mode
      this.myDiagram = new go.Diagram(this.diagramId, {
        allowMove: true,
        allowCopy: false,
        allowDelete: false,
        allowInsert: false,
        hasHorizontalScrollbar: true,
        hasVerticalScrollbar: true,
        initialContentAlignment: go.Spot.Center,
      })

      // grid
      this.myDiagram.grid = new go.Panel('Grid')
        .add(new go.Shape('LineH', { stroke: 'rgba(0,0,0,0.1)', strokeWidth: 1 }))
        .add(new go.Shape('LineV', { stroke: 'rgba(0,0,0,0.1)', strokeWidth: 1 }))
      this.myDiagram.grid.visible = true
      this.myDiagram.grid.gridCellSize = new go.Size(20, 20)

      this.setupNodeTemplate()
      this.setupGroupTemplate()
      this.setupLinkTemplate()

      // Load initial data
      this.updateDiagram()
    },

    setupNodeTemplate() {
      this.myDiagram.nodeTemplate = new go.Node('Spot', {
        locationSpot: go.Spot.Center,
        locationObjectName: 'BODY',
        selectionObjectName: 'BODY',
        toolTip: this.makeToolTip(),
      })
        .bind(new go.Binding('location', 'loc', go.Point.parse))
        .add(
          new go.Panel('Auto', { name: 'BODY' })
            .add(
              new go.Picture({
                width: 50,
                height: 50,
                portId: '',
              }).bind('source', 'type', (type) => this.getIconForType(type))
            )
            .add(
              new go.TextBlock({
                font: 'bold 5pt Helvetica, Arial, sans-serif',
                margin: 8,
                maxSize: new go.Size(160, NaN),
                wrap: go.TextBlock.WrapFit,
                background: '#fff',
                editable: false,
              }).bind(new go.Binding('text', 'text'))
            )
        )
    },

    setupGroupTemplate() {
      this.myDiagram.groupTemplate = new go.Group('Vertical', {
        locationSpot: go.Spot.Center,
        padding: 5,
        selectable: false,
        computesBoundsAfterDrag: true,
        computesBoundsIncludingLocation: true,
      })
        .add(
          new go.TextBlock({
            alignment: go.Spot.Left,
            font: '12px georgia',
            editable: false,
          }).bind(new go.Binding('text'))
        )
        .add(
          new go.Panel('Auto')
            .add(
              new go.Shape('RoundedRectangle', {
                strokeDashArray: [2, 6],
                stroke: '#333',
                fill: 'white',
                cornerRadius: 10,
                minSize: new go.Size(100, 100),
              })
            )
            .add(
              new go.Placeholder({
                padding: 5,
                alignment: go.Spot.Center,
              })
            )
        )
    },

    setupLinkTemplate() {
      this.myDiagram.linkTemplate = new go.Link({
        routing: go.Link.Normal,
        curve: go.Link.None,
        selectable: false,
      })
        .add(
          new go.Shape({
            strokeWidth: 1.5,
          })
        )
        .add(
          new go.Shape({
            toArrow: 'Standard',
          })
        )
        .add(
          new go.TextBlock({
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: 0,
            segmentFraction: 0.1,
            segmentOffset: new go.Point(0, -12),
            background: 'rgba(255, 255, 255, 0.9)',
            margin: 2,
            editable: false,
          }).bind(new go.Binding('text', 'startLabel'))
        )
        .add(
          new go.TextBlock({
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: 0,
            segmentFraction: 0.9,
            segmentOffset: new go.Point(0, -12),
            background: 'rgba(255, 255, 255, 0.9)',
            margin: 2,
            editable: false,
          }).bind(new go.Binding('text', 'endLabel'))
        )
    },

    getIconForType(type) {
      const iconMap = {
        Cloud: cloudIcon,
        Firewall: firewallIcon,
        Switch: switchIcon,
        Server: serverIcon,
        WebServer: serverIcon,
        DatabaseServer: serverIcon,
        FileServer: serverIcon,
        MailServer: serverIcon,
        Router: routerIcon,
        PC: pcIcon,
      }
      return iconMap[type] || cloudIcon
    },

    makeToolTip() {
      return new go.Adornment('Auto').add(new go.Shape({ fill: '#FFFFCC' })).add(
        new go.TextBlock({ margin: 4 }).bind('text', '', (data) => {
          return `Type: ${data.type}\nText: ${data.text || 'N/A'}`
        })
      )
    },

    updateDiagram() {
      if (!this.myDiagram || !this.hasData) {
        return
      }

      try {
        // Use effective data (props or mock)
        const model = new go.GraphLinksModel(
          JSON.parse(JSON.stringify(this.effectiveNodes)),
          JSON.parse(JSON.stringify(this.effectiveLinks))
        )

        this.myDiagram.model = model

        // Center the diagram after loading
        this.myDiagram.delayInitialization(() => {
          this.myDiagram.centerRect(this.myDiagram.documentBounds)
        })
      } catch (error) {
        console.error('Error updating network diagram:', error)
      }
    },
  },
}
</script>

<style scoped>
.network-viewer-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.diagram-wrapper {
  display: flex;
  flex: 1;
}

.diagram {
  flex-grow: 1;
  height: 500px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #ffffff;
}

.no-data-message {
  flex-grow: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-height: 400px;
}

.no-data-content {
  text-align: center;
  max-width: 300px;
}

.no-data-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  color: #9ca3af;
}

.no-data-content h3 {
  margin: 0 0 8px 0;
  color: #374151;
  font-size: 18px;
  font-weight: 600;
}

.no-data-content p {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  line-height: 1.5;
}
</style>
