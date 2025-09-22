<template>
  <div>
    <div ref="mxDiagramDiv" :style="{ width: '100%', height: height, border: '1px solid #ddd' }"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
import { getTopologyById } from '../api/topology'

const mx204Data = {
  nodes: [
    // Groups
    { key: 'INTERNET', isGroup: true, loc: '600 50' },
    { key: 'EDGE', isGroup: true, loc: '600 200' },
    { key: 'ACCESS', isGroup: true, loc: '600 350' },

    // Internet Layer
    {
      key: 'INTERNET-CLOUD',
      label: 'INTERNET',
      subtitle: 'Cloud',
      type: 'internet',
      color: '#e0f2fe',
      group: 'INTERNET',
      loc: '600 80',
    },
    {
      key: 'FPT',
      label: 'FPT',
      subtitle: 'ASN:18403, IP: 58.187.147.1/29',
      type: 'isp',
      color: '#fff3cd',
      group: 'INTERNET',
      loc: '400 120',
    },
    {
      key: 'CMC',
      label: 'CMC',
      subtitle: 'ASN:45903, IP: 113.20.97.249/29',
      type: 'isp',
      color: '#fff3cd',
      group: 'INTERNET',
      loc: '800 120',
    },
    {
      key: 'VIETTEL',
      label: 'Viettel',
      subtitle: 'ASN:7552, IP: 125.234.176.153/30',
      type: 'isp',
      color: '#fff3cd',
      group: 'INTERNET',
      loc: '200 120',
    },

    // DDoS Protection Layer
    {
      key: 'DDOS-01',
      label: 'DDOS',
      subtitle: 'FPT Protection',
      type: 'ddos',
      color: '#f8d7da',
      group: 'INTERNET',
      loc: '400 160',
    },
    {
      key: 'DDOS-02',
      label: 'DDOS',
      subtitle: 'CMC Protection',
      type: 'ddos',
      color: '#f8d7da',
      group: 'INTERNET',
      loc: '800 160',
    },

    // Edge Router Layer
    {
      key: 'MX204-EDGE-01',
      label: 'MX204-EDGE-01',
      subtitle: 'Edge Router',
      type: 'edge',
      color: '#d1ecf1',
      group: 'EDGE',
      loc: '450 240',
    },
    {
      key: 'MX204-EDGE-02',
      label: 'MX204-EDGE-02',
      subtitle: 'Edge Router',
      type: 'edge',
      color: '#d1ecf1',
      group: 'EDGE',
      loc: '750 240',
    },

    // Access Layer
    {
      key: 'MX-LEAF-01',
      label: 'LEAF-01',
      subtitle: 'Access Switch',
      type: 'access',
      color: '#d4edda',
      group: 'ACCESS',
      loc: '400 400',
    },
    {
      key: 'MX-LEAF-02',
      label: 'LEAF-02',
      subtitle: 'Access Switch',
      type: 'access',
      color: '#d4edda',
      group: 'ACCESS',
      loc: '800 400',
    },
    {
      key: 'C9300-01',
      label: 'C9300-01',
      subtitle: 'Management Switch',
      type: 'mgmt',
      color: '#e2e3e5',
      group: 'ACCESS',
      loc: '300 320',
    },
    {
      key: 'C9300-02',
      label: 'C9300-02',
      subtitle: 'Management Switch',
      type: 'mgmt',
      color: '#e2e3e5',
      group: 'ACCESS',
      loc: '900 320',
    },
  ],
  links: [
    // Internet to DDoS connections
    { from: 'INTERNET-CLOUD', to: 'DDOS-01', label: 'G1-OUT FPT', isHighlighted: true },
    { from: 'INTERNET-CLOUD', to: 'DDOS-02', label: 'G3-OUT CMC', isHighlighted: true },

    // DDoS to Edge connections
    { from: 'DDOS-01', to: 'MX204-EDGE-01', label: 'Xe-0/1/3 (.4)', isHighlighted: true },
    { from: 'DDOS-01', to: 'MX204-EDGE-01', label: 'Xe-0/1/2 (.154)', isHighlighted: true },
    { from: 'DDOS-02', to: 'MX204-EDGE-02', label: 'Xe-0/1/3 (.250)', isHighlighted: true },
    { from: 'DDOS-02', to: 'MX204-EDGE-02', label: 'Xe-0/1/2', isHighlighted: true },

    // Edge to Management connections
    { from: 'MX204-EDGE-01', to: 'C9300-01', label: 'Gi1/0/42 (MGMT)', isHighlighted: false },
    { from: 'MX204-EDGE-02', to: 'C9300-02', label: 'Gi2/0/42 (MGMT)', isHighlighted: false },

    // Edge to Leaf connections (ae0 aggregation)
    { from: 'MX204-EDGE-01', to: 'MX-LEAF-01', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
    { from: 'MX204-EDGE-01', to: 'MX-LEAF-01', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },
    { from: 'MX204-EDGE-01', to: 'MX-LEAF-02', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
    { from: 'MX204-EDGE-01', to: 'MX-LEAF-02', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },

    { from: 'MX204-EDGE-02', to: 'MX-LEAF-02', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
    { from: 'MX204-EDGE-02', to: 'MX-LEAF-02', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },
    { from: 'MX204-EDGE-02', to: 'MX-LEAF-01', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
    { from: 'MX204-EDGE-02', to: 'MX-LEAF-01', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },

    // Leaf to Edge return connections
    { from: 'MX-LEAF-01', to: 'MX204-EDGE-01', label: 'E1/14 (ae0)', isHighlighted: true },
    { from: 'MX-LEAF-01', to: 'MX204-EDGE-01', label: 'E1/15 (ae0)', isHighlighted: true },
    { from: 'MX-LEAF-01', to: 'MX204-EDGE-02', label: 'E1/14 (ae0)', isHighlighted: true },
    { from: 'MX-LEAF-01', to: 'MX204-EDGE-02', label: 'E1/15 (ae0)', isHighlighted: true },

    { from: 'MX-LEAF-02', to: 'MX204-EDGE-02', label: 'E1/14 (ae0)', isHighlighted: true },
    { from: 'MX-LEAF-02', to: 'MX204-EDGE-02', label: 'E1/15 (ae0)', isHighlighted: true },
    { from: 'MX-LEAF-02', to: 'MX204-EDGE-01', label: 'E1/14 (ae0)', isHighlighted: true },
    { from: 'MX-LEAF-02', to: 'MX204-EDGE-01', label: 'E1/15 (ae0)', isHighlighted: true },
  ],
}

export default {
  name: 'NetworkTopology',
  data() {
    return { diagram: null, nodes: mx204Data.nodes, links: mx204Data.links, height: '600px' }
  },
  mounted() {
      this.$nextTick(() => {
    this.fetchTopology()
  })
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
    async fetchTopology() {
      try {
        const res = await getTopologyById(3)
        this.nodes = res.data.nodes || []
        this.links = res.data.links || []
      } catch (err) {
        console.error('Failed to fetch topology:', err)
        // fallback to default
        this.nodes = mx204Data.nodes
        this.links = mx204Data.links
      }

      // after fetching (success or fallback), init the diagram
      this.initDiagram()
    },
    initDiagram() {
      const $ = go.GraphObject.make
      const diagramDiv = this.$refs.mxDiagramDiv

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
        const diagramDiv = this.$refs.mxDiagramDiv
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
