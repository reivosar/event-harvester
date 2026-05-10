import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EventCard } from '../components/EventCard'
import type { HarvestEvent } from '../types'

const baseEvent: HarvestEvent = {
  event_title: 'Test Conference',
  event_date: '2025-06-15',
  event_time: '14:00',
  event_location: 'Osaka',
  event_description: '<p>A <strong>test</strong> event description.</p>',
  source_url: 'https://example.com/event',
  category: '防災関連',
  is_event: true,
}

describe('EventCard', () => {
  it('renders event title', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText('Test Conference')).toBeTruthy()
  })

  it('renders formatted date', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText('2025年6月15日')).toBeTruthy()
  })

  it('renders category badge', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText('防災関連')).toBeTruthy()
  })

  it('renders location when present', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText(/Osaka/)).toBeTruthy()
  })

  it('strips HTML from description', () => {
    render(<EventCard event={baseEvent} />)
    expect(screen.getByText(/A test event description/)).toBeTruthy()
  })

  it('renders link with rel noopener noreferrer', () => {
    render(<EventCard event={baseEvent} />)
    const link = screen.getByRole('link', { name: '詳細を見る' }) as HTMLAnchorElement
    expect(link.rel).toContain('noopener')
    expect(link.rel).toContain('noreferrer')
    expect(link.href).toBe('https://example.com/event')
  })

  it('renders placeholder date when event_date is null', () => {
    render(<EventCard event={{ ...baseEvent, event_date: null }} />)
    expect(screen.getByText('日時未定')).toBeTruthy()
  })

  it('does not render location section when event_location is null', () => {
    const { container } = render(<EventCard event={{ ...baseEvent, event_location: null }} />)
    expect(container.querySelector('.event-location')).toBeNull()
  })
})
