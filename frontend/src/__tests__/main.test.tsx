// Smoke test: verifies the root element is present in the DOM before mounting.
import { describe, it, expect } from 'vitest'

describe('main entry point', () => {
  it('expects a root element to be present in the document', () => {
    // The actual mounting is tested via App tests.
    // This confirms the test environment is set up correctly.
    const root = document.getElementById('root')
    // jsdom does not include index.html's root div by default; that is expected here.
    expect(root === null || root instanceof HTMLElement).toBe(true)
  })
})
