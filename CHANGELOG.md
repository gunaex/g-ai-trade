# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

- Activity Log stability: eliminated flicker by decoupling state and switching to a table layout; preserved prior entries when backend returns empty; stable keys and memoization to reduce re-renders; auto-scroll only on new entries.
- Stop flow improvements: "🛑 Auto Trading Stopped" is logged on stop; status endpoint now returns recent `activity_log` and `config` even when the bot is stopped.
- Timezone standardization: all timestamps use server local time; added `/api/server-info` endpoint; UI displays 24-hour time and includes a small footer note with an "About Timezones" link.
- Logging cleanup: removed leftover `console.log` in the frontend and `print()` statements in backend error paths; replaced with `logger.error` where appropriate.
- Documentation: added `TIMEZONE_INFO.md` explaining timezone handling and verification steps.

