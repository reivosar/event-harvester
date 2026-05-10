import type { HarvestEvent } from '../types'
import { stripHtml, formatDate } from '../utils/eventHelpers'

interface Props {
  event: HarvestEvent
}

export function EventCard({ event }: Props) {
  const description = stripHtml(event.event_description).slice(0, 100)
  const dateStr = formatDate(event.event_date)
  const timeStr = event.event_time ?? ''

  return (
    <div className="event-card">
      <span className="category-badge">{event.category}</span>
      <h3 className="event-title">{event.event_title}</h3>
      <p className="event-meta">
        <span className="event-date">{dateStr}</span>
        {timeStr && <span className="event-time"> {timeStr}</span>}
      </p>
      {event.event_location && (
        <p className="event-location">場所: {event.event_location}</p>
      )}
      {description && <p className="event-description">{description}</p>}
      <a
        href={event.source_url}
        target="_blank"
        rel="noopener noreferrer"
        className="event-link"
      >
        詳細を見る
      </a>
    </div>
  )
}
