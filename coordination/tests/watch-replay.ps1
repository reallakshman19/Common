# watch-replay.ps1
# Deterministic Replay and Acceptance Test Harness for watch.ps1 rowsjson Bridge
param(
  [string]$WatchScript = 'C:\Users\reall\.claude\skills\coordinator-protocol\scripts\watch.ps1',
  [string]$Tabs = '1=c35d978a',
  [string]$Session = 'Session_Replay',
  [int]$Cycle = 15
)

$ErrorActionPreference = 'Stop'
Write-Host "Running watch-replay on $WatchScript..."

if (-not (Test-Path $WatchScript)) {
  Write-Error "Coordinator script not found at $WatchScript"
  exit 1
}

# 1. Test -Action rowsjson
Write-Host "Testing -Action rowsjson..."
$jsonOutput = & powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File $WatchScript -Action rowsjson -Tabs $Tabs -Session $Session -Cycle $Cycle
if (-not $jsonOutput) {
  Write-Error "Empty output from watch.ps1 -Action rowsjson"
  exit 1
}

$rows = $jsonOutput | ConvertFrom-Json
$arr = @($rows | ForEach-Object { $_ })
if ($arr.Count -lt 1) {
  Write-Error "Expected at least 1 row in rowsjson output, got $($arr.Count)"
  exit 1
}

$first = $arr[0]
$expectedFields = @('tab', 'status', 'aim', 'plan', 'ac', 'ci', 'meter', 'due', 'checked', 'next', 'tab_position', 'chat_id', 'binding_generation', 'observed_at_utc', 'probe_status')
foreach ($f in $expectedFields) {
  if (-not ($first.PSObject.Properties[$f])) {
    Write-Error "Missing required field '$f' in rowsjson output"
    exit 1
  }
}
Write-Host " [PASS] rowsjson output valid with $($arr.Count) rows and all required fields."

# 2. Test -Action rows
Write-Host "Testing -Action rows..."
$rowsOutput = & powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File $WatchScript -Action rows -Tabs $Tabs -Session $Session -Cycle $Cycle
$tableText = $rowsOutput -join "`n"
if ($tableText -notmatch '\| Tab \| Status \| Aim \| Plan \| AC \| CI \| Meter \| Due \| Checked \| Next \|') {
  Write-Error "-Action rows output does not contain expected markdown header"
  exit 1
}
Write-Host " [PASS] rows markdown table format verified."

# 3. Test -Action report
Write-Host "Testing -Action report..."
$repOutput = & powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File $WatchScript -Action report -Tabs $Tabs -Session $Session -Cycle $Cycle
$repText = $repOutput -join "`n"
if ($repText -notmatch '\*\*Needs you\*\*') {
  Write-Error "-Action report output does not contain '**Needs you**'"
  exit 1
}
Write-Host " [PASS] report format verified."

Write-Host "WATCH_REPLAY_PASS: All coordinator bridge actions verified successfully."
exit 0
