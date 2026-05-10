import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { CategoryFilter } from '../components/CategoryFilter'
import { CATEGORIES } from '../constants'

describe('CategoryFilter', () => {
  it('renders all category buttons', () => {
    render(<CategoryFilter selected={new Set(CATEGORIES)} onChange={vi.fn()} />)
    CATEGORIES.forEach(cat => {
      expect(screen.getByText(cat)).toBeTruthy()
    })
  })

  it('renders "all" button', () => {
    render(<CategoryFilter selected={new Set(CATEGORIES)} onChange={vi.fn()} />)
    expect(screen.getByText('全て')).toBeTruthy()
  })

  it('marks "all" button as active when all categories selected', () => {
    render(<CategoryFilter selected={new Set(CATEGORIES)} onChange={vi.fn()} />)
    const allBtn = screen.getByText('全て')
    expect(allBtn.className).toContain('active')
  })

  it('marks "all" button as inactive when not all categories selected', () => {
    render(<CategoryFilter selected={new Set(['防災関連'])} onChange={vi.fn()} />)
    const allBtn = screen.getByText('全て')
    expect(allBtn.className).not.toContain('active')
  })

  it('calls onChange with __all__ when all button clicked', () => {
    const onChange = vi.fn()
    render(<CategoryFilter selected={new Set(CATEGORIES)} onChange={onChange} />)
    fireEvent.click(screen.getByText('全て'))
    expect(onChange).toHaveBeenCalledWith('__all__')
  })

  it('calls onChange with category name when category button clicked', () => {
    const onChange = vi.fn()
    render(<CategoryFilter selected={new Set(CATEGORIES)} onChange={onChange} />)
    fireEvent.click(screen.getByText('防災関連'))
    expect(onChange).toHaveBeenCalledWith('防災関連')
  })
})
