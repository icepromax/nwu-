import axios from 'axios'
import { BASE_URL } from '@/api/config'

// axios实例
const service = axios.create({
  baseURL: BASE_URL,
  timeout: 600000,
})


axios.defaults.timeout = 600000;

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 加通用请求头
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
// 跨域问题后端处理
service.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

export const get = (url, params) => {
  return service({
    url,
    method: 'get',
    params
  })
}

export const post = (url, data) => {
  return service({
    url,
    method: 'post',
    data
  })
}
