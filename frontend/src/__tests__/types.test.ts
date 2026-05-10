// Type-level tests: verify HarvestEvent shape compiles correctly.
import { describe, it, expect } from 'vitest'
import type { HarvestEvent } from '../types'

describe('HarvestEvent type', () => {
  it('accepts a fully-populated event object', () => {
    const event: HarvestEvent = {
      event_title: 'Test',
      event_date: '2025-06-01',
      event_time: '10:00',
      event_location: 'Tokyo',
      event_description: 'Description',
      source_url: 'https://example.com',
      category: '防災関連',
      is_event: true,
    }
    expect(event.event_title).toBe('Test')
  })

  it('accepts null for optional fields', () => {
    const event: HarvestEvent = {
      event_title: 'Test',
      event_date: null,
      event_time: null,
      event_location: null,
      event_description: 'Description',
      source_url: 'https://example.com',
      category: '防災関連',
      is_event: false,
    }
    expect(event.event_date).toBeNull()
  })
})
