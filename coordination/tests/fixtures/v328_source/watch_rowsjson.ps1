# Per-chat watch (Owner, 10 Oct 2026, 23:0x-23:1x): batch size from the agent's real working time, the handover meter, and the red flag.
# One line per chat in the shared state file, key claude_code_hw_<id8>. Only these keys are touched.
# Run it like this (every probed tab, every cycle, STEP 3b):
#   & ([scriptblock]::Create((Get-Content -Raw 'C:\Users\reall\.claude\skills\coordinator-protocol\scripts\watch.ps1'))) -Action see -Id 6aca11db -Worked '10m 27s|5m 21s|6m 1s' -State IDLE -WkAll 54.2 -Scr 12.5 -Tp 1.4
# Actions:
#   see      -Id id8 -Worked '<probe worked, joined with |>' -State <state> [-Err '<err>'] [-Hint '<hint>'] -WkAll <wkAll> -Scr <scr> -Tp <tp> -Pos <tab position> [-Log '<probe lg>']
#            [-Session <session folder, e.g. Session_Oct07>]
#            v3.9 (Owner, 11 Oct): the tab order is frozen; a chat whose log folder is <session>/Tab<M>_... but sits at position N (M not N), or whose
#            session folder is not -Session, prints TAB_MOVED. Each Claude session has its own folder: coordination/<session folder>/Tab<N>_<purpose>/.
#   grounded -Id id8     the grounding prompt was sent for a RED_FLAG (it is then not asked again until the flag clears and comes back)
#   timeout  -Id id8     a probe of this tab timed out (45 s); reported only
#   recon    -Id id8 -Mode on|skip|auto|sent [-Step k]   the reconciliation sequence (v3.11, Owner 11 Oct): 'on' = the Owner said "recon tab N",
#                        'skip' = "skip recon tab N", 'auto' = back to the rule, 'sent' = RECON step k was DELIVERED
#   batched  -Id id8     a batch message was delivered (Owner, 11 Oct: log turn lengths before and after); the first call per chat keeps
#                        the median of the last 3 as "before", every later Worked-for label counts as "after" (BATCH_EFFECT line)
#   show     [-Id id8]
# Rules (Owner):
#   BATCH        n = 25 minutes (the Owner's maximum) / median of the last 3 Worked-for labels; ask for n-2 to n-1 tasks (5 min -> 3-4); 1 = no batch.
#   HANDOVER_DUE add up ALL the working minutes: 70 or more (Owner, 11 Oct 06:3x; it was 90) -> plan for handover; 20 pages or more -> also (Owner, 11 Oct; it was more than 30: chats hit
#                the length limit at 25 to 30 pages, and the handover itself needs about 5 pages). Also a red "Message delivery timed out" (22:4x).
#   LIMIT        the length-limit page: the chat is full, no H1 there; tell the Owner and keep its URL.
#   RECON_DUE    (v3.11) the 3rd agent of a tab, and every 3rd after it (-Gen from the ledger's GEN line), or the Owner's "recon tab N": from 12 pages or
#                55 minutes worked, send RECON 1 to 4 (one per idle turn, -Rcn = the probe's rcn); it replaces the normal handover, RECON 4 ends with the brief. Agent hints ("Time for Runner" ...) and errors or probe timeouts are only reported (NOTE).
#   RED_FLAG     the last 3 turns worked under 5 minutes in total -> send the grounding prompt (recipe HANDOVER H4 text) once.
#   Cumulative minutes and pages start from what is loaded at first sight (wkAll, scr: a lower bound for a long chat) and grow as new turns appear
#   (minutes: each new Worked-for label; pages: the newest turn's height tp). What is loaded now is always a lower bound too.
param(
  [Parameter(Mandatory = $true)][ValidateSet('see', 'grounded', 'timeout', 'batched', 'recon', 'rows', 'rowsjson', 'report', 'due', 'cycle', 'mark', 'carry', 'show', 'gate', 'peek')][string]$Action,
  [int]$Gen = 0, [int]$Bs = 0, [string]$Url = '', [string]$Title = '', [int]$Rcn = 0, [string]$Mode = '', [int]$Step = 0, [double]$ReconPages = 12, [double]$ReconMin = 55,
  [string]$Id = '', [string]$Worked = '', [string]$State = '', [string]$Err = '', [string]$Hint = '',
  [double]$WkAll = 0, [double]$Scr = 0, [double]$Tp = 0, [int]$Pos = 0, [string]$Log = '', [string]$Session = '', [string]$Prog = '', [string]$Ac = '', [int]$EvNew = 0, [string]$Tabs = '', [int]$Cycle = 15, [string]$What = '', [string]$Tests = '', [string]$Pr = '', [string]$Blocker = '', [int]$DoneN = 0, [string]$LogLine = '', [string]$St = '', [string]$Ft = '', [switch]$HoldReply, [string]$From = '',
  [double]$Target = 25, [double]$StableMin = 60, [double]$MaxMin = 35, [double]$MaxPages = 20, [int]$MaxTurns = 6, [string]$Meter = '', [switch]$Quick, [switch]$Short, [double]$RedMin = 5,
  [string]$Stage = '', [string]$Turns = '', [string]$Repo = '', [string]$RepoVis = '', [string]$Probes = '', [string]$Ctx = '', [string]$PlanUse = '', [string]$NextAt = '', [string]$StateFile = 'C:\Users\reall\.claude\coordinator-state.json'
)
$ErrorActionPreference = 'Stop'
. ([scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\state-io.ps1')))  # v3.27: Commit-Diff (one lock, re-read, atomic swap)
. ([scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\aim-lib.ps1', [Text.Encoding]::UTF8)))  # v3.28: sticky labels (references/aim-architecture.md)
# v3.23 F3 (Owner, 11 Oct 16:1x): the meter is a stated cycle parameter, -Meter 'min/pages/turns' (cron prompt "Meter = 35/20/6"), never a session's private memory.
if ($Meter -match '^\s*(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)\s*/\s*(\d+)\s*$') { $MaxMin = [double]$Matches[1]; $MaxPages = [double]$Matches[2]; $MaxTurns = [int]$Matches[3] }
$anchor = '"claude_code_log_anchor": 0,'
$utf8 = New-Object System.Text.UTF8Encoding($false)
$inv = [System.Globalization.CultureInfo]::InvariantCulture
$text = [System.IO.File]::ReadAllText($StateFile); $diskText = $text  # v3.27: $diskText = the file as this run last read or wrote it; Commit-Diff writes only the difference
$now = (Get-Date).ToString('s', $inv)

# The reconciliation sequence (Owner, 11 Oct, from "Building a Reliable Reconciliation System for Long-Running AI Projects"): {0} = session folder, {1} = tab, {2} = date.
$RECON = @(
  'RECON 1 of 4 (Owner WHY). Before more work, reconcile from evidence, not memory. If your tab folder coordination/{0}/Tab{1}_<purpose>/ on main of reallakshman19/Common does not exist yet, create it first (LINEAGE.md, ARTIFACTS.md, EVIDENCE.log, CHECKPOINTS.md, DECISIONS.md, INPUTS.md, handovers/) from your issue and this chat; <purpose> is 2 to 4 words for what this chat is for, never PR or issue numbers; plain text, append only, commit message coord-log: Tab{1} <what> [skip ci], no secrets or personal data. Then, from the owning issue, its parent, the roadmap and the folder''s DECISIONS and INPUTS: state the Owner''s original outcome in the Owner''s terms, every acceptance criterion as AC-1..n, the inputs, golden fixtures and benchmarks that prove each one (path and SHA), and every Owner decision with its answer or open. Mark each item verified in a document, or claim. Write it to RECON/{2}/1-why.md in the folder. In this chat give at most 15 lines, and end this and every later reply with one line in this form: LOG | chat=<this chat id> | tab=Tab{1} | folder=coordination/{0}/Tab{1}_<purpose>/ | commit=<latest log commit> | issue=<owning issue> | plan=<plan revision> | progress=<done>/<total> | done=<task IDs closed in this reply, or none> | next=<next task IDs in order> | ac=<criteria met>/<total> | health=<GREEN, AMBER or RED>:<reason> | blocker=<NONE, OWNER:<decision IDs>, PERSON:<who>, CI, MACHINE:<what a local run or file read would clear>, or EXTERNAL:<what>> | PR=<number>@<sha>:<CI state green, red, queued or not-run, or none> | tests=<passed>/<run> | release=<HOLD or its state> | handover=<no, due, or ready:<path>>'
  'RECON 2 of 4 (source truth). At the exact head (repo, branch, commit SHA) inspect the current source, not issue or PR text: the entrypoints and the call path to each output, modules that exist but are not wired in, flags and guards that switch work off (preview-only, ready=false), and code that is never called. Then take every claim in ARTIFACTS.md, CHECKPOINTS.md and EVIDENCE.log and mark it confirmed or contradicted by the source, with file:line. Write 2-source.md in the same RECON folder as step 1. In this chat at most 15 lines, contradictions first, and the LOG line'
  'RECON 3 of 4 (proof). For each AC from step 1 say implemented (code exists), connected (on the running path) and proven (a test or CI run at this SHA that really ran it with the oracle input; a green run that skipped it, or a dummy input, is not proof). Then answer: can the Owner use it now, yes or no, with which inputs and settings, and what happens if they try. Write 3-proof.md in the same RECON folder. In this chat at most 15 lines and the LOG line'
  'RECON 4 of 4 (reconcile and hand over). Your tab folder is coordination/{0}/Tab{1}_<purpose>/ on main of reallakshman19/Common, even when your code lives in another repository. If its RECON/{2}/ has no 1-why.md, 2-source.md or 3-proof.md (for example steps 1 to 3 were done in this chat), first write them there from your answers in this chat; do not search anywhere else. Then combine steps 1 to 3 into 4-report.md in that RECON folder: owner outcome, source snapshot, product flow, implemented / connected / proven per AC, inputs and acceptance coverage, contradictions and superseded assumptions, missing integrations and blockers, the usability decision, the next 3 high-ROI tasks (source location, outcome, acceptance check, XS/S/M/L; reuse before rewrite), evidence and unknowns. Publish it as a PLAN_UPDATE on the owning issue, add the next plan revision to CHECKPOINTS.md and the superseded assumptions to LINEAGE.md. Then give the boarding brief for the next engineer in ONE plain text code block of at most 10000 characters that starts from that report: first line Tab{1} | folder coordination/{0}/Tab{1}_<purpose>/, no triple backticks inside, no attachments or download links, last line === END OF HANDOVER ===. After the block, end with exactly one line in this form: LOG | chat=<this chat id> | tab=Tab{1} | folder=coordination/{0}/Tab{1}_<purpose>/ | commit=<latest log commit> | issue=<owning issue> | plan=<new plan revision> | ac=<criteria met>/<total> | release=<HOLD or its state> | handover=ready:<report path>. Then stop: start no new work in this chat.'
)
function ToMin($s) { $m = 0.0; if ($s -match '(\d+)\s*h') { $m += 60 * [double]$Matches[1] }; if ($s -match '(\d+)\s*m(?!s)') { $m += [double]$Matches[1] }; if ($s -match '(\d+)\s*s') { $m += [double]$Matches[1] / 60 }; [Math]::Round($m, 1) }
function Get-Line($t, $id) { $m = [regex]::Match($t, '(?m)^[ \t]*"claude_code_hw_' + $id + '":[ \t]*(\{.*\}),?[ \t]*\r?\n?'); if ($m.Success) { $m } else { $null } }
function New-Rec { [pscustomobject]@{ id = $Id; actAt = ''; lastState = ''; unknown = ''; nudgeTurn = -1; fLine = ''; prevId = ''; nextId = ''; aLane = ''; bRev = ''; bPrompt = ''; fHr = ''; url = ''; title = ''; buddy = ''; bSent = 0; bTry = 0; bNeed = 0; bPub1 = ''; bPub2 = ''; bAss = ''; bWhy = ''; bV = ''; aPub = ''; yLast = ''; pStage = ''; sentWhat = ''; evChat = 0; yDec = ''; costK = 0.0; costDay = ''; seenK = @(); doneHist = @(); planSeen = @(); fAim = ''; fOut = ''; fUser = ''; userNoN = 0; aimSends = 0; aimIntro = ''; judgeKeys = @(); repo = ''; ciHeads = @(); ciLimSent = ''; firstAt = $now; last3 = @(); sumMin = 0.0; sumPages = 0.0; turns = 0; soft = @(); hard = ''; hint = ''; redSent = ''; bAt = ''; bMed = 0.0; bAfter = @(); folder = ''; lastLog = ''; gen = 0; rcn = 0; reconMode = ''; reconDate = ''; pd = -1; pt = -1; aca = -1; act = -1; dPd = 0; dAc = 0; noProg = 0; evN = 0; evLast = 0; lastSeen = ''; evSince = 0; ckAt = 0; soonSent = ''; heavySent = ''; driftTurn = -1; planDoneAt = ''; lastTp = 0; lastTp2 = 0; fresh = $false; redN = 0; ciSent = ''; fixSent = ''; rcAsk = ''; lastBk = ''; prState = ''; lastTests = ''; fPlan = ''; fDone = ''; fNext = ''; fRel = ''; fBk = ''; fBr = ''; fHv = ''; fPr = ''; fTests = ''; fMissing = ''; fHead = ''; fProof = ''; stale = ''; footAsk = ''; lastKind = ''; parkAt = ''; pingAt = ''; parkWhy = '' } }
function Load-Rec {
  $m = Get-Line $text $Id; if (-not $m) { return New-Rec }
  $r = $m.Groups[1].Value | ConvertFrom-Json
  $def = @{ actAt = ''; lastState = ''; unknown = ''; nudgeTurn = -1; fLine = ''; prevId = ''; nextId = ''; aLane = ''; bRev = ''; bPrompt = ''; fHr = ''; url = ''; title = ''; buddy = ''; bSent = 0; bTry = 0; bNeed = 0; bPub1 = ''; bPub2 = ''; bAss = ''; bWhy = ''; bV = ''; aPub = ''; yLast = ''; pStage = ''; sentWhat = ''; evChat = 0; yDec = ''; costK = 0.0; costDay = ''; seenK = @(); doneHist = @(); planSeen = @(); fAim = ''; fOut = ''; fUser = ''; userNoN = 0; aimSends = 0; aimIntro = ''; judgeKeys = @(); repo = ''; ciHeads = @(); ciLimSent = ''; sumPages = 0.0; hint = ''; redSent = ''; hard = ''; bAt = ''; bMed = 0.0; bAfter = @(); folder = ''; lastLog = ''; gen = 0; rcn = 0; reconMode = ''; reconDate = ''; pd = -1; pt = -1; aca = -1; act = -1; dPd = 0; dAc = 0; noProg = 0; evN = 0; evLast = 0; lastSeen = ''; evSince = 0; ckAt = 0; soonSent = ''; heavySent = ''; driftTurn = -1; planDoneAt = ''; lastTp = 0; lastTp2 = 0; fresh = $false; redN = 0; ciSent = ''; fixSent = ''; rcAsk = ''; lastBk = ''; prState = ''; lastTests = ''; fPlan = ''; fDone = ''; fNext = ''; fRel = ''; fBk = ''; fBr = ''; fHv = ''; fPr = ''; fTests = ''; fMissing = ''; fHead = ''; fProof = ''; stale = ''; footAsk = ''; lastKind = ''; parkAt = ''; pingAt = ''; parkWhy = '' }
  foreach ($k in $def.Keys) { if (-not $r.PSObject.Properties[$k]) { $r | Add-Member -NotePropertyName $k -NotePropertyValue $def[$k] } }
  $r
}
function Set-Other($oid, $kv) {
  # v3.22: the two chats of a Buddy lane point to each other (prevId / nextId) and the outgoing chat has its own lane state (aLane).
  if (-not $oid) { return }
  $t0 = [IO.File]::ReadAllText($StateFile, $utf8); $mo = Get-Line $t0 $oid; if (-not $mo) { return }
  $o = $mo.Groups[1].Value | ConvertFrom-Json
  foreach ($k in $kv.Keys) { if ($o.PSObject.Properties[$k]) { $o.$k = $kv[$k] } else { $o | Add-Member -NotePropertyName $k -NotePropertyValue $kv[$k] } }
  $t1 = $t0.Replace($mo.Groups[1].Value, (ConvertTo-Json -InputObject $o -Depth 6 -Compress)); try { [void]($t1 | ConvertFrom-Json) } catch { return }
  $res = Commit-Diff $StateFile $t0 $t1; if ($res) { $script:text = $res; $script:diskText = $res }
}
function Set-AimField($work, $field, $value) {
  # v3.28: a delivered AIM_NEW / GROUND_AIM clears the work's groundDue flag (aim.ps1 sets it).
  $t0 = [IO.File]::ReadAllText($StateFile, $utf8); $m = [regex]::Match($t0, '(?m)^[ \t]*"claude_code_aim_' + [regex]::Escape($work) + '":[ \t]*(\{.*\}),?[ \t]*\r?$'); if (-not $m.Success) { return }
  $o = $m.Groups[1].Value | ConvertFrom-Json; if ($o.PSObject.Properties[$field]) { $o.$field = $value } else { $o | Add-Member -NotePropertyName $field -NotePropertyValue $value }
  $t1 = $t0.Replace($m.Groups[1].Value, (ConvertTo-Json -InputObject $o -Depth 8 -Compress)); try { [void]($t1 | ConvertFrom-Json) } catch { return }
  $res = Commit-Diff $StateFile $t0 $t1; if ($res) { $script:text = $res; $script:diskText = $res }
}
function Med($vals) { $s = @($vals | Where-Object { $_ -gt 0 } | Sort-Object); if ($s.Count) { $s[[int][Math]::Floor($s.Count / 2)] } else { $null } }
function Save-Rec($r) {
  $line = '"claude_code_hw_' + $Id + '": ' + (ConvertTo-Json -InputObject $r -Depth 6 -Compress) + ','
  $m = Get-Line $text $Id; $new = $text
  if ($m) { $new = $new.Replace($m.Value, '') }
  if (-not $new.Contains($anchor)) { 'anchor missing - nothing written'; return $false }
  $new = $new.Replace($anchor, $line + "`n  " + $anchor)
  try { [void]($new | ConvertFrom-Json) } catch { 'bad json - nothing written'; return $false }
  $res = Commit-Diff $StateFile $diskText $new; if ($null -eq $res) { 'state file busy or invalid - nothing written'; return $false }; $script:text = $res; $script:diskText = $res; return $true
}
function Recent($r) { @($r.soft | Where-Object { $_ -and ((Get-Date) - [datetime]::Parse(($_ -split '\|')[0], $inv)).TotalMinutes -le 60 }) }
function Last3($lab) { [Math]::Round([double](@($lab | ForEach-Object { ToMin $_ }) | Measure-Object -Sum).Sum, 1) }
function MapFolder($pos) {
  # v3.19: the tab map (cyclestate.ps1 map) says which stream folder belongs at this position; folders are never renamed, so the map is the truth.
  if (-not $Session -or -not $pos) { return '' }
  $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return '' }
  foreach ($e in @(($mm.Groups[1].Value | ConvertFrom-Json).map)) { if ($e) { $q = $e -split '\|'; if ($q[0] -eq "$pos") { return [string]$q[2] } } }
  ''
}
function SeenAt($pos) {
  # v3.20 audit: Checked belongs to the tab POSITION (cyclestate seen), so it survives a new chat; the chat's own lastSeen is the fallback.
  if (-not $Session -or -not $pos) { return '' }
  $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return '' }
  foreach ($e in @(($mm.Groups[1].Value | ConvertFrom-Json).seen)) { if ($e) { $q = $e -split '\|'; if ($q[0] -eq "$pos" -and $q.Count -ge 3) { return [string]$q[2] } } }
  ''
}
function MapInfo($pos, $chat) {
  # v3.20 identity check against the tab map, the same kind of detection as STALE (Owner, 11 Oct: "think of how to wire with stale logics"):
  # '' = the map knows this chat at this position (or there is no map yet); 'new' = a chat the map does not know (an ad hoc tab, or a chat change not recorded);
  # 'shifted:<Q>' = the map has this chat at position Q (a tab was inserted or closed before it).
  if (-not $Session -or -not $pos) { return '' }
  $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return '' }
  $ents = @(@(($mm.Groups[1].Value | ConvertFrom-Json).map) | Where-Object { $_ } | ForEach-Object { , @($_ -split '\|') })
  if ($ents.Count -eq 0) { return '' }
  foreach ($q in $ents) { if ($q[0] -eq "$pos" -and $q[1] -eq $chat) { return '' } }
  foreach ($q in $ents) { if ($q[1] -eq $chat) { return 'shifted:' + $q[0] } }
  # v3.22: during a Buddy lane the tab switches between the two links of one work (Owner-approved): the mapped chat's predecessor is known here.
  foreach ($q in $ents) { if ($q[0] -eq "$pos" -and $q[1]) { $pm = Get-Line $text $q[1]; if ($pm) { $po = $pm.Groups[1].Value | ConvertFrom-Json; if ($po.prevId -eq $chat) { return '' } } } }
  'new'
}
function MapName($pos) {
  if (-not $Session -or -not $pos) { return '' }
  $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return '' }
  foreach ($e in @(($mm.Groups[1].Value | ConvertFrom-Json).map)) { if ($e) { $q = $e -split '\|'; if ($q[0] -eq "$pos") { return [string]$q[3] } } }
  ''
}
function MapLearn($t0, $pos, $folder, $chat) {
  # v3.20 (Owner, 11 Oct: "New tab, how tab status should be wired"): a tab with no folder in the map takes it from its first footer; a folder already in the map is never overwritten (that case is TAB_MOVED).
  $mm = [regex]::Match($t0, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return $t0 }
  $c = $mm.Groups[1].Value | ConvertFrom-Json; if (-not $c.PSObject.Properties['map']) { $c | Add-Member -NotePropertyName map -NotePropertyValue @() }
  $hit = $false; $lst = @()
  foreach ($e in @($c.map | Where-Object { $_ })) { $q = @($e -split '\|'); while ($q.Count -lt 5) { $q += '' }; if ($q[0] -eq "$pos") { $hit = $true; if (-not $q[2]) { $q[2] = $folder }; if (-not $q[1]) { $q[1] = $chat } }; $lst += ($q -join '|') }
  if (-not $hit) { $lst += ('{0}|{1}|{2}|Tab{0}|{3}' -f $pos, $chat, $folder, $now) }
  $c.map = $lst
  $t0.Replace($mm.Groups[1].Value, (ConvertTo-Json -InputObject $c -Depth 5 -Compress))
}
function RepoVis($repo, [switch]$CacheOnly) {
  # v3.27 (Owner, 11 Oct 21:0x: the CI text "only if private repo"; "limit CI runs (highlight in tab status)"): private / public / '' (unknown), cached a day
  # under claude_code_repo_<name>. -RepoVis 'owner/repo=private;...' answers without the network (tests). The check is a read-only GitHub API call.
  if (-not $repo) { return '' }
  foreach ($kv in ($RepoVis -split '[;,]' | Where-Object { $_ -match '=' })) { $q = $kv -split '=', 2; if ($q[0].Trim() -eq $repo) { return $q[1].Trim() } }
  $key = 'claude_code_repo_' + ($repo -replace '[^A-Za-z0-9_]', '_')
  $mm = [regex]::Match($text, '(?m)^[ \t]*"' + $key + '":[ \t]*(\{.*\})')
  if ($mm.Success) { $c = $mm.Groups[1].Value | ConvertFrom-Json; if ($CacheOnly -or ((Get-Date) - [datetime]::Parse($c.at, $inv)).TotalHours -lt 24) { return [string]$c.vis } }
  if ($CacheOnly) { return '' }
  $vis = ''
  try { if (Get-Command gh -ErrorAction SilentlyContinue) { $o = (& gh api ('repos/' + $repo) --jq '.private' 2>$null); if ($o -eq 'true') { $vis = 'private' } elseif ($o -eq 'false') { $vis = 'public' } } } catch { }
  if (-not $vis) { try { $w0 = Invoke-WebRequest -UseBasicParsing -Uri ('https://api.github.com/repos/' + $repo) -TimeoutSec 8 -ErrorAction Stop; $vis = $(if (($w0.Content | ConvertFrom-Json).private) { 'private' } else { 'public' }) } catch { if ($_.Exception.Response -and [int]$_.Exception.Response.StatusCode -eq 404) { $vis = 'private' } } }
  if ($vis) { $line = '"' + $key + '": ' + (ConvertTo-Json -InputObject ([ordered]@{ repo = $repo; vis = $vis; at = $now }) -Compress) + ','; $t2 = $text; $m2 = [regex]::Match($t2, '(?m)^[ \t]*"' + $key + '":[^\r\n]*\r?\n?'); if ($m2.Success) { $t2 = $t2.Remove($m2.Index, $m2.Length) }; $t2 = $t2.Replace($anchor, $line + "`n  " + $anchor); $res = Commit-Diff $StateFile $diskText $t2; if ($res) { $script:text = $res; $script:diskText = $res } }
  $vis
}
function ModeOf($pos, $r) {
  # v3.26 (Owner, 11 Oct 20:0x-20:1x): per-tab mode. Speed for a chat's first 5 task evidence, then Economy, unless the Owner set it (cyclestate mode);
  # coder RC / NC from the Owner's per-tab setting or the session mode; handover 'hold' = no 1a request until the Owner says.
  $o = @{ speed = $(if ([int]$r.evChat -lt 5) { 'speed' } else { 'economy' }); coder = 'RC'; hold = ''; set = '' }
  if (-not $Session) { return $o }
  $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return $o }
  $c = $mm.Groups[1].Value | ConvertFrom-Json
  if ($c.mode -eq 'NON_CODER') { $o.coder = 'NC' }
  if ($c.PSObject.Properties['modes']) { foreach ($e in @($c.modes)) { if ($e) { $q = @($e -split '\|'); while ($q.Count -lt 4) { $q += '' }; if ($q[0] -eq "$pos") { if ($q[1]) { $o.speed = $q[1]; $o.set = 'Owner' }; if ($q[2]) { $o.coder = $q[2] }; $o.hold = $q[3] } } } }
  $o
}
function Badge($md) { $(if ($md.speed -eq 'speed') { [string][char]0x26A1 } else { [char]::ConvertFromUtf32(0x1F422) }) + ' ' + $md.coder + $(if ($md.hold -eq 'hold') { ' ' + [char]::ConvertFromUtf32(0x270B) + 'hold' } else { '' }) }
function MapSetChat($t0, $pos, $chat) {
  # v3.25: the work at this position continues in a new chat (carry): the map line keeps its folder and name, takes the new chat and the time.
  $mm = [regex]::Match($t0, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
  if (-not $mm.Success) { return $t0 }
  $c = $mm.Groups[1].Value | ConvertFrom-Json; if (-not $c.PSObject.Properties['map']) { $c | Add-Member -NotePropertyName map -NotePropertyValue @() }
  $hit = $false; $lst = @()
  foreach ($e in @($c.map | Where-Object { $_ })) { $q = @($e -split '\|'); while ($q.Count -lt 5) { $q += '' }; if ($q[0] -eq "$pos") { $hit = $true; $q[1] = $chat; $q[4] = $now }; $lst += ($q -join '|') }
  if (-not $hit) { $lst += ('{0}|{1}||Tab{0}|{2}' -f $pos, $chat, $now) }
  $c.map = $lst
  $t0.Replace($mm.Groups[1].Value, (ConvertTo-Json -InputObject $c -Depth 5 -Compress))
}
function Verdict($r, $lab) {
  $reconText = $null
  $mins = @($lab | ForEach-Object { ToMin $_ } | Where-Object { $_ -gt 0 } | Sort-Object)
  $batch = '1'; $med = $null
  if ($mins.Count) {
    $med = $mins[[int][Math]::Floor($mins.Count / 2)]; $n = [Math]::Floor($Target / [Math]::Max(0.5, $med))
    $hi = [Math]::Min(5, [Math]::Max(1, $n - 1)); $lo = [Math]::Min($hi, [Math]::Max(1, $n - 2))
    $batch = $(if ($hi -le 1) { '1' } elseif ($lo -eq $hi) { "$hi" } else { "$lo-$hi" })
  }
  $l3 = Last3 $lab; $wt = ($r.parkAt -or (@('OWNER', 'PERSON', 'EXTERNAL') -contains [string]$r.fBk) -or $r.fHv -eq 'ready'); $red = ($lab.Count -ge 3 -and $l3 -lt $RedMin -and -not $wt)  # v3.20 (Owner, 11 Oct "red flag now ... why?"): short replies while the agent waits on a person, is parked or has a ready brief are expected, not a red flag
  # v3.13 (Owner, 11 Oct 06:4x: "3rd agent chain is missing in metric", "3 turns - is it traceable", "no planned progress ... should be wired with metrics"):
  # the meter shows every number a trigger uses: the agent number, the three Worked-for turns, and progress / AC from the status line with replies since either moved.
  $turns = (@($lab | ForEach-Object { '{0}m' -f (ToMin $_) }) -join ' + ')
  $prog = $(if ([int]$r.pd -ge 0) { 'progress {0}/{1} ({2:+0;-0;+0})' -f $r.pd, $(if ([int]$r.pt -ge 0) { $r.pt } else { '?' }), [int]$r.dPd } else { 'progress -' })
  $acs = $(if ([int]$r.aca -ge 0) { 'AC {0}/{1} ({2:+0;-0;+0})' -f $r.aca, $(if ([int]$r.act -ge 0) { $r.act } else { '?' }), [int]$r.dAc } else { 'AC -' })
  'METER {0}: agent {1} | {2:N0} min worked, {3:N0} pages | last 3 turns = {4} = {5} min{6} | {7}, {8}, evidence {10} (+{11}), no planned progress for {9} replies' -f $Id, $(if ([int]$r.gen -gt 0) { 'g' + $r.gen } else { 'g?' }), [double]$r.sumMin, [double]$r.sumPages, $(if ($turns) { $turns } else { '-' }), $l3, $(if ($red) { ' RED FLAG' } else { '' }), $prog, $acs, [int]$r.noProg, [int]$r.evN, [int]$r.evLast
  if ([int]$r.noProg -ge 3) { 'STALL_DUE {0}: progress and AC unchanged for {1} replies (rule: 3) - send the reconcile (status.ps1 RECONCILE text) unless the chat only waits for the Owner' -f $Id, [int]$r.noProg }
  # v3.26 (Owner, 11 Oct: "not always [bigger batches], check the response quality in the 5th Y, then decide"): Speed asks 1-2 tasks; Economy asks 4-5 only after
  # a Y said CONTINUE / NO_CHANGE, and stays at 1-2 after CORRECT, VERIFY_FIRST or BLOCKED; with no Y yet the median rule stands.
  $md = ModeOf $Pos $r
  if ($md.speed -eq 'speed') { $batch = '1-2' } elseif ($r.yDec -match '^(CONTINUE|NO_CHANGE)') { $batch = '4-5' } elseif ($r.yDec) { $batch = '1-2' }
  'BATCH {0} {1} (median worked {2}, target {3}m; mode {4}{5})' -f $Id, $batch, $(if ($null -ne $med) { "$($med)m" } else { 'unknown' }), $Target, (Badge $md), $(if ($r.yDec) { ', last Y ' + $r.yDec } else { '' })
  if ($r.bAt) { $aft = @($r.bAfter); $ma = Med $aft; 'BATCH_EFFECT {0}: median worked {1}m before the first batch message ({2}), {3} after it over {4} turns' -f $Id, $r.bMed, $r.bAt, $(if ($null -ne $ma) { "$($ma)m" } else { 'none yet' }), $aft.Count }
  $why = ''
  if ($r.hard -eq 'conversation length limit') { 'LIMIT {0}: the chat is full - no H1 in this chat; tell the Owner, keep its URL (urls.ps1 mark LIMIT); a new chat needs the Owner or a report already given' -f $Id }
  elseif ($r.hard) { $why = $r.hard }
  elseif ([double]$r.sumMin -ge 0.95 * $MaxMin) { $why = 'cum working time {0:N1} min (rule: {1}; 95 % counts as reached, the handover needs the next turns)' -f [double]$r.sumMin, $MaxMin }
  elseif ([double]$r.sumPages -ge 0.95 * $MaxPages) { $why = 'cum pages {0:N1} (rule: {1}; 95 % counts as reached, the handover needs the next turns)' -f [double]$r.sumPages, $MaxPages }
  elseif ([int]$r.turns -ge $MaxTurns) { $why = '{0} turns (rule: {1} or more; turns predict a full chat best, Owner analysis 11 Oct)' -f [int]$r.turns, $MaxTurns }
  $sess = $(if ($r.folder -match '^(.+)/') { $Matches[1] } else { '' })
  $expF = MapFolder $Pos; $movedNow = ($expF -and $r.folder -and [string]$r.folder -ne $expF)
  if ($r.stale) { 'STALE {0}: the footer names chat {1}, not this chat - ignored this cycle' -f $Id, $r.stale }
  if ($r.unknown -eq 'new') { 'UNKNOWN_TAB {0}: tab {1} holds a chat the tab map does not know - send nothing; ask the Owner once (Needs you: "new tab {1}: which work, or not mine?"), then onboard.ps1 or NEW-CHAT' -f $Id, $Pos }
  if ($r.unknown -like 'shifted:*') { 'TAB_SHIFTED {0}: the map has this chat at tab {1}, it is now at tab {2} - send nothing; report "tabs shifted: confirm the new order?" and update the map on the Owner''s word' -f $Id, ($r.unknown -split ':')[1], $Pos }
  if ($movedNow) { 'TAB_MOVED {0}: its footer folder is {1} but the tab map has {2} at tab {3} - send nothing to this tab, tell the Owner and wait for their word (or update the map: cyclestate.ps1 map)' -f $Id, $r.folder, $expF, $Pos }

  elseif ($r.folder) { 'LOG {0}: {1}{2}' -f $Id, $r.folder, $(if ($r.lastLog) { ' @ ' + $r.lastLog } else { '' }) }
  # v3.11 reconciliation sequence: the 3rd agent of a tab and every 3rd after it (or the Owner's "recon tab N"); it replaces the soft handover trigger.
  $isRecon = ($r.reconMode -eq 'on')  # v3.21: Buddy at every handover replaces the automatic RECON of every 3rd agent; RECON only on the Owner's 'recon tab N'
  if ($isRecon -and [int]$r.rcn -lt 4 -and -not $r.hard) {
    $go = ([int]$r.rcn -ge 1) -or ($r.reconMode -eq 'on') -or ([double]$r.sumPages -ge $ReconPages) -or ([double]$r.sumMin -ge $ReconMin)
    if ($go) {
      $k = [int]$r.rcn + 1; $d = $(if ($r.reconDate) { $r.reconDate } else { (Get-Date).ToString('yyyy-MM-dd', $inv) })
      'RECON_DUE {0}: step {1} of 4 (agent {2}{3}) - send it on this idle turn instead of a nudge or H1, then -Action recon -Id {0} -Mode sent -Step {1}' -f $Id, $k, $(if ([int]$r.gen -gt 0) { 'g' + $r.gen } else { 'number unknown' }), $(if ($r.reconMode -eq 'on') { ', ordered by the Owner' } else { '' })
      $reconText = ($RECON[$k - 1] -f $(if ($Session) { $Session } else { '<session folder>' }), $(if ($Pos) { $Pos } else { '<N>' }), $d)
    }
    else { 'RECON {0}: agent g{1}: the reconciliation sequence starts at {2} pages or {3} min worked' -f $Id, $r.gen, $ReconPages, $ReconMin }
    $why = ''
  }
  elseif ($isRecon -and [int]$r.rcn -ge 4 -and -not $r.hard) {
    'RECON {0}: all 4 steps sent; RECON 4 is the handover prompt (no H1): when the probe stage is REPORT_READY, move the brief (recipe HANDOVER H3b, then H3 steps 3 to 7)' -f $Id
    $why = ''
  }
  $held = ($md.hold -eq 'hold')
  if ($why -and $held) { 'HANDOVER_HELD {0}: {1} - the Owner holds the handover for this tab: no 1a request{2}' -f $Id, $why, $(if ([double]$r.sumPages -ge 27) { '; NEAR FULL at {0:N0} pages: ask the Owner once (Needs you)' -f [double]$r.sumPages } else { '' }); $why = '' }
  if ($why) { 'HANDOVER_DUE {0}: {1} - plan for handover: recipe HANDOVER H1 on the next idle turn, with the row 8b checks (ho, scan, ledger); never twice' -f $Id, $why }
  if ($red -and -not $r.redSent) { 'RED_FLAG {0}: the last 3 turns worked {1} min in total (under {2}): send the grounding prompt (recipe HANDOVER H4 text) once, then -Action grounded' -f $Id, $l3, $RedMin }
  if ($r.hint) { 'NOTE {0}: the agent hints at a handover: {1}' -f $Id, $r.hint }
  $soft = @(Recent $r); if ($soft.Count) { 'NOTE {0}: {1} within 60 minutes' -f $Id, (@($soft | ForEach-Object { ($_ -split '\|')[1] }) -join ', ') }
  if ([int]$r.dAc -gt 0 -and $r.fresh) { 'MILESTONE {0}: AC +{1}, now {2}/{3} - report it to the Owner' -f $Id, [int]$r.dAc, $r.aca, $(if ([int]$r.act -ge 0) { $r.act } else { '?' }) }
  # v3.17 (Owner, 11 Oct 07:4x: "wire these with triggers, e.g. task evidence count with 5/10/15 logic; what else can we?"): ONE action per tab, highest priority first.
  # The exact text follows as SEND; after DELIVERED run the MARK line (so it is not sent twice). NONE = the tab's normal route decides (status.ps1 / evidence.ps1 / rows 9-12).
  $hasSt = ([int]$r.pd -ge 0 -or [int]$r.aca -ge 0)
  $near = ([double]$r.sumMin -ge 0.8 * $MaxMin -or [double]$r.sumPages -ge 0.8 * $MaxPages -or [int]$r.turns -ge ($MaxTurns - 1))
  $moved = $movedNow
  $ckList = $(if ($md.speed -eq 'speed') { @(5, 10, 15, 19) } else { @(5, 10) })  # v3.26 (Owner): Economy runs Y at 5 and 10 only
  $ckNext = @($ckList | Where-Object { $_ -gt [int]$r.ckAt })[0]; if (-not $ckNext) { $ckNext = 0 }
  $ciAct = $null
  $vis = RepoVis $r.repo
  if ([int]$r.redN -ge 2) {
    # v3.27 (Owner): the CI text only for a PRIVATE repository (paid Actions minutes); a public repository's CI wait is reported, not answered with it.
    if ($r.lastBk -eq 'CI' -or $r.prState -match '^(queued|not-run|none)$') { if ($vis -eq 'private' -and -not $r.ciSent) { $ciAct = @('CI', ('CI red in {0} replies in a row, CI named as the blocker, private repository {1}' -f [int]$r.redN, $r.repo), $T_CI, 'mark -What ci') } elseif ($vis -ne 'private') { 'NOTE {0}: CI not green in {1} replies, but {2} is {3}: no CI text (Owner: only for private repositories)' -f $Id, [int]$r.redN, $(if ($r.repo) { $r.repo } else { 'the repository' }), $(if ($vis) { $vis } else { 'not known (no repository in the footer)' }) } }
    elseif ($r.lastBk -eq 'MACHINE' -and -not $r.rcAsk) { $ciAct = @('RC_ASK', ('tests red in {0} replies and the agent cannot run them itself: recipe RC, ask the Owner first' -f [int]$r.redN), '', 'mark -What rc') }
    elseif ($r.lastBk -notin 'CI', 'MACHINE' -and -not $r.fixSent) { $ciAct = @('FIX_FIRST', ('tests or PR checks red in {0} replies in a row ({1})' -f [int]$r.redN, $(if ($r.lastTests) { 'tests ' + $r.lastTests } else { 'PR ' + $r.prState })), ($T_FIX -f $(if ($r.lastTests) { $r.lastTests } else { 'PR checks ' + $r.prState })), 'mark -What fix') }
  }
  # v3.27 (Owner: "limit CI runs (highlight in tab status)"): a private repository with 4 or more CI heads (PR@sha) today gets one reminder.
  $ciN = @($r.ciHeads | Where-Object { $_ -like ((Get-Date).ToString('yyyy-MM-dd', $inv) + '|*') }).Count
  if (-not $ciAct -and $vis -eq 'private' -and $ciN -ge 4 -and $r.ciLimSent -ne (Get-Date).ToString('yyyy-MM-dd', $inv)) { $ciAct = @('CI_LIMIT', ('private repository {0}: {1} CI runs today' -f $r.repo, $ciN), ($T_CILIM -f $ciN), 'mark -What cilimit') }
  $act = $null; $mn = [string](MapName $Pos); $v16 = ($r.bV -eq '16')
  # v3.25 (Owner, 11 Oct snap 1): a tab the Owner marked [OUT] (not in my scope) or [HOLD] in the tab map gets no trigger and no send at all.
  if ($mn.StartsWith('[OUT]')) { $act = @('OUT_OF_SCOPE', 'the Owner marked this tab not in my scope: no trigger, send nothing', '', '') }
  elseif ($mn.StartsWith('[HOLD]')) { $act = @('ON_HOLD', 'the Owner put this tab on hold: no trigger, send nothing', '', '') }
  elseif ($r.hard -eq 'conversation length limit') { $act = @('LIMIT', 'the chat is full: tell the Owner', '', '') }
  elseif ($r.unknown -like 'shifted:*') { $act = @('TAB_SHIFTED', ('the map has this chat at tab {0}: the tab order changed; confirm with the Owner' -f ($r.unknown -split ':')[1]), '', '') }
  elseif ($r.unknown -eq 'new') { $act = @('UNKNOWN_TAB', 'a chat the tab map does not know: ask the Owner which work', '', '') }
  elseif ($moved) { $act = @('TAB_MOVED', 'the tab order changed: tell the Owner', '', '') }
  elseif ($r.buddy -eq 'blocked') { $act = @('BUDDY_BLOCKED', ('Buddy lane stopped: {0}. Send nothing more to this tab; tell the Owner (information, not a decision)' -f $r.bWhy), '', '') }
  elseif ($r.buddy -and $r.buddy -ne 'done') {
    switch ($r.buddy) {
      'due' { $act = @('BUDDY_S1', $(if ($v16) { 'new chat of ongoing work: BuddyRunner v1.6 response 1b first (G2 investigates once)' } else { 'new chat of ongoing work: BuddyRunner v1.5 Stage 1 first (read-only purpose reconstruction)' }), $(if ($r.bPrompt) { '(onboard.ps1 -Case TAKEOVER -Id {0} -Prompt ''{1}'' -Gen {2})' -f $Id, $r.bPrompt, [int]$r.gen } else { '(onboard.ps1 -Case TAKEOVER: no 1a, the case packet)' }), 'mark -What buddy1') }
      's1ok' {
        $ao = $null; if ($r.prevId) { $am = Get-Line ([IO.File]::ReadAllText($StateFile, $utf8)) $r.prevId; if ($am) { $ao = $am.Groups[1].Value | ConvertFrom-Json } }
        if ($ao -and $ao.hard -ne 'conversation length limit') { $act = @('BUDDY_A_REVIEW', $(if ($v16) { '1b published: {0}. G1 {1} now writes response 2 (final direction, workpack, 12-section handover) and closes' -f $r.bPub1, $r.prevId } else { 'Stage 1 published: {0}. The outgoing agent {1} reviews it first (Stage 1 reconciliation = the Stage 2 input)' -f $r.bPub1, $r.prevId }), ('(switch the tab to {0}; onboard.ps1 -Case A2 -Gen {4} -Next {1} -Pub ''{2}'' -Assessed ''{3}'')' -f $(if ($ao.url) { $ao.url } else { $r.prevId }), $Id, $r.bPub1, $r.bAss, [int]$ao.gen), 'mark -What areview') }
        elseif ($v16) { $r.buddy = 'blocked'; $r.bWhy = 'G1 cannot write response 2 (no record of it, or its chat is full); v1.6 has no Stage 2 for G2'; $act = @('BUDDY_BLOCKED', ('Buddy lane stopped: {0}. Send nothing more to this tab; tell the Owner (information, not a decision)' -f $r.bWhy), '', '') }
        else { $act = @('BUDDY_S2', ('Stage 1 published: {0}; the outgoing agent cannot review (no record or its chat is full): Stage 2 without its review' -f $r.bPub1), ('(onboard.ps1 -Case BUDDY2 -Pub ''{0}'' -Assessed ''{1}'')' -f $r.bPub1, $r.bAss), 'mark -What buddy2') }
      }
      'areview' {
        $ao = $null; if ($r.prevId) { $am = Get-Line ([IO.File]::ReadAllText($StateFile, $utf8)) $r.prevId; if ($am) { $ao = $am.Groups[1].Value | ConvertFrom-Json } }
        if ($ao -and ($ao.aLane -eq 's2ready' -or $ao.fHv -eq 's2ready') -and $ao.fHr) {
          $r.bRev = [string]$ao.fHr
          # v3.25: under v1.6 G1's response 2 closes the handover; the successor only starts the workpack (no Stage 2). A v1.5 lane finishes with its Stage 2 (F5).
          if ($v16) { if ($ao.PSObject.Properties['aPub'] -and $ao.aPub) { $r.bPub2 = [string]$ao.aPub }; $act = @('BUDDY_START', ('G1 closed the handover with response 2: {0}' -f $r.bRev), ('(onboard.ps1 -Case BSTART -Id {0} -Review ''{1}''{2})' -f $Id, $r.bRev, $(if ($r.bPub2) { ' -Pub ''' + $r.bPub2 + '''' } else { '' })), 'mark -What bstart') }
          else { $act = @('BUDDY_S2', ('the outgoing agent reviewed Stage 1: {0}' -f $r.bRev), ('(onboard.ps1 -Case BUDDY2 -Review ''{0}'' -Pub ''{1}'' -Assessed ''{2}'')' -f $r.bRev, $r.bPub1, $r.bAss), 'mark -What buddy2') }
        }
        else { $act = @('BUDDY_WAIT', $(if ($v16) { 'waiting for G1 {0} to write response 2 (probe it on its link)' -f $r.prevId } else { 'waiting for the outgoing agent {0} to review Stage 1 (probe it on its link)' -f $r.prevId }), '', '') }
      }
      default {
        if ([int]$r.bNeed -gt 0 -and [int]$r.bTry -lt 1) { $act = @('BUDDY_PUBLISH', ('Stage {0} reply without a verified publication ({1})' -f $r.bNeed, $r.bWhy), ($T_BPUB -f $r.bNeed, $r.bWhy), 'mark -What bpub') }
        elseif ([int]$r.bNeed -gt 0) { $r.buddy = 'blocked'; $r.bWhy = ('Stage {0} still not published after one ask ({1})' -f $r.bNeed, $r.bWhy); $act = @('BUDDY_BLOCKED', ('Buddy lane stopped: {0}. Send nothing more to this tab; tell the Owner (information, not a decision)' -f $r.bWhy), '', '') }
        else { $act = @('BUDDY_WAIT', $(if ($v16) { 'Buddy 1b is running: no nudge, no other trigger until its reply' } else { 'Buddy Stage {0} is running: no nudge, no other trigger until its reply' -f $(if ($r.buddy -eq 's2') { 2 } else { 1 }) }), '', '') }
      }
    }
  }
  elseif ($r.aLane -in 'asked', 'moved', 'review', 's2ready') {
    if ($r.aLane -eq 'asked' -and $r.fHv -eq 'ready' -and $r.fHr -and -not $r.stale) { $act = @('BRIEF_READY', ('G1 wrote artifact 1a {0} and holds: open a new chat in this tab and send the 1b pointer' -f $r.fHr), ('(recipe BUDDY B1: New chat; onboard.ps1 -Case TAKEOVER -Id new -Prompt ''{0}'' -Gen {1})' -f $r.fHr, ([int]$r.gen + 1)), '') }
    elseif ($r.aLane -eq 'review' -and $r.fHv -eq 's2ready' -and $r.fHr) { $r.aLane = 's2ready'; $act = @('A_REVIEW_READY', ('G1''s answer is in: {0}. Switch the tab to its successor {1}; the successor''s ACTION says what to send' -f $r.fHr, $r.nextId), '', '') }
    elseif ($r.aLane -in 'asked', 'review') { $act = @('A_WAIT', $(if ($r.aLane -eq 'asked') { 'G1 is writing artifact 1a (then it holds)' } else { 'G1 is writing response 2 (a v1.5 lane: its Stage 1 review)' }), '', '') }
    else { $act = @('A_HOLD', ('G1 of a Buddy lane (successor {0}): it holds, no nudge; it writes response 2 after the successor''s 1b' -f $r.nextId), '', '') }
  }
  elseif ($r.fHv -eq 'ready' -and -not $r.stale) { $act = @('BRIEF_READY', 'the footer says handover=ready: move the brief to a new chat this cycle (runbook G: a ready brief is never a question)', '(recipe HANDOVER H3, then NEW-CHAT with carry)', '') }
  elseif ($reconText) { $act = @('RECON', ('reconciliation step {0} of 4 (agent g{1})' -f ([int]$r.rcn + 1), $r.gen), $reconText, ('recon -Mode sent -Step ' + ([int]$r.rcn + 1))) }
  elseif ($why -and -not $r.aLane) { $act = @('HANDOVER', $why, '(onboard.ps1 -Case A1: G1 writes artifact 1a, the successor''s prompt, then holds; recipe BUDDY B0)', 'mark -What a1') }
  elseif ($red -and -not $r.redSent) { $act = @('GROUND', ('the last 3 turns worked {0} min (under {1})' -f $l3, $RedMin), '(recipe HANDOVER H4 text)', 'grounded') }
  elseif ($r.parkAt) {
    $since = $(if ($r.pingAt) { $r.pingAt } else { $r.parkAt }); $mins = ((Get-Date) - [datetime]::Parse($since, $inv)).TotalMinutes
    if ($mins -ge $Cycle - 1) { $act = @('PING', ('parked since {0} ({1}); one ping per cycle' -f ([datetime]::Parse($r.parkAt, $inv)).ToString('HH:mm', $inv), $r.parkWhy), $(if ($r.fMissing) { $T_PING + '; and add to it: ' + ($r.fMissing -replace ',', ', ') } else { $T_PING }), 'mark -What ping') }
    else { $act = @('PARKED', ('parked since {0} ({1}); next ping at {2}' -f ([datetime]::Parse($r.parkAt, $inv)).ToString('HH:mm', $inv), $r.parkWhy, ([datetime]::Parse($since, $inv)).AddMinutes($Cycle).ToString('HH:mm', $inv)), '', '') }
  }
  elseif ($r.fMissing -and $r.footAsk -ne $r.fMissing) { $act = @('FOOTER_ASK', ('the footer lacks: ' + $r.fMissing), ($T_FOOTER -f ($r.fMissing -replace ',', ', ')), 'mark -What footer') }
  elseif ($ciAct) { $act = $ciAct }
  elseif ([int]$r.evSince -ge 20 -or ($hasSt -and [int]$r.noProg -ge 3)) { $act = @('RECONCILE', $(if ([int]$r.evSince -ge 20) { '{0} evidence blocks since the last reconcile (rule: 20)' -f [int]$r.evSince } else { 'progress and AC unchanged for {0} replies (rule: 3)' -f [int]$r.noProg }), $T_RECONCILE, 'mark -What reconcile') }
  elseif ($hasSt -and $r.fresh -and [int]$r.evLast -ge 3 -and [int]$r.dPd -le 0 -and [int]$r.dAc -le 0 -and [int]$r.driftTurn -ne [int]$r.turns) { $act = @('DRIFT', ('the last reply added {0} evidence blocks but no planned task closed and no AC moved' -f [int]$r.evLast), ($T_DRIFT -f [int]$r.evLast), 'mark -What drift') }
  elseif ([int]$r.pd -ge 1 -and [int]$r.pd -eq [int]$r.pt -and $r.planDoneAt -ne ('{0}/{1}' -f $r.pd, $r.pt)) { $act = @('PLAN_DONE', ('the plan shows {0}/{1} done' -f $r.pd, $r.pt), ($T_PLANDONE -f $r.pd, $r.pt), 'mark -What plandone') }
  elseif ($ckNext -gt 0 -and [int]$r.evSince -ge $ckNext -and [int]$r.evSince -lt 20) { $act = @('CHECKPOINT', ('{0} task evidence since the last reconcile (rule: {1}): one BuddyRunner v1.6 Y on the latest Task Evidence' -f [int]$r.evSince, $(if ($md.speed -eq 'speed') { 'Speed, at 5, 10, 15, 19' } else { 'Economy, at 5 and 10' })), ($T_CHECKPOINT -f [int]$r.evSince), 'mark -What checkpoint') }
  elseif ($near -and -not $r.soonSent -and -not $isRecon -and -not $held) { $act = @('HANDOVER_SOON', ('{0:N0}/{1} min, {2:N0}/{3} pages, {4}/{5} turns (near a trigger)' -f [double]$r.sumMin, $MaxMin, [double]$r.sumPages, $MaxPages, [int]$r.turns, $MaxTurns), $T_SOON, 'mark -What soon') }
  elseif ([double]$r.lastTp -ge 3 -and [double]$r.lastTp2 -ge 3 -and -not $r.heavySent) { $act = @('CHAT_HEAVY', ('the last two replies took {0} and {1} pages' -f $r.lastTp2, $r.lastTp), $T_HEAVY, 'mark -What heavy') }
  # v3.28 sticky labels (architecture v2, references/aim-architecture.md): the label bound to this tab steers the message; the hold points ask me for a
  # judgement (H1 checkpoint, H2 handover after 1b, H3 triggers, adoption); an engineering-critical work with an open card gets nothing until the Owner answers.
  $aim = $(if ($Session -and $Pos) { Find-Aim $text $Session $Pos } else { $null }); $aimOn = ($aim -and $aim.status -eq 'ACTIVE')
  if ($aimOn) {
    $av = Aim-Ver $aim; $jk = @($r.judgeKeys | Where-Object { $_ }); $jq = @()
    if ($act -and $act[0] -eq 'CHECKPOINT') { $jq += , @(('H1@' + [int]$r.evSince), ('H1 checkpoint at {0} task evidence' -f [int]$r.evSince)) }
    if ($r.fresh -and [int]$r.userNoN -ge 3) { $jq += , @(('H3@user' + [int]$r.turns), ('H3: {0} replies in a row with nothing new in the user''s workflow (user=no)' -f [int]$r.userNoN)) }
    if ($r.fresh -and $r.fBk -eq 'OWNER' -and $r.fBr) { $jq += , @(('H3@bk' + $r.fBr), ('H3: Owner blocker {0} - on the path of the task aim (a Decision card), or not needed now (a Park card with evidence)?' -f $r.fBr)) }
    if ($r.buddy -eq 's1ok' -and $r.bPub1) { $jq += , @(('H2@' + $r.bPub1), 'H2 handover: 1b is published - review the main aim and the successor''s first task aim before step 2 (a card only if a change is due)') }
    if ($aim.adopt -and $r.fresh) { $jq += , @(('H3@adopt' + $aim.adopt.card + '.' + [int]$r.turns), ('adoption of {0}: do the plan, next action and acceptance checks reflect {1}? (judge -Adopt yes|no)' -f $aim.adopt.card, $aim.adopt.ver)) }
    foreach ($q in $jq) { if ($jk -notcontains $q[0]) { 'JUDGE {0}: {1} - read __coord.lastEvidence(5); judge each block for alignment, demonstrated progress and evidence confidence (open the proof of every outcome claim{2}); record aim.ps1 judge -Work {3} -Hold {4} -Chat {0}, then follow its NEXT lines' -f $Id, $q[1], $(if ((Aim-Crit $aim) -eq 'critical') { ' and every enabling claim' } else { '' }), $aim.work, ($q[0] -split '@')[0]; $jk += $q[0] } }
    $r.judgeKeys = @($jk | Select-Object -Last 16)
    if ($r.fAim -and $r.fAim -ne $av) { 'NOTE {0}: the footer says aim={1}, the label is {2}' -f $Id, $r.fAim, $av }
    $open = @(Get-OpenCards $text $aim.work | Where-Object { [string]$_.change -match '^(technical doubt|authority for):' })  # only doubt / authority cards stop a critical tab (12 Oct: a pending decision card must not block grounding)
    $quiet = @('OUT_OF_SCOPE', 'ON_HOLD', 'LIMIT', 'TAB_SHIFTED', 'UNKNOWN_TAB', 'TAB_MOVED', 'BUDDY_BLOCKED', 'BUDDY_WAIT', 'A_WAIT', 'A_HOLD', 'PARKED')
    if ((Aim-Crit $aim) -eq 'critical' -and $open.Count -and -not ($act -and $quiet -contains $act[0])) { $act = @('AIM_HOLD', ('engineering-critical work {0}: card {1} waits for the Owner - send nothing until it is answered' -f $aim.work, $open[0].id), '', '') }
    elseif ($act) { $act = AimSwap $act $r $aim }
  }
  if ($act) {
    'ACTION {0}: {1} - {2}' -f $Id, $act[0], $act[1]
    'SEND: ' + $(if ($act[2]) { $act[2] } else { 'nothing' })
    if ($act[3]) { 'MARK: after DELIVERED run & $w -Action {0} -Id {1}' -f $act[3], $Id }
  }
  else {
    # v3.26: an idle chat with its own next tasks gets the nudge sized by its mode (Speed 1-2 tasks; Economy 4-5 after a good Y); otherwise the normal route.
    $own = @(([string]$r.fNext) -split ',' | Where-Object { $_ -and $_ -notmatch '^(OWNER|PERSON|EXTERNAL|NONE|WAIT|HOLD)' })
    if ($State -eq 'IDLE' -and $own.Count -and -not $r.parkAt -and -not $r.stale -and -not $r.fMissing) {
      $pre = @('proceed with', 'ok proceed with', 'go on with', 'continue with')[[int]$r.turns % 4]
      $nt = $(if ($batch -eq '4-5') { '{0} the next 4-5 tasks of your plan in one go ({1}), and end with the LOG line in its code block' -f $pre, ((@($own | Select-Object -First 5)) -join ', ') } else { '{0} {1}, and end with the LOG line in its code block' -f $pre, ((@($own | Select-Object -First 2)) -join ' then ') })
      $act = @('NUDGE', ('idle with its own next tasks; mode {0}, batch {1}' -f (Badge $md), $batch), $nt, 'mark -What nudge')
      if ($aimOn) { $act = AimSwap $act $r $aim }
      'ACTION {0}: {1} - {2}' -f $Id, $act[0], $act[1]; 'SEND: ' + $act[2]; 'MARK: after DELIVERED run & $w -Action {0} -Id {1}' -f $act[3], $Id
    }
    else { 'ACTION {0}: NONE - no metric trigger; the normal route decides (status.ps1 / evidence.ps1 / rows 9 to 12)' -f $Id }
  }
  $r.lastKind = $(if ($act) { $act[0] } else { 'NONE' }); [void](Save-Rec $r)
}
# v3.25 (Owner, 11 Oct: "Y step ... wire with grounding prompt triggers at task evidence 5/10/15/19"): the checkpoint is one BuddyRunner v1.6 Y on the agent's
# latest Task Evidence (a self-check unless the Owner names a separate buddy); it replaces the old "What next? checklist" text.
$T_CHECKPOINT = 'BuddyRunner v1.6 Y at {0} task evidence blocks: read skills/buddy-runner-v1-6/references/Y_INTERVENE.md and CONTRACT.md at commit 30c9f635 of reallakshman19/Common (pinned) and apply Y once to your latest Task Evidence, checked against the source, not the report: decide CONTINUE / NO_CHANGE, CORRECT, VERIFY_FIRST or BLOCKED_AFFECTED_TASK (for NO_CHANGE give only the evidence identity, the decision and its basis) and add it to CHECKPOINTS.md. Close it with the line Y | INTERVENTION=CLOSED | EVIDENCE=<canonical key> | NO_FOLLOWUP_REVIEW, then continue with the next tasks of your plan (or the correction), and end with the LOG line in its code block'
$T_RECONCILE = 'reconcile with your issue now: what closed since the last reconcile, what is stuck and why, which evidence moved an acceptance criterion; publish the plan as a new revision and recommend continue, revamp or handover, and end with the LOG line'
$T_DRIFT = 'back to the plan: your last reply added {0} evidence blocks but no planned task closed and no acceptance criterion moved. name the planned task each block serves; next do only tasks from your plan, and end with the LOG line'
$T_PLANDONE = 'your plan shows {0}/{1} done. reconcile it with your issue: what of the original goal is still open? publish the next plan revision with task IDs and estimates, then continue, and end with the LOG line'
$T_SOON = 'this chat is near its handover point: in this turn bring your tab log fully up to date (EVIDENCE.log, CHECKPOINTS.md, DECISIONS.md, INPUTS.md, LINEAGE.md), then continue with your plan, and end with the LOG line'
$T_CI = 'skip in valid workflow. if credits are done, check locally and proceed.'
$T_CILIM = 'this repository is private, so every CI run costs paid minutes ({0} runs today): from now on push once per batch, only after your local checks pass, and run only the required workflow; then continue with your plan, and end with the LOG line in its code block'
$T_FIX = 'tests are red in two replies in a row ({0}): fix them before any new task. name each failing test and its cause, fix it, rerun, and end with the LOG line with tests= and PR=<number>@<sha>:<CI state>'
$T_BPUB = 'BuddyRunner v1.5: your Stage {0} publication is not verified yet ({1}). You are authorized to publish it as a comment on the current issue: publish it, read it back, and end with the LOG line with stage=BUDDY_S{0} | pub=<comment URL>#sha256:<SHA-256 of the comment body exactly as GitHub returns it>. If you really cannot publish, say why in one line with pub=NOT_PUBLISHED:<reason>'
$T_PING = 'any critical-path work possible now? if not, reply HOLD in one line, with the LOG line'
$T_FOOTER = 'add these fields to the LOG line at the end of every reply, and keep the rest as it is: {0}. Put the LOG line alone in a plain text code block. (folder=<session folder>/Tab<N>_<purpose>@<latest log commit> in reallakshman19/Common; blocker=NONE, OWNER:<decision IDs>, PERSON:<who>, CI, MACHINE:<what> or EXTERNAL:<what>; handover=no, due or ready:<path>; plan=<plan revision>; done=<task IDs closed in this reply, or none>; next=<next task IDs in order>; ac=<criteria met>/<total>)'
$T_HEAVY = 'keep chat replies short from now on: at most 15 lines here, all detail in your tab folder files; then continue with your plan, and end with the LOG line'
# v3.28 sticky labels: a plain send to a tab with an active label (a) first introduces a new label version (AIM_NEW: re-plan against it), (b) carries the
# Ground questions on every 3rd routine message, or on the next one after a judgement found drift (GROUND_AIM; never an extra message), (c) names the task aim
# instead of "your plan". Recipe sends ('(onboard.ps1 ...)') are left as they are.
function AimText($kind, $s, $aim) {
  $ta = [string]$aim.label.task; $av = Aim-Ver $aim
  switch ($kind) {
    'DRIFT' { return ('back to the aim: your last reply added evidence but nothing changed in the user''s workflow. say which outcome each block serves (or which outcome a prerequisite serves); next do only tasks that move your task aim ({0}), and end with the LOG line' -f $ta) }
    'FIX_FIRST' { return ('first decide with evidence: do these failures block your task aim ({0}) or its acceptance? if not, say so in one line with the reason and continue with the task aim (parking them is the Owner''s decision). if they do: {1}' -f $ta, $s) }
    'PING' { return ('any work that moves your task aim ({0}) possible now? if not, reply HOLD in one line, with the LOG line' -f $ta) }
    'RECONCILE' { return ([string]$s -replace '^reconcile with your issue now', ('reconcile with the Owner''s sticky label {0} now (task aim: {1})' -f $av, $ta)) }
  }
  ([string]$s).Replace('continue with the next tasks of your plan', 'continue with the next task that moves your task aim (' + $ta + ')').Replace('continue with your plan', 'continue with the task that moves your task aim (' + $ta + ')')
}
function AimSwap($act, $r, $aim) {
  if (-not $act -or -not $act[2] -or ([string]$act[2]).StartsWith('(')) { return $act }
  $av = Aim-Ver $aim
  if ($r.aimIntro -ne $av -or $aim.groundDue -eq 'new') { return @('AIM_NEW', ('sticky label {0} is new for this chat (instead of {1}): re-plan against it' -f $av, $act[0]), ((Aim-Ground $aim -New) + $(if ([string]$r.fMissing -match 'chat=') { ' In the LOG line use chat=' + $Id + ' (this chat''s id) instead of chat=new.' } else { '' })), ('mark -What aimintro -Mode ' + $aim.work + '@' + $av)) }
  if ($act[0] -in 'NUDGE', 'PING' -and (([int]$r.aimSends % 3) -eq 2 -or $aim.groundDue -eq 'ground')) { return @('GROUND_AIM', $(if ($aim.groundDue -eq 'ground') { 'the last judgement found drift: this routine message carries the Ground questions' } else { 'every 3rd routine message carries the Ground questions (Owner, 8 Oct)' }), (Aim-Ground $aim), ('mark -What aimground -Mode ' + $aim.work + '@' + $av)) }
  @($act[0], $act[1], (AimText $act[0] $act[2] $aim), $act[3])
}

if ($Action -notin 'show', 'rows', 'rowsjson', 'report', 'due', 'cycle' -and $Id -notmatch '^[0-9a-f]{8}$') { 'need -Id (first 8 letters of the conversation id)'; return }
# Control Tower WP2 v3.28 source-level observation capture:
# The display cells are captured only after RowsOut calculates them. This helper
# never writes state, never decides status, and never changes legacy report text.
function Capture-RowJson($cells, $position, $cid, $generation, $probe, $seen) {
  if ($Action -ne 'rowsjson') { return }
  $probeTime = $null
  if ($seen) { try { $probeTime = ([datetime]::Parse([string]$seen, $inv)).ToUniversalTime().ToString('o') } catch { $probeTime = $null } }
  $g = [Math]::Max(1, [int]$generation)
  [void]$script:RowsJson.Add([ordered]@{
    tab = [string]$cells[0]; status = [string]$cells[1]; aim = [string]$cells[2]
    plan = [string]$cells[3]; ac = [string]$cells[4]; ci = [string]$cells[5]
    meter = [string]$cells[6]; due = [string]$cells[7]; checked = [string]$cells[8]
    next = [string]$cells[9]; tab_position = [string]$position; chat_id = [string]$cid
    binding_generation = $g; observed_at_utc = $script:RowGeneratedAtUtc
    probe_status = [string]$probe; last_probe_at_utc = $probeTime
  })
}
function RowsOut {
    $D_GRN = [char]::ConvertFromUtf32(0x1F7E2); $D_YEL = [char]::ConvertFromUtf32(0x1F7E1); $D_RED = [char]::ConvertFromUtf32(0x1F534); $D_BLU = [char]::ConvertFromUtf32(0x1F535); $D_WHT = [string][char]0x26AA
    # v3.25 (Owner, 11 Oct snaps 1-3): readable cells. Lists are cut at a separator, text at a word, never inside a word or an ID; CI shows at most 2 PRs.
    $cutL = { param($s, $n) $a = @(([string]$s) -split ',' | Where-Object { $_ }); $o = @(); $len = 0; foreach ($x in $a) { if ($o.Count -and $len + $x.Length + 1 -gt $n) { break }; $o += $x; $len += $x.Length + 1 }; ($o -join ',') + $(if ($o.Count -lt $a.Count) { ' +' + ($a.Count - $o.Count) } else { '' }) }
    $cutW = { param($s, $n) $s = ([string]$s -replace '\s+', ' ').Trim(); if ($s.Length -le $n) { $s } else { $k = $s.LastIndexOf(' ', $n); if ($k -lt $n / 2) { $k = $n }; $s.Substring(0, $k).TrimEnd(' ', ',', ';', '-', ':') + '…' } }
    $ciCell = { param($pr, $head) $it = @(([string]$pr) -split '[,;]\s*|\s+(?=#?\d+@)' | Where-Object { $_.Trim() } | ForEach-Object { $_.Trim() -replace '@([0-9a-f]{7})[0-9a-f]+', '@$1' })
      if ($it.Count -eq 1 -and $head -and $it[0] -notmatch '@') { $it[0] += '@' + ([string]$head).Substring(0, [Math]::Min(7, ([string]$head).Length)) }
      (@($it | Select-Object -First 2) -join ' · ') + $(if ($it.Count -gt 2) { ' +' + ($it.Count - 2) } else { '' }) }
    # v3.19 (Owner, 11 Oct: footer-driven table): one row per tab position, every cell from the records (footer fields, meter, last action); nothing retyped.
    # Status and Next can still be overridden by hand when the page shows something the footer does not (generating, error, parked).
    '| Tab | Status | Aim | Plan | AC | CI | Meter | Due | Checked | Next |'
    '|---|---|---|---|---|---|---|---|---|---|'
    $foot = @(); $shifted = @(); $costs = @(); $anyAim = $false
    $nextWords = @{ PING = 'ping (parked)'; PARKED = 'nothing (parked)'; NONE = 'normal route'; CHECKPOINT = 'Y check (v1.6)'; RECONCILE = 'reconcile'; DRIFT = 'back to the plan'; PLAN_DONE = 'next plan revision'; HANDOVER = 'ask G1 for 1a'; HANDOVER_SOON = 'bring log up to date'; CHAT_HEAVY = 'shorter replies'; GROUND = 'grounding prompt'; RECON = 'RECON step'; CI = 'CI text'; FIX_FIRST = 'fix tests first'; RC_ASK = 'ask you (restricted coder)'; FOOTER_ASK = 'ask missing footer fields'; TAB_MOVED = 'tell you: tab moved'; UNKNOWN_TAB = 'ask you: which work?'; BUDDY_S1 = 'send 1b pointer'; BUDDY_A_REVIEW = 'switch: ask G1 for 2'; A_REVIEW_READY = 'switch: start successor'; A_WAIT = 'wait (G1)'; A_HOLD = 'nothing (G1 holds)'; BUDDY_START = 'send start (workpack)'; OUT_OF_SCOPE = 'nothing (not mine)'; ON_HOLD = 'nothing (on hold)'; SENT = 'wait for the reply'; NUDGE = 'nudge (sized batch)'; BUDDY_S2 = 'Buddy Stage 2'; BUDDY_PUBLISH = 'ask to publish'; BUDDY_WAIT = 'wait for Buddy reply'; BUDDY_BLOCKED = 'tell you: Buddy blocked'; BRIEF_READY = 'new chat: 1b pointer'; TAB_SHIFTED = 'ask you: confirm new order'; LIMIT = 'tell you: chat full'; AIM_NEW = 'send the new sticky label'; GROUND_AIM = 'step back to the label'; AIM_HOLD = 'nothing (card waits for you)' }
    foreach ($p in ($Tabs -split ';' | Where-Object { $_ -match '=' })) {
      $q = $p -split '='; $pos = $q[0].Trim(); $Id = $q[1].Trim()
      $nm = 'Tab' + $pos; $mnm = [string](MapName $pos)
      # v3.25 (Owner, 11 Oct snap 1): [OUT] in the map name = not in my scope, [HOLD] = on hold by the Owner: shown, never triggered or sent to.
      if ($mnm -match '^\[(OUT|HOLD)\]') { $w8 = $(if ($Matches[1] -eq 'OUT') { 'not in my scope' } else { 'on hold (Owner)' })
        if ($Action -eq 'rowsjson') { Capture-RowJson @((('{0} · {1} · {2}' -f $nm, $Id, (& $cutW $mnm 40))), (('{0} {1}' -f $D_WHT, $w8)), '-', '-', '-', '-', '-', '-', '-', 'nothing') $pos $Id 1 'UNKNOWN' $null }
        '| {0} · {1} · {2} | {3} {4} | - | - | - | - | - | - | - | nothing |' -f $nm, $Id, (& $cutW $mnm 40), $D_WHT, $w8; continue }
      $fd = MapFolder $pos; if ($fd) { $foot += ,@($pos, $fd) }
      $ui = MapInfo $pos $Id; if ($ui -like 'shifted:*') { $shifted += [int]$pos }
      $uiTxt = $(if ($ui -eq 'new') { $D_YEL + ' new: waits on you (which work?)' } elseif ($ui) { $D_RED + ' shifted: was Tab' + ($ui -split ':')[1] } else { '' })
      $m = Get-Line $text $Id
      if (-not $m) {
        if ($Action -eq 'rowsjson') {
          $missingStatus = $(if ($uiTxt) { $uiTxt } else { 'new chat: not measured yet' })
          $missingNext = $(if ($ui -eq 'new') { 'ask you: which work?' } elseif ($ui) { 'ask you: confirm new order' } else { 'read it next cycle' })
          Capture-RowJson @((('{0} · {1}' -f $nm, $Id)), $missingStatus, '-', '-', '-', '-', '-', '-', '**never**', $missingNext) $pos $Id 1 'NEVER_PROBED' $null
        }
        '| {0} · {1} | {2} | - | - | - | - | - | - | **never** | {3} |' -f $nm, $Id, $(if ($uiTxt) { $uiTxt } else { 'new chat: not measured yet' }), $(if ($ui -eq 'new') { 'ask you: which work?' } elseif ($ui) { 'ask you: confirm new order' } else { 'read it next cycle' }); continue }
      $o = Load-Rec
      $b = { param($v, $lim, $txt) if ($lim -gt 0 -and [double]$v -ge 0.8 * $lim) { '**' + $txt + '**' } else { $txt } }
      $status = $(if ($o.hard -eq 'conversation length limit') { 'full chat' } elseif ($o.fHv -eq 'ready') { 'brief ready' } elseif (-not $o.fLine -and $o.pStage -eq 'REPORT_READY') { 'brief ready (page)' } elseif ([int]$o.rcn -gt 0 -and [int]$o.rcn -lt 4) { 'RECON ' + $o.rcn + '/4' } elseif ($o.fBk -eq 'OWNER') { 'waits on you' } elseif ($o.fBk -eq 'PERSON') { 'waits on a person' } elseif ($o.fBk -eq 'CI') { 'CI blocked' } elseif ($o.fBk -eq 'MACHINE') { 'machine blocker' } elseif ($o.stale) { 'stale footer' } else { 'working' })
      if ($o.fRel) { $status += ' · release ' + $o.fRel }
      $plan = @(); if ($o.fPlan) { $plan += (& $cutW $o.fPlan 24) }; if ($o.fDone) { $plan += ('done ' + (& $cutL $o.fDone 24)) }; if ($o.fNext) { $plan += ('next ' + (& $cutL $o.fNext 24)) }
      if ([int]$o.pd -ge 0) { $plan += ('{0}/{1}' -f $o.pd, $o.pt) }
      if ([int]$o.evN -gt 0) { $plan += ('TE {0} (+{1})' -f $o.evN, $o.evLast) }
      $ac = $(if ([int]$o.aca -ge 0) { '{0}/{1}' -f $o.aca, $(if ([int]$o.act -ge 0) { $o.act } else { '?' }) } else { '-' })
      $ci = @(); $vz = RepoVis $o.repo -CacheOnly
      if ($vz -eq 'private') { $cn = @($o.ciHeads | Where-Object { $_ -like ((Get-Date).ToString('yyyy-MM-dd', $inv) + '|*') }).Count; $ci += ((& { param($t0) if ($cn -ge 4) { '**' + $t0 + '**' } else { $t0 } } ([char]::ConvertFromUtf32(0x1F512) + ' private · CI runs today ' + $cn))) }
      if ($o.fPr -and $o.fPr -notmatch '^(none|-)$') { $ci += (& $ciCell $o.fPr $o.fHead) }
      if ($o.fTests) { $ci += $o.fTests } elseif ($o.fProof) { $ci += (& $cutW $o.fProof 22) }
      if ([int]$o.redN -ge 2) { $ci += ('**not green x' + $o.redN + '**') }
      $meter = (& $b $o.sumMin $MaxMin ('{0:N0}/{1} min' -f [double]$o.sumMin, $MaxMin)) + ' · ' + (& $b $o.sumPages $MaxPages ('{0:N0}/{1} pages' -f [double]$o.sumPages, $MaxPages)) + ' · ' + (& $b $o.turns $MaxTurns ('{0}/{1} turns' -f [int]$o.turns, $MaxTurns))
      if ([int]$o.gen -gt 0) { $nm += ' g' + $o.gen }; $mdr = ModeOf $pos $o; $nm += ' ' + (Badge $mdr); $costs += ('Tab{0} ~{1:N0}K' -f $pos, [double]$(if ($o.costDay -eq (Get-Date).ToString('yyyy-MM-dd', $inv)) { $o.costK } else { 0 }))
      $nm += ' · ' + $(if ($o.url) { '[' + $Id + '](' + $o.url + ')' } else { $Id }) + $(if ($o.title) { ' · ' + (& $cutW ($o.title -replace '[|\r\n]', ' ') 40) } else { '' })
      $seen = $o.lastSeen; $sp = SeenAt $pos; if ($sp -and (-not $seen -or [datetime]::Parse($sp, $inv) -gt [datetime]::Parse($seen, $inv))) { $seen = $sp }
      $age = $(if ($seen) { [int]((Get-Date) - [datetime]::Parse($seen, $inv)).TotalMinutes } else { -1 })
      $chk = $(if ($age -lt 0) { 'not recorded' } elseif ($age -gt 2 * $Cycle) { '**{0} min ago**' -f $age } else { '{0} min ago' -f $age })
      # Due = the next time-based event for this tab (v3.19): a parked ping, the RECON or handover point in worked minutes, pages left, the red flag.
      $dueL = @()
      if ($o.parkAt) { $sx = $(if ($o.pingAt) { $o.pingAt } else { $o.parkAt }); $dueL += ('ping ' + ([datetime]::Parse($sx, $inv)).AddMinutes($Cycle).ToString('HH:mm', $inv)) }
      $isRc = ($o.reconMode -eq 'on')
      if ($isRc -and [int]$o.rcn -eq 0) { $dueL += ('RECON in {0:N0} min' -f [Math]::Max(0, $ReconMin - [double]$o.sumMin)) }
      elseif ($mdr.hold -eq 'hold') { $dueL += 'handover on hold (Owner)' }
      elseif (-not $o.hard -and [int]$o.rcn -eq 0) { $dueL += ('handover in {0:N0} min, {1:N0} pages or {2} turns' -f [Math]::Max(0, $MaxMin - [double]$o.sumMin), [Math]::Max(0, $MaxPages - [double]$o.sumPages), [Math]::Max(0, $MaxTurns - [int]$o.turns)) }
      if (@($o.last3).Count -ge 3 -and (Last3 @($o.last3)) -lt $RedMin -and -not $o.redSent -and -not ($o.parkAt -or (@('OWNER', 'PERSON', 'EXTERNAL') -contains [string]$o.fBk) -or $o.fHv -eq 'ready')) { $dueL += ([char]::ConvertFromUtf32(0x1F6A9) + ' red flag') }
      # v3.20 audit: recovery waits (recipes ERROR / LOADFAIL: 10 min, unusual activity: 35 min) are shown, not only kept in the records.
      $probErr = ''
      if (@('ERROR', 'LOADFAIL', 'NOBOX', 'UNUSUAL') -contains [string]$o.lastState) {
        $fs = @(Recent $o | Where-Object { ($_ -split '\|')[1] -eq $o.lastState })[0]; $since = $(if ($fs) { ($fs -split '\|')[0] } else { $o.lastSeen })
        $wait = $(if ($o.lastState -eq 'UNUSUAL') { 35 } else { 10 })
        $probErr = 'problem: {0} since {1}' -f $o.lastState.ToLower(), ([datetime]::Parse($since, $inv)).ToString('HH:mm', $inv)
        $dueL = @(('retry {0}' -f ([datetime]::Parse($since, $inv)).AddMinutes($wait).ToString('HH:mm', $inv))) + $dueL
      }
      $v16 = ($o.bV -eq '16')
      if ($o.bPub1) { $plan += $(if ($v16) { 'Buddy 1b ' + [char]0x2713 + $(if ($o.buddy -eq 'done') { ' 2 ' + [char]0x2713 } else { '' }) } else { 'Buddy S1 ' + [char]0x2713 + $(if ($o.bPub2) { ' S2 ' + [char]0x2713 } else { '' }) }) }
      if ($o.yLast) { $plan += ('Y ' + [char]0x2713 + ' ' + $o.yLast) }
      $dueTxt = $(if ($dueL.Count) { $dueL -join ' · ' } else { '-' })
      $nx = $(if ($o.lastKind -and $nextWords.ContainsKey([string]$o.lastKind)) { $nextWords[[string]$o.lastKind] } else { 'normal route' })
      if ($o.lastKind -eq 'SENT' -and $o.sentWhat) { $nx = 'wait for the reply (' + $o.sentWhat + ' sent)' }
      if ($o.fMissing -and $o.lastKind -ne 'FOOTER_ASK') { $nx += ' (footer lacks ' + $o.fMissing + ')' }
      if ($o.parkAt) { $status = 'parked: ' + $o.parkWhy }
      if ($probErr) { $status = $probErr }
      if ($o.buddy -and $o.buddy -ne 'done' -and -not $probErr) {
        # v3.25: lane words by version (v1.6: 1a -> 1b -> 2 -> start; v1.5 lanes finish as they began). Next follows the lane state, not the last action (snap 3).
        if ($v16) {
          $status = @{ due = 'Buddy 1b next'; s1 = 'Buddy 1b: G2 investigates'; s1ok = 'Buddy: G1 writes 2 next'; areview = 'Buddy: G1 writes 2'; blocked = 'Buddy blocked: ' + $o.bWhy }[[string]$o.buddy]
          $dueTxt = (@{ due = 'send 1b pointer'; s1 = '1b reply'; s1ok = 'ask G1 for 2'; areview = 'G1''s 2, then start'; blocked = '-' }[[string]$o.buddy])
          $nx = (@{ due = 'send 1b pointer'; s1 = 'wait for 1b'; s1ok = 'switch: ask G1 for 2'; areview = $(if ($o.lastKind -eq 'BUDDY_START') { 'send start (workpack)' } else { 'wait for G1''s 2' }); blocked = 'tell you: Buddy blocked' }[[string]$o.buddy])
        }
        else {
          $status = @{ due = 'Buddy S1 next'; s1 = 'Buddy S1: purpose'; s1ok = 'Buddy: outgoing review next'; areview = 'Buddy: outgoing agent reviews Stage 1'; s2 = 'Buddy S2: reconcile + baseline'; blocked = 'Buddy blocked: ' + $o.bWhy }[[string]$o.buddy]
          $dueTxt = (@{ due = 'send Stage 1'; s1 = 'Stage 1 reply'; s1ok = 'ask the outgoing agent to review'; areview = 'outgoing review, then Stage 2'; s2 = 'Stage 2 reply, then plan'; blocked = '-' }[[string]$o.buddy])
          $nx = (@{ due = 'send Stage 1'; s1 = 'wait for Stage 1'; s1ok = 'switch: outgoing review'; areview = $(if ($o.lastKind -eq 'BUDDY_S2') { 'send Stage 2' } else { 'wait for the outgoing review' }); s2 = 'wait for Stage 2'; blocked = 'tell you: Buddy blocked' }[[string]$o.buddy])
        }
        if ([int]$o.bTry -gt 0 -and $o.buddy -ne 'blocked') { $status += ' · publish asked' }
      }
      elseif ($o.aLane -in 'asked', 'moved', 'review', 's2ready', 'retired' -and -not $probErr) {
        $status = @{ asked = $(if ($o.fHv -eq 'ready') { 'Buddy: 1a ready (G1 holds)' } else { 'Buddy: G1 writes 1a' }); moved = 'Buddy: G1 holds'; review = 'Buddy: G1 writes 2'; s2ready = 'Buddy: G1 closed (2)'; retired = 'retired (handed over)' }[[string]$o.aLane]
        $nx = @{ asked = $(if ($o.fHv -eq 'ready') { 'new chat: 1b pointer' } else { 'wait for 1a' }); moved = 'nothing (G1 holds)'; review = 'wait for G1''s 2'; s2ready = 'switch: start successor'; retired = 'nothing (retired)' }[[string]$o.aLane]
      }
      if (-not $o.fPlan -and -not $o.folder -and -not $o.fMissing -and -not $o.fBk -and [int]$o.evN -eq 0 -and $status -eq 'working') { $status = 'onboarding: no footer yet' } elseif ($o.fMissing -and $status -eq 'working') { $status = 'footer incomplete' }
      # v3.20 (Owner, 11 Oct: "> 60 min of inactivity its a stable tab (shall be marked in diff color in tab status)"): no new reply and not generating for StableMin.
      $idle = $(if ($o.actAt) { [int]((Get-Date) - [datetime]::Parse($o.actAt, $inv)).TotalMinutes } else { -1 })
      $dot = $(if ($status -match '^(full chat|stale|CI blocked|machine|problem|Buddy blocked)' -or $age -gt 2 * $Cycle) { $D_RED } elseif ($status -match '^retired') { $D_WHT } elseif ($status -match '^(waits|parked|brief ready|RECON|onboarding|footer incomplete|Buddy)') { $D_YEL } else { $D_GRN })
      if ($idle -ge $StableMin -and -not $probErr) { if ($status -match '^working') { $nx = 'ask you: still mine to drive?' }; $dot = $D_BLU; $status = 'stable ' + $idle + ' min · ' + $status }
      $status = $dot + ' ' + $status
      if ($uiTxt) { $status = $uiTxt; $nx = $(if ($ui -eq 'new') { 'ask you: which work?' } else { 'ask you: confirm new order' }) }
      # v3.28 sticky labels: Aim = label version · last judgement (task outcome, demonstrated progress with confidence, why) · open card · adoption.
      $aimC = '-'; $am = $(if ($Session) { Find-Aim $text $Session $pos } else { $null })
      if ($am) {
        $anyAim = $true; $oc = @(Get-OpenCards $text $am.work); $shd = $(if ((Aim-Crit $am) -eq 'critical') { $AimShield + ' ' } else { '' })
        if ($am.status -ne 'ACTIVE') { $aimC = $shd + 'label draft' + $(if ($oc.Count) { ' · card ' + $oc[0].id + ' waits for you' } else { '' }) + $(if ((Aim-Crit $am) -eq 'unknown') { ' · critical? ask' } else { '' }) }
        else {
          $jd = $am.judge
          $aimC = $shd + (Aim-Ver $am) + ' · ' + $(if ($jd -and $jd.color) { $AimDot[[string]$jd.color] + ' ' + (& $cutW $jd.sum 60) + $(if ($jd.why) { ' · ' + (& $cutW $jd.why 50) } else { '' }) } else { $am.label.taskOutcome + ' · not judged yet' })
          if ($oc.Count) { $aimC += ' · card ' + $oc[0].id + $(if ($oc.Count -gt 1) { ' +' + ($oc.Count - 1) } else { '' }) }
          if ($am.adopt) { $aimC += ' · adopting ' + $am.adopt.card }
          if ($o.fAim -and $o.fAim -ne (Aim-Ver $am)) { $aimC += ' · footer ' + $o.fAim } elseif (-not $o.fAim -and $o.aimIntro) { $aimC += ' · footer lacks aim' }
          if (Aim-Pending $am) { $aimC += ' · done-when pending' }
        }
      }
      if ($Action -eq 'rowsjson') {
        $probeKind = $(if ([string]$o.lastState -in @('ERROR','LOADFAIL','NOBOX','UNUSUAL')) { [string]$o.lastState } elseif ($seen -and $o.lastState) { 'SUCCESS' } else { 'UNKNOWN' })
        $lastProbe = $seen
        $lastTimeout = @((Recent $o | Where-Object { $_ -match ('\\|probe timeout' + '$') }) | Select-Object -Last 1)
        if ($lastTimeout.Count) {
          $timeoutTime = ($lastTimeout[0] -split '\\|')[0]
          if (-not $seen -or ([datetime]::Parse($timeoutTime, $inv) -ge [datetime]::Parse($seen, $inv))) { $probeKind = 'TIMEOUT'; $lastProbe = $null }
        }
        Capture-RowJson @($nm, $status, $aimC, $(if ($plan.Count) { $plan -join ' · ' } else { '-' }), $ac, $(if ($ci.Count) { $ci -join ' · ' } else { '-' }), $meter, $dueTxt, $chk, $nx) $pos $Id $o.gen $probeKind $lastProbe
      }
      '| {0} | {1} | {10} | {2} | {3} | {4} | {5} | {6} | {7} | {8} |' -f $nm, $status, $(if ($plan.Count) { $plan -join ' · ' } else { '-' }), $ac, $(if ($ci.Count) { $ci -join ' · ' } else { '-' }), $meter, $dueTxt, $chk, $nx, '', $aimC
    }
    if ($shifted.Count) { ''; ('**Tabs shifted from position {0}: confirm the new order?** (no sends to the shifted tabs until then)' -f ($shifted | Measure-Object -Minimum).Minimum) }
    ''; ('{0} working · {1} waits or onboarding · {2} problem · {3} stable (no new reply for {4} min or more) · {7} not mine, on hold or retired · {5} red flag (last 3 turns under {6} min while working)' -f $D_GRN, $D_YEL, $D_RED, $D_BLU, $StableMin, [char]::ConvertFromUtf32(0x1F6A9), $RedMin, $D_WHT)
    ('{0} Speed (urgent: full check each firing, Y at 5/10/15/19, 1-2 tasks) · {1} Economy (page watcher, Y at 5 and 10, 4-5 tasks after a good Y) · RC restrained coder · NC non-coder' -f [string][char]0x26A1, [char]::ConvertFromUtf32(0x1F422))
    if ($anyAim) { ('Aim: label version · last judgement: {0} on aim (outcome or enabling progress, proof opened) · {1} unverified claims, drift or a scope question · {2} stuck on your decision · {3} contradicted proof, no authority, or doubt on critical work · {4} engineering-critical' -f $AimDot.green, $AimDot.amber, $AimDot.yellow, $AimDot.red, $AimShield) }
    ('cost: context {0} per firing · plan {1} · my checks today, est.: {2}' -f $(if ($Ctx) { $Ctx } else { '? (pass -Ctx from get_usage)' }), $(if ($PlanUse) { $PlanUse } else { '?' }), $(if ($costs.Count) { $costs -join ', ' } else { '-' }))
    ('rows v3.28 · meter {0}/{1}/{2} · session {3} · {4} - paste this table and these lines unchanged (runbook G, F1)' -f $MaxMin, $MaxPages, $MaxTurns, $Session, (Get-Date).ToString('HH:mm', $inv))
    if ($foot.Count) { 'Folders (reallakshman19/Common, coordination/; one work per folder, a tab never changes work, a work is in one tab at a time): ' + (($foot | Group-Object { $_[1] } | ForEach-Object { (@($_.Group | ForEach-Object { 'Tab' + $_[0] }) -join ' + ') + ' -> ' + $_.Name + $(if ($_.Count -gt 1) { ' **CONFLICT: one work in ' + $_.Count + ' tabs at once - tell the Owner**' } else { '' }) }) -join '; ') }
  }
switch ($Action) {
  'see' {
    $r = Load-Rec
    # v3.19 (Owner, 11 Oct: "integrate tab protocol with the task evidence footer ... and your table status"): the probe's parsed footer (-St = st, -Ft = ft)
    # fills every input the triggers need, unless a value was passed by hand. A footer whose chat= is another chat is stale: ignored and reported.
    # v3.21 (Owner, 11 Oct 13:0x: "tab link should be the identifier, tab names are for reference only ... drop the tab rename system"): the chat link is the identity, the live title is refreshed on every probe.
    if ($Url) { $r.url = $Url }; if ($Title) { $r.title = $Title }; if ($Repo) { $r.repo = $Repo }; if ($Stage) { $r.pStage = $Stage }  # v3.25: the probe's page stage (REPORT_READY ...) for the table when a chat has no footer
    $stO = $null; $ftO = $null; $bMiss = ''; $doneNow = $false; $laneOn = (($r.buddy -and $r.buddy -notin 'done', 'blocked') -or ($r.aLane -in 'asked', 'moved', 'review', 's2ready'))  # lane state BEFORE this reply: the reply that completes Stage 2 is a Buddy reply too
    if ($St) { try { $stO = $St | ConvertFrom-Json } catch { $stO = $null } }
    if ($Ft) { try { $ftO = $Ft | ConvertFrom-Json } catch { $ftO = $null } }
    $r.stale = ''
    if ($ftO -and $ftO.chat -and [string]$ftO.chat -ne $Id -and -not ([string]$ftO.chat -eq 'new')) { $r.stale = [string]$ftO.chat; $ftO = $null; $stO = $null }
    # v3.28 (restart in a fresh chat, 12 Oct): chat=new is this chat until it is told its id; the footer asks for it (the AIM_NEW text carries it too).
    if ($ftO -and [string]$ftO.chat -eq 'new' -and $r.buddy -notin 'due', 's1') { $ftO | Add-Member -NotePropertyName missing -NotePropertyValue @(@($ftO.missing | Where-Object { $_ }) + ('chat=' + $Id)) -Force }
    if ($stO) {
      if (-not $Prog -and $null -ne $stO.pd -and $null -ne $stO.pt) { $Prog = '{0}/{1}' -f $stO.pd, $stO.pt }
      if (-not $Ac -and $null -ne $stO.aca) { $Ac = '{0}/{1}' -f $stO.aca, $(if ($null -ne $stO.act) { $stO.act } else { 0 }) }
      if (-not $Tests -and $stO.tests) { $Tests = [string]$stO.tests }
      if (-not $Pr -and $stO.pr) { $Pr = [string]$stO.pr }
      if (-not $Blocker -and $stO.bk) { $Blocker = [string]$stO.bk }
      # v3.27 (review finding 6): a done ID counts once (done history), and only a planned one (seen earlier in a next= list) moves progress.
      $hist0 = @(@($r.doneHist) + @(([string]$r.fDone) -split ',') | Where-Object { $_ }); $dn0 = @($stO.done | Where-Object { $_ }); $newD = @($dn0 | Where-Object { $hist0 -notcontains $_ })
      $npl = $(if (@($r.planSeen).Count -eq 0) { $newD.Count } else { @($newD | Where-Object { @($r.planSeen) -contains $_ }).Count })  # no plan seen yet (new chat): new done IDs count
      $r.doneHist = @(@($hist0) + $dn0 | Select-Object -Unique | Select-Object -Last 150); $r.planSeen = @(@($r.planSeen) + @($stO.next | Where-Object { $_ }) | Select-Object -Unique | Select-Object -Last 100)
      if ($stO.pr -match '@([0-9a-f]{7,40})') { $hd = (Get-Date).ToString('yyyy-MM-dd', $inv) + '|' + ([string]$stO.pr -replace '\s', ''); if (@($r.ciHeads) -notcontains $hd) { $r.ciHeads = @(@($r.ciHeads) + $hd | Select-Object -Last 30) } }
      if (-not $DoneN) { $prevDone = $hist0; $DoneN = @($stO.done | Where-Object { $_ -and $prevDone -notcontains $_ }).Count }  # v3.24 (live 16:45): done IDs repeated from the previous footer are not new evidence
      $r.fPlan = [string]$stO.rev; $r.fDone = (@($stO.done) -join ','); $r.fNext = (@($stO.next) -join ','); $r.fRel = [string]$stO.rel
      $r.fBk = [string]$stO.bk; $r.fBr = [string]$stO.br; $r.fHv = [string]$stO.hv; $r.fHr = [string]$stO.hr; $r.fPr = [string]$stO.pr; $r.fTests = [string]$stO.tests
    }
    $r.unknown = MapInfo $Pos $Id
    if ($ftO -and $ftO.tab -and $Pos -and ([string]$ftO.tab -match '(\d+)') -and [int]$Matches[1] -ne $Pos) { $ftO | Add-Member -NotePropertyName missing -NotePropertyValue @(@($ftO.missing | Where-Object { $_ }) + ('tab=Tab{0} (not {1})' -f $Pos, $ftO.tab)) -Force }
    if ($ftO) {
      if (-not $LogLine) { $LogLine = [string]$ftO.line }
      if (-not $Log -and $ftO.folder) { $Log = [string]$ftO.folder + $(if ($ftO.commit) { '@' + $ftO.commit } else { '' }) }
      # v3.21 Buddy lane (Owner, 11 Oct: BuddyRunner v1.5 at every handover, run by the incoming agent; agents publish without the Owner).
      # States: due (Stage 1 to send) -> s1 (sent) -> s1ok (Stage 1 published with URL#sha256) -> s2 (Stage 2 sent) -> done; blocked = still unpublished after one ask, or STAGE1_NOT_VERIFIED.
      if ($r.buddy -and $r.buddy -notin 'done', 'blocked') {
        $bsx = [Math]::Max([int]$Bs, [int]$r.bSent); if ($bsx -ge 1 -and $r.buddy -eq 'due') { $r.buddy = 's1' }; if ($bsx -ge 2 -and $r.buddy -in 's1', 's1ok', 'areview') { $r.buddy = 's2' }
        $fs = [string]$ftO.stage; $fp = [string]$ftO.pub; if ($ftO.assessed) { $r.bAss = [string]$ftO.assessed }
        $okp = ($fp -match '^https?://\S+#sha256:[0-9a-f]{64}$')
        if ((([string]$ftO.line) + ' ' + $LogLine) -match 'STAGE1_NOT_VERIFIED') { $r.buddy = 'blocked'; $r.bWhy = 'Stage 2 says STAGE1_NOT_VERIFIED' }
        elseif ($r.buddy -eq 's1' -and $fs -match '^(BUDDY_S1|1B)$' -and $okp) { $r.bPub1 = $fp; $r.buddy = 's1ok'; $r.bNeed = 0; $r.bWhy = '' }
        elseif ($r.buddy -eq 's2' -and $fs -match '^(BUDDY_S2|WORK)$' -and $okp) { $r.bPub2 = $fp; $r.buddy = 'done'; $r.bNeed = 0; $r.bWhy = ''; $r.evSince = 0; $r.ckAt = 0; $r.noProg = 0; $doneNow = $true; 'BUDDY_DONE {0}: Stage 2 published ({1}); evidence since the last reconcile reset to 0; the normal route starts with the plan in the footer' -f $Id, $fp }
        elseif ($r.buddy -in 's1', 's2') { $bMiss = $(if ($fp -match 'NOT_PUBLISHED') { $fp } elseif ($fp) { 'pub= has no URL#sha256:<digest>' } elseif ($fs) { 'stage=' + $fs + ' but no pub=' } else { 'no stage= / pub= in the LOG line' }) }
      }
      if ($ftO.line) { $r.fLine = [string]$ftO.line; $r.fMissing = (@($ftO.missing) -join ','); $r.fHead = [string]$ftO.head; $r.fProof = [string]$ftO.proof }  # v3.25: a reply with only a v1.6 ending line keeps the last footer
      # v3.25 BuddyRunner v1.6: G1's own publication (1a / 2) is kept for the successor's start; a Y ending line records the intervention as closed.
      if ($r.aLane -and $ftO.pub) { $r.aPub = [string]$ftO.pub }
      if ([string]$ftO.end -eq 'Y') { if ($ftO.PSObject.Properties['yd'] -and $ftO.yd) { $r.yDec = ([string]$ftO.yd -replace '\s', '') }; $r.yLast = 'at {0}{2} · {1}' -f [int]$r.ckAt, (Get-Date).ToString('HH:mm', $inv), $(if ($r.yDec) { ' ' + $r.yDec } else { '' }); 'Y_CLOSED {0}: the agent closed its Y intervention ({1})' -f $Id, $(if ($ftO.yk) { $ftO.yk } else { 'no evidence key' }) }
    }
    # v3.19 (Owner, 11 Oct: "audit all triggers which are time based ... wire them with Tab status"): the parked state is RECORDED, never kept in memory.
    # Parked = the agent says only the Owner or a person can unblock it (footer blocker OWNER / PERSON / EXTERNAL with no next task, or a reply that starts with HOLD).
    $waitBk = (@('OWNER', 'PERSON', 'EXTERNAL') -contains [string]$r.fBk)
    $ownNext = @(([string]$r.fNext) -split ',' | Where-Object { $_ -and $_ -notmatch '^(OWNER|PERSON|EXTERNAL|NONE|WAIT|HOLD)' })  # v3.24 (live 16:58): next items that are all Owner / person / external gated are no next task
    if ($HoldReply -or ($waitBk -and $ownNext.Count -eq 0)) { if (-not $r.parkAt) { $r.parkAt = $now; $r.pingAt = ''; $r.parkWhy = $(if ($HoldReply) { 'HOLD reply' } else { 'blocker ' + $r.fBk + ':' + $r.fBr }) } }
    elseif ($r.parkAt -and $stO) { $r.parkAt = ''; $r.pingAt = ''; $r.parkWhy = '' }
    $lab = @($Worked -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    if ($lab.Count -eq 0 -or $State -eq 'GENERATING') { $lab = @($r.last3) }  # v3.24 (live 16:30): a running turn shows an interim 'Worked for'; only finished turns count  # v3.22 (live 15:13): a call without labels (state or link only) must not reset the stored last 3, or the next probe counts them twice
    # New labels: the part of the probe's last 3 that does not overlap the stored last 3 (so each label is counted once).
    $old = @($r.last3); $k = 0
    for ($j = [Math]::Min($old.Count, $lab.Count); $j -ge 1; $j--) { if ((@($old | Select-Object -Last $j) -join '|') -eq (@($lab | Select-Object -First $j) -join '|')) { $k = $j; break } }
    $added = @($lab | Select-Object -Skip $k)
    # v3.27 (review findings 3 and 5): turns are counted by ChatGPT's turn key (probe turns = '<key8>=<Worked for label or ->'), never by matching labels.
    if ($Turns -and $State -ne 'GENERATING') {
      $tk = @($Turns -split '\|' | Where-Object { $_ -match '=' }); $keys = @($tk | ForEach-Object { ($_ -split '=', 2)[0] })
      $labOf = { param($x) $l = ($x -split '=', 2)[1]; if (-not $l -or $l -eq '-') { '0s' } else { $l } }
      if (@($r.seenK).Count -eq 0 -and ([int]$r.turns -gt 0 -or @($r.last3).Count -gt 0)) { $nNew = [Math]::Max(0, $added.Count); $r.seenK = @($keys | Select-Object -First ([Math]::Max(0, $keys.Count - $nNew))) }  # first v3.27 look at a known chat: only what the label rule saw as new is new
      $added = @($tk | Where-Object { @($r.seenK) -notcontains ($_ -split '=', 2)[0] } | ForEach-Object { & $labOf $_ })
      $r.seenK = @(@($r.seenK) + $keys | Select-Object -Unique | Select-Object -Last 12)
      $lab = @($tk | ForEach-Object { & $labOf $_ } | Select-Object -Last 3)
    }
    $first = ($old.Count -eq 0 -and [double]$r.sumMin -eq 0)
    foreach ($a in $added) { $r.sumMin = [Math]::Round([double]$r.sumMin + (ToMin $a), 1); $r.turns = [int]$r.turns + 1 }
    if ($r.bAt -and $added.Count) { $r.bAfter = @(@($r.bAfter) + @($added | ForEach-Object { ToMin $_ })) }
    if ($first) { $r.sumPages = $Scr } elseif ($added.Count) { $r.sumPages = [Math]::Round([double]$r.sumPages + $Tp, 1) }
    if ($WkAll -gt [double]$r.sumMin) { $r.sumMin = $WkAll }
    if ($Scr -gt [double]$r.sumPages) { $r.sumPages = $Scr }
    # progress from the status line (probe st): -Prog '<done>/<total>' -Ac '<met>/<total>'; a new reply with neither moving counts toward the stall rule
    $base = ([int]$r.pd -ge 0 -or [int]$r.aca -ge 0)
    if ($Prog -match '^(\d+)/(\d+)$') { $np = [int]$Matches[1]; $r.dPd = $(if ([int]$r.pd -ge 0) { $np - [int]$r.pd } else { 0 }); $r.pd = $np; $r.pt = [int]$Matches[2] } elseif ($added.Count) { $r.dPd = 0 }
    if ($Ac -match '^(\d+)/(\d+)$') { $na = [int]$Matches[1]; $r.dAc = $(if ([int]$r.aca -ge 0) { $na - [int]$r.aca } else { 0 }); $r.aca = $na; $r.act = [int]$Matches[2] } elseif ($added.Count) { $r.dAc = 0 }
    if ($stO -and [int]$r.dPd -le 0) { $r.dPd = [int]$npl }  # v3.19: footer done= IDs are planned tasks closed
    if ($added.Count -and ($Prog -or $Ac) -and $base) { if ([int]$r.dPd -gt 0 -or [int]$r.dAc -gt 0) { $r.noProg = 0 } else { $r.noProg = [int]$r.noProg + 1 } }
    # v3.18.4 (Owner, 11 Oct 10:2x: "the problem was this never ran"): agents report finished work in their LOG line, not in my TASK EVIDENCE block,
    # so a reply's evidence count is the largest of: evidence blocks (-EvNew), done IDs (-DoneN = st.done count), and "X=done" / "..._COMPLETE" tokens in the raw LOG line.
    $tok = 0; if ($LogLine) { $tok = ([regex]::Matches($LogLine, '\b[A-Za-z0-9_-]+=done\b')).Count + ([regex]::Matches($LogLine, '\b[A-Z0-9_]*COMPLETE[A-Z0-9_]*\b')).Count }
    $evCount = [Math]::Max([Math]::Max($EvNew, $DoneN), $tok)
    if ($laneOn) {
      $evCount = 0; $r.noProg = 0; $r.dPd = 0
      if (-not $ftO) { $bsx = [Math]::Max([int]$Bs, [int]$r.bSent); if ($bsx -ge 1 -and $r.buddy -eq 'due') { $r.buddy = 's1' }; if ($bsx -ge 2 -and $r.buddy -in 's1', 's1ok', 'areview') { $r.buddy = 's2' }
        if (-not $r.stale) { $bMiss = 'no LOG line in the reply' } }
      if ($added.Count -and $bMiss -and $r.buddy -in 's1', 's2') { $r.bNeed = $(if ($r.buddy -eq 's1') { 1 } else { 2 }); $r.bWhy = $bMiss }
    }  # v3.21: Buddy stages are not TASK_EVIDENCE (Buddy README)
    $day = (Get-Date).ToString('yyyy-MM-dd', $inv); if ($r.costDay -ne $day) { $r.costDay = $day; $r.costK = 0.0 }; $r.costK = [Math]::Round([double]$r.costK + ($St.Length + $Ft.Length + $Worked.Length + $LogLine.Length + 2000) / 4000.0, 1)  # v3.26: estimated tokens my check of this chat read (probe ~2000 chars + footer), per day
    if ($added.Count) { $r.evChat = [int]$r.evChat + $evCount; $r.evLast = $evCount; $r.evN = [int]$r.evN + $evCount; $r.evSince = [int]$r.evSince + $evCount; $r.lastTp2 = $r.lastTp; $r.lastTp = $Tp }; if ($State) { $r.lastSeen = $now }; $r.fresh = [bool]$added.Count  # v3.21: a call without -State (link/title only) is not a check; if ($added.Count -or $State -eq 'GENERATING' -or -not $r.actAt) { $r.actAt = $now }
    # v3.18 (Owner, 11 Oct 07:5x: "a red tests= or PR= value twice in a row would go straight to the CI or restricted-coder path ... implement"): count fresh replies with red CI.
    if ($added.Count -and ($Tests -or $Pr) -and -not $laneOn) {  # v3.26 (live 20:49): a Buddy-lane reply (1b, 1a, 2) is not a red CI reply
      $st8 = $(if ($Pr -match ':\s*([A-Za-z-]+)\s*$') { $Matches[1].ToLower() } else { '' })
      $redT = ($Tests -match '^\s*(\d+)\s*/\s*(\d+)') -and ([int]$Matches[1] -lt [int]$Matches[2])
      if ($redT -or $st8 -match '^(red|fail|failed|failure|queued|not-run)$') { $r.redN = [int]$r.redN + 1 } else { $r.redN = 0; $r.ciSent = ''; $r.fixSent = ''; $r.rcAsk = '' }
      $r.prState = $st8; $r.lastTests = $Tests
    }
    if ($added.Count) { $r.lastBk = $Blocker.ToUpper() }
    # v3.28 sticky labels: the footer's aim / outcome / user fields (aim-lib Aim-Rule); user=no three replies in a row is a hold-point trigger (H3).
    if ($ftO -and $ftO.PSObject.Properties['aim'] -and $ftO.aim) { $r.fAim = [string]$ftO.aim; $r.fOut = [string]$ftO.outcome; if ($added.Count -and -not $laneOn) { $r.fUser = [string]$ftO.user; if ($r.fUser -match '^(?i)no') { $r.userNoN = [int]$r.userNoN + 1 } elseif ($r.fUser -match '^(?i)yes') { $r.userNoN = 0 } } }
    $r.last3 = $lab
    if ($lab.Count -ge 3 -and (Last3 $lab) -ge $RedMin) { $r.redSent = '' }
    if ($State -eq 'LIMIT') { $r.hard = 'conversation length limit' }
    elseif ($Err -match 'delivery timed out') { $r.hard = 'Message delivery timed out' }
    $r.hint = $Hint
    if ($Gen -gt 0) { $r.gen = $Gen }; if ($Rcn -gt [int]$r.rcn) { $r.rcn = $Rcn }
    if ($Log -and $Pos -and $Session -and -not $r.stale -and -not $r.unknown -and -not (MapFolder $Pos)) { $t1 = MapLearn $text $Pos (($Log -split '@')[0]) $Id; if ($t1 -ne $text) { $text = $t1; 'MAP_LEARNED tab {0} -> {1} (first footer of {2})' -f $Pos, (($Log -split '@')[0]), $Id } }
    if ($Log) { $r.folder = ($Log -split '@')[0]; $r.lastLog = $(if ($Log -match '@(.+)$') { $Matches[1] } else { '' }) }
    if (@('ERROR', 'LOADFAIL', 'NOBOX', 'UNUSUAL') -contains $State -and -not ($Err -match 'delivery timed out')) { $r.soft = @(@(Recent $r) + ($now + '|' + $State)) } else { $r.soft = @(Recent $r) }
    if ($State) { $r.lastState = $State }
    if (Save-Rec $r) { Verdict $r $lab }
    if ($doneNow -and $r.prevId) { Set-Other $r.prevId @{ aLane = 'retired' }; 'RETIRE_PREV {0}: Stage 2 is done, so the outgoing chat is retired now (urls.ps1 mark HANDED_OVER; no rename, its link stays in the records)' -f $r.prevId }
  }
  'grounded' { $r = Load-Rec; $r.redSent = $now; if (Save-Rec $r) { 'GROUNDED_RECORDED ' + $Id } }
  'recon' {
    $r = Load-Rec
    switch ($Mode) {
      'on' { $r.reconMode = 'on' } 'skip' { $r.reconMode = 'skip' } 'auto' { $r.reconMode = '' }
      'sent' { if ($Step -gt [int]$r.rcn) { $r.rcn = $Step }; if ($Step -eq 1 -and -not $r.reconDate) { $r.reconDate = (Get-Date).ToString('yyyy-MM-dd', $inv) } }
      default { 'need -Mode on|skip|auto|sent'; return }
    }
    if (Save-Rec $r) { 'RECON_RECORDED {0} {1}{2}' -f $Id, $Mode, $(if ($Step) { ' step ' + $Step } else { '' }) }
  }
  'batched' {
    $r = Load-Rec
    if ($r.bAt) { 'BATCH_KEPT {0}: the before-median from {1} stays' -f $Id, $r.bAt }
    else {
      $m = Med @($r.last3 | ForEach-Object { ToMin $_ }); $r.bAt = (Get-Date).ToString('dd MMM HH:mm', $inv); $r.bMed = $(if ($null -ne $m) { $m } else { 0.0 }); $r.bAfter = @()
      if (Save-Rec $r) { 'BATCHED_RECORDED {0}: median worked before = {1}m' -f $Id, $r.bMed }
    }
  }
  'timeout' { $r = Load-Rec; $r.soft = @(@(Recent $r) + ($now + '|probe timeout')); if (Save-Rec $r) { 'TIMEOUT_RECORDED ' + $Id; Verdict $r @($r.last3) } }
  'mark' {
    $markOther = $null
    # v3.17: record that a metric-triggered message was DELIVERED, so the same trigger does not fire again
    $r = Load-Rec
    switch ($What) {
      'checkpoint' { $r.ckAt = [int](@(5, 10, 15, 19 | Where-Object { $_ -le [int]$r.evSince } | Select-Object -Last 1)[0]) }
      'reconcile' { $r.evSince = 0; $r.ckAt = 0; $r.noProg = 0 }
      'drift' { $r.driftTurn = [int]$r.turns }
      'plandone' { $r.planDoneAt = '{0}/{1}' -f $r.pd, $r.pt }
      'soon' { $r.soonSent = $now }
      'heavy' { $r.heavySent = $now }
      'cilimit' { $r.ciLimSent = (Get-Date).ToString('yyyy-MM-dd', $inv) }
      'ci' { $r.ciSent = $now }
      'fix' { $r.fixSent = $now }
      'rc' { $r.rcAsk = $now }
      'footer' { $r.footAsk = $r.fMissing }
      'ping' { $r.pingAt = $now; $r.aimSends = [int]$r.aimSends + 1 }
      'unpark' { $r.parkAt = ''; $r.pingAt = ''; $r.parkWhy = '' }
      'buddy' { $r.buddy = 'due'; $r.bSent = 0; $r.bTry = 0; $r.bNeed = 0; $r.bPub1 = ''; $r.bPub2 = ''; $r.bWhy = '' }
      'buddy1' { $r.bSent = [Math]::Max(1, [int]$r.bSent); if ($r.buddy -in '', 'due') { $r.buddy = 's1' } }
      'buddy2' { $r.bSent = 2; $r.buddy = 's2'; $r.bTry = 0; $r.bNeed = 0 }
      'a1' { $r.aLane = 'asked' }
      'nudge' { $r.nudgeTurn = [int]$r.turns; $r.costK = [Math]::Round([double]$r.costK + 0.3, 1); $r.aimSends = [int]$r.aimSends + 1 }
      'aimintro' { $q = @($Mode -split '@'); if ($q.Count -ge 2) { $r.aimIntro = $q[1]; Set-AimField $q[0] 'groundDue' '' }; $r.aimSends = [int]$r.aimSends + 1 }
      'aimground' { $q = @($Mode -split '@'); if ($q[0]) { Set-AimField $q[0] 'groundDue' '' }; $r.aimSends = [int]$r.aimSends + 1 }
      'aimmsg' { $r.aimSends = [int]$r.aimSends + 1 }
      'areview' { $r.buddy = 'areview'; $markOther = @($r.prevId, 'aLane', 'review') }
      'retire' { $r.aLane = 'retired' }
      'bpub' { $r.bTry = [int]$r.bTry + 1; $r.bNeed = 0 }
      # v3.25 (BuddyRunner v1.6): the successor's start was delivered: the lane is done, evidence counting starts from 0, G1 is retired.
      'bstart' { $r.buddy = 'done'; $r.redN = 0; $r.ciSent = ''; $r.fixSent = ''; $r.evSince = 0; $r.ckAt = 0; $r.noProg = 0; $markOther = @($r.prevId, 'aLane', 'retired') }
      default { 'need -What aimintro|aimground|aimmsg|checkpoint|reconcile|drift|plandone|soon|heavy|ci|fix|rc|footer|ping|unpark|buddy|buddy1|buddy2|bstart|bpub|a1|areview|retire|cilimit'; return }
    }
    # v3.25 (Owner, 11 Oct snap 3: the Next column was stale): a delivered message makes this chat's Next "wait for the reply" until its next see.
    if ($What -notin 'rc', 'unpark', 'buddy', 'retire') { $r.lastKind = 'SENT'; $r.sentWhat = $What }
    if (Save-Rec $r) { 'MARKED {0} {1}' -f $Id, $What; if ($markOther -and $markOther[0]) { Set-Other $markOther[0] @{ $markOther[1] = $markOther[2] }; 'MARKED {0} {1}={2} (the other chat of this Buddy lane)' -f $markOther[0], $markOther[1], $markOther[2] } }
  }
  'carry' {
    # v3.19 (Owner, 11 Oct: "how is task evidence handled in handover"): the NEW chat gets a fresh meter (minutes, pages, turns) but continues the stream's
    # evidence cadence (evidence since the last reconcile, checkpoint level, total) and its plan fields; run it right after the brief is moved (recipe NEW-CHAT).
    if ($From -notmatch '^[0-9a-f]{8}$') { 'need -From <old id8>'; return }
    $old = $null; $mo = Get-Line $text $From; if ($mo) { $old = $mo.Groups[1].Value | ConvertFrom-Json }
    $r = Load-Rec
    if ($old) { foreach ($k in 'evN', 'evSince', 'ckAt', 'fPlan', 'fDone', 'fNext', 'fRel', 'doneHist', 'planSeen', 'repo') { if ($old.PSObject.Properties[$k]) { $r.$k = $old.$k } }; if ([int]$old.gen -gt 0) { $r.gen = [int]$old.gen + 1 } }
    $r.prevId = $From; if ($old -and $old.PSObject.Properties['fHr'] -and $old.fHv -eq 'ready') { $r.bPrompt = [string]$old.fHr }; $r.bV = '16'; $r.buddy = 'due'; $r.bSent = 0; $r.bTry = 0; $r.bNeed = 0; $r.bPub1 = ''; $r.bPub2 = ''; $r.bAss = ''; $r.bWhy = ''  # v3.21: every new chat of a work starts with Buddy
    # v3.25 (Owner, 11 Oct snap: Tab 2 showed UNKNOWN because the map step was skipped after carry): carry moves the tab map to the new chat in the same write.
    $mapMsg = ''
    if ($Session -and $Pos) { $t2 = MapSetChat $text $Pos $Id; if ($t2 -ne $text) { $text = $t2; $mapMsg = 'MAP_SET tab {0} -> chat {1} (the work''s folder and name stay)' -f $Pos, $Id } }
    else { $mapMsg = 'MAP: not moved (give -Session and -Pos): run cyclestate.ps1 map -Pos <N> -Chat ' + $Id }
    $saved = Save-Rec $r; if ($saved) { Set-Other $From @{ aLane = 'moved'; nextId = $Id } }
    if ($saved) { 'CARRIED {0} -> {1}: evidence {2} total, {3} since the last reconcile, checkpoint level {4}; meter starts at 0; Buddy lane (v1.6) due' -f $From, $Id, $r.evN, $r.evSince, $r.ckAt; $mapMsg }
  }
  'rows' { RowsOut }
  'rowsjson' {
    $script:RowsJson = New-Object System.Collections.ArrayList
    $script:RowGeneratedAtUtc = [datetime]::UtcNow.ToString('o')
    RowsOut | Out-Null
    ConvertTo-Json -InputObject @($script:RowsJson.ToArray()) -Depth 8 -Compress
  }
  'report' {
    # v3.26 (Owner, 11 Oct 20:1x: "there is very little improvement in tab status"; the runner typed a 4-column table by hand): the WHOLE report comes from
    # the records, so nothing is typed. Paste it unchanged and add only one "What changed" line (the agents' claims).
    $lines = @(RowsOut)
    $cnt = @{ y = 0; g = 0; r = 0; b = 0 }; foreach ($l in $lines) { if ($l -match '^\| Tab') { $c3 = ($l -split ' \| ')[1]; if ($c3 -match [char]::ConvertFromUtf32(0x1F7E2)) { $cnt.g++ } elseif ($c3 -match [char]::ConvertFromUtf32(0x1F534)) { $cnt.r++ } elseif ($c3 -match [char]::ConvertFromUtf32(0x1F7E1)) { $cnt.y++ } elseif ($c3 -match [char]::ConvertFromUtf32(0x1F535)) { $cnt.b++ } } }
    $need = @(); $briefs = 0
    foreach ($p in ($Tabs -split ';' | Where-Object { $_ -match '=' })) {
      $q = $p -split '='; $pos = $q[0].Trim(); $Id = $q[1].Trim(); $m = Get-Line $text $Id; if (-not $m) { continue }; $o = Load-Rec; $md = ModeOf $pos $o
      $since = $(if ($o.parkAt) { [int]((Get-Date) - [datetime]::Parse($o.parkAt, $inv)).TotalMinutes } else { -1 })
      if ($o.hard -eq 'conversation length limit') { $need += ('**Tab {0}:** the chat is full: a new chat needs your word *(answer here)*' -f $pos) }
      if ($o.buddy -eq 'blocked') { $need += ('**Tab {0}:** handover stopped: {1} *(answer here)*' -f $pos, $o.bWhy) }
      if ($o.parkAt -and $o.fBk -eq 'OWNER') { $need += ('**Tab {0}:** decisions {1} wait for you *(waiting {2} min · answer in tab {0})*' -f $pos, $(if ($o.fBr) { $o.fBr } else { '(see the tab)' }), $since) }
      if ($o.parkAt -and $o.fBk -eq 'PERSON') { $need += ('**Tab {0}:** waits on a person: {1} *(waiting {2} min)*' -f $pos, $o.fBr, $since) }
      if ($md.hold -eq 'hold' -and [double]$o.sumPages -ge 27) { $need += ('**Tab {0}:** near full at {1:N0} pages with its handover on hold: hand it over now? *(say "go Tab {0}" or "wait")*' -f $pos, [double]$o.sumPages) }
      if ($o.fHv -eq 'ready' -or ($o.aLane -eq 'asked' -and $o.fHv -eq 'ready')) { $briefs++ }
      $ui = MapInfo $pos $Id; if ($ui -eq 'new') { $need += ('**Tab {0}:** a chat I do not know ({1}): which work, or not mine? *(answer here)*' -f $pos, $Id) }
    }
    # v3.28 sticky labels: open cards are decisions (Needs you); the full report shows the labels of its tabs and the card changes of the last 24 h.
    $aimT = @(); foreach ($p in ($Tabs -split ';' | Where-Object { $_ -match '=' })) { $q = $p -split '='; $am = $(if ($Session) { Find-Aim $text $Session $q[0].Trim() } else { $null }); if ($am) { $aimT += , @($q[0].Trim(), $am) } }
    $seenW = @{}; $needNote = ''
    foreach ($x in $aimT) { $am = $x[1]; if ($seenW[$am.work]) { continue }; $seenW[$am.work] = 1
      foreach ($cd in @(Get-OpenCards $text $am.work)) { $ag = [int]((Get-Date) - [datetime]::Parse([string]$cd.raised, $inv)).TotalMinutes
        if ($cd.cls -eq 'Create') { $need += ('**Tab {0} · {1}:** new sticky label for {2} (see Labels){3} *(approve / keep / edit · waiting {4} min)*' -f $x[0], $cd.id, $am.work, $(if (-not [string]$cd.set.crit -and (Aim-Crit $am) -eq 'unknown') { ' · engineering-critical, yes or no?' } else { '' }), $ag) }
        elseif ($cd.cls -eq 'Decision') { $need += ('**Tab {0} · {1}:** {2}{3} *(answer in tab {0}, then done · waiting {4} min)*' -f $x[0], $cd.id, $cd.change, $(if ($cd.unblocks) { ' · unblocks ' + $cd.unblocks } else { '' }), $ag) }
        else { $need += ('**Tab {0} · {1}:** {2}{3}{4}{5} *(approve / keep / edit · waiting {6} min)*' -f $x[0], $cd.id, $cd.change, $(if ($cd.why) { ' · why: ' + $cd.why } else { '' }), $(if ($cd.stops) { ' · stops: ' + $cd.stops } else { '' }), $(if ($cd.unblocks) { ' · unblocks: ' + $cd.unblocks } else { '' }), $ag) } }
      if ((Aim-Crit $am) -eq 'unknown' -and -not @(Get-OpenCards $text $am.work | Where-Object { $_.cls -eq 'Create' }).Count) { $need += ('**Tab {0}:** is the work {1} engineering-critical, yes or no? *(answer here)*' -f $x[0], $am.work) } }
    if (@($need | Where-Object { $_ -match ' · CP-' }).Count -gt 1) { $needNote = '*More than one card is open: name the card in your answer, e.g. "approve CP-...".*' }
    $hm = (Get-Date).ToString('HH:mm', $inv)
    # v3.27.1 (Owner, 11 Oct 21:5x: "news vs old, why several features dropped" - I had typed a short table by hand between full reports): the short line also comes
    # from the records, so no tab status is ever typed. -Short = one line: time, decisions, each tab's dot and status, next check.
    if ($Short) { $ts = @($lines | Where-Object { $_ -match '^\| Tab\d' } | ForEach-Object { $c = $_ -split ' \| '; (($c[0] -replace '^\|\s*', '') -split ' ')[0] + ' ' + $c[1] + $(foreach ($dk in 'red', 'yellow', 'amber', 'green') { if ($c.Count -gt 2 -and $c[2].Contains($AimDot[$dk])) { ' · aim ' + $AimDot[$dk]; break } }) }); '**{0}** · {1} · {2} · next check {3} (full table at the report interval)' -f $hm, $(if ($need.Count) { '{0} decision{1} need{2} you' -f $need.Count, $(if ($need.Count -gt 1) { 's' } else { '' }), $(if ($need.Count -gt 1) { '' } else { 's' }) } else { 'nothing needs you' }), ($ts -join ' · '), $(if ($NextAt) { $NextAt } else { '<HH:MM>' }); return }
    '**{0} · {1} · {2} brief{3} ready · {4} tab{5} working · {6}**' -f $hm, $(if ($need.Count) { '{0} decision{1} need{2} you' -f $need.Count, $(if ($need.Count -gt 1) { 's' } else { '' }), $(if ($need.Count -gt 1) { '' } else { 's' }) } else { 'nothing needs you' }), $briefs, $(if ($briefs -eq 1) { '' } else { 's' }), $cnt.g, $(if ($cnt.g -eq 1) { '' } else { 's' }), $(if ($cnt.r) { '{0} problem{1}' -f $cnt.r, $(if ($cnt.r -gt 1) { 's' } else { '' }) } else { 'no problems' })
    ''; '**Needs you**'; if ($need.Count) { $i = 0; foreach ($n in $need) { $i++; '{0}. {1}' -f $i, $n } } else { 'Nothing.' }
    if ($needNote) { $needNote }
    if ($aimT.Count) { ''; '**Labels**'; $seenL = @{}
      foreach ($x in $aimT) { $am = $x[1]; if ($seenL[$am.work]) { continue }; $seenL[$am.work] = 1
        if ($am.status -eq 'ACTIVE') { $L = $am.label; 'Tab{0} {1}{2} · **Main:** {3} · **Task ({4}):** {5} · **Done when:** {6}' -f $x[0], (Aim-Ver $am), $(if ((Aim-Crit $am) -eq 'critical') { ' ' + $AimShield } else { '' }), $L.main, $L.taskOutcome, $L.task, $L.done }
        else { $cc = @(Get-OpenCards $text $am.work | Where-Object { $_.cls -eq 'Create' })[0]; if ($cc) { $s0 = $cc.set; 'Tab{0} draft {1}{2} · **Problem:** {3} · **Main:** {4} · **Outcomes:** {5}{6} · **Task ({7}):** {8} · **Done when:** {9}{10}' -f $x[0], $cc.id, $(if ((Aim-Crit $am) -eq 'critical' -or [string]$s0.crit -eq 'critical') { ' ' + $AimShield } else { '' }), $s0.problem, $s0.main, ((Aim-Outs $s0) -join '; '), $(if (@($s0.constraints | Where-Object { $_ }).Count) { ' · **Owner constraints:** ' + (@($s0.constraints | Where-Object { $_ }) -join '; ') } else { '' }), $s0.taskOutcome, $s0.task, $s0.done, $(if (@($s0.park | Where-Object { $_ }).Count) { ' · **Not now:** ' + (@($s0.park | Where-Object { $_ }) -join '; ') } else { '' }) } } } }
    ''; $lines
    $chg = @(); foreach ($x in $aimT) { foreach ($cd in @(Get-Cards $text $x[1].work | Where-Object { $_.decided -and ((Get-Date) - [datetime]::Parse([string]$_.decided, $inv)).TotalHours -le 24 })) { $chg += ('{0} {1} {2}' -f $cd.id, ([string]$cd.state).ToLower(), ([datetime]::Parse([string]$cd.decided, $inv)).ToString('HH:mm', $inv)) } }
    if ($chg.Count) { ''; '**Aim changes (24 h):** ' + (@($chg | Select-Object -Unique) -join ' · ') }
    ''; '**What changed:** <one line: what the agents say, as their claims>'
    ''; '**Next check:** ' + $(if ($NextAt) { $NextAt } else { '<HH:MM>' })
  }
  'due' {
    # v3.26: what this firing does per tab (Owner: Speed = urgent, Economy = long-running). Speed tabs get the full check every firing; Economy tabs only the
    # page-watcher read (one javascript call for all of them, PEEK_JS), and the full check only when it says CHANGED / ERROR / WATCHER_*.
    $full = @(); $peek = @()
    foreach ($p in ($Tabs -split ';' | Where-Object { $_ -match '=' })) {
      $q = $p -split '='; $pos = $q[0].Trim(); $Id = $q[1].Trim(); $o = Load-Rec; $md = ModeOf $pos $o
      $lane = (($o.buddy -and $o.buddy -notin 'done', 'blocked') -or $o.aLane -in 'asked', 'review')
      $how = $(if ($md.speed -eq 'speed') { 'FULL' } else { 'PEEK' })
      'DUE Tab {0} {1} {2}: {3}{4}' -f $pos, $Id, (Badge $md), $how, $(if ($lane) { ' (Buddy lane: only its reply matters)' } else { '' })
      if ($how -eq 'FULL') { $full += $pos } else { $peek += $Id }
    }
    $cy = $null; $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})'); if ($mm.Success) { $cy = $mm.Groups[1].Value | ConvertFrom-Json }
    $lf = $(if ($cy -and $cy.lastFull) { ((Get-Date) - [datetime]::Parse($cy.lastFull, $inv)).TotalMinutes } else { 9999 })
    $every = $(if ($full.Count) { 20 } else { 30 })
    # v3.28 (review: with no new evidence no checkpoint fires; on 11-12 Oct, 22:35-02:48, I checked 17 times and nothing changed): every tab quiet for 3 cycles
    # and parked on the Owner -> one ranked decision card, and the heartbeat backs off to 60 min until a tab changes or the Owner answers.
    $stall = @(); $live = 0
    foreach ($p in ($Tabs -split ';' | Where-Object { $_ -match '=' })) { $q = $p -split '='; $Id = $q[1].Trim(); $o = Load-Rec; if (-not $o.lastSeen) { continue }; $live++
      $qm = $(if ($o.actAt) { ((Get-Date) - [datetime]::Parse($o.actAt, $inv)).TotalMinutes } else { 9999 }); if ($o.parkAt -and $qm -ge 3 * $Cycle) { $stall += ('Tab{0} quiet {1:N0} min' -f $q[0].Trim(), $qm) } }
    if ($live -and $stall.Count -eq $live) { 'STALL: no new activity and every tab waits on the Owner ({0}) - give ONE ranked decision card in the report (what unblocks most), then back the heartbeat off to 60 min (CronDelete + CronCreate, cyclestate set -Cycle 60) until a tab changes or the Owner answers; then return to the Owner''s cycle' -f ($stall -join ', ') }
    if ($peek.Count) { 'PEEK_JS: window.__coord.peekAll(''' + ($peek -join ',') + ''')' }
    if ($lf -ge $every) { 'REPORT_DUE: full report now (last {0}; every {1} min) - watch.ps1 -Action report' -f $(if ($lf -lt 9999) { '{0:N0} min ago' -f $lf } else { 'never' }), $every } else { 'REPORT: one short line (full report in {0:N0} min); silent if nothing changed and nothing needs the Owner' -f ($every - $lf) }
  }
  'peek' {
    # v3.24 (Owner, 11 Oct 16:3x: "pass 1 is not a trigger for the agent but for you, to see which tab earlier than the standard cycle; if pass 1 finds
    # task evidence changes it should trigger pass 2, else no trigger"). READ-ONLY: compares the probe with the record and writes nothing, so pass 2 still
    # sees the new reply as new. CHANGED = a finished reply since the last full check (new Worked-for label), a different footer, or a new error / full state.
    $m0 = Get-Line ([IO.File]::ReadAllText($StateFile, $utf8)) $Id
    if (-not $m0) { 'PEEK_CHANGED {0}: no record yet (new chat) -> run pass 2 now' -f $Id; return }
    $o = $m0.Groups[1].Value | ConvertFrom-Json
    $lab = @($Worked -split '\|' | ForEach-Object { $_.Trim() } | Where-Object { $_ }); $old = @($o.last3); $k = 0
    for ($j = [Math]::Min($old.Count, $lab.Count); $j -ge 1; $j--) { if ((@($old | Select-Object -Last $j) -join '|') -eq (@($lab | Select-Object -First $j) -join '|')) { $k = $j; break } }
    $new = @($lab | Select-Object -Skip $k)
    $line = ''; if ($Ft) { try { $line = [string](($Ft | ConvertFrom-Json).line) } catch { } }
    $why = $(if ($State -eq 'GENERATING') { '' } elseif ($new.Count -and $State -eq 'IDLE') { 'finished reply (' + ($new -join ', ') + ')' } elseif ($line -and $line -ne [string]$o.fLine -and $State -eq 'IDLE') { 'footer changed' } elseif (@('ERROR', 'LOADFAIL', 'LIMIT', 'UNUSUAL', 'NOBOX') -contains $State -and $State -ne [string]$o.lastState) { 'state ' + $State } else { '' })
    if ($why) { 'PEEK_CHANGED {0}: {1} -> run pass 2 now' -f $Id, $why } else { 'PEEK_SAME {0}: {1}' -f $Id, $(if ($State -eq 'GENERATING') { 'still working' } else { 'no new task evidence' }) }
  }
  'cycle' {
    # v3.27 (review: "direct raw-probe transfer and compact cycle output"): ONE call for all probed chats. -Probes = a JSON array of window.__coord.mini()
    # results, pasted unchanged. Each chat is matched to its tab by the map (or as the Buddy-lane predecessor of the mapped chat), then `see` runs for it
    # and only the lines that matter are printed. Unknown chats get nothing.
    $self = [scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\watch.ps1', $utf8))
    $pa = $Probes | ConvertFrom-Json; $arr = @($pa | ForEach-Object { $_ }); $seenT = @()  # PS 5.1 returns a JSON array as one object: enumerate it
    $mm = [regex]::Match($text, '(?m)^[ \t]*"claude_code_cycle_' + ($Session -replace '[^A-Za-z0-9_]', '') + '":[ \t]*(\{.*\})')
    $ents = $(if ($mm.Success) { @(@(($mm.Groups[1].Value | ConvertFrom-Json).map) | Where-Object { $_ } | ForEach-Object { , @($_ -split '\|') }) } else { @() })
    foreach ($p in $arr) {
      $cid = [string]$p.id; $pos = 0
      foreach ($q in $ents) { if ($q[1] -eq $cid) { $pos = [int]$q[0] } }
      if (-not $pos) { foreach ($q in $ents) { if ($q[1]) { $pm = Get-Line $text $q[1]; if ($pm -and ($pm.Groups[1].Value | ConvertFrom-Json).prevId -eq $cid) { $pos = [int]$q[0] } } } }
      if (-not $pos) { 'CYCLE {0}: not one of the mapped tabs - send nothing; ask the Owner which tab this is' -f $cid; continue }
      $a = @{ Action = 'see'; Id = $cid; Pos = $pos; Session = $Session; Cycle = $Cycle; StateFile = $StateFile; State = [string]$p.state; Worked = (@($p.worked) -join '|'); Turns = (@($p.turns) -join '|')
        WkAll = [double]$p.wkAll; Scr = [double]$p.scr; Tp = [double]$p.tp; Stage = [string]$p.stage; Bs = [int]$p.bs; Url = [string]$p.url; Title = [string]$p.title; Repo = [string]$p.repo; HoldReply = [bool]$p.hold }
      if ($Meter) { $a.Meter = $Meter }; if ($RepoVis) { $a.RepoVis = $RepoVis }; if ($p.err) { $a.Err = [string]$p.err }
      if ($p.st) { $a.St = (ConvertTo-Json -InputObject $p.st -Depth 6 -Compress) }; if ($p.ft) { $a.Ft = (ConvertTo-Json -InputObject $p.ft -Depth 6 -Compress) }
      $o = @(& $self @a)
      'Tab{0} {1} {2}{3}' -f $pos, $cid, $p.state, $(if ($p.errQuoted) { ' (quoted error text ignored: ' + $p.errQuoted + ')' } else { '' })
      $o | Where-Object { $_ -match '^(ACTION|SEND|MARK|STALE|TAB_|UNKNOWN|Y_CLOSED|BUDDY_DONE|RETIRE_PREV|HANDOVER_HELD|HANDOVER_DUE|MILESTONE|NOTE|LIMIT|JUDGE|anchor|bad json|state file)' } | ForEach-Object { '  ' + $_ }
      $seenT += ('{0}={1}' -f $pos, $cid)
    }
    if ($seenT.Count) { $csb = [scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\cyclestate.ps1', $utf8)); [void](& $csb -Action seen -Session $Session -Tabs ($seenT -join ';') -StateFile $StateFile) }
  }
  'gate' {
    # v3.23 F2 (Owner, 11 Oct RCA): no message without a `see` of that chat in this cycle; recipe SEND runs this first.
    $r = Load-Rec
    $age = $(if ($r.lastSeen) { ((Get-Date) - [datetime]::Parse($r.lastSeen, $inv)).TotalMinutes } else { 9999 })
    if ($age -le [Math]::Max(5, $Cycle / 2)) { 'GATE_OK {0}: seen {1:N0} min ago, last action {2}' -f $Id, $age, $r.lastKind }
    else { 'GATE_STOP {0}: no watch see of this chat in this cycle (last {1}) - run STEP 3b first, then send what its ACTION says' -f $Id, $(if ($r.lastSeen) { '{0:N0} min ago' -f $age } else { 'never' }) }
  }
  'show' {
    foreach ($m in [regex]::Matches($text, '(?m)^[ \t]*"claude_code_hw_([0-9a-f]{8})":[ \t]*(\{.*\}),?')) {
      $o = $m.Groups[2].Value | ConvertFrom-Json
      if ($Id -and $o.id -ne $Id) { continue }
      'HW {0}: cum {1:N0} min, {2:N0} pages, {3} turns since {4}; hard {5}' -f $o.id, [double]$o.sumMin, [double]$o.sumPages, $o.turns, $o.firstAt, $(if ($o.hard) { $o.hard } else { '-' })
    }
  }
}
