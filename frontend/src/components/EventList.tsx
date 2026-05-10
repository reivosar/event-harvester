import type { HarvestEvent } from '../types'
import { EventCard } from './EventCard'

interface Props {
  events: HarvestEvent[]
  loading: boolean
  error: string | null
}

export function EventList({ events, loading, error }: Props) {
  if (loading) {
    return <div className="state-message">読み込み中...</div>
  }
  if (error) {
    return <div className="state-message error">エラー: {error}</div>
  }
  if (events.length === 0) {
    return <div className="state-message">該当するイベントはありません</div>
  }
  return (
    <div className="event-grid">
      {events.map((event, i) => (
        <EventCard key={`${event.source_url}-${i}`} event={event} />
      ))}
    </div>
  )
}
