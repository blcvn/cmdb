<template>
  <div v-if="isAdmin" class="w-full">
    <h2 style="margin-top: 40px">Example Topology</h2>
  </div>
  <div v-else>
    <a-result status="403" title="403" sub-title="Topology view access required" />
  </div>
</template>

<script>
import LogicalTopology from '../components/LogicalTopology.vue'
import TemplateDiagram from '../components/ACI.vue'
import FabricTopology from '../components/FabricTopology.vue'
import AsrCoreWan from '../components/AsrCoreWan.vue'
import PhysicalWanPartner from '../components/PhysicalWanPartner.vue'
import Mho from '../components/Mho.vue'
import Pan from '../components/Pan.vue'
import ExampleTopology from '../components/ExampleTopology'
import RouterVPN from '../components/RouterVPN.vue'
import Citrix from '../components/Citrix.vue'
import DiagramViewer from '../components/DiagramViewer.vue'
import { currentUser } from '../../acl/api/user'

// SVG icons
import switchIcon from '@/assets/icons/switch-svgrepo-com.svg'
import nodeIcon from '@/assets/icons/node-svgrepo-com.svg'
import routerIcon from '@/assets/icons/router-svgrepo-com.svg'

export default {
  name: 'GDSView',
  components: {
    LogicalTopology,
    TemplateDiagram,
    FabricTopology,
    AsrCoreWan,
    PhysicalWanPartner,
    Mho,
    Pan,
    ExampleTopology,
    RouterVPN,
    Citrix,
    DiagramViewer,
  },
  setup() {},
  data() {
    return {
      isAdmin: false,
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
      // NETWORK TOPOLOGY DATA
      networkData: {
        nodes: [
          // Groups
          { key: 'DMZ', isGroup: true, category: 'area', text: 'DMZ' },
          { key: 'CORE', isGroup: true, category: 'area', text: 'CORE' },
          // LEAF
          { key: 'LEAF', category: 'net', text: 'LEAF', loc: '0 120', size: '1180 90' },
          // INTERNET EDGE cluster (phải, phía trên LEAF)
          { key: 'INTERNET', category: 'label', text: 'INTERNET', loc: '520 -60' },
          { key: 'EDGE', category: 'label', text: 'INTERNET EDGE', loc: '520 -10' },
          { key: 'LB', category: 'net', text: 'LB', loc: '470 40', size: '90 54' },
          { key: 'VPN', category: 'net', text: 'VPN ROUTER', loc: '570 40', size: '120 54' },

          // DMZ area members (trái, trên LEAF)
          { key: 'DMZ-SRV', category: 'default', text: 'DMZ SERVER', group: 'DMZ', loc: '-430 -100', size: '120 64' },
          { key: 'WEB-SRV', category: 'default', text: 'WEB SERVER', group: 'DMZ', loc: '-300 -100', size: '120 64' },

          // DMZ firewall
          {
            key: 'FW-DMZ',
            category: 'security',
            text: 'FIREWALL DMZ PALO ALTO',
            loc: '30 -100',
            size: '160 64',
          },
          { key: 'WAF', category: 'security', text: 'WAF DMZ', loc: '0 0', size: '120 54' },
          { key: 'IPS', category: 'security', text: 'IPS', loc: '0 -40', size: '120 54' },

          // CORE area members (giữa dưới LEAF)
          { key: 'JUMP', category: 'default', text: 'JUMP SERVER', group: 'CORE', loc: '-260 220', size: '120 64' },
          { key: 'CORE-SRV', category: 'default', text: 'CORE', group: 'CORE', loc: '-160 220', size: '120 64' },

          // WAN (phải, ngang LEAF)
          { key: 'WAN', category: 'net', text: 'WAN', loc: '760 120', size: '120 54' },
        ],
        links: [
          // INTERNET EDGE flows
          { from: 'INTERNET', to: 'EDGE' },
          { from: 'EDGE', to: 'LB' },
          { from: 'EDGE', to: 'VPN' },
          { from: 'LB', to: 'LEAF' },
          { from: 'VPN', to: 'LEAF' },

          // DMZ chain
          { from: 'DMZ-SRV', to: 'LEAF' },
          { from: 'WEB-SRV', to: 'LEAF' },
          { from: 'WAF', to: 'IPS' },
          { from: 'IPS', to: 'FW-DMZ' },
          { from: 'FW-DMZ', to: 'LEAF' },

          // CORE chain
          { from: 'LEAF', to: 'FW-CORE' },
          { from: 'FW-CORE', to: 'CORE-SRV' },
          { from: 'FW-CORE', to: 'JUMP' },

          // LEAF to WAN
          { from: 'LEAF', to: 'WAN' },
          { from: 'LEAF', to: 'WAF' },
          { from: 'CORE', to: 'LEAF' },
        ],
      },
      // ACI DATA
      aciData: {
        nodes: [
          // Groups
          { key: 'SPINE', isGroup: true },
          { key: 'LEAF', isGroup: true },
          { key: 'APIC', isGroup: true },

          // SPINE nodes
          { key: 'SPINE-01', label: 'SPINE-01', type: 'spine', color: '#9ec5fe', group: 'SPINE' },
          { key: 'SPINE-02', label: 'SPINE-02', type: 'spine', color: '#9ec5fe', group: 'SPINE' },

          // LEAF nodes (10 nodes như mẫu)
          { key: 'LEAF-01', label: 'LEAF-01', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-02', label: 'LEAF-02', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-03', label: 'LEAF-03', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-04', label: 'LEAF-04', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-05', label: 'LEAF-05', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-06', label: 'LEAF-06', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-07', label: 'LEAF-07', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-08', label: 'LEAF-08', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-09', label: 'LEAF-09', type: 'leaf', color: '#bde0fe', group: 'LEAF' },
          { key: 'LEAF-10', label: 'LEAF-10', type: 'leaf', color: '#bde0fe', group: 'LEAF' },

          // APIC nodes
          { key: 'APIC-01', label: 'APIC-01', type: 'apic', color: '#d6f7dd', group: 'APIC' },
          { key: 'APIC-02', label: 'APIC-02', type: 'apic', color: '#d6f7dd', group: 'APIC' },
          { key: 'APIC-03', label: 'APIC-03', type: 'apic', color: '#d6f7dd', group: 'APIC' },
        ],
        links: [
          // SPINE-01 connections (highlighted in blue)
          { from: 'SPINE-01', to: 'LEAF-01', label: 'E1/59', isHighlighted: true },
          { from: 'SPINE-01', to: 'LEAF-02', label: 'E1/59', isHighlighted: true },
          { from: 'SPINE-01', to: 'LEAF-03', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-04', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-05', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-06', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-07', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-08', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-09', label: 'E1/23-32' },
          { from: 'SPINE-01', to: 'LEAF-10', label: 'E1/23-32' },

          // SPINE-02 connections (highlighted in blue)
          { from: 'SPINE-02', to: 'LEAF-01', label: 'E1/60', isHighlighted: true },
          { from: 'SPINE-02', to: 'LEAF-02', label: 'E1/60', isHighlighted: true },
          { from: 'SPINE-02', to: 'LEAF-03', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-04', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-05', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-06', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-07', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-08', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-09', label: 'E1/23-32' },
          { from: 'SPINE-02', to: 'LEAF-10', label: 'E1/23-32' },

          // LEAF to APIC connections (highlighted in blue)
          { from: 'LEAF-01', to: 'APIC-01', label: 'E1/1', isHighlighted: true },
          { from: 'LEAF-02', to: 'APIC-02', label: 'E1/2', isHighlighted: true },
          { from: 'LEAF-03', to: 'APIC-03', label: 'E1/3', isHighlighted: true },
        ],
      },
      // MX204 Edge Topology DATA
      mx204Data: {
        nodes: [
          // Groups
          { key: 'INTERNET', isGroup: true, loc: '600 50' },
          { key: 'EDGE', isGroup: true, loc: '600 200' },
          { key: 'ACCESS', isGroup: true, loc: '600 350' },

          // Internet Layer
          {
            key: 'INTERNET-CLOUD',
            label: 'INTERNET',
            subtitle: 'Cloud',
            type: 'internet',
            color: '#e0f2fe',
            group: 'INTERNET',
            loc: '600 80',
          },
          {
            key: 'FPT',
            label: 'FPT',
            subtitle: 'ASN:18403, IP: 58.187.147.1/29',
            type: 'isp',
            color: '#fff3cd',
            group: 'INTERNET',
            loc: '400 120',
          },
          {
            key: 'CMC',
            label: 'CMC',
            subtitle: 'ASN:45903, IP: 113.20.97.249/29',
            type: 'isp',
            color: '#fff3cd',
            group: 'INTERNET',
            loc: '800 120',
          },
          {
            key: 'VIETTEL',
            label: 'Viettel',
            subtitle: 'ASN:7552, IP: 125.234.176.153/30',
            type: 'isp',
            color: '#fff3cd',
            group: 'INTERNET',
            loc: '200 120',
          },

          // DDoS Protection Layer
          {
            key: 'DDOS-01',
            label: 'DDOS',
            subtitle: 'FPT Protection',
            type: 'ddos',
            color: '#f8d7da',
            group: 'INTERNET',
            loc: '400 160',
          },
          {
            key: 'DDOS-02',
            label: 'DDOS',
            subtitle: 'CMC Protection',
            type: 'ddos',
            color: '#f8d7da',
            group: 'INTERNET',
            loc: '800 160',
          },

          // Edge Router Layer
          {
            key: 'MX204-EDGE-01',
            label: 'MX204-EDGE-01',
            subtitle: 'Edge Router',
            type: 'edge',
            color: '#d1ecf1',
            group: 'EDGE',
            loc: '450 240',
          },
          {
            key: 'MX204-EDGE-02',
            label: 'MX204-EDGE-02',
            subtitle: 'Edge Router',
            type: 'edge',
            color: '#d1ecf1',
            group: 'EDGE',
            loc: '750 240',
          },

          // Access Layer
          {
            key: 'MX-LEAF-01',
            label: 'LEAF-01',
            subtitle: 'Access Switch',
            type: 'access',
            color: '#d4edda',
            group: 'ACCESS',
            loc: '400 400',
          },
          {
            key: 'MX-LEAF-02',
            label: 'LEAF-02',
            subtitle: 'Access Switch',
            type: 'access',
            color: '#d4edda',
            group: 'ACCESS',
            loc: '800 400',
          },
          {
            key: 'C9300-01',
            label: 'C9300-01',
            subtitle: 'Management Switch',
            type: 'mgmt',
            color: '#e2e3e5',
            group: 'ACCESS',
            loc: '300 320',
          },
          {
            key: 'C9300-02',
            label: 'C9300-02',
            subtitle: 'Management Switch',
            type: 'mgmt',
            color: '#e2e3e5',
            group: 'ACCESS',
            loc: '900 320',
          },
        ],
        links: [
          // Internet to DDoS connections
          { from: 'INTERNET-CLOUD', to: 'DDOS-01', label: 'G1-OUT FPT', isHighlighted: true },
          { from: 'INTERNET-CLOUD', to: 'DDOS-02', label: 'G3-OUT CMC', isHighlighted: true },

          // DDoS to Edge connections
          { from: 'DDOS-01', to: 'MX204-EDGE-01', label: 'Xe-0/1/3 (.4)', isHighlighted: true },
          { from: 'DDOS-01', to: 'MX204-EDGE-01', label: 'Xe-0/1/2 (.154)', isHighlighted: true },
          { from: 'DDOS-02', to: 'MX204-EDGE-02', label: 'Xe-0/1/3 (.250)', isHighlighted: true },
          { from: 'DDOS-02', to: 'MX204-EDGE-02', label: 'Xe-0/1/2', isHighlighted: true },

          // Edge to Management connections
          { from: 'MX204-EDGE-01', to: 'C9300-01', label: 'Gi1/0/42 (MGMT)', isHighlighted: false },
          { from: 'MX204-EDGE-02', to: 'C9300-02', label: 'Gi2/0/42 (MGMT)', isHighlighted: false },

          // Edge to Leaf connections (ae0 aggregation)
          { from: 'MX204-EDGE-01', to: 'MX-LEAF-01', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
          { from: 'MX204-EDGE-01', to: 'MX-LEAF-01', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },
          { from: 'MX204-EDGE-01', to: 'MX-LEAF-02', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
          { from: 'MX204-EDGE-01', to: 'MX-LEAF-02', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },

          { from: 'MX204-EDGE-02', to: 'MX-LEAF-02', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
          { from: 'MX204-EDGE-02', to: 'MX-LEAF-02', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },
          { from: 'MX204-EDGE-02', to: 'MX-LEAF-01', label: 'Xe-0/1/0 (ae0)', isHighlighted: true },
          { from: 'MX204-EDGE-02', to: 'MX-LEAF-01', label: 'Xe-0/1/1 (ae0)', isHighlighted: true },

          // Leaf to Edge return connections
          { from: 'MX-LEAF-01', to: 'MX204-EDGE-01', label: 'E1/14 (ae0)', isHighlighted: true },
          { from: 'MX-LEAF-01', to: 'MX204-EDGE-01', label: 'E1/15 (ae0)', isHighlighted: true },
          { from: 'MX-LEAF-01', to: 'MX204-EDGE-02', label: 'E1/14 (ae0)', isHighlighted: true },
          { from: 'MX-LEAF-01', to: 'MX204-EDGE-02', label: 'E1/15 (ae0)', isHighlighted: true },

          { from: 'MX-LEAF-02', to: 'MX204-EDGE-02', label: 'E1/14 (ae0)', isHighlighted: true },
          { from: 'MX-LEAF-02', to: 'MX204-EDGE-02', label: 'E1/15 (ae0)', isHighlighted: true },
          { from: 'MX-LEAF-02', to: 'MX204-EDGE-01', label: 'E1/14 (ae0)', isHighlighted: true },
          { from: 'MX-LEAF-02', to: 'MX204-EDGE-01', label: 'E1/15 (ae0)', isHighlighted: true },
        ],
      },
      // AsrCoreWan Data
      asrData: {
        nodes: [
          { key: 'SW1', label: 'C9300_GDS_\nSW_WAN_ST\nA', category: 'core', icon: switchIcon },
          { key: 'SW2', label: 'C9300_GDS\nSW_WAN_ST\nA', category: 'core', icon: switchIcon },
          { key: 'PO2_1', label: 'Po2', category: 'po' },
          { key: 'PO2_2', label: 'Po2', category: 'po' },
          { key: 'NCS1', label: 'NCS-01\n10.29.2.86', category: 'core', icon: nodeIcon },
          { key: 'NCS2', label: 'NCS-01\n10.29.2.87', category: 'core', icon: nodeIcon },
          { key: 'C9300-01', label: 'C9300-01', category: 'leaf', icon: routerIcon },
          { key: 'C9300-02', label: 'C9300-02', category: 'leaf', icon: routerIcon },
          { key: 'PO1_1', label: 'Po1', category: 'po' },
          { key: 'PO1_2', label: 'Po1', category: 'po' },
          { key: 'LEAF-01', label: 'LEAF-01', category: 'leaf', icon: routerIcon },
          { key: 'LEAF-02', label: 'LEAF-02', category: 'leaf', icon: routerIcon },
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
      },
      // MHO
      mhoData: {
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
      },
      // PAN
      panData: {
        nodes: [],
        links: [],
      },
    }
  },
  async mounted() {
    try {
      const { result } = await currentUser()
      this.isAdmin = result.role.permissions.includes('admin')
    } catch (error) {
      console.error('Failed to check admin role:', error)
      this.isAdmin = false
    }
  },
}
</script>
