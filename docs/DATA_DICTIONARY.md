# Data dictionary

Every entity has a stable numeric `id`. References are arrays of ids (`;`-separated in CSV). Empty values are `null` in JSON and empty in CSV.

## organizations
`id`, `name`, `sector` (Academy, Business, Government, Hub, Expert …; original W3I labels), `country`, `website`, `aliases[]`, `description`, `tag_ids[]` → tags

## people
`id`, `name`, `organization_ids[]` → organizations, `project_ids[]` → projects, `tag_ids[]` → tags. Nothing else is released. Only people with at least one recorded organization are included.

## projects
`id`, `name`, `type` (Pilot, Course, Startup, Research, Policy, Event, Circle …), `aliases[]`, `website`, `description`, `organization_ids[]`, `related_project_ids[]`, `tag_ids[]`

## tags
`id`, `name`, `category` (topic or cohort), `aliases[]`

## materials
`slug`, `title`, `type`, `format` (report, talk, post …), `date`, `tags[]` (topic labels as text, not ids), `excerpt`, `url` (page on w3i.network), `pdf`, `event`, `event_url`, `youtube`. Only items already published on the W3I site.
