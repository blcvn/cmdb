<template>
  <div class="network-diagram">
    <h2>Complex Network Topology with Security Layer</h2>
    <div
      id="myDiagramDiv"
      style="width: 100%; height: 700px; border: 1px solid #ccc;"
    />
  </div>
</template>

<script>
import * as go from 'gojs'

export default {
  name: 'ComplexNetworkDiagram',
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
        allowMove: true,
        allowCopy: false,
        allowDelete: false
      })

      // Define leaf switch template (blue switches)
      this.diagram.nodeTemplateMap.add('leaf',
        $(go.Node, 'Auto',
          $(go.Shape, 'RoundedRectangle', {
            fill: '#4A90E2',
            stroke: 'black',
            strokeWidth: 2,
            width: 120,
            height: 80
          }),
          $(go.Panel, 'Vertical',
            $(go.TextBlock, {
              font: 'bold 12px sans-serif',
              stroke: 'white',
              margin: 2
            }, new go.Binding('text', 'name')),
            $(go.Panel, 'Horizontal',
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              })
            ),
            $(go.Panel, 'Horizontal',
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              })
            )
          )
        )
      )

      // Define PAN device template (blue firewalls)
      this.diagram.nodeTemplateMap.add('pan',
        $(go.Node, 'Auto',
          $(go.Shape, 'RoundedRectangle', {
            fill: '#4A90E2',
            stroke: 'black',
            strokeWidth: 2,
            width: 120,
            height: 100
          }),
          $(go.Panel, 'Vertical',
            $(go.TextBlock, {
              font: 'bold 12px sans-serif',
              stroke: 'white',
              margin: 2
            }, new go.Binding('text', 'name')),
            $(go.Shape, 'Ellipse', {
              width: 30,
              height: 30,
              fill: 'white',
              stroke: 'gray',
              margin: 5
            }),
            $(go.Panel, 'Horizontal',
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              }),
              $(go.Shape, 'Rectangle', {
                width: 8,
                height: 8,
                fill: 'red',
                stroke: 'black',
                margin: 1
              })
            )
          )
        )
      )

      // Define IPS Tapping Point template (black device)
      this.diagram.nodeTemplateMap.add('ips',
        $(go.Node, 'Auto',
          $(go.Shape, 'Rectangle', {
            fill: '#2C2C2C',
            stroke: 'black',
            strokeWidth: 2,
            width: 200,
            height: 60
          }),
          $(go.Panel, 'Horizontal',
            $(go.TextBlock, {
              font: 'bold 12px sans-serif',
              stroke: 'white',
              margin: 5
            }, new go.Binding('text', 'name')),
            $(go.Panel, 'Vertical',
              $(go.Panel, 'Horizontal',
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                })
              ),
              $(go.Panel, 'Horizontal',
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                })
              )
            )
          )
        )
      )

      // Define WAF Imperva template (gray device)
      this.diagram.nodeTemplateMap.add('waf',
        $(go.Node, 'Auto',
          $(go.Shape, 'Rectangle', {
            fill: '#A0A0A0',
            stroke: 'black',
            strokeWidth: 2,
            width: 200,
            height: 60
          }),
          $(go.Panel, 'Horizontal',
            $(go.TextBlock, {
              font: 'bold 12px sans-serif',
              stroke: 'black',
              margin: 5
            }, new go.Binding('text', 'name')),
            $(go.Panel, 'Vertical',
              $(go.Panel, 'Horizontal',
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                })
              ),
              $(go.Panel, 'Horizontal',
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                }),
                $(go.Shape, 'Rectangle', {
                  width: 6,
                  height: 6,
                  fill: 'red',
                  margin: 1
                })
              )
            )
          )
        )
      )

      // Define aggregation connection template (ae1, ae2)
      this.diagram.linkTemplateMap.add('aggregation',
        $(go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            corner: 0
          },
          $(go.Shape, {
            strokeWidth: 3,
            stroke: 'blue'
          }),
          $(go.Shape, 'Ellipse', {
            width: 60,
            height: 20,
            fill: 'lightblue',
            stroke: 'blue',
            strokeWidth: 2,
            segmentIndex: 0.5,
            segmentOffset: new go.Point(0, 0)
          }),
          $(go.TextBlock, {
            textAlign: 'center',
            font: 'bold 10px sans-serif',
            stroke: 'blue',
            segmentIndex: 0.5,
            segmentOffset: new go.Point(0, 0)
          }, new go.Binding('text', 'label'))
        )
      )

      // Define HA connection template (red connections)
      this.diagram.linkTemplateMap.add('ha',
        $(go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            corner: 0
          },
          $(go.Shape, {
            strokeWidth: 2,
            stroke: 'red'
          }),
          $(go.TextBlock, {
            textAlign: 'center',
            font: '9px sans-serif',
            stroke: 'red',
            segmentIndex: 0.5,
            segmentOffset: new go.Point(0, -10)
          }, new go.Binding('text', 'label'))
        )
      )

      // Define default link template
      this.diagram.linkTemplate =
        $(go.Link,
          {
            routing: go.Link.Normal,
            curve: go.Link.None,
            corner: 0
          },
          $(go.Shape, {
            strokeWidth: 2,
            stroke: 'black'
          })
        )

      // Set up the model data
      this.diagram.model = new go.GraphLinksModel([
        // Top leaf switches
        { key: 'leaf1-top', category: 'leaf', name: 'LEAF-01' },
        { key: 'leaf2-top', category: 'leaf', name: 'LEAF-02' },

        // PAN devices (middle layer)
        { key: 'pan1', category: 'pan', name: 'PAN-01' },
        { key: 'pan2', category: 'pan', name: 'PAN-02' },

        // Security devices (bottom middle)
        { key: 'ips', category: 'ips', name: 'IPS Tapping Point' },
        { key: 'waf', category: 'waf', name: 'WAF Imperva' },

        // Bottom leaf switches
        { key: 'leaf1-bottom', category: 'leaf', name: 'LEAF-01' },
        { key: 'leaf2-bottom', category: 'leaf', name: 'LEAF-02' }
      ], [
        // Cross connections between top leaf switches and PAN devices
        { from: 'leaf1-top', to: 'pan1' },
        { from: 'leaf1-top', to: 'pan2' },
        { from: 'leaf2-top', to: 'pan1' },
        { from: 'leaf2-top', to: 'pan2' },

        // Aggregation connections
        { from: 'pan1', to: 'ips', category: 'aggregation', label: 'ae1' },
        { from: 'pan2', to: 'ips', category: 'aggregation', label: 'ae2' },

        // HA connections between PAN devices
        { from: 'pan1', to: 'pan2', category: 'ha', label: 'HA-1' },
        { from: 'pan1', to: 'pan2', category: 'ha', label: 'HA-2' },

        // Connections from security layer to bottom leaf switches
        { from: 'ips', to: 'leaf1-bottom' },
        { from: 'ips', to: 'leaf2-bottom' },
        { from: 'waf', to: 'leaf1-bottom' },
        { from: 'waf', to: 'leaf2-bottom' },

        // Cross connections from WAF to bottom leafs
        { from: 'waf', to: 'leaf1-bottom' },
        { from: 'waf', to: 'leaf2-bottom' }
      ])

      // Position the nodes
      this.$nextTick(() => {
        // Top layer
        this.diagram.findNodeForKey('leaf1-top').position = new go.Point(100, 50)
        this.diagram.findNodeForKey('leaf2-top').position = new go.Point(400, 50)

        // Middle layer - PAN devices
        this.diagram.findNodeForKey('pan1').position = new go.Point(100, 200)
        this.diagram.findNodeForKey('pan2').position = new go.Point(400, 200)

        // Security layer
        this.diagram.findNodeForKey('ips').position = new go.Point(200, 350)
        this.diagram.findNodeForKey('waf').position = new go.Point(200, 430)

        // Bottom layer
        this.diagram.findNodeForKey('leaf1-bottom').position = new go.Point(100, 550)
        this.diagram.findNodeForKey('leaf2-bottom').position = new go.Point(400, 550)
      })
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
