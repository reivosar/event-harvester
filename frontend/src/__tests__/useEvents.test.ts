import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useEvents } from '../hooks/useEvents'

describe('useEvents', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('starts in loading state', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    const { result } = renderHook(() => useEvents())
    expect(result.current.loading).toBe(true)
    expect(result.current.events).toHaveLength(0)
    expect(result.current.error).toBeNull()
  })

  it('populates events on successful fetch', async () => {
    const mockData = [
      {
        event_title: 'Test',
        event_date: '2025-06-01',
        event_time: null,
        event_location: null,
        event_description: 'Desc',
        source_url: 'https://example.com',
        category: '防災関連',
        is_event: true,
      },
    ]
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve(mockData) })
    ))
    const { result } = renderHook(() => useEvents())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.events).toHaveLength(1)
    expect(result.current.error).toBeNull()
  })

  it('sets error state on non-ok response', async () => {
    vi.stubGlobal('fetch', vi.fn(() =>
      Promise.resolve({ ok: false, status: 404 })
    ))
    const { result } = renderHook(() => useEvents())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('HTTP 404')
    expect(result.current.events).toHaveLength(0)
  })

  it('sets error state on network failure', async () => {
    vi.stubGlobal('fetch', vi.fn(() => Promise.reject(new Error('network error'))))
    const { result } = renderHook(() => useEvents())
    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('network error')
  })
})
