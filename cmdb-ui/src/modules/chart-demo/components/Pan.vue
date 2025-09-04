<template>
  <div class="network-topology-diagram">
    <div id="networkTopologyDiv" style="width: 100%; height: 800px; background-color: #f9f9f9"></div>
  </div>
</template>

<script>
import * as go from 'gojs'
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import nodeIcon from '@/assets/icons/node-svgrepo-com.svg'
import routerIcon from '@/assets/icons/router-svgrepo-com.svg'

export default {
  name: 'NetworkTopologyDiagram',
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
      this.diagram = $(go.Diagram, 'networkTopologyDiv', {
        'undoManager.isEnabled': true,
        layout: $(go.Layout), // No automatic layout
        'grid.visible': true,
        'grid.gridCellSize': new go.Size(10, 10),
        initialPosition: new go.Point(0, 0),
        initialContentAlignment: go.Spot.TopLeft,
      })

      // LEAF Switch Node Template with icon behind white rectangle
      this.diagram.nodeTemplateMap.add(
        'leaf',
        $(
          go.Node,
          'Position',
          { locationSpot: go.Spot.Center },
          // Icon (background)
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
          // White rectangle with text (centered on top)
          $(
            go.Panel,
            'Auto',
            { alignment: go.Spot.Center },
            $(go.Shape, 'RoundedRectangle', {
              fill: 'white',
              stroke: '#333',
              strokeWidth: 1,
              width: 70,
              height: 20,
              parameter1: 8,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 10px Arial',
                stroke: '#000',
                textAlign: 'center',
                margin: 2,
              },
              new go.Binding('text', 'label')
            )
          )
        )
      )

      // PAN Switch Node Template with icon behind white rectangle
      this.diagram.nodeTemplateMap.add(
        'pan',
        $(
          go.Node,
          'Position',
          { locationSpot: go.Spot.Center },
          // Icon (background)
          $(
            go.Picture,
            {
              width: 90,
              height: 90,
              imageStretch: go.GraphObject.Uniform,
              alignment: go.Spot.Center,
            },
            new go.Binding('source', 'icon')
          ),
          // White rectangle with text (centered on top)
          $(
            go.Panel,
            'Auto',
            { alignment: go.Spot.Center },
            $(go.Shape, 'RoundedRectangle', {
              fill: 'white',
              stroke: '#333',
              strokeWidth: 1,
              width: 70,
              height: 22,
              parameter1: 8,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 10px Arial',
                stroke: '#000',
                textAlign: 'center',
                margin: 2,
              },
              new go.Binding('text', 'label')
            )
          )
        )
      )

      // IPS Device Template with icon behind white rectangle
      this.diagram.nodeTemplateMap.add(
        'ips',
        $(
          go.Node,
          'Position',
          { locationSpot: go.Spot.Center },
          // Icon (background)
          $(
            go.Picture,
            {
              width: 100,
              height: 60,
              imageStretch: go.GraphObject.Uniform,
              alignment: go.Spot.Center,
            },
            new go.Binding('source', 'icon')
          ),
          // White rectangle with text (centered on top)
          $(
            go.Panel,
            'Auto',
            { alignment: go.Spot.Center },
            $(go.Shape, 'RoundedRectangle', {
              fill: 'white',
              stroke: '#333',
              strokeWidth: 1,
              width: 90,
              height: 20,
              parameter1: 8,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 9px Arial',
                stroke: '#000',
                textAlign: 'center',
                margin: 2,
              },
              new go.Binding('text', 'label')
            )
          )
        )
      )

      // WAF Device Template with icon behind white rectangle
      this.diagram.nodeTemplateMap.add(
        'waf',
        $(
          go.Node,
          'Position',
          { locationSpot: go.Spot.Center },
          // Icon (background)
          $(
            go.Picture,
            {
              width: 100,
              height: 60,
              imageStretch: go.GraphObject.Uniform,
              alignment: go.Spot.Center,
            },
            new go.Binding('source', 'icon')
          ),
          // White rectangle with text (centered on top)
          $(
            go.Panel,
            'Auto',
            { alignment: go.Spot.Center },
            $(go.Shape, 'RoundedRectangle', {
              fill: 'white',
              stroke: '#333',
              strokeWidth: 1,
              width: 90,
              height: 20,
              parameter1: 8,
            }),
            $(
              go.TextBlock,
              {
                font: 'bold 9px Arial',
                stroke: '#000',
                textAlign: 'center',
                margin: 2,
              },
              new go.Binding('text', 'label')
            )
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

        // From-side label
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentFraction: 0,
            segmentOffset: new go.Point(-30, -10),
            background: 'white',
            margin: 1,
          },
          new go.Binding('text', 'fromText')
        ),

        // To-side label
        $(
          go.TextBlock,
          {
            font: '8px Arial',
            stroke: '#000',
            segmentFraction: -1,
            segmentOffset: new go.Point(30, -10),
            background: 'white',
            margin: 1,
          },
          new go.Binding('text', 'toText')
        )
      )

      // Oval/Circle Template for ae1 and ae2 labels (keep as is)
      this.diagram.nodeTemplateMap.add(
        'ae',
        $(
          go.Node,
          'Auto',
          { locationSpot: go.Spot.Center },
          $(go.Shape, 'Ellipse', {
            fill: 'lightblue',
            stroke: '#4682B4',
            strokeWidth: 1,
            width: 60,
            height: 20,
          }),
          $(
            go.TextBlock,
            {
              font: '10px Arial',
              stroke: '#000',
              textAlign: 'center',
            },
            new go.Binding('text', 'label')
          )
        )
      )

      // Node Data with icons
      const nodeDataArray = [
        // Top layer - LEAF switches
        { key: 'LEAF-01-TOP', label: 'LEAF-01', category: 'leaf', icon: switchIcon },
        { key: 'LEAF-02-TOP', label: 'LEAF-02', category: 'leaf', icon: switchIcon },

        // ae2 labels for top layer
        { key: 'ae2-left-top', label: 'ae2', category: 'ae' },
        { key: 'ae2-right-top', label: 'ae2', category: 'ae' },

        // Second layer - PAN switches
        { key: 'PAN-01', label: 'PAN-01', category: 'pan', icon: routerIcon },
        { key: 'PAN-02', label: 'PAN-02', category: 'pan', icon: routerIcon },

        // ae1 labels for middle layer
        { key: 'ae1-left', label: 'ae1', category: 'ae' },
        { key: 'ae1-right', label: 'ae1', category: 'ae' },

        // Core network devices
        { key: 'IPS', label: 'IPS Tipping Point', category: 'ips', icon: nodeIcon },
        { key: 'WAF', label: 'WAF Imperva', category: 'waf', icon: nodeIcon },

        // Bottom layer - LEAF switches
        { key: 'LEAF-01-BOTTOM', label: 'LEAF-01', category: 'leaf', icon: switchIcon },
        { key: 'LEAF-02-BOTTOM', label: 'LEAF-02', category: 'leaf', icon: switchIcon },
      ]

      // Link Data - recreating the crossing pattern and connections
      const linkDataArray = [
        // Top LEAF to ae2 connections
        { from: 'LEAF-01-TOP', to: 'ae2-left-top' },
        { from: 'LEAF-02-TOP', to: 'ae2-right-top' },

        // ae2 to PAN connections (crossed)
        { from: 'ae2-left-top', to: 'PAN-01' },
        { from: 'ae2-left-top', to: 'PAN-02' },
        { from: 'ae2-right-top', to: 'PAN-01' },
        { from: 'ae2-right-top', to: 'PAN-02' },

        // HA connections between PANs
        { from: 'PAN-01', to: 'PAN-02', label: 'HA-1', category: 'ha' },
        { from: 'PAN-01', to: 'PAN-02', label: 'HA-2', category: 'ha' },

        // PAN to ae1 connections
        { from: 'PAN-01', to: 'ae1-left' },
        { from: 'PAN-02', to: 'ae1-right' },

        // ae1 to core devices connections
        { from: 'ae1-left', to: 'IPS' },
        { from: 'ae1-right', to: 'IPS' },
        { from: 'IPS', to: 'WAF' },

        // Core devices to bottom LEAF connections (crossed)
        { from: 'WAF', to: 'LEAF-01-BOTTOM' },
        { from: 'WAF', to: 'LEAF-02-BOTTOM' },
        { from: 'IPS', to: 'LEAF-01-BOTTOM' },
        { from: 'IPS', to: 'LEAF-02-BOTTOM' },
      ]

      this.diagram.model = new go.GraphLinksModel(nodeDataArray, linkDataArray)

      // Set manual positions to match the diagram layout
      this.diagram.addDiagramListener('InitialLayoutCompleted', () => {
        this.setNodePositions()
      })
    },

    setNodePositions() {
      const positions = {
        'LEAF-01-TOP': new go.Point(150, 80),
        'LEAF-02-TOP': new go.Point(550, 80),

        'ae2-left-top': new go.Point(150, 180),
        'ae2-right-top': new go.Point(550, 180),

        'PAN-01': new go.Point(150, 280),
        'PAN-02': new go.Point(550, 280),

        'ae1-left': new go.Point(150, 400),
        'ae1-right': new go.Point(550, 400),

        IPS: new go.Point(250, 480),
        WAF: new go.Point(450, 520),

        'LEAF-01-BOTTOM': new go.Point(150, 640),
        'LEAF-02-BOTTOM': new go.Point(550, 640),
      }

      Object.keys(positions).forEach((key) => {
        const node = this.diagram.findNodeForKey(key)
        if (node) {
          node.location = positions[key]
        }
      })
    },
  },
}
</script>

<style scoped>
.network-topology-diagram {
  width: 100%;
  height: 800px;
  padding: 20px;
  box-sizing: border-box;
}

#networkTopologyDiv {
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #f9f9f9;
}
</style>
