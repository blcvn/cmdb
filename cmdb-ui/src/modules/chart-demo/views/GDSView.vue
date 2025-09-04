<template>
  <div class="w-full">
    <h2>Network Diagram</h2>
    <NetworkDiagram :nodes="diagramNodes" :links="diagramLinks" />

    <h2 style="margin-top: 40px">Fabric Topology</h2>
    <FabricTopology />

    <h2 style="margin-top: 40px">MX204 Edge Topology</h2>
    <MX204EdgeTopology />

    <h2 style="margin-top: 40px">ASR-CoreWan & WanPartner</h2>
    <AsrCoreWan :nodes="asrData.nodes" :links="asrData.links" />

    <h2 style="margin-top: 40px">Physical Wan Partner</h2>
    <PhysicalWanPartner />

    <h2 style="margin-top: 40px">MHO</h2>
    <Mho />

    <h2 style="margin-top: 40px">PAN</h2>
    <Pan />

    <h2 style="margin-top: 40px">RouterVPN</h2>
    <RouterVPN />

    <h2 style="margin-top: 40px">Example Topology</h2>
    <!-- Truyền topologyData vào ExampleTopology -->
    <ExampleTopology :topologyData="topologyData" />
  </div>
</template>

<script>
import FabricTopology from '../components/FabricTopology.vue'
import MX204EdgeTopology from '../components/MX204EdgeTopology.vue'
import NetworkDiagram from '../components/NetworkDiagram.vue'
import AsrCoreWan from '../components/AsrCoreWan.vue'
import PhysicalWanPartner from '../components/PhysicalWanPartner.vue'
import Mho from '../components/Mho.vue'
import Pan from '../components/Pan.vue'
import ExampleTopology from '../components/ExampleTopology'
import RouterVPN from '../components/RouterVPN.vue'

// SVG icons
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import node from '@/assets/icons/node-svgrepo-com.svg'
import router from '@/assets/icons/router-svgrepo-com.svg'

export default {
  name: 'GDSView',
  components: {
    NetworkDiagram,
    FabricTopology,
    MX204EdgeTopology,
    AsrCoreWan,
    PhysicalWanPartner,
    Mho,
    Pan,
    ExampleTopology,
    RouterVPN
  },
  data() {
    return {
      topologyData: {
        class: 'go.GraphLinksModel',
        nodeDataArray: [
          { key: 0, type: 'Cloud', loc: '0 0', text: 'Internet' },
          { key: 1, type: 'Firewall', loc: '100 0' },
          { key: 2, type: 'Router', loc: '200 0' },
          { key: 3, type: 'Server', loc: '300 0' },
          { key: 4, type: 'Switch', loc: '200 100' },
          { key: 5, type: 'Firewall', loc: '25 100' },
          { key: 6, type: 'Router', loc: '25 200' },
          { key: 7, type: 'Switch', loc: '400 100' },

          { key: 10, isGroup: true, text: 'Intranet 1' },
          { key: 11, type: 'PC', loc: '150 220', group: 10 },
          { key: 12, type: 'PC', loc: '250 220', group: 10 },
          { key: 13, type: 'PC', loc: '150 270', group: 10 },
          { key: 14, type: 'PC', loc: '250 270', group: 10 },

          { key: 20, isGroup: true, text: 'Intranet 2' },
          { key: 21, type: 'PC', loc: '350 220', group: 20 },
          { key: 22, type: 'PC', loc: '450 220', group: 20 },
          { key: 23, type: 'PC', loc: '350 270', group: 20 },
          { key: 24, type: 'PC', loc: '450 270', group: 20 },

          { key: 30, isGroup: true, text: 'Isolation test' },
          { key: 31, type: 'PC', loc: '-100 172', group: 30 },
          { key: 32, type: 'PC', loc: '-100 242', group: 30 },
        ],
        linkDataArray: [
          { from: 0, to: 1 },
          { from: 1, to: 2 },
          { from: 2, to: 3 },
          { from: 2, to: 4 },
          { from: 5, to: 4 },
          { from: 5, to: 6 },
          { from: 4, to: 7 },
          { from: 4, to: 10 },
          { from: 7, to: 20 },
          { from: 6, to: 30 },
        ],
      },

      diagramNodes: [
        // Groups
        { key: 'LEAF', isGroup: true, category: 'band', text: 'LEAF', loc: '0 120', size: '1180 90' },
        { key: 'DMZ', isGroup: true, category: 'area', text: 'DMZ' },
        { key: 'CORE', isGroup: true, category: 'area', text: 'CORE' },

        // INTERNET EDGE cluster (phải, phía trên LEAF)
        { key: 'INTERNET', category: 'label', text: 'INTERNET', loc: '520 -60' },
        { key: 'EDGE', category: 'label', text: 'INTERNET EDGE', loc: '520 -10' },
        { key: 'LB', category: 'net', text: 'LB', loc: '470 40', size: '90 54' },
        { key: 'VPN', category: 'net', text: 'VPN ROUTER', loc: '570 40', size: '120 54' },

        // DMZ area members (trái, trên LEAF)
        { key: 'DMZ-SRV', category: 'default', text: 'DMZ SERVER', group: 'DMZ', loc: '-430 -100', size: '120 64' },
        { key: 'WEB-SRV', category: 'default', text: 'WEB SERVER', group: 'DMZ', loc: '-300 -100', size: '120 64' },
        { key: 'WAF', category: 'security', text: 'WAF DMZ', group: 'DMZ', loc: '-150 60', size: '120 54' },
        { key: 'IPS', category: 'security', text: 'IPS', group: 'DMZ', loc: '-150 10', size: '120 54' },
        {
          key: 'FW-DMZ',
          category: 'security',
          text: 'FIREWALL DMZ PALO ALTO',
          group: 'DMZ',
          loc: '-60 -40',
          size: '160 64',
        },

        // CORE area members (giữa dưới LEAF)
        { key: 'JUMP', category: 'default', text: 'JUMP SERVER', group: 'CORE', loc: '-260 220', size: '120 64' },
        { key: 'CORE-SRV', category: 'default', text: 'CORE', group: 'CORE', loc: '-160 220', size: '120 64' },
        {
          key: 'FW-CORE',
          category: 'security',
          text: 'FIREWALL CORE CHECKPOINT',
          group: 'CORE',
          loc: '160 190',
          size: '190 64',
        },

        // WAN (phải, ngang LEAF)
        { key: 'WAN', category: 'net', text: 'WAN', loc: '760 120', size: '120 54' },
      ],
      diagramLinks: [
        // INTERNET EDGE flows
        { from: 'INTERNET', to: 'EDGE' },
        { from: 'EDGE', to: 'LB' },
        { from: 'EDGE', to: 'VPN' },
        { from: 'LB', to: 'LEAF' },
        { from: 'VPN', to: 'LEAF' },

        // DMZ chain
        { from: 'DMZ-SRV', to: 'WAF' },
        { from: 'WEB-SRV', to: 'WAF' },
        { from: 'WAF', to: 'IPS' },
        { from: 'IPS', to: 'FW-DMZ' },
        { from: 'FW-DMZ', to: 'LEAF' },

        // CORE chain
        { from: 'LEAF', to: 'FW-CORE' },
        { from: 'FW-CORE', to: 'CORE-SRV' },
        { from: 'FW-CORE', to: 'JUMP' },

        // LEAF to WAN
        { from: 'LEAF', to: 'WAN' },
      ],
      // AsrCoreWan Data
      asrData: {
        nodes: [
          { key: 'SW1', label: 'C9300_GDS_\nSW_WAN_ST\nA', category: 'core', icon: switchIcon },
          { key: 'SW2', label: 'C9300_GDS\nSW_WAN_ST\nA', category: 'core', icon: switchIcon },
          { key: 'PO2_1', label: 'Po2', category: 'po' },
          { key: 'PO2_2', label: 'Po2', category: 'po' },
          { key: 'NCS1', label: 'NCS-01\n10.29.2.86', category: 'core', icon: node },
          { key: 'NCS2', label: 'NCS-01\n10.29.2.87', category: 'core', icon: node },
          { key: 'C9300-01', label: 'C9300-01', category: 'leaf', icon: router },
          { key: 'C9300-02', label: 'C9300-02', category: 'leaf', icon: router },
          { key: 'PO1_1', label: 'Po1', category: 'po' },
          { key: 'PO1_2', label: 'Po1', category: 'po' },
          { key: 'LEAF-01', label: 'LEAF-01', category: 'leaf', icon: router },
          { key: 'LEAF-02', label: 'LEAF-02', category: 'leaf', icon: router },
        ],
        links: [
          // Stack connection
          { from: 'SW1', to: 'SW2', label: 'STACK', category: 'stack' },
          // Top level connections
          { from: 'SW1', to: 'PO2_1', label: 'Te1/1/6' },
          { from: 'SW1', to: 'PO2_2', label: 'Te1/1/8' },
          { from: 'SW2', to: 'PO2_1', label: 'Te1/1/6' },
          { from: 'SW2', to: 'PO2_2', label: 'Te1/1/8' },
          // Po2 to NCS connections
          { from: 'PO2_1', to: 'NCS1', label: 'Te0/0/0/2' },
          { from: 'PO2_1', to: 'NCS2', label: 'Te0/0/0/3' },
          { from: 'PO2_2', to: 'NCS1', label: 'Te0/0/0/2' },
          { from: 'PO2_2', to: 'NCS2', label: 'Te0/0/0/3' },
          // NCS to C9300 connections
          { from: 'NCS1', to: 'C9300-01', label: 'Gi1/0/43\nMGMT' },
          { from: 'NCS2', to: 'C9300-02', label: 'Gi2/0/43\nMGMT' },
          // Po1 connections
          { from: 'NCS1', to: 'PO1_1', label: 'Te0/0/0/0' },
          { from: 'NCS1', to: 'PO1_2', label: 'Te0/0/0/1' },
          { from: 'NCS2', to: 'PO1_1', label: 'Te0/0/0/0' },
          { from: 'NCS2', to: 'PO1_2', label: 'Te0/0/0/1' },
          // Po1 to LEAF connections
          { from: 'PO1_1', to: 'LEAF-01', label: 'E1/16' },
          { from: 'PO1_1', to: 'LEAF-02', label: 'E/17' },
          { from: 'PO1_2', to: 'LEAF-01', label: 'E1/16' },
          { from: 'PO1_2', to: 'LEAF-02', label: 'E/17' },
        ],
      },
      // PhysicalWanPartner
      physicalWanData: {
        nodes: [],
        links: [],
      },
    }
  },
}
</script>
