import { CATEGORIES } from '../constants'

interface Props {
  selected: Set<string>
  onChange: (cat: string) => void
}

export function CategoryFilter({ selected, onChange }: Props) {
  const allSelected = selected.size === CATEGORIES.length

  return (
    <div className="category-filter">
      <button
        className={`category-btn ${allSelected ? 'active' : ''}`}
        onClick={() => onChange('__all__')}
      >
        全て
      </button>
      {CATEGORIES.map(cat => (
        <button
          key={cat}
          className={`category-btn ${selected.has(cat) ? 'active' : ''}`}
          onClick={() => onChange(cat)}
        >
          {cat}
        </button>
      ))}
    </div>
  )
}
