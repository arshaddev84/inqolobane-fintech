# Changes

## 2026-10-23

- Restored the dark customer-operations workbench in the Next.js frontend.
- Added live frontend requests for cases, profile snapshots, source documents, and FastAPI database readiness. The interface shows API errors instead of fabricated records.
- Added case detail selection, profile snapshot review, document reading, search, refresh, responsive navigation, loading/empty states, and database connection status.
- Replaced default Next.js page metadata with Inqolobane Operations metadata.
- Added a separate C# WinUI 3 Windows desktop client under `desktop/`, using the existing FastAPI read-only endpoints.
- Added Windows PowerShell smoke-test commands in `desktop/SMOKE-TESTS.md`.
- Fixed desktop startup loading to use the WinUI `Window.Activated` event instead of the unavailable `Window.Loaded` event.
- Added local startup/exception diagnostics for investigating the Windows-only WinUI launch crash.
- Fixed invalid space-separated WinUI `Grid.ColumnDefinitions` shorthand that caused a XAML parse crash during `MainWindow` initialization.
- Stretched desktop list-item content to keep profile columns and all row dividers aligned, and matched selected-row colors to the web workbench palette.
- Removed an unresolved `DefaultListViewItemStyle` static lookup; list item alignment is now applied through the generated-container event while retaining the WinUI default template.