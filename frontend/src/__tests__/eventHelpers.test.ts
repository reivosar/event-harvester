import { describe, it, expect } from 'vitest'
import { stripHtml, formatDate, sortByDate, filterByCategories } from '../utils/eventHelpers'
import type { HarvestEvent } from '../types'

const makeEvent = (overrides: Partial<HarvestEvent> = {}): HarvestEvent => ({
  event_title: 'Test Event',
  event_date: '2025-06-01',
  event_time: '10:00',
  event_location: 'Tokyo',
  event_description: 'Description',
  source_url: 'https://example.com',
  category: '防災関連',
  is_event: true,
  ...overrides,
})

describe('stripHtml', () => {
  it('removes HTML tags from a string', () => {
    expect(stripHtml('<p>Hello <strong>world</strong></p>')).toBe('Hello world')
  })

  it('returns plain text unchanged', () => {
    expect(stripHtml('plain text')).toBe('plain text')
  })

  it('returns empty string for empty input', () => {
    expect(stripHtml('')).toBe('')
  })
})

describe('formatDate', () => {
  it('formats a YYYY-MM-DD date string into Japanese format', () => {
    expect(formatDate('2025-06-01')).toBe('2025年6月1日')
  })

  it('returns placeholder when date is null', () => {
    expect(formatDate(null)).toBe('日時未定')
  })

  it('strips leading zeros from month and day', () => {
    expect(formatDate('2025-09-05')).toBe('2025年9月5日')
  })
})

describe('sortByDate', () => {
  it('sorts events by ascending date', () => {
    const events = [
      makeEvent({ event_date: '2025-08-01' }),
      makeEvent({ event_date: '2025-06-01' }),
      makeEvent({ event_date: '2025-07-01' }),
    ]
    const sorted = sortByDate(events)
    expect(sorted[0].event_date).toBe('2025-06-01')
    expect(sorted[2].event_date).toBe('2025-08-01')
  })

  it('places null-date events at the end', () => {
    const events = [
      makeEvent({ event_date: null }),
      makeEvent({ event_date: '2025-06-01' }),
    ]
    const sorted = sortByDate(events)
    expect(sorted[0].event_date).toBe('2025-06-01')
    expect(sorted[1].event_date).toBeNull()
  })

  it('does not mutate the original array', () => {
    const events = [makeEvent({ event_date: '2025-08-01' }), makeEvent({ event_date: '2025-06-01' })]
    const original = [...events]
    sortByDate(events)
    expect(events[0].event_date).toBe(original[0].event_date)
  })
})

describe('filterByCategories', () => {
  it('returns all events when selected set is empty', () => {
    const events = [makeEvent({ category: 'A' }), makeEvent({ category: 'B' })]
    expect(filterByCategories(events, new Set())).toHaveLength(2)
  })

  it('filters events to only selected categories', () => {
    const events = [makeEvent({ category: 'A' }), makeEvent({ category: 'B' }), makeEvent({ category: 'A' })]
    const result = filterByCategories(events, new Set(['A']))
    expect(result).toHaveLength(2)
    expect(result.every(e => e.category === 'A')).toBe(true)
  })

  it('returns empty array when no events match selected categories', () => {
    const events = [makeEvent({ category: 'A' })]
    expect(filterByCategories(events, new Set(['B']))).toHaveLength(0)
  })
})
