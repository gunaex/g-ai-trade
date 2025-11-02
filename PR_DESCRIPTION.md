# PR: Stabilize Activity Log, Standardize Timezones, Improve Stop Flow, and Clean Up Debug Logs

## Summary
- Fixes Activity Log flicker and disappearing entries.
- Ensures stop events are visible and logs persist after stopping the bot.
- Standardizes all timestamps to server local time with UI notes and a new server info endpoint.
- Cleans up leftover debug logging across frontend and backend.

## Changes
- Frontend
  - Activity Log rendering stabilized (table layout, memoized props, stable keys, auto-scroll only on new items).
  - Polling logic decoupled activities from status to avoid churn.
  - UI shows 24-hour time and adds a footer link: "About Timezones" pointing to `TIMEZONE_INFO.md`.
  - Removed stray `console.log` from components.
- Backend
  - `/api/server-info` endpoint exposes server local time, timezone, and offset.
  - Stop behavior logs "🛑 Auto Trading Stopped" and keeps recent `activity_log` available via `/api/auto-bot/status` when not running.
  - Replaced `print()` in error paths with structured `logger.error` (with `exc_info`).

## Testing
- Verified Activity Log updates steadily every 2 seconds without flicker; entries no longer disappear when backend returns empty arrays.
- Confirmed stop action logs the stop event; logs remain visible after stop; `is_running` returns `false`.
- Confirmed `/api/server-info` returns server local time, timezone, and offset; UI shows times in 24-hour format and the footer note is visible.
- Sanity-checked error paths to ensure errors are logged via `logger` (no stdout prints).

## Risks / Impact
- Minimal. UI changes are additive/non-breaking; backend endpoints retain existing contracts while adding a new informational endpoint.
- Backtesting console prints remain intact (intended for CLI output).

## Rollback Plan
- Revert this PR; no migrations or persistent schema changes were introduced.

## Notes
- See `TIMEZONE_INFO.md` for details about timezone handling.
