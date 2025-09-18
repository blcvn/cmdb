import { BasicLayout, BlankLayout } from '@/layouts'
import { diagramRoutes } from './diagramRoute'

export default () => [
  {
    path: '/chart-demo',
    name: 'chart-demo',
    component: BasicLayout,
    redirect: '/chart-demo/gds/logical-topology',
    meta: { title: 'Chart Demo', icon: 'gridSvg', selectedIcon: 'gridSvg' },
    children: [
      {
        path: 'gds',
        name: 'chart_demo_gds',
        meta: { title: 'Topo GDS', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
        component: BlankLayout,
        children: diagramRoutes
      }
    ]
  }
]
