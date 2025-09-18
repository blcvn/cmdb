<template>
  <div class="w-full">
    <div ref="diagramDiv" class="go-diagram"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
const defaultNodes = {
  // Core network/
  nodes: [
    // Groups
    { key: 'DMZ', isGroup: true, category: 'area', text: 'DMZ' },
    { key: 'CORE', isGroup: true, category: 'area', text: 'CORE' },
    // LEAF
    { key: 'LEAF', category: 'net', text: 'LEAF', loc: '0 120', size: '1180 90' },
    // INTERNET EDGE cluster (phải, phía trên LEAF)
    { key: 'INTERNET', category: 'label', text: 'INTERNET', loc: '520 -60' },
    { key: 'EDGE', category: 'label', text: 'INTERNET EDGE', loc: '520 -10' },
    { key: 'LB', category: 'net', text: 'LB', loc: '470 40', size: '90 54' },
    { key: 'VPN', category: 'net', text: 'VPN ROUTER', loc: '570 40', size: '120 54' },

    // DMZ area members (trái, trên LEAF)
    { key: 'DMZ-SRV', category: 'default', text: 'DMZ SERVER', group: 'DMZ', loc: '-430 -100', size: '120 64' },
    { key: 'WEB-SRV', category: 'default', text: 'WEB SERVER', group: 'DMZ', loc: '-300 -100', size: '120 64' },

    // DMZ firewall
    {
      key: 'FW-DMZ',
      category: 'security',
      text: 'FIREWALL DMZ PALO ALTO',
      loc: '30 -100',
      size: '160 64',
    },
    { key: 'WAF', category: 'security', text: 'WAF DMZ', loc: '0 0', size: '120 54' },
    { key: 'IPS', category: 'security', text: 'IPS', loc: '0 -40', size: '120 54' },

    // CORE area members (giữa dưới LEAF)
    { key: 'JUMP', category: 'default', text: 'JUMP SERVER', group: 'CORE', loc: '-260 220', size: '120 64' },
    { key: 'CORE-SRV', category: 'default', text: 'CORE', group: 'CORE', loc: '-160 220', size: '120 64' },

    // WAN (phải, ngang LEAF)
    { key: 'WAN', category: 'net', text: 'WAN', loc: '760 120', size: '120 54' },
  ],
  links: [
    // INTERNET EDGE flows
    { from: 'INTERNET', to: 'EDGE' },
    { from: 'EDGE', to: 'LB' },
    { from: 'EDGE', to: 'VPN' },
    { from: 'LB', to: 'LEAF' },
    { from: 'VPN', to: 'LEAF' },

    // DMZ chain
    { from: 'DMZ-SRV', to: 'LEAF' },
    { from: 'WEB-SRV', to: 'LEAF' },
    { from: 'WAF', to: 'IPS' },
    { from: 'IPS', to: 'FW-DMZ' },
    { from: 'FW-DMZ', to: 'LEAF' },

    // CORE chain
    { from: 'LEAF', to: 'FW-CORE' },
    { from: 'FW-CORE', to: 'CORE-SRV' },
    { from: 'FW-CORE', to: 'JUMP' },

    // LEAF to WAN
    { from: 'LEAF', to: 'WAN' },
    { from: 'LEAF', to: 'WAF' },
    { from: 'CORE', to: 'LEAF' },
  ],
}

export default {
  name: 'LogicalTopologyDiagram',
  props: {
    nodes: { type: Array, default: () => defaultNodes.nodes },
    links: { type: Array, default: () => defaultNodes.links },
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

      this.diagram = $(go.Diagram, this.$refs.diagramDiv, {
        initialContentAlignment: go.Spot.Center,
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
      })

      // Disable animation for smoother loading
      this.diagram.animationManager.isEnabled = false

      // ===== Node Helpers =====
      const LBL = (key = 'text', opts = {}) =>
        $(
          go.TextBlock,
          {
            margin: new go.Margin(8, 10, 4, 10),
            font: 'bold 12pt Segoe UI',
            stroke: '#202124',
            textAlign: 'center',
            ...opts,
          },
          new go.Binding('text', key)
        )

      const SUB = (key = 'subtitle') =>
        $(
          go.TextBlock,
          { margin: new go.Margin(0, 10, 8, 10), font: '10pt Segoe UI', stroke: '#5f6368', textAlign: 'center' },
          new go.Binding('text', key)
        )

      // ===== Nodes =====
      const nodeTemplate = (fill, stroke, textStroke) =>
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center, movable: true },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          $(go.Shape, 'RoundedRectangle', { fill, stroke, strokeWidth: 1.2, parameter1: 6 }),
          $(go.Panel, 'Vertical', { margin: 2 }, LBL('text', { stroke: textStroke }), SUB('subtitle'))
        )

      this.diagram.nodeTemplateMap.add('default', nodeTemplate('#ffffff', '#5f6368', '#202124'))
      this.diagram.nodeTemplateMap.add('security', nodeTemplate('#fee2e2', '#ef4444', '#7f1d1d'))
      this.diagram.nodeTemplateMap.add('net', nodeTemplate('#e0f2fe', '#0284c7', '#0c4a6e'))
      this.diagram.nodeTemplateMap.add(
        'label',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center, movable: true },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          $(go.Shape, 'RoundedRectangle', { fill: '#eef2ff', stroke: '#6366f1', strokeWidth: 1.2, parameter1: 12 }),
          LBL('text', { margin: new go.Margin(10, 16, 10, 16) })
        )
      )

      // ===== Groups =====
      this.diagram.groupTemplateMap.add(
        'area',
        $(
          go.Group,
          'Auto',
          {
            computesBoundsAfterDrag: true,
            locationSpot: go.Spot.Center,
            handlesDragDropForMembers: true,
            layout: $(go.Layout),
          },
          $(go.Shape, 'RoundedRectangle', { fill: 'rgba(237,242,247,0.7)', stroke: '#94a3b8', strokeWidth: 1.2 }),
          $(
            go.Panel,
            'Table',
            $(go.Panel, 'Auto', { row: 0, margin: 6 }, $(go.Placeholder, { padding: 16 })),
            $(
              go.Panel,
              'Auto',
              { row: 1 },
              $(go.Shape, 'Rectangle', { fill: '#fde68a', stroke: '#f59e0b' }),
              $(
                go.TextBlock,
                { margin: new go.Margin(4, 10), font: 'bold 12pt Segoe UI', stroke: '#92400e', textAlign: 'center' },
                new go.Binding('text', 'text')
              )
            )
          )
        )
      )

      this.diagram.groupTemplateMap.add(
        'band',
        $(
          go.Group,
          'Auto',
          { selectable: false, locationSpot: go.Spot.Center },
          new go.Binding('location', 'loc', go.Point.parse),
          $(
            go.Shape,
            'RoundedRectangle',
            { fill: '#d9f99d', stroke: '#65a30d', strokeWidth: 1.2, parameter1: 6 },
            new go.Binding('desiredSize', 'size', go.Size.parse)
          ),
          $(go.TextBlock, { margin: 6, font: 'bold 12pt Segoe UI', stroke: '#1b4332' }, new go.Binding('text', 'text'))
        )
      )

      // ===== Links (straight, no arrows) =====
      this.diagram.linkTemplate = $(
        go.Link,
        { routing: go.Link.Normal, curve: go.Link.None, corner: 0, selectable: true },
        $(go.Shape, { strokeWidth: 1.6, stroke: '#0284c7' })
      )

      // Grid
      this.diagram.grid = $(
        go.Panel,
        'Grid',
        $(go.Shape, 'LineH', { stroke: 'rgba(0,0,0,0.08)', strokeWidth: 1 }),
        $(go.Shape, 'LineV', { stroke: 'rgba(0,0,0,0.08)', strokeWidth: 1 })
      )
      this.diagram.grid.visible = true
      this.diagram.toolManager.draggingTool.isGridSnapEnabled = true
      this.diagram.grid.gridCellSize = new go.Size(20, 20)

      // Load initial data
      this.updateDiagram()
    },

    updateDiagram() {
      if (this.diagram && this.nodes.length > 0) {
        // Create a fresh GraphLinksModel so each diagram is independent
        this.diagram.model = new go.GraphLinksModel(
          JSON.parse(JSON.stringify(this.nodes)),
          JSON.parse(JSON.stringify(this.links))
        )

        // Center diagram after loading
        this.diagram.delayInitialization(() => {
          this.diagram.centerRect(this.diagram.documentBounds)
        })
      }
    },
  },
}
</script>

<style scoped>
.go-diagram {
  width: 100%;
  height: 720px;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  background: #ffffff;
}
</style>
