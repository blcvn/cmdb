<template>
  <div id="myDiagramDiv" style="width:100%; height:600px; border:1px solid black"></div>
</template>

<script>
import * as go from 'gojs'

export default {
  name: 'Diagram',
  mounted() {
    const $ = go.GraphObject.make

    const myDiagram = $(go.Diagram, 'myDiagramDiv', {
      'undoManager.isEnabled': true
    })

    // Node template
    myDiagram.nodeTemplate =
      $(go.Node, 'Auto',
        $(go.Shape, 'RoundedRectangle',
          { strokeWidth: 0, fill: 'lightblue' },
          new go.Binding('fill', 'color')
        ),
        $(go.TextBlock,
          { margin: 8, font: 'bold 12px sans-serif', stroke: '#333' },
          new go.Binding('text', 'key')
        )
      )

    // Link template with arrow and text
    myDiagram.linkTemplate =
      $(go.Link,
        { routing: go.Link.AvoidsNodes, corner: 5 },
        $(go.Shape),
        $(go.Shape, { toArrow: 'Standard' }),
        $(go.TextBlock,
          { segmentOffset: new go.Point(0, -10), font: '10px sans-serif', stroke: 'black' },
          new go.Binding('text', 'text')
        )
      )

    // Sample model
    myDiagram.model = new go.GraphLinksModel(
      [
        { key: 'Start', color: 'lightgreen' },
        { key: 'Step 1', color: 'lightblue' },
        { key: 'Step 2', color: 'lightyellow' },
        { key: 'End', color: 'pink' }
      ],
      [
        { from: 'Start', to: 'Step 1', text: 'First arrow' },
        { from: 'Step 1', to: 'Step 2', text: 'Next' },
        { from: 'Step 2', to: 'End', text: 'Finish' }
      ]
    )
  }
}
</script>
