export interface HarvestEvent {
  event_title: string
  event_date: string | null
  event_time: string | null
  event_location: string | null
  event_description: string
  source_url: string
  category: string
  is_event: boolean
}
