import { BasicLayout } from '@/layouts'

export default () => [
  {
    path: '/chart-editor',
    name: 'chart-editor',
    component: BasicLayout,
    redirect: '/chart-editor/edit',
    meta: { title: 'Chart Editor', icon: 'gridSvg', selectedIcon: 'gridSvg' },
    children: [
      {
        path: 'edit',
        name: 'chart_editor_edit',
        meta: { title: 'Editor', icon: 'ops_move_icon', selectedIcon: 'ops_move_icon' },
        component: () => import('@/modules/chart-editor/views/EditorView')
      },
    ]
  }
]
