<template>
  <div class="mho-diagram">
    <div id="mhoDiagramDiv" style="width: 100%; height: 600px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'

export default {
  name: 'MHODiagram',
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
    }
  },
  methods: {
    initDiagram() {
      const $ = go.GraphObject.make
      this.diagram = $(go.Diagram, 'mhoDiagramDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(20, 20),
        'grid.gridOrigin': new go.Point(0, 0),
        allowDrop: true,
      })
      this.diagram.nodeTemplateMap.add(
        'switch',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'RoundedRectangle', {
            fill: '#5DADE2',
            stroke: '#2E5C8A',
            strokeWidth: 2,
            minSize: new go.Size(100, 60),
          }),
          $(
            go.TextBlock,
            {
              margin: 8,
              font: 'bold 10px Arial',
              stroke: 'white',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )
      this.diagram.nodeTemplateMap.add(
        'mho',
        $(
          go.Node,
          'Vertical',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'RoundedRectangle', {
            fill: '#87CEEB',
            stroke: '#4682B4',
            strokeWidth: 2,
            width: 100,
            height: 120,
          }),
          $(
            go.Panel,
            'Vertical',
            { margin: 10 },
            $(
              go.TextBlock,
              {
                font: 'bold 10px Arial',
                stroke: '#333',
                margin: 2,
                textAlign: 'center',
              },
              new go.Binding('text', 'label1')
            ),
            $(
              go.TextBlock,
              {
                font: 'bold 10px Arial',
                stroke: '#333',
                margin: 2,
                textAlign: 'center',
              },
              new go.Binding('text', 'label2')
            )
          )
        )
      )
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
            segmentOffset: new go.Point(0, -12),
            segmentOrientation: go.Link.OrientUpright,
            background: 'rgba(255, 255, 255, 0.9)',
            margin: 3,
            maxSize: new go.Size(80, NaN),
            wrap: go.TextBlock.WrapFit,
            textAlign: 'center',
          },
          new go.Binding('text', 'label')
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
      const nodeDataArray = [
        { key: 'C9300-01', label: 'C9300-01', category: 'switch' },
        { key: 'C9300-02', label: 'C9300-02', category: 'switch' },
        { key: 'CP-MHO-01', label1: 'CP-', label2: 'MHO-01', category: 'mho' },
        { key: 'CP-MHO-02', label1: 'CP-', label2: 'MHO-02', category: 'mho' },
        { key: 'E5-8-1', label: 'E5-8', category: 'aggregation' },
        { key: 'E5-8-2', label: 'E5-8', category: 'aggregation' },
        { key: 'E1-4-7-1', label: 'E1/4-7', category: 'aggregation' },
        { key: 'E1-4-7-2', label: 'E1/4-7', category: 'aggregation' },
        { key: 'LEAF-01', label: 'LEAF-01', category: 'switch' },
        { key: 'LEAF-02', label: 'LEAF-02', category: 'switch' },
      ]
      const linkDataArray = [
        { from: 'C9300-01', to: 'CP-MHO-01', label: 'Gi1/0/37' },
        { from: 'C9300-01', to: 'CP-MHO-01', label: 'MGMT-02' },
        { from: 'C9300-01', to: 'CP-MHO-01', label: 'Gi1/0/39' },
        { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/13' },
        { from: 'C9300-02', to: 'CP-MHO-02', label: 'MGMT-02' },
        { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/37' },
        { from: 'C9300-02', to: 'CP-MHO-02', label: 'Gi2/0/39' },
        { from: 'CP-MHO-01', to: 'CP-MHO-02', label: 'SYNC', category: 'sync' },
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
