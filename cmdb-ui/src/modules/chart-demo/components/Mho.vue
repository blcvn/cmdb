<template>
  <div class="mho-diagram">
    <div id="mhoDiagramDiv" style="width: 100%; height: 600px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import nodeIcon from '@/assets/icons/node-svgrepo-com.svg'
import { getTopologyById } from '../api/topology'

const mhoData = {
  nodes: [
    { key: 'C9300-01', label: 'C9300-01', category: 'switch', icon: switchIcon },
    { key: 'C9300-02', label: 'C9300-02', category: 'switch', icon: switchIcon },
    { key: 'CP-MHO-01', label: 'CP-MHO-01', category: 'mho', icon: nodeIcon },
    { key: 'CP-MHO-02', label: 'CP-MHO-02', category: 'mho', icon: nodeIcon },
    { key: 'E5-8-1', label: 'E5-8', category: 'aggregation' },
    { key: 'E5-8-2', label: 'E5-8', category: 'aggregation' },
    { key: 'E1-4-7-1', label: 'E1/4-7', category: 'aggregation' },
    { key: 'E1-4-7-2', label: 'E1/4-7', category: 'aggregation' },
    { key: 'LEAF-01', label: 'LEAF-01', category: 'switch', icon: switchIcon },
    { key: 'LEAF-02', label: 'LEAF-02', category: 'switch', icon: switchIcon },
  ],
  links: [
    { from: 'C9300-01', to: 'CP-MHO-01', fromText: 'Gi1/0/37', toText: 'MGMT-02' },
    { from: 'C9300-01', to: 'CP-MHO-01', fromText: 'Gi1/0/38', toText: 'MGMT-01' },
    { from: 'C9300-01', to: 'CP-MHO-01', fromText: 'Gi1/0/39', toText: 'E1' },
    { from: 'C9300-02', to: 'CP-MHO-02', fromText: 'Gi2/0/37', toText: 'MGMT-02' },
    { from: 'C9300-02', to: 'CP-MHO-02', fromText: 'Gi2/0/38', toText: 'MGMT-01' },
    { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/37' },
    { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/39' },
    { from: 'CP-MHO-01', to: 'CP-MHO-02', fromText: 'E48', toText: 'E48' },
    { from: 'CP-MHO-01', to: 'E5-8-1' },
    { from: 'CP-MHO-02', to: 'E5-8-2' },
    { from: 'E5-8-1', to: 'E5-8-2', label: 'bond1', category: 'bond' },
    { from: 'E5-8-1', to: 'E1-4-7-1' },
    { from: 'E5-8-1', to: 'E1-4-7-2' },
    { from: 'E5-8-2', to: 'E1-4-7-1' },
    { from: 'E5-8-2', to: 'E1-4-7-2' },
    { from: 'E1-4-7-1', to: 'LEAF-01' },
    { from: 'E1-4-7-2', to: 'LEAF-02' },
  ],
}
export default {
  name: 'MHODiagram',
  data() {
    return {
      diagram: null,
      nodes: mhoData.nodes,
      links: mhoData.links,
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
        const res = await getTopologyById(6)
        this.nodes = res.data.nodes || []
        this.links = res.data.links || []
      } catch (err) {
        console.error('Failed to fetch topology:', err)
        // fallback to default
        this.nodes = mhoData.nodes
        this.links = mhoData.links
      }

      // after fetching (success or fallback), init the diagram
      this.initDiagram()
    },
    initDiagram() {
      const $ = go.GraphObject.make
      this.diagram = $(go.Diagram, 'mhoDiagramDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(20, 20),
        'grid.gridOrigin': new go.Point(0, 0),
        allowDrop: true,
        initialPosition: new go.Point(0, 0),
        initialContentAlignment: go.Spot.TopLeft,
      })

      // Switch Node Template with icon behind smaller white rectangle
      this.diagram.nodeTemplateMap.add(
        'switch',
        $(
          go.Node,
          'Position', // Use Position to layer elements
          { locationSpot: go.Spot.Center },
          // Icon (background, larger)
          $(
            go.Picture,
            {
              width: 80,
              height: 80,
              imageStretch: go.GraphObject.Uniform,
              alignment: go.Spot.Center,
            },
            new go.Binding('source', 'icon')
          ),
          // White rectangle (smaller, on top, with text inside)
          $(
            go.Panel,
            'Auto',
            {
              alignment: go.Spot.Center,
            },
            $(go.Shape, 'RoundedRectangle', {
              fill: 'white',
              stroke: '#333',
              strokeWidth: 1,
              width: 60,
              height: 20,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 9px Arial',
                stroke: '#333',
                textAlign: 'center',
                margin: 2,
              },
              new go.Binding('text', 'label')
            )
          )
        )
      )

      // MHO Node Template with icon behind smaller white rectangle
      this.diagram.nodeTemplateMap.add(
        'mho',
        $(
          go.Node,
          'Position', // Use Position to layer elements
          { locationSpot: go.Spot.Center },
          // Icon (background, larger)
          $(
            go.Picture,
            {
              width: 100,
              height: 100,
              imageStretch: go.GraphObject.Uniform,
              alignment: go.Spot.Center,
            },
            new go.Binding('source', 'icon')
          ),
          // White rectangle (smaller, on top, with text inside)
          $(
            go.Panel,
            'Auto',
            {
              alignment: go.Spot.Center,
            },
            $(go.Shape, 'RoundedRectangle', {
              fill: 'white',
              stroke: '#333',
              strokeWidth: 1,
              width: 80,
              height: 25,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 9px Arial',
                stroke: '#333',
                textAlign: 'center',
                margin: 2,
                wrap: go.TextBlock.WrapFit,
              },
              new go.Binding('text', 'label')
            )
          )
        )
      )

      // Aggregation Node Template (unchanged)
      this.diagram.nodeTemplateMap.add(
        'aggregation',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'Rectangle', {
            fill: 'white',
            stroke: '#333',
            strokeWidth: 1,
            width: 60,
            height: 25,
          }),
          $(
            go.TextBlock,
            {
              font: '9px Arial',
              stroke: '#333',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // Link templates (unchanged)
      this.diagram.linkTemplate = $(
        go.Link,
        {
          routing: go.Link.Normal,
          curve: go.Link.None,
          selectable: false,
        },
        new go.Binding('fromSpot', 'fromSpot', go.Spot.parse),
        new go.Binding('toSpot', 'toSpot', go.Spot.parse),
        new go.Binding('curviness'),
        $(go.Shape, { strokeWidth: 1.5, stroke: '#333' }),
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: 0,
            segmentOffset: new go.Point(-30, -10),
            segmentOrientation: go.Link.OrientUpright,
            margin: 2,
          },
          new go.Binding('text', 'fromText')
        ),
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentIndex: -1,
            segmentOffset: new go.Point(30, -10),
            segmentOrientation: go.Link.OrientUpright,
            margin: 2,
          },
          new go.Binding('text', 'toText')
        )
      )

      this.diagram.linkTemplateMap.add(
        'sync',
        $(
          go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            selectable: false,
          },
          $(go.Shape, {
            strokeWidth: 2,
            stroke: 'red',
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 9px Arial',
              stroke: 'red',
              segmentOffset: new go.Point(0, -15),
              segmentOrientation: go.Link.OrientUpright,
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 3,
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      this.diagram.linkTemplateMap.add(
        'bond',
        $(
          go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            selectable: false,
          },
          $(go.Shape, {
            strokeWidth: 3,
            stroke: '#4682B4',
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 10px Arial',
              stroke: '#4682B4',
              segmentOffset: new go.Point(0, -15),
              segmentOrientation: go.Link.OrientUpright,
              background: 'rgba(255, 255, 255, 0.9)',
              margin: 3,
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // Node Data Array with icons
      const nodeDataArray = [
        { key: 'C9300-01', label: 'C9300-01', category: 'switch', icon: switchIcon },
        { key: 'C9300-02', label: 'C9300-02', category: 'switch', icon: switchIcon },
        { key: 'CP-MHO-01', label: 'CP-MHO-01', category: 'mho', icon: nodeIcon },
        { key: 'CP-MHO-02', label: 'CP-MHO-02', category: 'mho', icon: nodeIcon },
        { key: 'E5-8-1', label: 'E5-8', category: 'aggregation' },
        { key: 'E5-8-2', label: 'E5-8', category: 'aggregation' },
        { key: 'E1-4-7-1', label: 'E1/4-7', category: 'aggregation' },
        { key: 'E1-4-7-2', label: 'E1/4-7', category: 'aggregation' },
        { key: 'LEAF-01', label: 'LEAF-01', category: 'switch', icon: switchIcon },
        { key: 'LEAF-02', label: 'LEAF-02', category: 'switch', icon: switchIcon },
      ]

      // Link Data Array (unchanged)
      const linkDataArray = [
        { from: 'C9300-01', to: 'CP-MHO-01', fromText: 'Gi1/0/37', toText: 'MGMT-02' },
        { from: 'C9300-01', to: 'CP-MHO-01', fromText: 'Gi1/0/38', toText: 'MGMT-01' },
        { from: 'C9300-01', to: 'CP-MHO-01', fromText: 'Gi1/0/39', toText: 'E1' },
        { from: 'C9300-02', to: 'CP-MHO-02', fromText: 'Gi2/0/37', toText: 'MGMT-02' },
        { from: 'C9300-02', to: 'CP-MHO-02', fromText: 'Gi2/0/38', toText: 'MGMT-01' },
        { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/37' },
        { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/39' },
        { from: 'CP-MHO-01', to: 'CP-MHO-02', fromText: 'E48', toText: 'E48' },
        { from: 'CP-MHO-01', to: 'E5-8-1' },
        { from: 'CP-MHO-02', to: 'E5-8-2' },
        { from: 'E5-8-1', to: 'E5-8-2', label: 'bond1', category: 'bond' },
        { from: 'E5-8-1', to: 'E1-4-7-1' },
        { from: 'E5-8-1', to: 'E1-4-7-2' },
        { from: 'E5-8-2', to: 'E1-4-7-1' },
        { from: 'E5-8-2', to: 'E1-4-7-2' },
        { from: 'E1-4-7-1', to: 'LEAF-01' },
        { from: 'E1-4-7-2', to: 'LEAF-02' },
      ]

      this.diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray)

      // Position nodes (unchanged)
      this.diagram.addDiagramListener('InitialLayoutCompleted', () => {
        const c930001 = this.diagram.findNodeForKey('C9300-01')
        const c930002 = this.diagram.findNodeForKey('C9300-02')
        if (c930001 && c930002) {
          c930001.location = new go.Point(80, 120)
          c930002.location = new go.Point(720, 120)
        }
        const cpmho01 = this.diagram.findNodeForKey('CP-MHO-01')
        const cpmho02 = this.diagram.findNodeForKey('CP-MHO-02')
        if (cpmho01 && cpmho02) {
          cpmho01.location = new go.Point(300, 120)
          cpmho02.location = new go.Point(500, 120)
        }
        const e581 = this.diagram.findNodeForKey('E5-8-1')
        const e582 = this.diagram.findNodeForKey('E5-8-2')
        if (e581 && e582) {
          e581.location = new go.Point(340, 260)
          e582.location = new go.Point(460, 260)
        }
        const e1471 = this.diagram.findNodeForKey('E1-4-7-1')
        const e1472 = this.diagram.findNodeForKey('E1-4-7-2')
        if (e1471 && e1472) {
          e1471.location = new go.Point(340, 360)
          e1472.location = new go.Point(460, 360)
        }
        const leaf01 = this.diagram.findNodeForKey('LEAF-01')
        const leaf02 = this.diagram.findNodeForKey('LEAF-02')
        if (leaf01 && leaf02) {
          leaf01.location = new go.Point(340, 460)
          leaf02.location = new go.Point(460, 460)
        }
      })
    },
  },
}
</script>

<style scoped>
.mho-diagram {
  width: 100%;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}
#mhoDiagramDiv {
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
