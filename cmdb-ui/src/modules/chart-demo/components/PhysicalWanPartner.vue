<template>
  <div class="physicalWan-diagram">
    <div id="physicalWanDiv" style="width: 100%; height: 700px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'

import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import routerIcon from '@/assets/icons/router-svgrepo-com.svg'

const physicalWanData = {
  nodes: [
    {
      key: 'NCS-01',
      label: 'NCS-01',
      ip: 'IP: 10.29.2.86',
      category: 'router',
      icon: routerIcon,
    },
    {
      key: 'NCS-02',
      label: 'NCS-02',
      ip: 'IP: 10.29.2.87',
      category: 'router',
      icon: routerIcon,
    },
    {
      key: 'C9300-01-WAN',
      label: 'C9300-01 WAN',
      ip: 'IP: 10.29.2.90',
      category: 'switch',
      icon: switchIcon,
    },
    {
      key: 'C9300-02-WAN',
      label: 'C9300-02 WAN',
      ip: 'IP: 10.29.2.90',
      category: 'switch',
      icon: switchIcon,
    },
    {
      key: 'C4431_GDS_RT_04',
      label: 'C4431_GDS_RT_04',
      ip: 'IP: 10.29.2.94',
      category: 'router',
      icon: routerIcon,
    },
    {
      key: 'C4431_GDS_RT_02',
      label: 'C4431_GDS_RT_02',
      ip: 'IP: 10.29.2.92',
      category: 'router',
      icon: routerIcon,
    },
    {
      key: 'C4431_GDS_RT_03',
      label: 'C4431_GDS_RT_03',
      ip: 'IP: 10.29.2.93',
      category: 'router',
      icon: routerIcon,
    },
  ],
  links: [
    { from: 'NCS-01', to: 'C9300-01-WAN', fromText: 'Te0/0/0/2', toText: 'Te1/1/6', category: 'close' },
    { from: 'NCS-01', to: 'C9300-02-WAN', fromText: 'Te0/0/0/3', toText: 'Te1/1/6', category: 'close' },
    { from: 'NCS-02', to: 'C9300-01-WAN', fromText: 'Te0/0/0/2', toText: 'Te1/1/8', category: 'close' },
    { from: 'NCS-02', to: 'C9300-02-WAN', fromText: 'Te0/0/0/2', toText: 'Te1/1/8', category: 'close' },
    { from: 'C9300-01-WAN', to: 'C4431_GDS_RT_04', fromText: 'Gi1/0/3', toText: 'Gi0/0/0', category: 'close' },
    { from: 'C9300-01-WAN', to: 'C4431_GDS_RT_02', fromText: 'Gi1/0/4', toText: 'Gi0/3/0', category: 'close' },
    { from: 'C9300-01-WAN', to: 'C9300-02-WAN', fromText: 'Te1/1/6', toText: 'Stack', category: 'close' },
    { from: 'C9300-01-WAN', to: 'C4431_GDS_RT_03', fromText: 'Gi1/0/5', toText: 'Gi0/0/0', category: 'close' },
    { from: 'C9300-02-WAN', to: 'C4431_GDS_RT_04', toText: 'Gi0/0/1', category: 'close' },
    { from: 'C9300-02-WAN', to: 'C4431_GDS_RT_02', fromText: 'Gi2/0/4', toText: 'Gi3/0/1', category: 'close' },
    { from: 'C9300-02-WAN', to: 'C4431_GDS_RT_03', fromText: 'Gi1/0/5', toText: 'Gi0/0/1', category: 'close' },
  ],
}

export default {
  name: 'PhysicalWanPartner',
  props: {
    nodes: {
      type: Array,
      required: true,
      default: () => physicalWanData.nodes,
    },
    links: {
      type: Array,
      required: true,
      default: () => physicalWanData.links,
    },
  },
  data() {
    return {
      diagram: null,
    }
  },
  mounted() {
    this.initDiagram()
  },
  beforeDestroy() {
    if (this.diagram) {
      this.diagram.div = null
      console.log('PhysicalWanPartner destroyed')
    }
  },
  methods: {
    initDiagram() {
      const $ = go.GraphObject.make
      this.diagram = $(go.Diagram, 'physicalWanDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.ForceDirectedLayout),
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(20, 20),
        initialPosition: new go.Point(0, 0),
        initialContentAlignment: go.Spot.TopLeft,
      })

      // Universal Node Template
      this.diagram.nodeTemplate = $(
        go.Node,
        'Vertical',
        { locationSpot: go.Spot.Center },
        $(
          go.Panel,
          'Auto',
          $(
            go.Picture,
            {
              width: 64,
              height: 64,
              imageStretch: go.GraphObject.Uniform,
            },
            new go.Binding('source', 'icon')
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

      // Improved Link Template with better label positioning
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
        // From label - positioned at start of link
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: 0, // First segment
            segmentFraction: 0.1, // 10% from start
            segmentOffset: new go.Point(0, -12), // Offset above the line
            background: 'rgba(255, 255, 255, 0.9)',
            margin: 2,
          },
          new go.Binding('text', 'fromText')
        ),
        // To label - positioned at end of link
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: 0, // First segment
            segmentFraction: 0.9, // 90% from start (near end)
            segmentOffset: new go.Point(0, -12), // Offset above the line
            background: 'rgba(255, 255, 255, 0.9)',
            margin: 2,
          },
          new go.Binding('text', 'toText')
        )
      )

      // Alternative approach with even closer positioning
      this.diagram.linkTemplateMap.add(
        'close',
        $(
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
          // From label - very close to source node
          $(
            go.TextBlock,
            {
              font: '8px Arial',
              stroke: '#000',
              segmentIndex: 0,
              segmentFraction: 0.05, // 5% from start - very close to node
              segmentOffset: new go.Point(0, -15),
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 1,
            },
            new go.Binding('text', 'fromText')
          ),
          // To label - very close to target node
          $(
            go.TextBlock,
            {
              font: '8px Arial',
              stroke: '#000',
              segmentIndex: 0,
              segmentFraction: 0.95, // 95% from start - very close to end node
              segmentOffset: new go.Point(0, -15),
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 1,
            },
            new go.Binding('text', 'toText')
          )
        )
      )

      // Dashed Link Template with improved positioning
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
              segmentIndex: 0,
              segmentFraction: 0.5, // Middle of the link
              segmentOffset: new go.Point(0, -12),
              segmentOrientation: go.Link.OrientUpright,
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 1,
            },
            new go.Binding('text', 'label')
          )
        )
      )
      this.diagram.model = new go.GraphLinksModel(this.nodes, this.links)

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
          sw01.location = new go.Point(400, 100)
          sw02.location = new go.Point(400, 400)
          rt04.location = new go.Point(700, 100)
          rt02.location = new go.Point(700, 300)
          rt03.location = new go.Point(700, 500)
        }
      })
    },
  },
}
</script>

<style scoped>
.physicalWan-diagram {
  width: 100%;
  height: 700px;
  padding: 20px;
  box-sizing: border-box;
}

#physicalWanDiv {
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}
</style>
