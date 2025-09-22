<template>
  <div class="asr-diagram">
    <div id="asrDiagramDiv" style="width: 100%; height: 600px; background-color: #f5f5f5"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import nodeIcon from '@/assets/icons/node-svgrepo-com.svg'
import routerIcon from '@/assets/icons/router-svgrepo-com.svg'
import { getTopologyById } from '../api/topology'

const asrData = {
  nodes: [
    { key: 'SW1', label: 'C9300_GDS_\nSW_WAN_ST\nA', category: 'core', icon: switchIcon },
    { key: 'SW2', label: 'C9300_GDS\nSW_WAN_ST\nA', category: 'core', icon: switchIcon },
    { key: 'PO2_1', label: 'Po2', category: 'po' },
    { key: 'PO2_2', label: 'Po2', category: 'po' },
    { key: 'NCS1', label: 'NCS-01\n10.29.2.86', category: 'core', icon: nodeIcon },
    { key: 'NCS2', label: 'NCS-01\n10.29.2.87', category: 'core', icon: nodeIcon },
    { key: 'C9300-01', label: 'C9300-01', category: 'leaf', icon: routerIcon },
    { key: 'C9300-02', label: 'C9300-02', category: 'leaf', icon: routerIcon },
    { key: 'PO1_1', label: 'Po1', category: 'po' },
    { key: 'PO1_2', label: 'Po1', category: 'po' },
    { key: 'LEAF-01', label: 'LEAF-01', category: 'leaf', icon: routerIcon },
    { key: 'LEAF-02', label: 'LEAF-02', category: 'leaf', icon: routerIcon },
  ],
  links: [
    // Stack connection
    { from: 'SW1', to: 'SW2', label: 'STACK', category: 'stack' },
    // Top level connections
    { from: 'SW1', to: 'PO2_1', label: 'Te1/1/6' },
    { from: 'SW1', to: 'PO2_2', label: 'Te1/1/8' },
    { from: 'SW2', to: 'PO2_1', label: 'Te1/1/6' },
    { from: 'SW2', to: 'PO2_2', label: 'Te1/1/8' },
    // Po2 to NCS connections
    { from: 'PO2_1', to: 'NCS1', label: 'Te0/0/0/2' },
    { from: 'PO2_1', to: 'NCS2', label: 'Te0/0/0/3' },
    { from: 'PO2_2', to: 'NCS1', label: 'Te0/0/0/2' },
    { from: 'PO2_2', to: 'NCS2', label: 'Te0/0/0/3' },
    // NCS to C9300 connections
    { from: 'NCS1', to: 'C9300-01', label: 'Gi1/0/43\nMGMT' },
    { from: 'NCS2', to: 'C9300-02', label: 'Gi2/0/43\nMGMT' },
    // Po1 connections
    { from: 'NCS1', to: 'PO1_1', label: 'Te0/0/0/0' },
    { from: 'NCS1', to: 'PO1_2', label: 'Te0/0/0/1' },
    { from: 'NCS2', to: 'PO1_1', label: 'Te0/0/0/0' },
    { from: 'NCS2', to: 'PO1_2', label: 'Te0/0/0/1' },
    // Po1 to LEAF connections
    { from: 'PO1_1', to: 'LEAF-01', label: 'E1/16' },
    { from: 'PO1_1', to: 'LEAF-02', label: 'E/17' },
    { from: 'PO1_2', to: 'LEAF-01', label: 'E1/16' },
    { from: 'PO1_2', to: 'LEAF-02', label: 'E/17' },
  ],
}

export default {
  name: 'AsrCoreWan',
  data() {
    return {
      diagram: null,
      nodes: asrData.nodes,
      links: asrData.links,
    }
  },
  mounted() {
    this.fetchTopology()
  },
  beforeDestroy() {
    if (this.diagram) {
      this.diagram.div = null
    }
  },
  methods: {
    async fetchTopology() {
      try {
        const res = await getTopologyById(4)
        this.nodes = res.data.nodes || []
        this.links = res.data.links || []
      } catch (err) {
        console.error('Failed to fetch topology:', err)
        // fallback to default
        this.nodes = asrData.nodes
        this.links = asrData.links
      }

      // after fetching (success or fallback), init the diagram
      this.initDiagram()
    },
    initDiagram() {
      const $ = go.GraphObject.make

      this.diagram = $(go.Diagram, 'asrDiagramDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
        // Use basic layout, we'll position manually
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(20, 20),
        initialPosition: new go.Point(0, 0),
        initialContentAlignment: go.Spot.TopLeft,
      })

      // Define node templates
      this.diagram.nodeTemplateMap.add(
        'core',
        $(
          go.Node,
          'Spot', // use Spot panel so objects can overlap
          { locationSpot: go.Spot.Center },
          // Picture behind rectangle
          $(
            go.Picture,
            {
              desiredSize: new go.Size(120, 120),
              alignment: go.Spot.Center, // center behind rectangle
              background: 'transparent',
            },
            new go.Binding('source', 'icon')
          ),
          // // Rectangle in the center
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#2E5C8A',
            strokeWidth: 2,
            minSize: new go.Size(20, 20),
          }),
          // Text on top
          $(
            go.TextBlock,
            {
              margin: 8,
              font: 'bold 11px Arial',
              stroke: 'black',
              textAlign: 'center',
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'label')
          )
        )
      )

      this.diagram.nodeTemplateMap.add(
        'leaf',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          // Picture behind rectangle
          $(
            go.Picture,
            {
              desiredSize: new go.Size(120, 120),
              alignment: go.Spot.Center, // center behind rectangle
              background: 'transparent',
            },
            new go.Binding('source', 'icon')
          ),
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#2E5C8A',
            strokeWidth: 2,
            minSize: new go.Size(100, 50),
          }),
          $(
            go.TextBlock,
            {
              margin: 8,
              font: 'bold 10px Arial',
              stroke: 'black',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      this.diagram.nodeTemplateMap.add(
        'po',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'Ellipse', {
            fill: '#fff',
            stroke: '#4A90E2',
            strokeWidth: 2,
            minSize: new go.Size(60, 40),
          }),
          $(
            go.TextBlock,
            {
              margin: 4,
              font: '10px Arial',
              stroke: 'black',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      this.diagram.nodeTemplateMap.add(
        'corewan',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'RoundedRectangle', {
            fill: '#FFE4B5',
            stroke: '#FF6B35',
            strokeWidth: 2,
            minSize: new go.Size(120, 50),
          }),
          $(
            go.TextBlock,
            {
              margin: 8,
              font: 'bold 12px Arial',
              stroke: '#D2691E',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // Define link template with straight lines
      this.diagram.linkTemplate = $(
        go.Link,
        {
          routing: go.Link.Normal, // Straight lines
          selectable: false,
          curve: go.Link.None, // No curves
        },
        $(go.Shape, {
          strokeWidth: 2,
          stroke: '#4A90E2',
        }),
        $(
          go.TextBlock,
          {
            font: '9px Arial',
            stroke: '#2E5C8A',
            segmentOffset: new go.Point(0, -12),
            segmentOrientation: go.Link.OrientUpright,
            background: 'rgba(255, 255, 255, 0.8)',
            margin: 2,
          },
          new go.Binding('text', 'label')
        )
      )

      // Stack link template for the dashed connection
      this.diagram.linkTemplateMap.add(
        'stack',
        $(
          go.Link,
          {
            routing: go.Link.Normal, // Straight line
            selectable: false,
            curve: go.Link.None,
          },
          $(go.Shape, {
            strokeWidth: 2,
            stroke: '#666',
            strokeDashArray: [8, 4],
          }),
          $(
            go.TextBlock,
            {
              font: '9px Arial',
              stroke: '#666',
              segmentOffset: new go.Point(0, -8),
              background: 'rgba(255, 255, 255, 0.8)',
              margin: 2,
            },
            new go.Binding('text', 'label')
          )
        )
      )
      // Pass in props data
      this.diagram.model = new go.GraphLinksModel(this.nodes, this.links)

      // Position nodes manually after model is set
      this.diagram.addDiagramListener('InitialLayoutCompleted', () => {
        // Position COREWAN at the top
        const coreWanNode = this.diagram.findNodeForKey('COREWAN')
        if (coreWanNode) {
          coreWanNode.location = new go.Point(400, 50)
        }

        // Position switches with more spacing
        const sw1 = this.diagram.findNodeForKey('SW1')
        const sw2 = this.diagram.findNodeForKey('SW2')
        if (sw1 && sw2) {
          sw1.location = new go.Point(280, 150)
          sw2.location = new go.Point(520, 150)
        }

        // Position Po2 nodes
        const po2_1 = this.diagram.findNodeForKey('PO2_1')
        const po2_2 = this.diagram.findNodeForKey('PO2_2')
        if (po2_1 && po2_2) {
          po2_1.location = new go.Point(350, 250)
          po2_2.location = new go.Point(450, 250)
        }

        // Position NCS nodes with more spacing
        const ncs1 = this.diagram.findNodeForKey('NCS1')
        const ncs2 = this.diagram.findNodeForKey('NCS2')
        if (ncs1 && ncs2) {
          ncs1.location = new go.Point(280, 350)
          ncs2.location = new go.Point(520, 350)
        }

        // Position C9300 nodes further out
        const c9300_01 = this.diagram.findNodeForKey('C9300-01')
        const c9300_02 = this.diagram.findNodeForKey('C9300-02')
        if (c9300_01 && c9300_02) {
          c9300_01.location = new go.Point(120, 350)
          c9300_02.location = new go.Point(680, 350)
        }

        // Position Po1 nodes
        const po1_1 = this.diagram.findNodeForKey('PO1_1')
        const po1_2 = this.diagram.findNodeForKey('PO1_2')
        if (po1_1 && po1_2) {
          po1_1.location = new go.Point(350, 450)
          po1_2.location = new go.Point(450, 450)
        }

        // Position LEAF nodes
        const leaf01 = this.diagram.findNodeForKey('LEAF-01')
        const leaf02 = this.diagram.findNodeForKey('LEAF-02')
        if (leaf01 && leaf02) {
          leaf01.location = new go.Point(300, 550)
          leaf02.location = new go.Point(500, 550)
        }
      })
    },
  },
}
</script>

<style scoped>
.asr-diagram {
  width: 100%;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}

#asrDiagramDiv {
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
