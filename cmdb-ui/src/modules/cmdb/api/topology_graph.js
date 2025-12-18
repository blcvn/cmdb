import { axios } from '@/utils/request'

export function getTopologyGraph(app_code, max_depth = null, max_nodes = null) {
  const params = {}

  if (app_code) {
    params.app_code = app_code
  }

  if (max_depth !== null) {
    params.max_depth = max_depth
  }

  if (max_nodes !== null) {
    params.max_nodes = max_nodes
  }

  return axios({
    url: '/v0.1/topology/graph',
    method: 'get',
    params
  })
}
