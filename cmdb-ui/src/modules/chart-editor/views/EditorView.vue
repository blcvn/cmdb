<template>
  <div class="network-config-container">
    <div class="diagram-wrapper">
      <!-- Main Palette with header -->
      <div class="palette-section">
        <div class="palette-header">
          <h3>Devices</h3>
        </div>
        <div class="palette-content">
          <!-- Device Types with GoJS Palettes -->
          <div class="device-types-list">
            <div v-for="deviceType in deviceTypes" :key="deviceType.id" class="device-type-group">
              <!-- Device Type Header -->
              <div
                class="device-type-header"
                @click="toggleDeviceTypeDropdown(deviceType.id)"
                :class="{ expanded: expandedTypes.includes(deviceType.id) }"
              >
                <div class="device-type-main">
                  <!-- <img :src="deviceType.icon" :alt="deviceType.name" class="device-icon" /> -->
                  <span class="device-name">{{ deviceType.name }}</span>
                </div>
                <div class="dropdown-arrow" :class="{ rotated: expandedTypes.includes(deviceType.id) }">▼</div>
              </div>

              <!-- GoJS Palette Container -->
              <div v-if="expandedTypes.includes(deviceType.id)" class="device-palette-container">
                <div v-if="deviceLoadingStates[deviceType.id]" class="loading-message">Loading devices...</div>
                <div
                  v-else-if="!devicesByTypeMap[deviceType.id] || devicesByTypeMap[deviceType.id].length === 0"
                  class="no-devices-message"
                >
                  No devices found
                </div>
                <div
                  v-else
                  :id="`palette-${deviceType.id}`"
                  class="gojs-palette"
                  @mouseenter="hideTooltip"
                  @mouseleave="hideTooltip"
                ></div>
              </div>
            </div>
          </div>
        </div>
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
      <textarea id="modelJson" class="json-output" v-model="initialModelJson" rows="20" cols="170"></textarea>
    </div>

    <!-- Save Modal -->
    <a-modal title="Save Diagram" v-model="saveModalVisible" @ok="handleSave" @cancel="handleCancel">
      <a-form layout="vertical">
        <a-form-item
          label="Diagram Name"
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
import { getDeviceTypes, getDevices, postTopology } from '../api/topology'

export default {
  name: 'EditorDiagram',
  data() {
    return {
      myDiagram: null,
      palettes: {}, // Store all palettes by device type
      saveModalVisible: false,
      topologyForm: {
        name: '',
        description: '',
      },
      // Device types from API
      deviceTypes: [],
      isLoadingDeviceTypes: false,
      // Dropdown state
      expandedTypes: [],
      // Devices data organized by type
      devicesByTypeMap: {},
      deviceLoadingStates: {},
      // Tooltip state
      showTooltip: false,
      tooltipDevice: null,
      tooltipPosition: { x: 0, y: 0 },
      tooltipTimeout: null,
      isDragging: false, // Track dragging state

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

  async mounted() {
    if (typeof go !== 'undefined') {
      await this.loadDeviceTypes()
      this.init()
    }
  },

  beforeUnmount() {
    if (this.tooltipTimeout) {
      clearTimeout(this.tooltipTimeout)
    }
    // Dispose all palettes
    Object.values(this.palettes).forEach((palette) => {
      if (palette) {
        palette.div = null
      }
    })
    if (this.myDiagram) {
      this.myDiagram.div = null
    }
  },

  methods: {
    // Load device types from API
    async loadDeviceTypes() {
      this.isLoadingDeviceTypes = true
      try {
        const response = await getDeviceTypes()
        this.deviceTypes = response.data || response
        console.log('Device types loaded:', this.deviceTypes)
      } catch (error) {
        console.error('Failed to load device types:', error)
        this.$message.error('Failed to load device types')
        this.deviceTypes = this.getDefaultDeviceTypes()
      } finally {
        this.isLoadingDeviceTypes = false
      }
    },

    // Toggle device type dropdown and create palette
    async toggleDeviceTypeDropdown(typeId) {
      const index = this.expandedTypes.indexOf(typeId)
      if (index > -1) {
        this.expandedTypes.splice(index, 1)
        // Dispose palette when closing
        if (this.palettes[typeId]) {
          this.palettes[typeId].div = null
          delete this.palettes[typeId]
        }
      } else {
        this.expandedTypes.push(typeId)
        const deviceType = this.deviceTypes.find((type) => type.id === typeId)
        await this.loadDevicesForType(deviceType)
        // Create palette after loading devices
        this.$nextTick(() => {
          this.createPaletteForType(typeId)
        })
      }
    },

    // Create GoJS palette for a device type
    createPaletteForType(typeId) {
      const paletteDiv = document.getElementById(`palette-${typeId}`)
      if (!paletteDiv || this.palettes[typeId]) return

      const devices = this.devicesByTypeMap[typeId] || []
      if (devices.length === 0) return

      // Create palette
      const palette = new go.Palette(paletteDiv, {
        // Allow zoom out but prevent zoom in to keep items small
        allowZoom: false,
        initialScale: 0.8,
        // Grid layout with appropriate sizing
        layout: new go.GridLayout({
          // wrappingColumn: 2,
          spacing: new go.Size(5, 5),
        }),
        // Make palette smaller and scrollable
        maxSelectionCount: 1,
        mouseWheelBehavior: go.ToolManager.WheelScroll,
      })

      // Use the same node template as main diagram but smaller
      palette.nodeTemplate = this.createPaletteNodeTemplate()

      // Prepare node data for palette
      const nodeDataArray = devices.map((device, index) => ({
        key: `${typeId}-${device.id}-${index}`,
        type: device.type,
        text: device.name,
        deviceId: device.id,
        status: device.status,
        metadata: device.metadata,
        // Add visual status indicator
        fillColor: device.status === 'active' ? 'lightgreen' : 'lightgray',
      }))

      palette.model = new go.GraphLinksModel(nodeDataArray)

      // Store palette reference
      this.palettes[typeId] = palette

      // Add drag start/end listeners to handle tooltip hiding
      palette.addDiagramListener('ExternalObjectsDropped', (e) => {
        this.isDragging = false
        this.hideTooltip()
      })

      palette.toolManager.draggingTool.doStart = function () {
        this.diagram.skipsUndoManager = true // Don't record palette operations
        // Hide tooltip when dragging starts
        if (this.diagram.vue) {
          this.diagram.vue.isDragging = true
          this.diagram.vue.hideTooltip()
        }
        return go.DraggingTool.prototype.doStart.call(this)
      }

      palette.toolManager.draggingTool.doStop = function () {
        if (this.diagram.vue) {
          this.diagram.vue.isDragging = false
        }
        return go.DraggingTool.prototype.doStop.call(this)
      }

      // Store reference to Vue component for callback
      palette.vue = this
    },

    // Create node template for palette
    createPaletteNodeTemplate() {
      return new go.Node('Table', {
        locationSpot: go.Spot.Center,
        selectionObjectName: 'BODY',
        toolTip: this.makePaletteToolTip(),
        margin: 2,
        spacing: 2,
      })
        .add(
          new go.Panel('Spot', { width: 52, height: 52 })
            .add(
              new go.Shape('RoundedRectangle', {
                width: 50,
                height: 50,
                strokeWidth: 1,
                stroke: 'grey',
                fill: 'lightgrey',
              })
            )
            .add(
              new go.Picture({
                width: 52,
                height: 52,
                visible: false,
              }).bind('source', 'type', (type, shape) => {
                const path = this.getIconPath(type)
                shape.visible = !!path
                return path
              })
            )
        )
        .add(
          new go.TextBlock({
            font: 'bold 8pt Helvetica, Arial, sans-serif',
            stroke: '#333',
            textAlign: 'center',
            maxSize: new go.Size(55, 20),
            wrap: go.TextBlock.WrapFit,
            margin: new go.Margin(2, 2, 0, 2),
          }).bind('text', 'text')
        )
    },

    // Create tooltip for palette items
    makePaletteToolTip() {
      return new go.Adornment('Auto')
        .add(new go.Shape({ fill: '#FFFFCC', stroke: '#666', figure: 'RoundedRectangle' }))
        .add(
          new go.TextBlock({ margin: 8, font: '10pt Helvetica', stroke: '#333' }).bind('text', '', (data) => {
            let tooltip = data.text || ''

            if (data.deviceId) tooltip += `\nDevice ID: ${data.deviceId}`
            if (data.status) tooltip += `\nStatus: ${data.status}`

            // Loop through all metadata properties
            if (data.metadata) {
              for (const key in data.metadata) {
                tooltip += `\n${key}: ${data.metadata[key]}`
              }
            }

            return tooltip
          })
        )
    },

    // Mock devices generator
    getMockDevices(typeId) {
      const baseDevices = {
        cloud: [
          { id: 'cloud-1', name: 'AWS Cloud', type: 'cloud', status: 'active', metadata: { ip: '52.12.34.56' } },
          { id: 'cloud-2', name: 'Azure Cloud', type: 'cloud', status: 'inactive', metadata: { ip: '40.112.22.11' } },
          { id: 'cloud-3', name: 'Cloudflare', type: 'cloud', status: 'inactive', metadata: { ip: '40.112.22.11' } },
        ],
        firewall: [
          { id: 'fw-1', name: 'Perimeter FW', type: 'firewall', status: 'active', metadata: { ip: '10.0.0.1' } },
          { id: 'fw-2', name: 'DMZ FW', type: 'firewall', status: 'active', metadata: { ip: '10.0.1.1' } },
        ],
        router: [
          { id: 'rtr-1', name: 'Core Router', type: 'router', status: 'active', metadata: { ip: '192.168.1.1' } },
          { id: 'rtr-2', name: 'Branch Router', type: 'router', status: 'inactive', metadata: { ip: '192.168.2.1' } },
        ],
        switch: [
          { id: 'sw-1', name: 'Main Switch', type: 'switch', status: 'active', metadata: { ip: '192.168.1.10' } },
          { id: 'sw-2', name: 'Access Switch', type: 'switch', status: 'active', metadata: { ip: '192.168.1.20' } },
        ],
        server: [
          { id: 'srv-1', name: 'Web Server', type: 'server', status: 'active', metadata: { ip: '172.16.0.5' } },
          { id: 'srv-2', name: 'DB Server', type: 'server', status: 'inactive', metadata: { ip: '172.16.0.6' } },
        ],
        pc: [
          { id: 'pc-1', name: 'Workstation 1', type: 'pc', status: 'active', metadata: { ip: '192.168.1.101' } },
          { id: 'pc-2', name: 'Laptop 1', type: 'pc', status: 'inactive', metadata: { ip: '192.168.1.102' } },
        ],
      }
      return baseDevices[typeId] || []
    },

    // Load devices for a specific type
    async loadDevicesForType(deviceType) {
      if (!deviceType || this.devicesByTypeMap[deviceType.id]) {
        return // Already loaded or invalid type
      }

      this.$set(this.deviceLoadingStates, deviceType.id, true)
      let devices = []
      try {
        const response = await getDevices({ type: deviceType.id })
        devices = response.data || response
        this.$set(this.devicesByTypeMap, deviceType.id, devices)
        console.log(`Devices loaded for type ${deviceType.id}:`, devices)
      } catch (error) {
        console.error(`Failed to load devices for type ${deviceType.id}:`, error)
        devices = this.getMockDevices(deviceType.id)
        this.$set(this.devicesByTypeMap, deviceType.id, devices)
      } finally {
        this.$set(this.deviceLoadingStates, deviceType.id, false)
      }
    },

    // Hide tooltip (improved to handle dragging)
    hideTooltip() {
      if (this.tooltipTimeout) {
        clearTimeout(this.tooltipTimeout)
        this.tooltipTimeout = null
      }
      this.showTooltip = false
      this.tooltipDevice = null
    },

    // Get device type icon
    getDeviceTypeIcon(typeId) {
      const deviceType = this.deviceTypes.find((type) => type.id === typeId)
      return deviceType ? deviceType.icon : '/icons/server-svgrepo-com.svg'
    },

    // Default device types as fallback
    getDefaultDeviceTypes() {
      return [
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
      ]
    },

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

    init() {
      // Configure the main diagram
      this.myDiagram = new go.Diagram('myDiagramDiv', {
        'undoManager.isEnabled': true,
        'draggingTool.dragsLink': false,
        'draggingTool.isGridSnapEnabled': true,
        'linkingTool.direction': go.LinkingTool.ForwardsOnly,
        'commandHandler.archetypeGroupData': { isGroup: true, text: 'Group' },
        allowDrop: true,
      })

      // Update JSON output whenever the diagram changes
      this.myDiagram.addModelChangedListener((evt) => {
        if (evt.isTransactionFinished) {
          this.initialModelJson = this.myDiagram.model.toJson()
        }
      })

      // Main diagram node template (same as before but improved)
      this.myDiagram.nodeTemplate = new go.Node('Vertical', {
        locationSpot: go.Spot.Center,
        selectionObjectName: 'BODY',
        toolTip: this.makeToolTip(),
        margin: 4,
      })
        .bind(new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify))
        .add(
          new go.Picture({
            width: 50,
            height: 50,
            fromLinkable: true,
            toLinkable: true,
            cursor: 'pointer',
            portId: '',
            margin: new go.Margin(4, 4, 2, 4),
          }).bind('source', 'type', (type) => this.getIconPath(type))
        )
        .add(
          new go.TextBlock({
            font: 'bold 9pt Helvetica, Arial, sans-serif',
            stroke: '#333',
            textAlign: 'center',
            maxSize: new go.Size(70, 24),
            wrap: go.TextBlock.WrapFit,
            editable: true,
            margin: new go.Margin(2, 4, 6, 4),
          }).bind(new go.Binding('text', 'text').makeTwoWay())
        )

      // Group template (same as before)
      this.myDiagram.groupTemplate = new go.Group('Vertical', {
        locationSpot: go.Spot.Center,
        padding: new go.Margin(15, 10, 15, 10),
        selectable: true,
        computesBoundsAfterDrag: true,
        computesBoundsIncludingLocation: true,
        layout: new go.GridLayout({
          wrappingColumn: 2,
          wrappingWidth: 400,
          cellSize: new go.Size(90, 80),
          spacing: new go.Size(10, 10),
        }),
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
                minSize: new go.Size(120, 100),
              })
            )
            .add(
              new go.Placeholder({
                padding: new go.Margin(10, 10, 10, 10),
                alignment: go.Spot.Center,
              })
            )
        )

      // Link template
      this.myDiagram.linkTemplate = new go.Link({
        routing: go.Link.Normal,
        curve: go.Link.None,
        corner: 5,
      })
        .add(
          new go.Shape({
            strokeWidth: 2,
          })
        )
        .add(
          new go.Shape({
            toArrow: 'Standard',
            strokeWidth: 0,
          })
        )
        .add(
          new go.TextBlock({
            font: '9px Arial',
            stroke: '#000',
            segmentIndex: 0,
            segmentFraction: 0.15,
            segmentOffset: new go.Point(0, -20),
            background: 'rgba(255, 255, 255, 0.95)',
            margin: 3,
            editable: true,
            maxSize: new go.Size(60, NaN),
          }).bind(new go.Binding('text', 'startLabel').makeTwoWay())
        )
        .add(
          new go.TextBlock({
            font: '9px Arial',
            stroke: '#000',
            segmentIndex: 0,
            segmentFraction: 0.85,
            segmentOffset: new go.Point(0, -20),
            background: 'rgba(255, 255, 255, 0.95)',
            margin: 3,
            editable: true,
            maxSize: new go.Size(60, NaN),
          }).bind(new go.Binding('text', 'endLabel').makeTwoWay())
        )

      this.load()
    },

    // Get icon path from device types
    getIconPath(type) {
      const deviceType = this.deviceTypes.find((device) => device.id === type)
      if (deviceType) {
        return deviceType.icon
      }

      const legacyMapping = {
        Cloud: '/icons/cloud-server-svgrepo-com.svg',
        Firewall: '/icons/firewalld2-svgrepo-com.svg',
        Switch: '/icons/switch-svgrepo-com.svg',
        Server: '/icons/server-svgrepo-com.svg',
        Router: '/icons/router-svgrepo-com.svg',
        PC: '/icons/pc-svgrepo-com.svg',
        cloud: '/icons/cloud-server-svgrepo-com.svg',
        firewall: '/icons/firewalld2-svgrepo-com.svg',
        switch: '/icons/switch-svgrepo-com.svg',
        server: '/icons/server-svgrepo-com.svg',
        router: '/icons/router-svgrepo-com.svg',
        pc: '/icons/pc-svgrepo-com.svg',
      }

      return legacyMapping[type] || '/icons/server-svgrepo-com.svg'
    },

    makeToolTip() {
      const $ = go.GraphObject.make

      return $(
        go.Adornment,
        'Auto',
        $(go.Shape, { fill: '#FFFFCC', stroke: '#666', figure: 'RoundedRectangle' }),
        $(
          go.Panel,
          'Vertical',
          { margin: 4 },
          new go.Binding('itemArray', '', (data) => {
            const items = []
            if (data.text) items.push({ text: data.text, bold: true })
            if (data.deviceId) items.push({ text: `Device ID: ${data.deviceId}` })
            if (data.status) items.push({ text: `Status: ${data.status}` })
            if (data.metadata) {
              for (const key in data.metadata) {
                items.push({ text: `${key}: ${data.metadata[key]}` })
              }
            }
            return items
          }),
          {
            itemTemplate: $(
              go.TextBlock,
              {
                font: '10pt Helvetica',
                stroke: '#333',
                margin: 2,
              },
              new go.Binding('text', 'text'),
              new go.Binding('font', 'bold', (b) => (b ? 'bold 10pt Helvetica' : '10pt Helvetica'))
            ),
          }
        )
      )
    },

    save() {
      const json = document.getElementById('modelJson')
      json.innerHTML = this.myDiagram.model.toJson()
      this.myDiagram.isModified = false
    },

    load() {
      this.myDiagram.model = go.Model.fromJson(this.initialModelJson)
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
  border: 1px solid #ddd;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
}

.palette-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #ddd;
  padding: 12px 16px;
  border-radius: 7px 7px 0 0;
}

.palette-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.palette-content {
  flex: 1;
  background-color: #fafbfc;
  border-radius: 0 0 7px 7px;
  overflow-y: auto;
}

.device-types-list {
  padding: 4px;
}

.device-type-group {
  margin-bottom: 2px;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  overflow: hidden;
}

.device-type-header {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.device-type-header:hover {
  background-color: #f1f3f4;
}

.device-type-header.expanded {
  background-color: #e8f0fe;
  border-bottom: 1px solid #dadce0;
}

.device-type-main {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 8px 12px;
}

.device-icon {
  width: 24px;
  height: 24px;
  margin-right: 8px;
  object-fit: contain;
}

.device-name {
  font-size: 13px;
  font-weight: 400;
  color: #3c4043;
}

.dropdown-arrow {
  padding: 8px 12px;
  font-size: 10px;
  color: #5f6368;
  transition: transform 0.2s ease;
  user-select: none;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

.device-palette-container {
  background: #f8f9fa;
  border-top: 1px solid #e8eaed;
}

.loading-message,
.no-devices-message {
  padding: 12px 16px;
  text-align: center;
  color: #5f6368;
  font-size: 12px;
  font-style: italic;
}

/* GoJS Palette Styling */
.gojs-palette {
  width: 100%;
  height: 140px;
  border: none;
  background: #f8f9fa;
  overflow: hidden;
}

/* Override GoJS default styles for palette */
.gojs-palette canvas {
  outline: none;
  border: none;
}

.diagram {
  flex-grow: 1;
  height: 600px;
  border: 1px solid black;
  border-radius: 8px;
}

.controls {
  margin-top: 10px;
  margin-bottom: 20px;
}

.btn {
  background: #f31c1c;
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
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.diagram-controls button:hover {
  background: #f0f0f0;
}

/* Animation for dropdown expand/collapse */
.device-palette-container {
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Scrollbar styling */
.palette-content::-webkit-scrollbar {
  width: 6px;
}

.palette-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.palette-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.palette-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Responsive design */
@media (max-width: 768px) {
  .palette-section {
    width: 160px;
  }

  .gojs-palette {
    height: 120px;
  }

  .device-name {
    font-size: 12px;
  }
}
</style>
