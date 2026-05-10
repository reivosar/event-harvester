import { useState, useMemo } from 'react'
import { useEvents } from './hooks/useEvents'
import { CategoryFilter } from './components/CategoryFilter'
import { EventList } from './components/EventList'
import { sortByDate, filterByCategories, filterUpcomingEvents } from './utils/eventHelpers'
import { CATEGORIES } from './constants'

export default function App() {
  const { events, loading, error } = useEvents()
  const [selected, setSelected] = useState<Set<string>>(new Set(CATEGORIES))

  function handleFilterChange(cat: string) {
    if (cat === '__all__') {
      setSelected(new Set(CATEGORIES))
      return
    }
    setSelected(prev => {
      const next = new Set(prev)
      if (next.has(cat)) {
        next.delete(cat)
        if (next.size === 0) return new Set(CATEGORIES)
      } else {
        next.add(cat)
      }
      return next
    })
  }

  const today = new Date().toISOString().split('T')[0]
  const displayed = useMemo(
    () => sortByDate(filterByCategories(filterUpcomingEvents(events, today), selected)),
    [events, selected, today]
  )

  return (
    <div className="app">
      <header className="app-header">
        <h1>イベント一覧</h1>
        <p className="event-count">{displayed.length} 件</p>
      </header>
      <CategoryFilter selected={selected} onChange={handleFilterChange} />
      <main>
        <EventList events={displayed} loading={loading} error={error} />
      </main>
    </div>
  )
}
