import { useState, useEffect } from 'react'
import type { HarvestEvent } from '../types'

interface UseEventsResult {
  events: HarvestEvent[]
  loading: boolean
  error: string | null
}

export function useEvents(): UseEventsResult {
  const [events, setEvents] = useState<HarvestEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/events.json')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data: HarvestEvent[]) => {
        setEvents(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message ?? 'データの読み込みに失敗しました')
        setLoading(false)
      })
  }, [])

  return { events, loading, error }
}
