import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'

const FASTAPI_URL = process.env.FASTAPI_INTERNAL_URL || 'http://localhost:8000'
const CORE_API_KEY = process.env.CORE_API_KEY || process.env.INTERNAL_API_KEY || ''
const CORE_API_KEY_HEADER = process.env.CORE_API_KEY_HEADER || 'X-API-Key'

export interface FastAPIResponse<T = any> {
  data?: T
  error?: string
  detail?: string
}

class FastAPIClient {
  private readonly client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: FASTAPI_URL,
      headers: {
        'Content-Type': 'application/json',
        [CORE_API_KEY_HEADER]: CORE_API_KEY,
      },
      timeout: 30000, // 30 seconds
    })
  }

  async post<T = any>(
    endpoint: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<FastAPIResponse<T>> {
    try {
      const response = await this.client.post<T>(endpoint, data, config)
      return { data: response.data }
    } catch (error: any) {
      return {
        error: error.response?.data?.detail || error.message || 'Unknown error'
      }
    }
  }

  async get<T = any>(
    endpoint: string,
    config?: AxiosRequestConfig
  ): Promise<FastAPIResponse<T>> {
    try {
      const response = await this.client.get<T>(endpoint, config)
      return { data: response.data }
    } catch (error: any) {
      return {
        error: error.response?.data?.detail || error.message || 'Unknown error'
      }
    }
  }

  async delete<T = any>(
    endpoint: string,
    config?: AxiosRequestConfig
  ): Promise<FastAPIResponse<T>> {
    try {
      const response = await this.client.delete<T>(endpoint, config)
      return { data: response.data }
    } catch (error: any) {
      return {
        error: error.response?.data?.detail || error.message || 'Unknown error'
      }
    }
  }

  async uploadFile(
    endpoint: string,
    file: File | Blob,
    additionalData?: Record<string, any>
  ): Promise<FastAPIResponse> {
    try {
      const formData = new FormData()
      formData.append('file', file)

      if (additionalData) {
        for (const [key, value] of Object.entries(additionalData)) {
          formData.append(key, String(value))
        }
      }

      const response = await this.client.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          [CORE_API_KEY_HEADER]: CORE_API_KEY,
        },
      })

      return { data: response.data }
    } catch (error: any) {
      return {
        error: error.response?.data?.detail || error.message || 'Upload failed'
      }
    }
  }
}

export const fastapi = new FastAPIClient()

// Specific API methods
export const authAPI = {
  register: async (data: {
    email: string
    username: string
    password: string
    faceImageBase64: string
  }) => {
    return fastapi.post('/internal/auth/register', {
      email: data.email,
      username: data.username,
      password: data.password,
      face_image_base64: data.faceImageBase64,
    })
  },

  validateCredentials: async (data: {
    email: string
    password: string
    faceImageBase64?: string
  }) => {
    return fastapi.post('/internal/auth/validate', {
      email: data.email,
      password: data.password,
      face_image_base64: data.faceImageBase64,
    })
  },
}

export const photosAPI = {
  processPhoto: async (file: File, userId: string) => {
    return fastapi.uploadFile('/internal/photos/process', file, { user_id: userId })
  },

  getUserPhotos: async (userId: string) => {
    return fastapi.get(`/internal/users/${userId}/photos`)
  },

  getUserFaces: async (userId: string) => {
    return fastapi.get(`/internal/users/${userId}/faces`)
  },
}

export const usersAPI = {
  getUnclaimedMatches: async (userId: string) => {
    return fastapi.get(`/internal/users/${userId}/unclaimed-matches`)
  },

  claimPersons: async (userId: string, personIds: number[]) => {
    return fastapi.post(`/internal/users/${userId}/claim`, { person_ids: personIds })
  },

  getUserStats: async (userId: string) => {
    return fastapi.get(`/internal/users/${userId}/stats`)
  },
}
