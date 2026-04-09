# v1.52 — Release Notes

## 🆕 New Feature

### [5] Who is out of office for date range
A new menu option that shows which employees are out of office across a date range, **broken down day by day** with full employee details (name, job title, sector) displayed inline for each day.

## 🐛 Bug Fix — Public holidays now correctly mark all employees as out

**Problem:** The BambooHR `/time_off/whos_out/` endpoint returns company-wide holiday entries (type `"holiday"`) without an `employeeId`. The old code only extracted `employeeId` from each entry, so holidays were silently ignored — on a public holiday like Greek Easter Monday (2026-04-13), only employees with *individual* time-off requests appeared as out of office.

**Fix:** `get_who_is_out_employees()` now detects holiday entries in the API response. When a holiday is present and `only_ids=True`, all employee IDs are returned — because everyone is off on a company holiday.

## ✨ Improvements

### Day-by-day date range processing
Options **[4]** and **[5]** now evaluate each working day independently instead of treating the entire range as a single binary check. This fixes the scenario where a holiday in the middle of a range (e.g. Monday is a holiday, Tuesday is not) would incorrectly show zero available employees for the whole range.

- **[4] Available employees** — shows a summary table with per-day counts, with interactive drill-down into any specific date.
- **[5] Out of office** — shows employee names, job titles, and sectors inline for each day.

### Improved date input
- All date prompts now **validate** `YYYY-MM-DD` format before proceeding, with a retry loop on invalid input.
- Start date fields default to **today** — press Enter to accept.

### Holiday awareness
- Options [4] and [5] display a notice when the queried range contains company holidays.
- The summary table marks holiday rows clearly (`Holiday` in the Out column, `-` for Available).

### Better terminal output
- Consistent `+---+` bordered ASCII tables for both the day-by-day summary and employee listings.
- Centered section headers.
- Employee table shows a `Total: N` footer and truncates long values to column width.
- `[n]` style menu numbering.
- Weekends are automatically skipped (only Mon–Fri shown).

### Empty result handling
- Options [2], [3], [4], [5] now display a clear message instead of an empty table when no employees match.

## 🔧 Code Structure

### New client methods (`client.py`)
| Method | Type | Description |
|---|---|---|
| `extract_holiday_dates(raw_whos_out)` | `@staticmethod` | Extracts and expands holiday dates from the raw `/time_off/whos_out/` response |
| `get_out_ids_for_date(raw_whos_out, target_date)` | `@staticmethod` | Returns employee IDs whose time-off overlaps a specific date |

### New helper (`helpers/helpers.py`)
| Function | Description |
|---|---|
| `iter_weekdays(start_str, end_str)` | Yields each weekday (`Mon`–`Fri`) `date` object in a range |

### New examples (`examples/`)
| File | Demonstrates |
|---|---|
| `get_whos_out_of_office.py` | Who is out today + who is out for a date range |
| `day_by_day_breakdown.py` | Per-day availability breakdown across a range with holidays |
| `iter_weekdays_and_holidays.py` | Listing working days vs holidays, computing effective work days |

### New tests (`tests/test_client.py`)
| Test | Covers |
|---|---|
| `test_get_who_is_out_employees_with_holiday_only_ids` | Holiday in response → all employee IDs returned |
| `test_get_who_is_out_employees_no_holiday_only_ids` | No holiday → only individual time-off IDs returned |

