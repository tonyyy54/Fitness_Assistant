import { AxiosError } from 'axios'

import api from './api'

export type WeightPlanInput = {
  target_weight_kg: number
  weekly_loss_kg: number
}

export type WeightPlan = WeightPlanInput & {
  id: string
  user_id: string
  current_weight_kg: number
  target_bmi: number
  daily_calorie_deficit: number
  recommended_daily_calories: number
  estimated_weeks: number
  warning: string | null
  created_at: string
  updated_at: string
}

export async function getWeightPlan(): Promise<WeightPlan | null> {
  try {
    const response = await api.get<WeightPlan>('/api/v1/plan')
    return response.data
  } catch (error) {
    if (error instanceof AxiosError && error.response?.status === 404) {
      return null
    }

    throw error
  }
}

export async function saveWeightPlan(
  plan: WeightPlanInput,
): Promise<WeightPlan> {
  const response = await api.put<WeightPlan>('/api/v1/plan', plan)
  return response.data
}
