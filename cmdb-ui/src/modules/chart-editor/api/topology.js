import { axios } from '@/utils/request'

const urlPrefix = '/v1/topology'

export function getTopology(params) {
  return axios({
    url: urlPrefix,
    method: 'GET',
    params: params
  })
}

export function postTopology(params) {
  return axios({
    url: urlPrefix,
    method: 'POST',
    data: params
  })
}

export function getTopologyById(id, params) {
  return axios({
    url: urlPrefix + `${id}`,
    method: 'GET',
    params: params,
  })
}

export function getDeviceTypes(params) {
    return axios({
    url: urlPrefix + `/device_types`,
    method: 'GET',
    params: params,
  })
}
