import { describe, it, expect } from 'vitest'
import { CATEGORIES } from '../constants'

describe('CATEGORIES', () => {
  it('contains exactly 5 categories', () => {
    expect(CATEGORIES).toHaveLength(5)
  })

  it('includes all expected category names', () => {
    expect(CATEGORIES).toContain('震災関連')
    expect(CATEGORIES).toContain('防災関連')
    expect(CATEGORIES).toContain('アール・ブリュット関連')
    expect(CATEGORIES).toContain('シンポジウム関連')
    expect(CATEGORIES).toContain('学会・サミット・フォーラム関連')
  })
})
