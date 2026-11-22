# Changelog

## 1.1.0

### Fixed
- **Data Explorer:** filters no longer disappear when another widget changes; multiple filters can be stacked and removed individually. Invalid values (e.g. text in a numeric comparison) show a message instead of an error.
- **Feedback messages:** "Applied / Loaded / Undid" confirmations are now visible (they were erased by an immediate rerun).
- **Light theme:** inputs, tables and charts now follow the selected theme instead of staying dark on a light page.
- **Fonts:** one typeface everywhere (Inter); removed the mix of DM Sans, JetBrains Mono and Streamlit's default, and the Unicode glyph icons that fell back to random system fonts.
- **Cleaning:** Trim/Standardize now see `string`-typed columns; mean/median fills no longer crash on nullable integers; constant fill no longer fails on empty or incompatible values; numeric-only strategies warn about skipped columns.
- **Import:** reliable delimiter/encoding detection, Brazilian decimal comma (`1.234,56`), `.xls` support (`xlrd` was missing from requirements), worksheet selection, duplicate column names, blank rows/columns from Excel exports.
- **Security:** dataset names are escaped before being rendered as HTML.
- **Performance:** Excel is generated only when downloading (it used to be rebuilt on every interaction); undo history stores references instead of full copies and is capped.
- Replaced deprecated `use_container_width` with `width="stretch"`.

### Added
- **Export Center** page (CSV/Excel, working copy or original, optional change-log sheet, frozen header).
- Trend-over-time chart in Analytics; sample dataset now has a real date column.
- "Restore original", day-first dates and decimal-comma options in Data Cleaning, quality/rows delta preview.
- Download of the filtered Explorer view.
- Light / Dark / System theme via Streamlit's native settings, logo, native sidebar navigation.
- 52 tests, including end-to-end tests that run the whole app.

### Changed
- `pages/` renamed to `views/`; session logic centralised in `state.py`.
- `pytest` moved to `requirements-dev.txt`.
