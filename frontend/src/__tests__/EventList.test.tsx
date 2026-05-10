import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { EventList } from '../components/EventList'
import type { HarvestEvent } from '../types'

const mockEvent: HarvestEvent = {
  event_title: 'Sample Event',
  event_date: '2025-07-01',
  event_time: null,
  event_location: null,
  event_description: 'Sample description',
  source_url: 'https://example.com',
  category: '防災関連',
  is_event: true,
}

describe('EventList', () => {
  it('shows loading message when loading is true', () => {
    render(<EventList events={[]} loading={true} error={null} />)
    expect(screen.getByText('読み込み中...')).toBeTruthy()
  })

  it('shows error message when error is set', () => {
    render(<EventList events={[]} loading={false} error="HTTP 500" />)
    expect(screen.getByText(/エラー/)).toBeTruthy()
    expect(screen.getByText(/HTTP 500/)).toBeTruthy()
  })

  it('shows empty state message when events array is empty', () => {
    render(<EventList events={[]} loading={false} error={null} />)
    expect(screen.getByText('該当するイベントはありません')).toBeTruthy()
  })

  it('renders event cards when events are provided', () => {
    render(<EventList events={[mockEvent, { ...mockEvent, event_title: 'Second Event' }]} loading={false} error={null} />)
    expect(screen.getByText('Sample Event')).toBeTruthy()
    expect(screen.getByText('Second Event')).toBeTruthy()
  })
})
