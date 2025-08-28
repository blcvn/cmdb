<template>
  <div class="pan-diagram">
    <div id="panDiagramDiv" style="width: 100%; height: 800px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'

export default {
  name: 'PanDiagram',
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
      this.diagram = $(go.Diagram, 'panDiagramDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
        'grid.visible': false,
      })
      this.diagram.nodeTemplateMap.add(
        'leaf',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'RoundedRectangle', {
            fill: '#5DADE2',
            stroke: '#2E5C8A',
            strokeWidth: 2,
            width: 100,
            height: 60,
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
        'pan',
        $(
          go.Node,
          'Vertical',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'RoundedRectangle', {
            fill: '#4A90E2',
            stroke: '#2E5C8A',
            strokeWidth: 2,
            width: 80,
            height: 100,
          }),
          $(
            go.Panel,
            'Vertical',
            { margin: 5 },
            $(go.Shape, 'Circle', {
              fill: 'white',
              stroke: '#2E5C8A',
              strokeWidth: 2,
              width: 30,
              height: 30,
              margin: 5,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 9px Arial',
                stroke: 'white',
                textAlign: 'center',
                margin: 2,
              },
              new go.Binding('text', 'label')
            )
          )
        )
      )
      this.diagram.nodeTemplateMap.add(
        'security',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'Rectangle', {
            fill: '#696969',
            stroke: '#333',
            strokeWidth: 2,
            width: 400,
            height: 80,
          }),
          $(
            go.Panel,
            'Horizontal',
            { margin: 10 },
            $(
              go.Panel,
              'Vertical',
              $(
                go.TextBlock,
                {
                  font: 'bold 10px Arial',
                  stroke: 'white',
                  textAlign: 'center',
                  margin: 2,
                },
                new go.Binding('text', 'label1')
              ),
              $(go.Shape, 'Rectangle', {
                fill: '#333',
                stroke: 'white',
                strokeWidth: 1,
                width: 150,
                height: 20,
                margin: 2,
              })
            ),
            $(
              go.Panel,
              'Vertical',
              { margin: new go.Margin(0, 0, 0, 20) },
              $(
                go.TextBlock,
                {
                  font: 'bold 10px Arial',
                  stroke: 'white',
                  textAlign: 'center',
                  margin: 2,
                },
                new go.Binding('text', 'label2')
              ),
              $(go.Shape, 'Rectangle', {
                fill: '#A9A9A9',
                stroke: 'white',
                strokeWidth: 1,
                width: 150,
                height: 20,
                margin: 2,
              })
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
          $(go.Shape, 'Ellipse', {
            fill: '#E8F4FD',
            stroke: '#4A90E2',
            strokeWidth: 2,
            width: 80,
            height: 30,
          }),
          $(
            go.TextBlock,
            {
              font: '9px Arial',
              stroke: '#2E5C8A',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )
      this.diagram.nodeTemplateMap.add(
        'zone',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'Rectangle', {
            fill: 'transparent',
            stroke: 'red',
            strokeWidth: 2,
            strokeDashArray: [10, 5],
            width: 600,
            height: 200,
          }),
          $(
            go.TextBlock,
            {
              font: 'bold 14px Arial',
              stroke: 'red',
              textAlign: 'center',
              angle: 90,
              alignment: go.Spot.Right,
              alignmentFocus: go.Spot.Right,
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
            segmentOffset: new go.Point(0, -8),
            segmentOrientation: go.Link.OrientUpright,
            background: 'white',
            margin: 1,
          },
          new go.Binding('text', 'label')
        )
      )
      this.diagram.linkTemplateMap.add(
        'ha',
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
              font: 'bold 8px Arial',
              stroke: 'red',
              segmentOffset: new go.Point(0, -8),
              segmentOrientation: go.Link.OrientUpright,
              background: 'white',
              margin: 1,
            },
            new go.Binding('text', 'label')
          )
        )
      )
      const nodeDataArray = [
        { key: 'LEAF-01-TOP', label: 'LEAF-01', category: 'leaf' },
        { key: 'LEAF-02-TOP', label: 'LEAF-02', category: 'leaf' },
        { key: 'ae2-1', label: 'ae2', category: 'aggregation' },
        { key: 'ae2-2', label: 'ae2', category: 'aggregation' },
        { key: 'PAN-01', label: 'PAN-01', category: 'pan' },
        { key: 'PAN-02', label: 'PAN-02', category: 'pan' },
        { key: 'ae1-1', label: 'ae1', category: 'aggregation' },
        { key: 'ae1-2', label: 'ae1', category: 'aggregation' },
        { key: 'SECURITY', label1: 'IPS Tipping Point', label2: 'WAF Imperva', category: 'security' },
        { key: 'LEAF-01-BOTTOM', label: 'LEAF-01', category: 'leaf' },
        { key: 'LEAF-02-BOTTOM', label: 'LEAF-02', category: 'leaf' },
        { key: 'OUT-ZONE', label: 'OUT', category: 'zone' },
        { key: 'IN-ZONE', label: 'IN', category: 'zone' },
      ]
      const linkDataArray = [
        { from: 'LEAF-01-TOP', to: 'ae2-1' },
        { from: 'LEAF-02-TOP', to: 'ae2-2' },
        { from: 'LEAF-01-TOP', to: 'ae2-2' },
        { from: 'LEAF-02-TOP', to: 'ae2-1' },
        { from: 'ae2-1', to: 'PAN-01' },
        { from: 'ae2-2', to: 'PAN-02' },
        { from: 'PAN-01', to: 'PAN-02', label: 'HA-1', category: 'ha' },
        { from: 'PAN-02', to: 'PAN-01', label: 'HA-2', category: 'ha' },
        { from: 'PAN-01', to: 'ae1-1' },
        { from: 'PAN-02', to: 'ae1-2' },
        { from: 'ae1-1', to: 'SECURITY' },
        { from: 'ae1-2', to: 'SECURITY' },
        { from: 'SECURITY', to: 'LEAF-01-BOTTOM' },
        { from: 'SECURITY', to: 'LEAF-02-BOTTOM' },
      ]
      this.diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray)
      this.diagram.addDiagramListener('InitialLayoutCompleted', () => {
        const outZone = this.diagram.findNodeForKey('OUT-ZONE')
        const inZone = this.diagram.findNodeForKey('IN-ZONE')
        if (outZone && inZone) {
          outZone.location = new go.Point(400, 150)
          inZone.location = new go.Point(400, 550)
        }
        const leaf01Top = this.diagram.findNodeForKey('LEAF-01-TOP')
        const leaf02Top = this.diagram.findNodeForKey('LEAF-02-TOP')
        if (leaf01Top && leaf02Top) {
          leaf01Top.location = new go.Point(200, 80)
          leaf02Top.location = new go.Point(600, 80)
        }
        const ae21 = this.diagram.findNodeForKey('ae2-1')
        const ae22 = this.diagram.findNodeForKey('ae2-2')
        if (ae21 && ae22) {
          ae21.location = new go.Point(250, 180)
          ae22.location = new go.Point(550, 180)
        }
        const pan01 = this.diagram.findNodeForKey('PAN-01')
        const pan02 = this.diagram.findNodeForKey('PAN-02')
        if (pan01 && pan02) {
          pan01.location = new go.Point(300, 280)
          pan02.location = new go.Point(500, 280)
        }
        const ae11 = this.diagram.findNodeForKey('ae1-1')
        const ae12 = this.diagram.findNodeForKey('ae1-2')
        if (ae11 && ae12) {
          ae11.location = new go.Point(300, 380)
          ae12.location = new go.Point(500, 380)
        }
        const security = this.diagram.findNodeForKey('SECURITY')
        if (security) {
          security.location = new go.Point(400, 480)
        }
        const leaf01Bottom = this.diagram.findNodeForKey('LEAF-01-BOTTOM')
        const leaf02Bottom = this.diagram.findNodeForKey('LEAF-02-BOTTOM')
        if (leaf01Bottom && leaf02Bottom) {
          leaf01Bottom.location = new go.Point(300, 620)
          leaf02Bottom.location = new go.Point(500, 620)
        }
      })
    },
  },
}
</script>

<style scoped>
.pan-diagram {
  width: 100%;
  height: 100vh;
  padding: 20px;
  box-sizing: border-box;
}
#panDiagramDiv {
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
