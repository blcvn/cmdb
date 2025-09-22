<template>
  <div class="router-vpn-diagram">
    <div id="routerVpnDiv" style="width: 100%; height: 700px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import routerIcon from '@/assets/icons/router-svgrepo-com.svg'
import { getTopologyById } from '../api/topology'

const routerData = {
  // Node Data
  nodes: [
    { key: 'LEAF-01-TOP', label: 'LEAF-01', category: 'leaf' },
    { key: 'LEAF-02-TOP', label: 'LEAF-02', category: 'leaf' },
    { key: 'C9300-01', label: 'C9300-01', category: 'c9300' },
    { key: 'C9300-02', label: 'C9300-02', category: 'c9300' },
    { key: 'ROUTER-VPN1', label1: 'ROUTER', label2: 'VPN1', category: 'router' },
    { key: 'ROUTER-VPN2', label1: 'ROUTER', label2: 'VPN2', category: 'router' },
    { key: 'LEAF-01-BOTTOM', label: 'LEAF-01', category: 'leaf' },
    { key: 'LEAF-02-BOTTOM', label: 'LEAF-02', category: 'leaf' },
  ],
  // Link Data - You can specify category: 'dual' for links that need dual labels
  links: [
    { from: 'LEAF-01-TOP', to: 'ROUTER-VPN1', label: 'E1/40' },
    { from: 'LEAF-01-TOP', to: 'ROUTER-VPN2', label: 'E1/42' },
    { from: 'LEAF-02-TOP', to: 'ROUTER-VPN1', label: 'E1/40' },
    { from: 'LEAF-02-TOP', to: 'ROUTER-VPN2', label: 'E1/42' },
    { from: 'C9300-01', to: 'ROUTER-VPN1', label: 'Gi1/0/36 MGMT' },
    { from: 'ROUTER-VPN2', to: 'C9300-02', label: 'MGMT Gi2/0/36' },

    // These could use dual template if you want to split the labels
    {
      from: 'ROUTER-VPN1',
      to: 'LEAF-01-BOTTOM',
      label: 'Gi0/0/2 OUTSIDE E1/41',
      category: 'dual',
      fromText: 'Gi0/0/2',
      toText: 'E1/41',
    },
    {
      from: 'ROUTER-VPN1',
      to: 'LEAF-02-BOTTOM',
      label: 'Gi0/0/3 E1/43',
      category: 'dual',
      fromText: 'Gi0/0/3',
      toText: 'E1/43',
    },
    {
      from: 'ROUTER-VPN2',
      to: 'LEAF-01-BOTTOM',
      label: 'Gi0/0/2 OUTSIDE E1/41',
      category: 'dual',
      fromText: 'Gi0/0/2',
      toText: 'E1/41',
    },
    {
      from: 'ROUTER-VPN2',
      to: 'LEAF-02-BOTTOM',
      label: 'Gi0/0/3 E1/43',
      category: 'dual',
      fromText: 'Gi0/0/3',
      toText: 'E1/43',
    },
  ],
}

export default {
  name: 'RouterVpnDiagram',
  data() {
    return {
      diagram: null,
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
        const res = await getTopologyById(8)
        this.nodes = res.data.nodes || []
        this.links = res.data.links || []
      } catch (err) {
        console.error('Failed to fetch topology:', err)
        // fallback to default
        this.nodes = routerData.nodes
        this.links = routerData.links
      }

      // after fetching (success or fallback), init the diagram
      this.initDiagram()
    },
    initDiagram() {
      const $ = go.GraphObject.make
      this.diagram = $(go.Diagram, 'routerVpnDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout), // No automatic layout
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(20, 20),
        initialPosition: new go.Point(0, 0),
        initialContentAlignment: go.Spot.TopLeft,
      })

      // ROUTERVPN Node Template (top left box)
      this.diagram.nodeTemplateMap.add(
        'routervpn',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Picture, {
            source: routerIcon,
            width: 80,
            height: 80,
            margin: 4,
          }),
          $(go.Shape, 'RoundedRectangle', {
            fill: '#F5DEB3',
            stroke: '#D2691E',
            strokeWidth: 2,
            width: 40,
            height: 40,
            parameter1: 8,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 10px Arial',
              stroke: '#B22222',
              textAlign: 'center',
              margin: 2,
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // LEAF Switch Node Template
      this.diagram.nodeTemplateMap.add(
        'leaf',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Picture, {
            source: switchIcon,
            width: 60,
            height: 60,
            margin: 4,
          }),
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#CD853F',
            strokeWidth: 2,
            width: 30,
            height: 30,
            parameter1: 8,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 8px Arial',
              stroke: '#000',
              textAlign: 'center',
              margin: 2,
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // C9300 Switch Node Template
      this.diagram.nodeTemplateMap.add(
        'c9300',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Picture, {
            source: switchIcon,
            width: 60,
            height: 60,
            margin: 4,
          }),
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#CD853F',
            strokeWidth: 2,
            width: 30,
            height: 30,
            parameter1: 8,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 7px Arial',
              stroke: '#000',
              textAlign: 'center',
              margin: 2,
              alignment: go.Spot.Center,
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // Router VPN Node Template (double line text inside)
      this.diagram.nodeTemplateMap.add(
        'router',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Picture, {
            source: routerIcon,
            width: 60,
            height: 60,
            margin: 4,
          }),
          $(go.Shape, 'RoundedRectangle', {
            fill: '#fff',
            stroke: '#CD853F',
            strokeWidth: 2,
            width: 30,
            height: 30,
            parameter1: 8,
            alignment: go.Spot.Center,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 6px Arial',
              stroke: 'black',
              textAlign: 'center',
              margin: 2,
              wrap: go.TextBlock.WrapFit,
              alignment: go.Spot.Center,
            },
            new go.Binding('text', '', (d) => `${d.label1}\n${d.label2}`)
          )
        )
      )

      // Improved Link Template with better positioning
      this.diagram.linkTemplate = $(
        go.Link,
        {
          routing: go.Link.Normal,
          curve: go.Link.None,
          selectable: false,
        },
        $(go.Shape, {
          strokeWidth: 1.5,
          stroke: '#000',
        }),
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: 0,
            segmentFraction: 0.5, // Center of the link
            segmentOffset: new go.Point(0, -12),
            segmentOrientation: go.Link.OrientUpright,
            background: 'rgba(255, 255, 255, 0.9)',
            margin: 2,
          },
          new go.Binding('text', 'label')
        )
      )

      // Alternative link template for dual-ended labels (if needed)
      this.diagram.linkTemplateMap.add(
        'dual',
        $(
          go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            selectable: false,
          },
          $(go.Shape, {
            strokeWidth: 1.5,
            stroke: '#000',
          }),
          // From label - close to source
          $(
            go.TextBlock,
            {
              font: '7px Arial',
              stroke: '#000',
              segmentIndex: 0,
              segmentFraction: 0.15, // 15% from start
              segmentOffset: new go.Point(0, -12),
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 1,
            },
            new go.Binding('text', 'fromText')
          ),
          // To label - close to target
          $(
            go.TextBlock,
            {
              font: '7px Arial',
              stroke: '#000',
              segmentIndex: 0,
              segmentFraction: 0.85, // 85% from start
              segmentOffset: new go.Point(0, -12),
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 1,
            },
            new go.Binding('text', 'toText')
          )
        )
      )

      this.diagram.model = new go.GraphLinksModel(routerData.nodes, routerData.links)

      // Manual layout
      this.diagram.addDiagramListener('InitialLayoutCompleted', () => {
        this.setNodePositions()
      })
    },

    setNodePositions() {
      const positions = {
        'LEAF-01-TOP': new go.Point(400, 120),
        'LEAF-02-TOP': new go.Point(600, 120),
        'C9300-01': new go.Point(200, 350),
        'ROUTER-VPN1': new go.Point(400, 350),
        'ROUTER-VPN2': new go.Point(600, 350),
        'C9300-02': new go.Point(800, 350),
        'LEAF-01-BOTTOM': new go.Point(400, 580),
        'LEAF-02-BOTTOM': new go.Point(600, 580),
      }

      Object.keys(positions).forEach((key) => {
        const node = this.diagram.findNodeForKey(key)
        if (node) node.location = positions[key]
      })
    },
  },
}
</script>

<style scoped>
.router-vpn-diagram {
  width: 100%;
  height: 700px;
  padding: 20px;
  box-sizing: border-box;
}

#routerVpnDiv {
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}
</style>
