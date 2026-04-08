# Feature: user-selectable naming convention

## Goal
Let users choose and reorder the fields used to build the output filename,
before downloading the zip.

## Fields available
| Field         | Default on? | Example value        |
|---------------|-------------|----------------------|
| Date of issue | yes         | today() → YYYY_MM_DD |
| Provider name | yes         | ACME                 |
| Amount        | yes         | 30.56                |
| Currency      | no          | USD                  |

## Default filename
`{today()} ACME 30.56.pdf`

## Behaviour
- Minimum 1 field must remain ticked — if the user tries to untick the last one, block it with an inline error
- Field order in the filename mirrors the order of the boxes on screen
- User reorders via drag-and-drop on the checkbox rows

## Live preview
Show a live example filename below the checkboxes, updating instantly on
every tick or drag. Use hardcoded example values except for date:
- Date → `today()` — always the current date, formatted as YYYY_MM_DD
- Provider → ACME
- Amount → 30.56
- Currency → USD

Example when all 4 fields are on, in default order:
`{today()} ACME 30.56 USD.pdf`

## Implementation note
`today()` must be evaluated client-side at render time using the local
system clock — never hardcoded, never server-side. Example:
```js
const today = new Date().toISOString().slice(0, 10).replace(/-/g, '_');
```

## UI placement
Below the file upload area, above the download button.
Section title: "Rename format"

## Out of scope
- Saving preferences across sessions (no auth yet)
- Custom free-text fields
- Per-file overrides
