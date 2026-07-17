import api from './api'

export type WeightEntryInput = {
  weight_kg: number
  recorded_on: string
  note?: string | null
}

export type WeightEntry = WeightEntryInput & {
  id: string
  user_id: string
  created_at: string
  updated_at: string
}

export async function getWeightEntries(): Promise<WeightEntry[]> {
  const response = await api.get<WeightEntry[]>('/api/v1/weights', {
    params: {
      limit: 365,
    },
  })
  return response.data
}

export async function saveWeightEntry(
  entry: WeightEntryInput,
): Promise<WeightEntry> {
  const response = await api.put<WeightEntry>('/api/v1/weights', entry)
  return response.data
}
