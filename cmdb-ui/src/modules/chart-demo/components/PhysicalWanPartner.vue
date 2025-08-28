<template>
  <div class="physicalWan-diagram">
    <div id="physicalWanDiv" style="width: 100%; height: 700px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'

export default {
  name: 'PhysicalWanPartner',
  data() {
    return {
      diagram: null,
    }
  },
  mounted() {
    console.log('Mounting PhysicalWanPartner, div:', document.getElementById('physicalWanDiv')) // Debug
    this.initDiagram()
  },
  beforeDestroy() {
    if (this.diagram) {
      this.diagram.div = null
      console.log('PhysicalWanPartner destroyed') // Debug
    }
  },
  methods: {
    initDiagram() {
      const $ = go.GraphObject.make
      this.diagram = $(go.Diagram, 'physicalWanDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.ForceDirectedLayout), // Improved layout as fallback
        'grid.visible': true, // Enable grid
        'grid.gridCellSize': new go.Size(20, 20), // Set grid cell size
        // 'grid.color': '#ddd', // Light gray grid lines
      })

      // Router Node Template
      this.diagram.nodeTemplateMap.add(
        'router',
        $(
          go.Node,
          'Vertical',
          { locationSpot: go.Spot.Center },
          $(
            go.Panel,
            'Auto',
            // $(go.Shape, 'Cylinder1', {
            //   fill: '#E8E8E8',
            //   stroke: '#999',
            //   strokeWidth: 2,
            //   width: 80,
            //   height: 60,
            // }),
            $(
              go.Panel,
              'Spot',
              { width: 80, height: 60 },
              $(go.Shape, 'LineH', {
                stroke: 'red',
                strokeWidth: 3,
                width: 30,
                height: 2,
                alignment: go.Spot.Center,
              }),
              $(go.Shape, 'LineV', {
                stroke: 'red',
                strokeWidth: 3,
                width: 2,
                height: 30,
                alignment: go.Spot.Center,
              }),
              $(go.Shape, {
                stroke: 'red',
                strokeWidth: 3,
                geometry: go.Geometry.parse('M -15 -15 L 15 15'),
                alignment: go.Spot.Center,
              }),
              $(go.Shape, {
                stroke: 'red',
                strokeWidth: 3,
                geometry: go.Geometry.parse('M 15 -15 L -15 15'),
                alignment: go.Spot.Center,
              })
            )
          ),
          $(
            go.TextBlock,
            {
              font: 'bold 10px Arial',
              stroke: '#333',
              textAlign: 'center',
              margin: new go.Margin(5, 0, 0, 0),
            },
            new go.Binding('text', 'label')
          ),
          $(
            go.TextBlock,
            {
              font: '9px Arial',
              stroke: '#666',
              textAlign: 'center',
            },
            new go.Binding('text', 'ip')
          )
        )
      )

      // Switch Node Template
      this.diagram.nodeTemplateMap.add(
        'switch',
        $(
          go.Node,
          'Vertical',
          { locationSpot: go.Spot.Center },
          $(
            go.Panel,
            'Auto',
            $(go.Shape, 'RoundedRectangle', {
              fill: '#D4D4D4',
              stroke: '#666',
              strokeWidth: 2,
              width: 100,
              height: 70,
              parameter1: 8,
            }),
            $(
              go.Panel,
              'Table',
              { width: 80, height: 50, margin: 10 },
              $(go.Shape, 'LineH', {
                row: 0,
                column: 0,
                stroke: 'red',
                strokeWidth: 2,
                width: 25,
                height: 1,
                margin: 2,
              }),
              $(go.Shape, 'LineH', {
                row: 0,
                column: 1,
                stroke: 'red',
                strokeWidth: 2,
                width: 25,
                height: 1,
                margin: 2,
              }),
              $(go.Shape, 'LineH', {
                row: 1,
                column: 0,
                stroke: 'red',
                strokeWidth: 2,
                width: 25,
                height: 1,
                margin: 2,
              }),
              $(go.Shape, 'LineH', {
                row: 1,
                column: 1,
                stroke: 'red',
                strokeWidth: 2,
                width: 25,
                height: 1,
                margin: 2,
              }),
              $(go.Shape, 'LineV', {
                row: 0,
                rowSpan: 2,
                column: 0,
                stroke: 'red',
                strokeWidth: 2,
                width: 1,
                height: 20,
                alignment: go.Spot.Left,
              }),
              $(go.Shape, 'LineV', {
                row: 0,
                rowSpan: 2,
                column: 1,
                stroke: 'red',
                strokeWidth: 2,
                width: 1,
                height: 20,
                alignment: go.Spot.Right,
              })
            )
          ),
          $(
            go.TextBlock,
            {
              font: 'bold 10px Arial',
              stroke: '#333',
              textAlign: 'center',
              margin: new go.Margin(5, 0, 0, 0),
            },
            new go.Binding('text', 'label')
          ),
          $(
            go.TextBlock,
            {
              font: '9px Arial',
              stroke: '#666',
              textAlign: 'center',
            },
            new go.Binding('text', 'ip')
          )
        )
      )

      // Link Template (Solid)
      this.diagram.linkTemplate = $(
        go.Link,
        {
          routing: go.Link.Normal,
          curve: go.Link.None,
          selectable: false,
        },
        $(go.Shape, {
          strokeWidth: 1.5,
          stroke: '#333',
        }),
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentOffset: new go.Point(0, -8),
            segmentOrientation: go.Link.OrientUpright,
            background: 'white',
            margin: 1,
          },
          new go.Binding('text', 'label')
        )
      )

      // Dashed Link Template
      this.diagram.linkTemplateMap.add(
        'dashed',
        $(
          go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            selectable: false,
          },
          $(go.Shape, {
            strokeWidth: 1.5,
            stroke: '#666',
            strokeDashArray: [4, 4],
          }),
          $(
            go.TextBlock,
            {
              font: '8px Arial',
              stroke: '#000',
              segmentOffset: new go.Point(0, -8),
              segmentOrientation: go.Link.OrientUpright,
              background: 'white',
              margin: 1,
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // Node Data
      const nodeDataArray = [
        { key: 'NCS-01', label: 'NCS-01', ip: 'IP: 10.29.2.86', category: 'router' },
        { key: 'NCS-02', label: 'NCS-02', ip: 'IP: 10.29.2.87', category: 'router' },
        { key: 'C9300-01-WAN', label: 'C9300-01 WAN', ip: 'IP: 10.29.2.90', category: 'switch' },
        { key: 'C9300-02-WAN', label: 'C9300-02 WAN', ip: 'IP: 10.29.2.90', category: 'switch' },
        { key: 'C4431_GDS_RT_04', label: 'C4431_GDS_RT_04', ip: 'IP: 10.29.2.94', category: 'router' },
        { key: 'C4431_GDS_RT_02', label: 'C4431_GDS_RT_02', ip: 'IP: 10.29.2.92', category: 'router' },
        { key: 'C4431_GDS_RT_03', label: 'C4431_GDS_RT_03', ip: 'IP: 10.29.2.93', category: 'router' },
      ]

      // Link Data
      const linkDataArray = [
        { from: 'NCS-01', to: 'C9300-01-WAN', label: 'Te1/1/6' },
        { from: 'NCS-02', to: 'C9300-02-WAN', label: 'Te1/1/8' },
        { from: 'NCS-01', to: 'C9300-02-WAN', label: 'Te0/0/0/3' },
        { from: 'NCS-02', to: 'C9300-01-WAN', label: 'Te0/0/0/2' },
        { from: 'C9300-01-WAN', to: 'C9300-02-WAN', label: 'Stack', category: 'dashed' },
        { from: 'C9300-01-WAN', to: 'C4431_GDS_RT_04', label: 'Gi1/0/3' },
        { from: 'C9300-02-WAN', to: 'C4431_GDS_RT_02', label: 'Gi2/0/4' },
        { from: 'C9300-02-WAN', to: 'C4431_GDS_RT_03', label: 'Gi1/0/5' },
        { from: 'NCS-01', to: 'C4431_GDS_RT_04', label: 'Te0/0/0/2', category: 'dashed' },
        { from: 'NCS-02', to: 'C4431_GDS_RT_02', label: 'Te0/0/0/3', category: 'dashed' },
        { from: 'NCS-01', to: 'C4431_GDS_RT_02', label: 'Po2', category: 'dashed' },
        { from: 'NCS-02', to: 'C4431_GDS_RT_03', label: 'Po1', category: 'dashed' },
      ]

      this.diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray)

      // Set initial node positions
      this.diagram.addDiagramListener('InitialLayoutCompleted', () => {
        const ncs01 = this.diagram.findNodeForKey('NCS-01')
        const ncs02 = this.diagram.findNodeForKey('NCS-02')
        const sw01 = this.diagram.findNodeForKey('C9300-01-WAN')
        const sw02 = this.diagram.findNodeForKey('C9300-02-WAN')
        const rt04 = this.diagram.findNodeForKey('C4431_GDS_RT_04')
        const rt02 = this.diagram.findNodeForKey('C4431_GDS_RT_02')
        const rt03 = this.diagram.findNodeForKey('C4431_GDS_RT_03')
        if (ncs01 && ncs02 && sw01 && sw02 && rt04 && rt02 && rt03) {
          ncs01.location = new go.Point(100, 100)
          ncs02.location = new go.Point(100, 400)
          sw01.location = new go.Point(300, 200)
          sw02.location = new go.Point(300, 400)
          rt04.location = new go.Point(500, 100)
          rt02.location = new go.Point(500, 300)
          rt03.location = new go.Point(500, 500)
        }
      })
    },
  },
}
</script>

<style scoped>
.physicalWan-diagram {
  width: 100%;
  height: 700px; /* Fixed height for consistency */
  padding: 20px;
  box-sizing: border-box;
}

#physicalWanDiv {
  height: 100%; /* Inherits from .network-diagram */
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9; /* Moved from inline style to CSS */
}
</style>
