export const diagramRoutes = [
  {
    path: 'logical-topology',
    name: 'lodical_topology',
    meta: { title: 'Logical Topology', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/LogicalTopology.vue'),
  },
  {
    path: 'aci',
    name: 'chart_demo_aci',
    meta: { title: 'ACI', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/ACI.vue'),
  },
  {
    path: 'mx204',
    name: 'chart_demo_mx204',
    meta: { title: 'MX204', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/MX204.vue'),
  },
  {
    path: 'asr-core-wan',
    name: 'chart_demo_asr_core_wan',
    meta: { title: 'ASR Core WAN', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/AsrCoreWan.vue'),
  },
  {
    path: 'physical-wan-partner',
    name: 'chart_demo_physical_wan_partner',
    meta: { title: 'Physical WAN Partner', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/PhysicalWanPartner.vue'),
  },
  {
    path: 'mho',
    name: 'chart_demo_mho',
    meta: { title: 'MHO', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/Mho.vue'),
  },
  {
    path: 'pan',
    name: 'chart_demo_pan',
    meta: { title: 'PAN', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/Pan.vue'),
  },
  {
    path: 'router-vpn',
    name: 'chart-demo-router',
    meta: { title: 'Router', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/RouterVPN.vue')
  },
  {
    path: 'citrix',
    name: 'chart-demo-citrix',
    meta: { title: 'Citrix', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
    component: () => import('@/modules/chart-demo/components/Citrix.vue')
  }
]
