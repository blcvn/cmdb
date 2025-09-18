<template>
  <div>
    <div ref="diagramDiv" :style="{ width: '100%', height: height, border: '1px solid #ddd' }"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
const aciData = {
  nodes: [
    // Groups
    { key: 'SPINE', isGroup: true },
    { key: 'LEAF', isGroup: true },
    { key: 'APIC', isGroup: true },

    // SPINE nodes
    { key: 'SPINE-01', label: 'SPINE-01', type: 'spine', color: '#9ec5fe', group: 'SPINE' },
    { key: 'SPINE-02', label: 'SPINE-02', type: 'spine', color: '#9ec5fe', group: 'SPINE' },

    // LEAF nodes (10 nodes như mẫu)
    { key: 'LEAF-01', label: 'LEAF-01', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-02', label: 'LEAF-02', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-03', label: 'LEAF-03', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-04', label: 'LEAF-04', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-05', label: 'LEAF-05', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-06', label: 'LEAF-06', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-07', label: 'LEAF-07', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-08', label: 'LEAF-08', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-09', label: 'LEAF-09', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
    { key: 'LEAF-10', label: 'LEAF-10', type: 'leaf', color: '#bde0fe', group: 'LEAF' },

    // APIC nodes
    { key: 'APIC-01', label: 'APIC-01', type: 'apic', color: '#d6f7dd', group: 'APIC' },
    { key: 'APIC-02', label: 'APIC-02', type: 'apic', color: '#d6f7dd', group: 'APIC' },
    { key: 'APIC-03', label: 'APIC-03', type: 'apic', color: '#d6f7dd', group: 'APIC' },
  ],
  links: [
    // SPINE-01 connections (highlighted in blue)
    { from: 'SPINE-01', to: 'LEAF-01', label: 'E1/59', isHighlighted: true },
    { from: 'SPINE-01', to: 'LEAF-02', label: 'E1/59', isHighlighted: true },
    { from: 'SPINE-01', to: 'LEAF-03', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-04', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-05', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-06', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-07', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-08', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-09', label: 'E1/23-32' },
    { from: 'SPINE-01', to: 'LEAF-10', label: 'E1/23-32' },

    // SPINE-02 connections (highlighted in blue)
    { from: 'SPINE-02', to: 'LEAF-01', label: 'E1/60', isHighlighted: true },
    { from: 'SPINE-02', to: 'LEAF-02', label: 'E1/60', isHighlighted: true },
    { from: 'SPINE-02', to: 'LEAF-03', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-04', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-05', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-06', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-07', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-08', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-09', label: 'E1/23-32' },
    { from: 'SPINE-02', to: 'LEAF-10', label: 'E1/23-32' },

    // LEAF to APIC connections (highlighted in blue)
    { from: 'LEAF-01', to: 'APIC-01', label: 'E1/1', isHighlighted: true },
    { from: 'LEAF-02', to: 'APIC-02', label: 'E1/2', isHighlighted: true },
    { from: 'LEAF-03', to: 'APIC-03', label: 'E1/3', isHighlighted: true },
  ],
}

export default {
  name: 'NetworkTopology',
  props: {
    nodes: {
      type: Array,
      default: () => aciData.nodes,
    },
    links: {
      type: Array,
      default: () => aciData.links,
    },
    height: {
      type: String,
      default: '700px',
    },
  },
  data() {
    return { diagram: null }
  },
  mounted() {
    this.initDiagram()
  },
  beforeDestroy() {
    if (this.diagram) this.diagram.div = null
  },
  watch: {
    nodes: {
      handler() {
        this.updateDiagram()
      },
      deep: true,
    },
    links: {
      handler() {
        this.updateDiagram()
      },
      deep: true,
    },
  },
  methods: {
    initDiagram() {
      const $ = go.GraphObject.make
      const diagramDiv = this.$refs.diagramDiv

      const diagram = $(go.Diagram, diagramDiv, {
        initialContentAlignment: go.Spot.TopCenter,
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
      })

      // Add grid
      diagram.grid = $(
        go.Panel,
        'Grid',
        $(go.Shape, 'LineH', { stroke: 'rgba(0,0,0,0.1)', strokeWidth: 1 }),
        $(go.Shape, 'LineV', { stroke: 'rgba(0,0,0,0.1)', strokeWidth: 1 })
      )
      diagram.grid.visible = true

      // --- Node template ---
      diagram.nodeTemplate = $(
        go.Node,
        'Auto',
        new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
        $(
          go.Shape,
          'RoundedRectangle',
          { stroke: '#444', strokeWidth: 1.5, minSize: new go.Size(100, 50) },
          new go.Binding('fill', 'color')
        ),
        $(
          go.Panel,
          'Vertical',
          { margin: 6 },
          $(go.TextBlock, { font: 'bold 11px sans-serif', textAlign: 'center' }, new go.Binding('text', 'label')),
          $(
            go.TextBlock,
            { font: '9px sans-serif', textAlign: 'center', stroke: '#666', maxLines: 2 },
            new go.Binding('text', 'subtitle')
          )
        )
      )

      // --- Group template ---
      diagram.groupTemplate = $(
        go.Group,
        'Auto',
        {
          movable: false,
          copyable: false,
          deletable: false,
        },
        $(go.Shape, 'RoundedRectangle', {
          fill: 'transparent',
          stroke: '#444',
          strokeDashArray: [6, 3],
          strokeWidth: 2,
        }),
        $(
          go.Panel,
          'Vertical',
          $(go.TextBlock, { margin: 6, font: 'bold 14px sans-serif' }, new go.Binding('text', 'key')),
          $(go.Placeholder, { padding: 8 })
        )
      )

      // --- Link template ---
      diagram.linkTemplate = $(
        go.Link,
        {
          routing: go.Link.Normal,
          curve: go.Link.None,
          corner: 0,
          toShortLength: 0,
          fromShortLength: 0,
        },
        $(go.Shape, { strokeWidth: 2, stroke: '#333' })
      )

      this.diagram = diagram
      this.updateDiagram()
    },
    updateDiagram() {
      if (this.diagram && this.nodes.length > 0) {
        const diagramDiv = this.$refs.diagramDiv
        const width = Math.max(diagramDiv.clientWidth || 1200, 1100)

        const computedNodes = JSON.parse(JSON.stringify(this.nodes))
        const centerX = width / 2

        computedNodes.forEach((node) => {
          if (node.isGroup) {
            const groupPositions = {
              SPINE: { x: centerX, y: 50 },
              LEAF: { x: centerX, y: 200 },
              APIC: { x: centerX, y: 350 },
              INTERNET: { x: centerX, y: 30 },
              EDGE: { x: centerX, y: 180 },
              ACCESS: { x: centerX, y: 280 },
            }
            const pos = groupPositions[node.key]
            if (pos) node.loc = `${pos.x} ${pos.y}`
          } else {
            const nodePositions = {
              // Internet layer
              'INTERNET-CLOUD': { x: centerX, y: 80 },
              FPT: { x: centerX - 200, y: 120 },
              CMC: { x: centerX + 200, y: 120 },
              VIETTEL: { x: centerX - 400, y: 120 },
              'DDOS-01': { x: centerX - 200, y: 160 },
              'DDOS-02': { x: centerX + 200, y: 160 },

              // Edge layer
              'MX204-EDGE-01': { x: centerX - 150, y: 240 },
              'MX204-EDGE-02': { x: centerX + 150, y: 240 },

              // Access layer
              'C9300-01': { x: centerX - 300, y: 320 },
              'C9300-02': { x: centerX + 300, y: 320 },
              'MX-LEAF-01': { x: centerX - 200, y: 400 },
              'MX-LEAF-02': { x: centerX + 200, y: 400 },

              // ACI Fabric nodes
              'SPINE-01': { x: centerX - 100, y: 120 },
              'SPINE-02': { x: centerX + 100, y: 120 },
              'LEAF-01': { x: centerX - 300, y: 320 },
              'LEAF-02': { x: centerX - 200, y: 320 },
              'LEAF-03': { x: centerX - 100, y: 320 },
              'LEAF-04': { x: centerX, y: 320 },
              'LEAF-05': { x: centerX + 100, y: 320 },
              'LEAF-06': { x: centerX + 200, y: 320 },
              'LEAF-07': { x: centerX + 300, y: 320 },
              'LEAF-08': { x: centerX + 400, y: 320 },
              'LEAF-09': { x: centerX + 500, y: 320 },
              'LEAF-10': { x: centerX + 600, y: 320 },
              'APIC-01': { x: centerX - 100, y: 520 },
              'APIC-02': { x: centerX, y: 520 },
              'APIC-03': { x: centerX + 100, y: 520 },
            }

            const pos = nodePositions[node.key]
            if (pos) {
              node.loc = `${pos.x} ${pos.y}`
            } else {
              const typeToY = {
                spine: 120,
                leaf: 320,
                apic: 520,
                internet: 80,
                isp: 120,
                ddos: 160,
                edge: 240,
                access: 320,
                mgmt: 400,
              }
              const y = typeToY[node.type] || 200
              const x = centerX + (Math.random() - 0.5) * 200
              node.loc = `${x} ${y}`
            }
          }
        })

        this.diagram.model = new go.GraphLinksModel(computedNodes, this.links)
        this.diagram.requestUpdate()
        setTimeout(() => this.diagram.commandHandler.zoomToFit(), 50)
      }
    },
  },
}
</script>
