import type { HarvestEvent } from '../types'

export function stripHtml(str: string): string {
  const doc = new DOMParser().parseFromString(str, 'text/html')
  return doc.body.textContent ?? ''
}

export function formatDate(date: string | null): string {
  if (!date) return '日時未定'
  const [y, m, d] = date.split('-')
  return `${y}年${parseInt(m)}月${parseInt(d)}日`
}

export function sortByDate(events: HarvestEvent[]): HarvestEvent[] {
  return [...events].sort((a, b) => {
    if (!a.event_date && !b.event_date) return 0
    if (!a.event_date) return 1
    if (!b.event_date) return -1
    return a.event_date.localeCompare(b.event_date)
  })
}

export function filterByCategories(events: HarvestEvent[], selected: Set<string>): HarvestEvent[] {
  if (selected.size === 0) return events
  return events.filter(e => selected.has(e.category))
}

export function filterUpcomingEvents(events: HarvestEvent[], today: string): HarvestEvent[] {
  return events.filter(e => e.event_date !== null && e.event_date >= today)
}
