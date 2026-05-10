import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from '../App'

vi.mock('../hooks/useEvents', () => ({
  useEvents: vi.fn(),
}))

import { useEvents } from '../hooks/useEvents'

describe('App', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('renders loading state', () => {
    vi.mocked(useEvents).mockReturnValue({ events: [], loading: true, error: null })
    render(<App />)
    expect(screen.getByText('読み込み中...')).toBeTruthy()
  })

  it('renders error state', () => {
    vi.mocked(useEvents).mockReturnValue({ events: [], loading: false, error: 'HTTP 404' })
    render(<App />)
    expect(screen.getByText(/エラー/)).toBeTruthy()
  })

  it('renders events and event count', () => {
    vi.mocked(useEvents).mockReturnValue({
      events: [
        {
          event_title: 'Sample Event',
          event_date: '2025-06-01',
          event_time: null,
          event_location: null,
          event_description: 'Sample description',
          source_url: 'https://example.com',
          category: '防災関連',
          is_event: true,
        },
      ],
      loading: false,
      error: null,
    })
    render(<App />)
    expect(screen.getByText('Sample Event')).toBeTruthy()
    expect(screen.getByText('1 件')).toBeTruthy()
  })

  it('renders empty state when no events match filter', () => {
    vi.mocked(useEvents).mockReturnValue({ events: [], loading: false, error: null })
    render(<App />)
    expect(screen.getByText('該当するイベントはありません')).toBeTruthy()
  })
})
