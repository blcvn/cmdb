<template>
  <div class="network-diagram">
    <h2>Network Topology Diagram</h2>
    <div
      id="myDiagramDiv"
      style="width: 100%; height: 600px; border: 1px solid #ccc;"
    />
  </div>
</template>

<script>
import * as go from 'gojs'

export default {
  name: 'NetworkDiagram',
  data() {
    return {
      diagram: null
    }
  },
  mounted() {
    this.initDiagram()
  },
  methods: {
    initDiagram() {
      const $ = go.GraphObject.make

      // Initialize the diagram
      this.diagram = $(go.Diagram, 'myDiagramDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout),
        allowMove: true,
        allowCopy: false,
        allowDelete: false
      })

      // Define node templates
      this.diagram.nodeTemplateMap.add('switch',
        $(go.Node, 'Auto',
          $(go.Shape, 'RoundedRectangle', {
            fill: 'white',
            stroke: 'black',
            strokeWidth: 2,
            width: 120,
            height: 80
          }),
          $(go.Panel, 'Vertical',
            $(go.TextBlock, {
              font: 'bold 12px sans-serif',
              margin: 2
            }, new go.Binding('text', 'name')),
            $(go.Panel, 'Horizontal',
              $(go.Shape, 'Rectangle', {
                width: 30,
                height: 20,
                fill: 'red',
                stroke: 'black',
                margin: 2
              }),
              $(go.Shape, 'Rectangle', {
                width: 30,
                height: 20,
                fill: 'white',
                stroke: 'black',
                margin: 2
              })
            ),
            $(go.TextBlock, {
              font: '10px sans-serif',
              margin: 2
            }, new go.Binding('text', 'ip'))
          )
        )
      )

      this.diagram.nodeTemplateMap.add('router',
        $(go.Node, 'Auto',
          $(go.Shape, 'Rectangle', {
            fill: 'lightgray',
            stroke: 'black',
            strokeWidth: 2,
            width: 100,
            height: 60
          }),
          $(go.Panel, 'Vertical',
            $(go.TextBlock, {
              font: 'bold 12px sans-serif',
              margin: 2
            }, new go.Binding('text', 'name')),
            $(go.Panel, 'Horizontal',
              $(go.Shape, 'Rectangle', {
                width: 15,
                height: 10,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 15,
                height: 10,
                fill: 'white',
                stroke: 'black',
                margin: 1
              })
            ),
            $(go.TextBlock, {
              font: '9px sans-serif',
              margin: 2
            }, new go.Binding('text', 'ip'))
          )
        )
      )

      this.diagram.nodeTemplateMap.add('endpoint',
        $(go.Node, 'Auto',
          $(go.Shape, 'Ellipse', {
            fill: 'white',
            stroke: 'black',
            strokeWidth: 2,
            width: 80,
            height: 60
          }),
          $(go.Panel, 'Vertical',
            $(go.Panel, 'Horizontal',
              $(go.Shape, 'Rectangle', {
                width: 20,
                height: 15,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 20,
                height: 15,
                fill: 'white',
                stroke: 'black',
                margin: 1
              })
            ),
            $(go.TextBlock, {
              font: 'bold 10px sans-serif',
              margin: 2
            }, new go.Binding('text', 'name')),
            $(go.TextBlock, {
              font: '8px sans-serif',
              margin: 1
            }, new go.Binding('text', 'ip'))
          )
        )
      )

      // Define link template with straight lines
      this.diagram.linkTemplate =
        $(go.Link,
          {
            routing: go.Link.Normal, // Changed from AvoidsNodes to Normal for straight lines
            curve: go.Link.None, // Changed from JumpOver to None
            corner: 0, // Removed corner rounding
            toShortLength: 4
          },
          $(go.Shape, {
            strokeWidth: 2,
            stroke: 'black'
          }),
          $(go.TextBlock, {
            textAlign: 'center',
            font: '9px sans-serif',
            stroke: 'blue',
            segmentIndex: 0,
            segmentOffset: new go.Point(0, -10),
            segmentOrientation: go.Link.OrientUpright
          }, new go.Binding('text', 'fromPort')),
          $(go.TextBlock, {
            textAlign: 'center',
            font: '9px sans-serif',
            stroke: 'blue',
            segmentIndex: -1,
            segmentOffset: new go.Point(0, -10),
            segmentOrientation: go.Link.OrientUpright
          }, new go.Binding('text', 'toPort'))
        )

      // Set up the model data
      this.diagram.model = new go.GraphLinksModel(
        [
          // Switches
          {
            key: 'NCS-01',
            category: 'switch',
            name: 'NCS-01',
            ip: 'IP: 10.29.2.86'
          },
          {
            key: 'NCS-02',
            category: 'switch',
            name: 'NCS-02',
            ip: 'IP: 10.29.2.87'
          },

          // Routers
          {
            key: 'C9300-01',
            category: 'router',
            name: 'C9300-01 WAN',
            ip: 'IP: 10.29.2.90'
          },
          {
            key: 'C9300-02',
            category: 'router',
            name: 'C9300-02 WAN',
            ip: 'IP: 10.29.2.90'
          },

          // Endpoints
          {
            key: 'C4431_GDS_RT_04',
            category: 'endpoint',
            name: 'C4431_GDS_RT_04',
            ip: 'IP: 10.29.2.94'
          },
          {
            key: 'C4431_GDS_RT_02',
            category: 'endpoint',
            name: 'C4431_GDS_RT_02',
            ip: 'IP: 10.29.2.92'
          },
          {
            key: 'C4431_GDS_RT_03',
            category: 'endpoint',
            name: 'C4431_GDS_RT_03',
            ip: 'IP: 10.29.2.93'
          }
        ],
        [
          // Links with port labels
          {
            from: 'NCS-01',
            to: 'C9300-01',
            fromPort: 'Te0/0/0/2',
            toPort: 'Te1/1/6'
          },
          {
            from: 'NCS-01',
            to: 'C9300-02',
            fromPort: 'Te0/0/1',
            toPort: 'Te1/1/8'
          },
          {
            from: 'NCS-02',
            to: 'C9300-01',
            fromPort: 'Te0/0/0/3',
            toPort: 'Te1/1/8'
          },
          {
            from: 'NCS-02',
            to: 'C9300-02',
            fromPort: 'Te0/0/2',
            toPort: 'Te1/1/6'
          },

          // Connections to endpoints
          {
            from: 'C9300-01',
            to: 'C4431_GDS_RT_04',
            fromPort: 'Gi1/0/3',
            toPort: 'Gi0/0/0'
          },
          {
            from: 'C9300-02',
            to: 'C4431_GDS_RT_02',
            fromPort: 'Gi1/0/5',
            toPort: 'Gi0/3/1'
          },
          {
            from: 'C9300-02',
            to: 'C4431_GDS_RT_03',
            fromPort: 'Gi2/0/4',
            toPort: 'Gi0/0/1'
          },

          // Cross connections
          {
            from: 'C9300-01',
            to: 'C9300-02',
            fromPort: 'StackWise',
            toPort: 'StackWise'
          }
        ]
      )

      // Position nodes to match the layout in the image
      this.diagram.findNodeForKey('NCS-01').position = new go.Point(50, 50)
      this.diagram.findNodeForKey('NCS-02').position = new go.Point(50, 300)
      this.diagram.findNodeForKey('C9300-01').position = new go.Point(300, 50)
      this.diagram.findNodeForKey('C9300-02').position = new go.Point(300, 300)
      this.diagram.findNodeForKey('C4431_GDS_RT_04').position = new go.Point(550, 50)
      this.diagram.findNodeForKey('C4431_GDS_RT_02').position = new go.Point(550, 200)
      this.diagram.findNodeForKey('C4431_GDS_RT_03').position = new go.Point(550, 350)
    }
  }
}
</script>

<style scoped>
.network-diagram {
  padding: 20px;
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 20px;
}

#myDiagramDiv {
  background-color: #f8f9fa;
  border-radius: 5px;
}
</style>
