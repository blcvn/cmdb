<template>
  <div class="citrix-topology">
    <div ref="citrixDiagram" class="diagram-container"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import nodeIcon from '@/assets/icons/node-svgrepo-com.svg'

export default {
  name: 'NetworkTopologyDiagram',
  data() {
    return {
      diagram: null,
    }
  },
  mounted() {
    // Use nextTick to ensure the DOM is fully rendered
    this.$nextTick(() => {
      this.initDiagram()
    })
  },
  methods: {
    initDiagram() {
      // Check if ref exists
      if (!this.$refs.citrixDiagram) {
        console.error('citrixDiagramref not found')
        return
      }

      const $ = go.GraphObject.make

      this.diagram = $(go.Diagram, this.$refs.citrixDiagram, {
        'undoManager.isEnabled': true,
        initialContentAlignment: go.Spot.Center,
        layout: $(go.Layout), // No automatic layout - we'll position manually
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(20, 20),
      })

      // VPX-GDS template (large green rectangle with router background)
      this.diagram.nodeTemplateMap.add(
        'vpx',
        $(
          go.Node,
          'Spot',
          {
            locationSpot: go.Spot.Center,
          },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          // Foreground rectangle
          $(go.Shape, 'Rectangle', {
            fill: '#c8d6a3',
            stroke: '#8b9b6b',
            strokeWidth: 2,
            width: 180,
            height: 100,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 16px Arial',
              stroke: '#2d3d1d',
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'name')
          )
        )
      )

      // LEAF switch template (blue server-like shape with switch background)
      this.diagram.nodeTemplateMap.add(
        'leaf',
        $(
          go.Node,
          'Spot',
          {
            locationSpot: go.Spot.Center,
          },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          // Background icon
          $(go.Picture, {
            source: switchIcon,
            width: 120,
            height: 100,
          }),
          // Foreground rectangle
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#4682b4',
            strokeWidth: 2,
            width: 80,
            height: 60,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 10px Arial',
              stroke: 'black',
              margin: new go.Margin(2, 0, 5, 0),
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'name')
          )
        )
      )

      // VLAN template (orange/red rectangles with network background)
      this.diagram.nodeTemplateMap.add(
        'vlan',
        $(
          go.Node,
          'Spot',
          {
            locationSpot: go.Spot.Center,
          },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          // Foreground rectangle
          $(
            go.Shape,
            'RoundedRectangle',
            {
              strokeWidth: 2,
              width: 120,
              height: 40,
              alignment: go.Spot.Center,
            },
            new go.Binding('fill', 'vlanType', (type) => (type === 'outside' ? '#ffd4a3' : '#ffb3a3')),
            new go.Binding('stroke', 'vlanType', (type) => (type === 'outside' ? '#ff8c00' : '#dc143c'))
          ),
          $(
            go.TextBlock,
            {
              font: 'bold 11px Arial',
              stroke: '#8b0000',
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'name')
          )
        )
      )

      // Citrix SDX template (blue server with details and node background)
      this.diagram.nodeTemplateMap.add(
        'sdx',
        $(
          go.Node,
          'Spot',
          {
            locationSpot: go.Spot.Center,
          },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          // Background icon
          $(go.Picture, {
            source: nodeIcon,
            width: 180,
            height: 120,
          }),
          // Foreground rectangle
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#4682b4',
            strokeWidth: 2,
            width: 140,
            height: 80,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 12px Arial',
              stroke: 'black',
              margin: new go.Margin(5, 0, 0, 0),
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'name')
          )
        )
      )

      // CLA1 switch template (small blue switch with switch background)
      this.diagram.nodeTemplateMap.add(
        'cla',
        $(
          go.Node,
          'Spot',
          {
            locationSpot: go.Spot.Center,
          },
          new go.Binding('location', 'loc', go.Point.parse).makeTwoWay(go.Point.stringify),
          // Background icon
          $(go.Picture, {
            source: switchIcon,
            width: 100,
            height: 80,
          }),
          // Foreground rectangle
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#4682b4',
            strokeWidth: 2,
            width: 60,
            height: 40,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 8px Arial',
              stroke: 'black',
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'name')
          ),
          $(
            go.Panel,
            'Horizontal',
            {
              margin: new go.Margin(2, 0, 3, 0),
              alignment: go.Spot.Center,
            },
            $(
              go.TextBlock,
              {
                font: '6px Arial',
                stroke: 'black',
              },
              new go.Binding('text', 'port1')
            ),
            $(
              go.TextBlock,
              {
                font: '6px Arial',
                stroke: 'black',
                margin: new go.Margin(0, 0, 0, 10),
              },
              new go.Binding('text', 'port2')
            )
          )
        )
      )

      // Custom link template with port labels
      this.diagram.linkTemplate = $(
        go.Link,
        {
          routing: go.Link.Normal,
          corner: 5,
          selectionAdorned: false,
        },
        $(go.Shape, {
          strokeWidth: 2,
          stroke: '#666',
        }),
        $(
          go.TextBlock,
          {
            segmentIndex: 0,
            segmentFraction: 0.2,
            font: '9px Arial',
            background: 'rgba(255,255,255,0.8)',
            margin: 2,
          },
          new go.Binding('text', 'fromPort')
        ),
        $(
          go.TextBlock,
          {
            segmentIndex: -1,
            segmentFraction: 0.8,
            font: '9px Arial',
            background: 'rgba(255,255,255,0.8)',
            margin: 2,
          },
          new go.Binding('text', 'toPort')
        )
      )

      // Model data matching your diagram
      this.diagram.model = new go.GraphLinksModel(
        [
          // VPX-GDS
          { key: 'VPX-GDS', name: 'VPX-GDS', category: 'vpx', loc: '-200 0' },

          // LEAF switches
          { key: 'LEAF-01', name: 'LEAF-01', category: 'leaf', loc: '-200 100' },
          { key: 'LEAF-02', name: 'LEAF-02', category: 'leaf', loc: '200 100' },
          { key: 'LEAF-03', name: 'LEAF-03', category: 'leaf', loc: '20 300' },
          { key: 'LEAF-04', name: 'LEAF-04', category: 'leaf', loc: '20 400' },

          // VLANs
          { key: 'OUTSIDE-110', name: 'OUTSIDE-110', category: 'vlan', vlanType: 'outside', loc: '20 100' },
          { key: 'INSIDE-101', name: 'INSIDE-101', category: 'vlan', vlanType: 'inside', loc: '20 150' },

          // Citrix SDX servers
          {
            key: 'SDX-01',
            name: 'Citrix SDX 01',
            category: 'sdx',
            mgmtPort: 'MGMT',
            rightPort: '8GE',
            loc: '-200 300',
          },
          { key: 'SDX-02', name: 'Citrix SDX 02', category: 'sdx', mgmtPort: 'MGMT', rightPort: '8GE', loc: '200 300' },

          // CLA1 switch
          { key: 'CLA1', name: 'CLA1', category: 'cla', loc: '0 200' },
        ],
        [
          // Connections from LEAF switches to SDX
          { from: 'LEAF-01', to: 'SDX-01', fromPort: 'E1/49' },
          { from: 'LEAF-01', to: 'SDX-02', fromPort: 'E1/49' },
          { from: 'LEAF-02', to: 'SDX-01', fromPort: 'E1/50' },
          { from: 'LEAF-02', to: 'SDX-02', fromPort: 'E1/50' },
        ]
      )

      // Remove the old location binding loop as it's now applied directly to templates
    },
  },
  beforeUnmount() {
    if (this.diagram) {
      this.diagram.div = null
    }
  },
}
</script>

<style scoped>
.citrix-topology {
  width: 100%;
  height: 600px;
  background-color: #f9f9f9;
}

.diagram-container {
  width: 100%;
  height: 100%;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
}
</style>
