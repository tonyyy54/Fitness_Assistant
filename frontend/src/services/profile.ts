import { AxiosError } from 'axios'

import api from './api'

export type BiologicalSex = 'male' | 'female'

export type ActivityLevel =
  | 'sedentary'
  | 'lightly_active'
  | 'moderately_active'
  | 'very_active'
  | 'extra_active'

export type ProfileInput = {
  biological_sex: BiologicalSex
  birth_date: string
  height_cm: number
  current_weight_kg: number
  activity_level: ActivityLevel
}

export type UserProfile = ProfileInput & {
  id: string
  user_id: string
  created_at: string
  updated_at: string
}

export async function getProfile(): Promise<UserProfile | null> {
  try {
    const response = await api.get<UserProfile>('/api/v1/profile')
    return response.data
  } catch (error) {
    if (error instanceof AxiosError && error.response?.status === 404) {
      return null
    }

    throw error
  }
}

export async function saveProfile(
  profile: ProfileInput,
): Promise<UserProfile> {
  const response = await api.put<UserProfile>('/api/v1/profile', profile)
  return response.data
}
