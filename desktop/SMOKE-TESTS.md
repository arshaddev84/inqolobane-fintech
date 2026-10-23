# Windows Smoke Tests

Run these commands in PowerShell on Windows with the .NET 10 SDK and Visual Studio's WinUI application development workload installed. The app is unpackaged and requires the Windows App Runtime 2.5.1 runtime on the test machine.

## 1. Verify the API

Start FastAPI so it is reachable from Windows, then open a PowerShell terminal at the repository root:

```powershell
$env:INQOLOBANE_API_URL = "http://localhost:8000/api/v1"

Invoke-RestMethod "$env:INQOLOBANE_API_URL/health/ready"
Invoke-RestMethod "$env:INQOLOBANE_API_URL/cases?limit=1"
Invoke-RestMethod "$env:INQOLOBANE_API_URL/profiles/snapshots"
Invoke-RestMethod "$env:INQOLOBANE_API_URL/documents"
```

The readiness response should report `database: ok`; each list endpoint should return `items` and `total`. If FastAPI is running in WSL or another host, set `INQOLOBANE_API_URL` to a URL reachable from Windows instead of `localhost`.

## 2. Build and launch

```powershell
Set-Location .\desktop\Inqolobane.Desktop
dotnet --version
dotnet restore .\Inqolobane.Desktop.csproj
dotnet build .\Inqolobane.Desktop.csproj --configuration Debug -p:Platform=x64
$env:INQOLOBANE_API_URL = "http://localhost:8000/api/v1"
dotnet run --project .\Inqolobane.Desktop.csproj --configuration Debug -p:Platform=x64
```

## 3. Verify the desktop workflow

- Confirm the window opens in the dark Inqolobane Operations theme and reports the API/database as connected.
- Confirm the case queue shows real complaint references and selecting a row updates the detail pane.
- Search by a known complaint or customer reference; verify the API-backed results change.
- Filter cases by status and verify the list refreshes.
- Open Profile review, filter by sync status, and confirm snapshot fields and values appear.
- Open Source library, select a document, and confirm its content and linked references appear.
- Stop or disconnect FastAPI, select Refresh, and confirm an error/offline state appears without fabricated records. Restart FastAPI and refresh again.

## Troubleshooting a window that exits or stays invisible

The desktop app appends startup checkpoints and unhandled exception details to:

```text
%LOCALAPPDATA%\Inqolobane\startup.log
```

Read the latest entries from PowerShell:

```powershell
Get-Content "$env:LOCALAPPDATA\Inqolobane\startup.log" -Tail 80
```

If the log reports that a `ColumnDefinitionCollection` could not be created from `* Auto`, update `MainWindow.xaml` from the workspace. WinUI's shorthand requires comma-separated widths (`*,Auto`). Then clean, rebuild, and launch again.