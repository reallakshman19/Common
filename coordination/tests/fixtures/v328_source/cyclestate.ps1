# Cycle state and timer guard (Owner, 11 Oct 2026 07:0x: "Looks timer miss firing. you have not checked several tabs for long ... use skill's cycle time").
# One line per Claude session in the shared state file, key claude_code_cycle_<session folder>. Only these keys are touched.
# The heartbeat is ONE recurring timer at the cycle time; adaptive one-shots are only extra early checks and never replace it. At the END OF EVERY TURN
# (an Owner message or a firing) run `show` and do what its GUARD line says with CronList / CronCreate / CronDelete.
# Run it like this:
#   & ([scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\cyclestate.ps1'))) -Action show -Session Session_Oct07
# Actions:
#   set   -Session S -Status RUNNING|HOLD|WAIT [-Cycle 15] [-Mode NON_CODER|RESTRAINED_CODER] [-Scope 'tabs 1-4'] [-Job <cron id>] [-Until HH:MM]
#   seen  -Session S -Tabs '1=6acae92b;2=6aca90eb'   positions probed in this cycle (stamps the time per position)
#   full  -Session S                                 a full status was given now
#   show  -Session S                                 CYCLE line, GUARD line, NOT_CHECKED lines for positions not probed for 2 cycles, MAP lines
#   map   -Session S -Pos N [-Chat id8] [-Folder <Session/TabX_purpose>] [-Name 'Tab3 3DC Authority']   v3.19 tab map: position -> current chat, the stream's
#         folder in Common (never renamed; it belongs to the work, not the position) and my display name. Empty values keep the old ones.
#   mode  -Session S -Pos N [-Speed auto|speed|economy] [-Coder auto|RC|NC] [-Handover auto|hold]   v3.26 per-tab mode (Owner, 11 Oct 20:0x: "think of 2 modes
#         (1) economy: long running project not urgent (2) speed: urgent and running projects"; "first 5 speed, then economy, unless override by me").
#         auto = the rule (speed for a chat's first 5 task evidence, then economy; coder from the session mode); hold = no handover until the Owner says.
param(
  [Parameter(Mandatory = $true)][ValidateSet('set', 'seen', 'full', 'show', 'map', 'pane', 'mode')][string]$Action,
  [Parameter(Mandatory = $true)][string]$Session,
  [string]$Status = '', [string]$Loaded = '', [string]$Pane = '', [int]$Cycle = 0, [string]$Mode = '', [string]$Scope = '', [string]$Job = '', [string]$Until = '', [string]$Tabs = '', [int]$Pos = 0, [string]$Chat = '', [string]$Folder = '', [string]$Name = '', [string]$Speed = '', [string]$Coder = '', [string]$Handover = '',
  [string]$StateFile = 'C:\Users\reall\.claude\coordinator-state.json'
)
$ErrorActionPreference = 'Stop'
$anchor = '"claude_code_log_anchor": 0,'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$inv = [System.Globalization.CultureInfo]::InvariantCulture
$text = [System.IO.File]::ReadAllText($StateFile, $utf8)
. ([scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\state-io.ps1')))  # v3.27: Commit-Diff (one lock, re-read, atomic swap)
$now = Get-Date; $nowS = $now.ToString('s', $inv)
$key = 'claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '')
function Get-Line($t) { $m = [regex]::Match($t, '(?m)^[ \t]*"' + $key + '":[ \t]*(\{.*\}),?[ \t]*\r?\n?'); if ($m.Success) { $m } else { $null } }
function Load-Rec {
  $m = Get-Line $text
  $r = $(if ($m) { $m.Groups[1].Value | ConvertFrom-Json } else { [pscustomobject]@{} })
  $def = @{ status = 'HOLD'; cycle = 15; mode = ''; scope = ''; job = ''; until = ''; since = $nowS; lastFull = ''; seen = @(); map = @(); modes = @() }
  foreach ($k in $def.Keys) { if (-not $r.PSObject.Properties[$k]) { $r | Add-Member -NotePropertyName $k -NotePropertyValue $def[$k] } }
  $r
}
function Save-Rec($r) {
  $line = '"' + $key + '": ' + (ConvertTo-Json -InputObject $r -Depth 5 -Compress) + ','
  $m = Get-Line $text; $new = $text
  if ($m) { $new = $new.Replace($m.Value, '') }
  if (-not $new.Contains($anchor)) { 'anchor missing - nothing written'; return $false }
  $new = $new.Replace($anchor, $line + "`n  " + $anchor)
  try { [void]($new | ConvertFrom-Json) } catch { 'bad json - nothing written'; return $false }
  $res = Commit-Diff $StateFile $text $new; if ($null -eq $res) { 'state file busy or invalid - nothing written'; return $false }; $script:text = $res; return $true
}
function HM($s) { if ($s) { ([datetime]::Parse($s, $inv)).ToString('HH:mm', $inv) } else { '-' } }
$r = Load-Rec
switch ($Action) {
  'set' {
    if ($Status -notin 'RUNNING', 'HOLD', 'WAIT') { 'need -Status RUNNING|HOLD|WAIT'; return }
    if ($Status -ne $r.status) { $r.since = $nowS }
    $r.status = $Status
    if ($Cycle -gt 0) { $r.cycle = $Cycle }; if ($Mode) { $r.mode = $Mode }; if ($Scope) { $r.scope = $Scope }
    $r.job = $Job; $r.until = $Until
    if (Save-Rec $r) { 'CYCLE_SET {0} {1} every {2} min{3}' -f $Session, $r.status, $r.cycle, $(if ($Job) { ', heartbeat job ' + $Job } else { '' }) }
  }
  'seen' {
    $map = @{}; foreach ($e in @($r.seen)) { if ($e) { $q = $e -split '\|'; $map[$q[0]] = $e } }
    foreach ($p in ($Tabs -split ';' | Where-Object { $_ -match '=' })) { $q = $p -split '='; $map[$q[0].Trim()] = $q[0].Trim() + '|' + $q[1].Trim() + '|' + $nowS }
    $r.seen = @($map.Keys | Sort-Object | ForEach-Object { $map[$_] })
    if (Save-Rec $r) { 'SEEN_RECORDED ' + (@($r.seen | ForEach-Object { ($_ -split '\|')[0] }) -join ',') }
  }
  'full' { $r.lastFull = $nowS; if (Save-Rec $r) { 'FULL_RECORDED ' + (HM $nowS) } }
  'mode' {
    # v3.26: one line per tab position 'pos|speed|coder|handover'; empty or auto = the rule.
    if ($Pos -lt 1) { 'need -Pos N'; return }
    if ($Speed -and $Speed -notin 'auto', 'speed', 'economy') { 'need -Speed auto|speed|economy'; return }
    if ($Coder -and $Coder -notin 'auto', 'RC', 'NC') { 'need -Coder auto|RC|NC'; return }
    if ($Handover -and $Handover -notin 'auto', 'hold') { 'need -Handover auto|hold'; return }
    $m2 = @{}; foreach ($e in @($r.modes)) { if ($e) { $q = @($e -split '\|'); while ($q.Count -lt 4) { $q += '' }; $m2[$q[0]] = $q } }
    $o = $(if ($m2.ContainsKey("$Pos")) { $m2["$Pos"] } else { @("$Pos", '', '', '') })
    if ($Speed) { $o[1] = $(if ($Speed -eq 'auto') { '' } else { $Speed }) }; if ($Coder) { $o[2] = $(if ($Coder -eq 'auto') { '' } else { $Coder }) }; if ($Handover) { $o[3] = $(if ($Handover -eq 'auto') { '' } else { $Handover }) }
    $m2["$Pos"] = $o
    $r.modes = @($m2.Keys | Sort-Object | ForEach-Object { $m2[$_] -join '|' })
    if (Save-Rec $r) { 'MODE_SET tab {0}: speed {1}, coder {2}, handover {3}' -f $Pos, $(if ($o[1]) { $o[1] } else { 'auto' }), $(if ($o[2]) { $o[2] } else { 'auto' }), $(if ($o[3]) { $o[3] } else { 'auto' }) }
  }
  'map' {
    if ($Pos -lt 1) { 'need -Pos N'; return }
    $m2 = @{}; foreach ($e in @($r.map)) { if ($e) { $q = $e -split '\|'; $m2[$q[0]] = $q } }
    $o = $(if ($m2.ContainsKey("$Pos")) { $m2["$Pos"] } else { @("$Pos", '', '', '', '') })
    $line = '{0}|{1}|{2}|{3}|{4}' -f $Pos, $(if ($Chat) { $Chat } else { $o[1] }), $(if ($Folder) { $Folder.Trim().Replace('coordination/', '').TrimEnd('/') } else { $o[2] }), $(if ($Name) { $Name -replace '\|', ' ' } else { $o[3] }), $(if ($Chat -and $Chat -ne $o[1]) { $nowS } else { $o[4] })
    $m2["$Pos"] = $line -split '\|'
    $r.map = @($m2.Keys | Sort-Object | ForEach-Object { $m2[$_] -join '|' })
    if (Save-Rec $r) { 'MAP_SET ' + $line }
  }
  'pane' {
    # v3.23 (Owner, 11 Oct 16:1x: "you are interacting with wrong page ... 6acb61cd is correct ... fix the root cause"). Root cause: "Tab N" was taken as the
    # Nth tab of my browser pane. The Owner's Tab N is a work stream bound to a LINK the Owner gave; the pane order means nothing. Each cycle (STEP 2) pass
    # every pane tab with its current URL: -Pane 'seed=<url>;tab-1=<url>;...'. Use the Tab numbers printed here as -Pos for watch.ps1, never the pane order.
    $ents = @(@($r.map) | Where-Object { $_ } | ForEach-Object { , @(($_ -split '\|') + @('', '', '', '', '')) })
    $seenChats = @{}; $pm = @()
    foreach ($p in ($Pane -split ';' | Where-Object { $_ -match '=' })) {
      $tabId = ($p -split '=', 2)[0].Trim(); $u = ($p -split '=', 2)[1].Trim(); $c8 = $(if ($u -match '/c/([0-9a-f]{8})') { $Matches[1] } else { '' })
      if (-not $c8) { 'PANE {0}: no conversation open ({1}) - send nothing' -f $tabId, $u; continue }
      $hit = @($ents | Where-Object { $_[1] -eq $c8 })[0]
      if (-not $hit) { foreach ($q in $ents) { $hw = [regex]::Match($text, '"claude_code_hw_' + $q[1] + '":[ \t]*(\{.*\})'); if ($hw.Success) { $ho = $hw.Groups[1].Value | ConvertFrom-Json; if ($ho.prevId -eq $c8) { $hit = $q; 'PANE {0} = Tab {1} (outgoing agent of its Buddy lane), chat {2} -> -Pos {1}' -f $tabId, $q[0], $c8; $seenChats[$q[1]] = 1; $pm += ('{0}={1}' -f $tabId, $q[0]) } } }; if ($hit) { continue } }
      if (-not $hit) { 'PANE {0} = UNKNOWN chat {1}: not one of the Owner''s tabs - send nothing; ask the Owner which tab this is' -f $tabId, $c8; continue }
      $seenChats[$hit[1]] = 1
      if ($hit[3] -match '^\[HOLD\]') { 'PANE {0} = Tab {1} ON HOLD ({2}), chat {3} - send nothing' -f $tabId, $hit[0], $hit[3], $c8; continue }
      if ($hit[3] -match '^\[OUT\]') { 'PANE {0} = Tab {1} NOT IN MY SCOPE ({2}), chat {3} - no see, no send' -f $tabId, $hit[0], $hit[3], $c8; continue }  # v3.25 (Owner, 11 Oct snap 1)
      'PANE {0} = Tab {1} ({2}), chat {3} -> -Pos {1}' -f $tabId, $hit[0], $hit[3], $c8; $pm += ('{0}={1}' -f $tabId, $hit[0])
    }
    foreach ($q in $ents) {
      if ($seenChats.ContainsKey($q[1]) -or $q[3] -match '^\[(HOLD|OUT)\]') { continue }
      $um = [regex]::Match($text, '"claude_code_url_' + $q[1] + '":[ \t]*\{[^\r\n]*?"url":"([^"]+)"'); $link = $(if ($um.Success) { $um.Groups[1].Value } else { 'chat ' + $q[1] })
      'NOT_IN_PANE Tab {0} ({1}), chat {2}: not open in my pane - Needs you: open {3} in the pane, or tell me to open it' -f $q[0], $q[3], $q[1], $link
    }
    'PANE_MAP ' + ($pm -join ';')
  }
  'show' {
    # v3.23 F6 (Owner, 11 Oct RCA): the session's loaded version (-Loaded, from its cron prompt "COORDINATOR CYCLE vX") against the skill file on disk.
    $skv = ''; try { $sk = [IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\SKILL.md'); $mv = [regex]::Match($sk, '# Coordinator protocol (v[\d.]+)'); if ($mv.Success) { $skv = $mv.Groups[1].Value } } catch { }
    if ($skv) { if ($Loaded -and $Loaded -ne $skv) { 'RELOAD: the skill file is {0}, this session runs {1}. Re-read SKILL.md, runbook.md (A, B, G) and recipes.md (BUDDY) now; the files win over anything remembered from a compacted summary; then recreate the timer with "COORDINATOR CYCLE {0}".' -f $skv, $Loaded } else { 'SKILL {0}{1}' -f $skv, $(if ($Loaded) { ' (loaded, current)' } else { ' (pass -Loaded <your cron prompt version> to check)' }) } }
    'CYCLE {0}: {1} every {2} min since {3}{4}{5}{6}; last full status {7}' -f $Session, $r.status, $r.cycle, (HM $r.since), $(if ($r.mode) { ', mode ' + $r.mode } else { '' }), $(if ($r.scope) { ', scope ' + $r.scope } else { '' }), $(if ($r.job) { ', heartbeat job ' + $r.job } else { '' }), (HM $r.lastFull)
    switch ($r.status) {
      'RUNNING' { 'GUARD: exactly ONE recurring heartbeat (every {0} min, off-minute; v3.26: each firing checks Speed tabs fully and Economy tabs by their page watchers) and at most ONE recurring quick pass (older v3.24 setups only) may exist: run CronList; if it is missing, recreate it with the cron template and run `set -Status RUNNING -Job <new id>`; delete any second one. One-shot early checks may exist besides it.' -f $r.cycle }
      'HOLD' { 'GUARD: no coordinator job may exist: run CronList and delete any coordinator job (heartbeat or one-shot) unless the Owner asked for that one-shot.' }
      'WAIT' { 'GUARD: exactly one one-shot resume at {0} must exist, and no heartbeat until then.' -f $r.until }
    }
    foreach ($e in @($r.map)) { if ($e) { $q = $e -split '\|'; 'MAP tab {0}: {1} | chat {2} | folder {3}' -f $q[0], $q[3], $q[1], $q[2] } }
    foreach ($e in @($r.modes)) { if ($e) { $q = @($e -split '\|'); while ($q.Count -lt 4) { $q += '' }; 'MODE tab {0}: speed {1}, coder {2}, handover {3}' -f $q[0], $(if ($q[1]) { $q[1] } else { 'auto' }), $(if ($q[2]) { $q[2] } else { 'auto' }), $(if ($q[3]) { $q[3] } else { 'auto' }) } }
    if ($r.status -eq 'RUNNING') {
      foreach ($e in @($r.seen)) { if (-not $e) { continue }; $q = $e -split '\|'; $age = ($now - [datetime]::Parse($q[2], $inv)).TotalMinutes
        if ($age -gt 2 * [int]$r.cycle) { 'NOT_CHECKED tab {0} ({1}) since {2} ({3:N0} min, more than 2 cycles): a problem row in the report' -f $q[0], $q[1], (HM $q[2]), $age } }
    }
  }
}
