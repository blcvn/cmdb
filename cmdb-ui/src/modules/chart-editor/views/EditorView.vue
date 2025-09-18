<template>
  <div class="network-config-container">
    <div class="diagram-wrapper">
      <!-- Main Palette with header -->
      <div class="palette-section">
        <div class="palette-header">
          <h3>Components</h3>
        </div>
        <div id="myPaletteDiv" class="palette"></div>
      </div>

      <!-- Server Types Submenu -->
      <div
        v-if="showServerMenu"
        class="server-menu"
        :style="{ top: serverMenuPosition.y + 'px', left: serverMenuPosition.x - 250 + 'px' }"
      >
        <div class="server-menu-header">
          <span>Server Types</span>
          <button @click="closeServerMenu" class="close-btn">×</button>
        </div>
        <div id="serverPaletteDiv" class="server-palette"></div>
      </div>
      <div class="diagram-container">
        <!-- Control Buttons -->
        <div class="diagram-controls">
          <button @click="zoomIn">＋</button>
          <button @click="zoomOut">－</button>
          <button @click="undo">⟲</button>
          <button @click="redo">⟳</button>
        </div>
        <div id="myDiagramDiv" class="diagram"></div>
      </div>
    </div>

    <div class="controls">
      <a-button @click="openSaveModal" class="btn">Save</a-button>
      <a-button @click="load" class="btn">Load</a-button>
    </div>

    <div class="model-display">
      <span>Diagram Model saved in JSON format:</span>
      <pre id="modelJson" class="json-output">{{ initialModelJson }}</pre>
    </div>

    <!-- Save Modal -->
    <a-modal title="Save Topology" v-model="saveModalVisible" @ok="handleSave" @cancel="handleCancel">
      <a-form layout="vertical">
        <a-form-item
          label="Topology Name"
          required
          :validate-status="!topologyForm.name ? 'error' : ''"
          help="Please enter a name"
        >
          <a-input v-model="topologyForm.name" placeholder="Enter name" />
        </a-form-item>

        <a-form-item label="Description">
          <a-textarea v-model="topologyForm.description" placeholder="Enter description (optional)" rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import * as go from 'gojs'
import { postTopology } from '../api/topology'

export default {
  name: 'EditorDiagram',
  data() {
    return {
      showServerMenu: false,
      serverMenuPosition: { x: 0, y: 0 },
      myDiagram: null, // assume this gets set up elsewhere
      saveModalVisible: false,
      topologyForm: {
        name: '',
        description: '',
      },
      // Main palette icons - API ready format
      paletteIcons: [
        {
          id: 'cloud',
          name: 'Cloud',
          icon: '/assets/icons/cloud-server-svgrepo-com.svg',
          category: 'network',
        },
        {
          id: 'firewall',
          name: 'Firewall',
          icon: '/icons/firewalld2-svgrepo-com.svg',
          category: 'security',
        },
        {
          id: 'switch',
          name: 'Switch',
          icon: '/icons/switch-svgrepo-com.svg',
          category: 'network',
        },
        {
          id: 'server',
          name: 'Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'compute',
        },
        {
          id: 'router',
          name: 'Router',
          icon: '/icons/router-svgrepo-com.svg',
          category: 'network',
        },
        {
          id: 'pc',
          name: 'PC',
          icon: '/icons/pc-svgrepo-com.svg',
          category: 'endpoint',
        },
      ],
      // Server types for submenu - API ready format
      serverTypeIcons: [
        {
          id: 'web-server',
          name: 'Web Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'web',
        },
        {
          id: 'database-server',
          name: 'Database Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'database',
        },
        {
          id: 'file-server',
          name: 'File Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'storage',
        },
        {
          id: 'mail-server',
          name: 'Mail Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'email',
        },
        {
          id: 'dns-server',
          name: 'DNS Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'network',
        },
        {
          id: 'dhcp-server',
          name: 'DHCP Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'network',
        },
        {
          id: 'proxy-server',
          name: 'Proxy Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'security',
        },
        {
          id: 'application-server',
          name: 'Application Server',
          icon: '/icons/server-svgrepo-com.svg',
          category: 'application',
        },
      ],

      initialModelJson: `{
  "class": "go.GraphLinksModel", 
  "nodeDataArray": [
    { "key": 0, "type": "cloud", "loc": "0 0", "text": "Internet" },
    { "key": 1, "type": "firewall", "loc": "100 0", "text": "Main Firewall" },
    { "key": 2, "type": "router", "loc": "200 0", "text": "Core Router" },
    { "key": 3, "type": "server", "loc": "300 0", "text": "Web Server" },
    { "key": 4, "type": "switch", "loc": "200 100", "text": "Main Switch" },
    { "key": 5, "type": "firewall", "loc": "25 100", "text": "DMZ Firewall" },
    { "key": 6, "type": "router", "loc": "25 200", "text": "Branch Router" },
    { "key": 7, "type": "switch", "loc": "400 100", "text": "Access Switch" },

    { "key": 10, "isGroup": true, "text": "Intranet 1" },
    { "key": 11, "type": "pc", "loc": "150 220", "group": 10, "text": "Workstation 1" },
    { "key": 12, "type": "pc", "loc": "250 220", "group": 10, "text": "Workstation 2" },
    { "key": 13, "type": "pc", "loc": "150 270", "group": 10, "text": "Laptop 1" },
    { "key": 14, "type": "pc", "loc": "250 270", "group": 10, "text": "Laptop 2" },

    { "key": 20, "isGroup": true, "text": "Intranet 2" },
    { "key": 21, "type": "pc", "loc": "350 220", "group": 20, "text": "Guest Device 1" },
    { "key": 22, "type": "pc", "loc": "450 220", "group": 20, "text": "Guest Device 2" },
    { "key": 23, "type": "pc", "loc": "350 270", "group": 20, "text": "Mobile Device 1" },
    { "key": 24, "type": "pc", "loc": "450 270", "group": 20, "text": "Mobile Device 2" },

    { "key": 30, "isGroup": true, "text": "Server Farm" },
    { "key": 31, "type": "server", "loc": "-100 172", "group": 30, "text": "Database Server" },
    { "key": 32, "type": "server", "loc": "-100 242", "group": 30, "text": "File Server" }
  ],
  "linkDataArray": [
    { "from": 0, "to": 1, "text": "0-1", "startLabel": "WAN", "endLabel": "LAN" },
    { "from": 1, "to": 2, "text": "1-2", "startLabel": "filtered", "endLabel": "clean" },
    { "from": 2, "to": 3, "text": "2-3", "startLabel": "HTTP", "endLabel": "web" },
    { "from": 2, "to": 4, "text": "2-4", "startLabel": "trunk", "endLabel": "switch" },
    { "from": 5, "to": 4, "text": "5-4", "startLabel": "DMZ", "endLabel": "internal" },
    { "from": 5, "to": 6, "text": "5-6", "startLabel": "secure", "endLabel": "branch" },
    { "from": 4, "to": 7, "text": "4-7", "startLabel": "uplink", "endLabel": "access" },
    { "from": 4, "to": 10, "text": "4-10", "startLabel": "office", "endLabel": "users" },
    { "from": 7, "to": 20, "text": "7-20", "startLabel": "guest", "endLabel": "isolated" },
    { "from": 6, "to": 30, "text": "6-30", "startLabel": "data", "endLabel": "servers" }
  ]
}`,
    }
  },

  mounted() {
    if (typeof go !== 'undefined') {
      this.init()
      // Simulate API loading
      this.loadIconsFromAPI()
    }
    // Close server menu when clicking outside
    document.addEventListener('click', this.handleClickOutside)
  },

  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    if (this.myDiagram) {
      this.myDiagram.div = null
    }
    if (this.myPalette) {
      this.myPalette.div = null
    }
    if (this.serverPalette) {
      this.serverPalette.div = null
    }
  },

  methods: {
    zoomIn() {
      if (this.myDiagram) this.myDiagram.commandHandler.increaseZoom()
    },
    zoomOut() {
      if (this.myDiagram) this.myDiagram.commandHandler.decreaseZoom()
    },
    undo() {
      if (this.myDiagram) this.myDiagram.commandHandler.undo()
    },
    redo() {
      if (this.myDiagram) this.myDiagram.commandHandler.redo()
    },
    openSaveModal() {
      this.saveModalVisible = true
    },

    handleCancel() {
      this.saveModalVisible = false
    },

    async handleSave() {
      if (!this.topologyForm.name) {
        this.$message.error('Name is required!')
        return
      }

      try {
        const modelJson = this.myDiagram.model.toJson()
        const parsed = JSON.parse(modelJson)

        const payload = {
          name: this.topologyForm.name,
          description: this.topologyForm.description,
          nodes: parsed.nodeDataArray || [],
          links: parsed.linkDataArray || [],
        }

        await postTopology(payload)

        this.$message.success('Topology saved!')
        this.saveModalVisible = false
        this.topologyForm = { name: '', description: '' }
      } catch (err) {
        console.error(err)
        this.$message.error('Failed to save topology')
      }
    },

    // Simulate loading icons from API
    async loadIconsFromAPI() {
      try {
        // In real implementation:
        // const paletteResponse = await fetch('/api/palette-icons')
        // this.paletteIcons = await paletteResponse.json()
        //
        // const serverResponse = await fetch('/api/server-icons')
        // this.serverTypeIcons = await serverResponse.json()

        this.updatePaletteIcons()
        console.log('Icons loaded from API:', {
          paletteIcons: this.paletteIcons.length,
          serverIcons: this.serverTypeIcons.length,
        })
      } catch (error) {
        console.error('Failed to load icons from API:', error)
      }
    },

    init() {
      // Configure the diagram
      this.myDiagram = new go.Diagram('myDiagramDiv', {
        'undoManager.isEnabled': true,
        'draggingTool.dragsLink': false,
        'draggingTool.isGridSnapEnabled': true,
        'linkingTool.direction': go.LinkingTool.ForwardsOnly,
        'commandHandler.archetypeGroupData': { isGroup: true, text: 'Group' },
      })

      // Update JSON output whenever the diagram changes
      this.myDiagram.addModelChangedListener((evt) => {
        if (evt.isTransactionFinished) {
          this.initialModelJson = this.myDiagram.model.toJson()
        }
      })

      // Update the node template to use API-driven icons
      this.myDiagram.nodeTemplate = new go.Node('Spot', {
        locationSpot: go.Spot.Center,
        locationObjectName: 'BODY',
        selectionObjectName: 'BODY',
        resizable: true,
        resizeObjectName: 'BODY',
        toolTip: this.makeToolTip(),
      })
        .bind(new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify))
        .add(
          new go.Panel('Auto', { name: 'BODY' })
            .add(
              new go.Picture({
                width: 50,
                height: 50,
                portId: '',
                fromLinkable: true,
                toLinkable: true,
                cursor: 'pointer',
              }).bind('source', 'type', (type) => this.getIconPath(type))
            )
            .add(
              new go.TextBlock({
                font: 'bold 10pt Helvetica, Arial, sans-serif',
                margin: 8,
                maxSize: new go.Size(160, NaN),
                wrap: go.TextBlock.WrapFit,
                background: 'rgba(255, 255, 255, 0.7)',
                editable: true,
              }).bind(new go.Binding('text', 'text').makeTwoWay())
            )
        )

      // Define the group template
      this.myDiagram.groupTemplate = new go.Group('Vertical', {
        locationSpot: go.Spot.Center,
        padding: 5,
        selectable: true,
        computesBoundsAfterDrag: true,
        computesBoundsIncludingLocation: true,
      })
        .add(
          new go.TextBlock({
            alignment: go.Spot.Left,
            font: '12px georgia',
            editable: true,
          }).bind(new go.Binding('text').makeTwoWay())
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

      // Add text to existing link template
      this.myDiagram.linkTemplate = new go.Link({
        routing: go.Link.Normal,
        curve: go.Link.None,
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
            editable: true,
          }).bind(new go.Binding('text', 'startLabel').makeTwoWay())
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
            editable: true,
          }).bind(new go.Binding('text', 'endLabel').makeTwoWay())
        )

      // Configure the main palette
      this.myPalette = new go.Palette('myPaletteDiv', {
        nodeTemplateMap: this.myDiagram.nodeTemplateMap,
        layout: new go.GridLayout({
          cellSize: new go.Size(1, 1),
          spacing: new go.Size(5, 5),
          wrappingColumn: 1,
        }),
      })

      // Add click event to palette for server menu
      this.myPalette.addDiagramListener('ObjectSingleClicked', (e) => {
        const part = e.subject.part
        if (part && part.data && part.data.type === 'server') {
          this.showServerSubmenu(e.event)
        }
      })

      this.load()
    },

    // Update main palette with icon array data
    updatePaletteIcons() {
      if (this.myPalette) {
        this.myPalette.model.nodeDataArray = this.paletteIcons.map((icon) => ({
          type: icon.id,
          text: icon.name,
        }))
      }
    },

    // Get icon path from arrays based on type
    getIconPath(type) {
      // Check main palette icons first
      const paletteIcon = this.paletteIcons.find((icon) => icon.id === type)
      if (paletteIcon) {
        return paletteIcon.icon
      }

      // Check server type icons
      const serverIcon = this.serverTypeIcons.find((icon) => icon.id === type)
      if (serverIcon) {
        return serverIcon.icon
      }

      // Fallback for legacy types (capitalized)
      const legacyMapping = {
        Cloud: '/icons/cloud-server-svgrepo-com.svg',
        Firewall: '/icons/firewalld2-svgrepo-com.svg',
        Switch: '/icons/switch-svgrepo-com.svg',
        Server: '/icons/server-svgrepo-com.svg',
        Router: '/icons/router-svgrepo-com.svg',
        PC: '/icons/pc-svgrepo-com.svg',
      }

      return legacyMapping[type] || '/icons/server-svgrepo-com.svg'
    },

    showServerSubmenu(event) {
      // Calculate position for the server menu
      const paletteRect = document.getElementById('myPaletteDiv').getBoundingClientRect()
      this.serverMenuPosition = {
        x: paletteRect.right,
        y: paletteRect.top,
      }

      this.showServerMenu = true

      // Initialize server palette after Vue updates the DOM
      this.$nextTick(() => {
        this.initServerPalette()
      })
    },

    initServerPalette() {
      if (this.serverPalette) {
        this.serverPalette.div = null
      }

      this.serverPalette = new go.Palette('serverPaletteDiv', {
        nodeTemplateMap: this.myDiagram.nodeTemplateMap,
        layout: new go.GridLayout({
          cellSize: new go.Size(1, 1),
          spacing: new go.Size(5, 5),
          wrappingColumn: 1,
        }),
      })

      // Use server type icons from array
      this.serverPalette.model.nodeDataArray = this.serverTypeIcons.map((server) => ({
        type: server.id,
        text: server.name,
      }))
    },

    handleClickOutside(event) {
      const serverMenu = document.querySelector('.server-menu')
      const palette = document.getElementById('myPaletteDiv')

      if (this.showServerMenu && serverMenu && !serverMenu.contains(event.target) && !palette.contains(event.target)) {
        this.closeServerMenu()
      }
    },

    makeToolTip() {
      return new go.Adornment('Auto')
        .add(new go.Shape({ fill: '#FFFFCC' }))
        .add(new go.TextBlock({ margin: 4 }).bind('text', 'text'))
    },

    save() {
      const json = document.getElementById('modelJson')
      json.innerHTML = this.myDiagram.model.toJson()
      this.myDiagram.isModified = false
    },

    load() {
      const json = document.getElementById('modelJson')
      this.myDiagram.model = go.Model.fromJson(json.textContent)
    },
    closeServerMenu() {
      this.showServerMenu = false
    },
  },
}
</script>

<style scoped>
.network-config-container {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
}

.diagram-wrapper {
  display: flex;
  flex: 1;
}

.palette-section {
  width: 200px;
  margin-right: 2px;
  background-color: white;
  border: 1px solid black;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.palette-header {
  background-color: #f5f5f5;
  border-bottom: 1px solid #ddd;
  padding: 10px 15px;
  border-radius: 7px 7px 0 0;
}

.palette-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.palette {
  flex: 1;
  height: 600px;
  background-color: whitesmoke;
  border-radius: 0 0 7px 7px;
}

.diagram {
  flex-grow: 1;
  height: 600px;
  border: 1px solid black;
  border-radius: 8px;
}

/* Server submenu styles */
.server-menu {
  position: absolute;
  z-index: 1000;
  background: white;
  border: 2px solid #333;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 150px;
  max-width: 200px;
}

.server-menu-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
  border-radius: 6px 6px 0 0;
  font-weight: bold;
  font-size: 12px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: #e0e0e0;
  color: #333;
}

.server-palette {
  height: 200px;
  background-color: whitesmoke;
  border-radius: 0 0 6px 6px;
}

.controls {
  margin-top: 10px;
  margin-bottom: 20px;
}

.btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  margin-right: 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn:hover {
  background: #0056b3;
}

.model-display {
  margin-top: 20px;
}

.model-display span {
  display: block;
  margin-bottom: 10px;
  font-weight: bold;
}

.json-output {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 15px;
  max-height: 600px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre;
  color: #333;
}

.diagram-container {
  position: relative;
  flex-grow: 1;
}

.diagram-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 6px;
  z-index: 2000;
}

.diagram-controls button {
  background: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  padding: 5px 8px;
  cursor: pointer;
  font-size: 14px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.1);
}

.diagram-controls button:hover {
  background: #f0f0f0;
}

</style>
