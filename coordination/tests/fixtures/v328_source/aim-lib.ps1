# Sticky labels: shared functions (v3.28, architecture v2: references/aim-architecture.md).
# Owner, 12 Oct 2026: "update the skill inline with architecture"; v2 folds in the review of v1 (Owner: "Yes"); criticality is asked per work at
# the start (Owner: "Based on Criticality. Initially itself ask if the project is Engg Critical or Not").
# Dot-sourced by aim.ps1, watch.ps1 and onboard.ps1:
#   . ([scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\aim-lib.ps1')))
# Records in the state file: claude_code_aim_<WORK> (label, guidance, bindings, history, last judgement, adoption, publication),
# claude_code_cp_<WORK>_<nn> (change cards), claude_code_judge_<WORK>_<stamp> (judgements, last 20 per work).
# Master copy of a label: relay/AIM/<WORK>.yaml on main of reallakshman19/Common (Owner, 12 Oct: "in main folder ... each folder hosting relay
# detail of v3.5"), beside relay/ROADMAP, WORK, CONTROLS, CHECKPOINTS. The work name is the global ID; "Tab N" is a per-session alias.
$AimRepo = 'reallakshman19/Common'; $AimDir = 'relay/AIM'
$AimDot = @{ green = [char]::ConvertFromUtf32(0x1F7E2); amber = [char]::ConvertFromUtf32(0x1F7E0); red = [char]::ConvertFromUtf32(0x1F534); yellow = [char]::ConvertFromUtf32(0x1F7E1); none = [string][char]0x26AA }
$AimShield = [char]::ConvertFromUtf32(0x1F6E1)
function Get-AimRecs([string]$t) {
  $o = @(); foreach ($m in [regex]::Matches($t, '(?m)^[ \t]*"claude_code_aim_[^"]+":[ \t]*(\{.*\}),?[ \t]*\r?$')) { try { $o += ($m.Groups[1].Value | ConvertFrom-Json) } catch { } }; $o
}
function Get-AimRec([string]$t, [string]$work) {
  $m = [regex]::Match($t, '(?m)^[ \t]*"claude_code_aim_' + [regex]::Escape($work) + '":[ \t]*(\{.*\}),?[ \t]*\r?$'); if ($m.Success) { $m.Groups[1].Value | ConvertFrom-Json } else { $null }
}
# The work bound to a tab of a session (binding = 'Session:pos|folder').
function Find-Aim([string]$t, [string]$session, $pos) {
  $k = '{0}:{1}' -f $session, $pos; foreach ($a in @(Get-AimRecs $t)) { foreach ($b in @($a.bind)) { if (([string]$b -split '\|')[0] -eq $k) { return $a } } }; $null
}
function Get-Cards([string]$t, [string]$work = '') {
  $o = @(); foreach ($m in [regex]::Matches($t, '(?m)^[ \t]*"claude_code_cp_[^"]+":[ \t]*(\{.*\}),?[ \t]*\r?$')) { try { $c = $m.Groups[1].Value | ConvertFrom-Json; if (-not $work -or $c.work -eq $work) { $o += $c } } catch { } }; $o
}
function Get-OpenCards([string]$t, [string]$work = '') { @(Get-Cards $t $work | Where-Object { $_.state -eq 'PROPOSED' } | Sort-Object raised) }
function Aim-Ver($a) { 'v{0}.{1}.{2}' -f [int]$a.vMain, [int]$a.vTask, [int]$a.vGuide }
function Aim-Crit($a) { $c = [string]$a.crit; if ($c -in 'critical', 'standard') { $c } else { 'unknown' } }
function Aim-Outs($L) { @($L.outcomes.PSObject.Properties | ForEach-Object { '{0} {1}' -f $_.Name, $_.Value }) }
function Aim-Pending($a) { ([string]$a.label.done) -match '^\s*PENDING' }
# Label block = what only the Owner changes (problem, main aim, outcomes, constraints, criticality, task aim, done when). Its hash identifies it.
function Aim-Canon($a) { $L = $a.label; (@('critical=' + (Aim-Crit $a), 'problem=' + $L.problem, 'main=' + $L.main) + @($L.outcomes.PSObject.Properties | ForEach-Object { $_.Name + '=' + $_.Value }) + @(@($L.constraints | Where-Object { $_ }) | ForEach-Object { 'constraint=' + $_ }) + @('taskOutcome=' + $L.taskOutcome, 'task=' + $L.task, 'done=' + $L.done)) -join "`n" }
function Aim-Sha($a) { $h = [System.Security.Cryptography.SHA256]::Create(); try { -join ($h.ComputeHash([Text.Encoding]::UTF8.GetBytes((Aim-Canon $a))) | ForEach-Object { $_.ToString('x2') }) } finally { $h.Dispose() } }
function Aim-Sha7($a) { $s = [string]$a.sha; $s.Substring(0, [Math]::Min(7, $s.Length)) }
function Aim-Tabs($a) { (@(@($a.bind | Where-Object { $_ }) | ForEach-Object { 'Tab ' + ((([string]$_ -split '\|')[0] -split ':')[1]) }) -join ', ') }
# The label as one paragraph for prompts and messages: the Owner's words, word for word, with the guidance that is in force.
function Aim-Block($a) {
  $L = $a.label; $cs = @($L.constraints | Where-Object { $_ }); $wt = @($a.watch | Where-Object { $_ }); $nn = @($a.notNow | Where-Object { $_ })
  ('STICKY LABEL {0} (the Owner''s words; do not paraphrase; master {1}/{2}.yaml on main of {3}, label_sha {4}; engineering-critical: {5}): Problem: {6} Main aim: {7} Outcomes: {8}.' -f (Aim-Ver $a), $AimDir, $a.work, $AimRepo, (Aim-Sha7 $a), $(if ((Aim-Crit $a) -eq 'critical') { 'yes' } elseif ((Aim-Crit $a) -eq 'standard') { 'no' } else { 'not set' }), $L.problem, $L.main, ((Aim-Outs $L) -join '; ')) +
  $(if ($cs.Count) { ' Owner constraints: ' + ($cs -join '; ') + '.' } else { '' }) +
  (' Task aim ({0}): {1} Done when: {2}' -f $L.taskOutcome, $L.task, $L.done) +
  $(if ($nn.Count) { ' Not now (Owner-approved, with the condition that brings it back): ' + ($nn -join '; ') + '.' } else { '' }) +
  $(if ($wt.Count) { ' Watch for (not forbidden; say how it serves an outcome if you do it): ' + ($wt -join '; ') + '.' } else { '' })
}
# What the agent adds so the coordinator can judge each task from its evidence and footer (and inspect the proof).
function Aim-Rule($a) { 'Open each TASK EVIDENCE with three lines: Outcome: <one of ' + (@($a.label.outcomes.PSObject.Properties | ForEach-Object { $_.Name }) -join ', ') + ', or the outcome a prerequisite serves>; For the user: <what changed in the user''s real workflow, or nothing yet>; Proof: <link to the run, test or output that shows it with the real workflow and inputs>. Add aim=' + (Aim-Ver $a) + ' | outcome=<outcome> | user=<yes or no> to the LOG line. If you think the label is wrong, add one line Aim request: <30 words>; never change it yourself.' }
function Aim-Questions() { 'In 3 plain sentences: what got better in the user''s real workflow from your last 3 tasks (with proof); what is still broken; why your next step is the shortest path to the task aim, and which outcome a prerequisite serves.' }
# The Ground questions ride on a message that is being sent anyway (every 3rd one, Owner 8 Oct) or introduce a new label version.
function Aim-Ground($a, [switch]$New) {
  $(if ($New) { 'New sticky label version from the Owner for this work. Re-plan against it before your next task: map your plan and next action to its outcomes, and say which earlier evidence still applies. ' } else { 'Step back to the Owner''s sticky label. ' }) + (Aim-Block $a) + ' ' + (Aim-Questions) + ' ' + (Aim-Rule $a) + ' Then continue with the next task that moves the task aim, and end with the LOG line in its code block.'
}
function YQ([string]$s) { '"' + ([string]$s).Replace('\', '\\').Replace('"', '\"').Replace("`r", ' ').Replace("`n", ' ') + '"' }
function YList($o, [string]$name, $vals, [string]$ind) { $v = @($vals | Where-Object { $_ }); if ($v.Count) { $o.Add($ind + $name + ':'); foreach ($x in $v) { $o.Add($ind + '  - ' + (YQ $x)) } } else { $o.Add($ind + $name + ': []') } }
# The master file. label = only the Owner changes it; guidance steers and is versioned too; history is append-only.
function Aim-Yaml($a) {
  $L = $a.label; $o = New-Object System.Collections.Generic.List[string]
  $o.Add('# Sticky label: the Owner''s aim for this work. Master copy, written by the coordinator (skill coordinator-protocol, scripts/aim.ps1)')
  $o.Add('# only after the Owner approves a change card. The label text is the Owner''s: never paraphrase it. Guidance (watch, not_now, notes) is')
  $o.Add('# versioned too: a change of what may be done is a change of the label. Every copy carries version and label_sha.')
  $o.Add('work: ' + (YQ $a.work)); $o.Add('repository: ' + (YQ $a.repo)); $o.Add('engineering_critical: ' + (YQ (Aim-Crit $a)))
  $o.Add('version: ' + (YQ ((Aim-Ver $a).TrimStart('v')))); $o.Add('label_sha: ' + (YQ (Aim-Sha7 $a)))
  $o.Add('label:'); $o.Add('  problem: ' + (YQ $L.problem)); $o.Add('  main_aim: ' + (YQ $L.main)); $o.Add('  outcomes:')
  foreach ($p in $L.outcomes.PSObject.Properties) { $o.Add('    ' + $p.Name + ': ' + (YQ $p.Value)) }
  YList $o 'owner_constraints' $L.constraints '  '
  $o.Add('  task_outcome: ' + (YQ $L.taskOutcome)); $o.Add('  task_aim: ' + (YQ $L.task)); $o.Add('  done_when: ' + (YQ $L.done))
  $o.Add('guidance:'); YList $o 'not_now' $a.notNow '  '; YList $o 'watch' $a.watch '  '; YList $o 'notes' $a.notes '  '
  $o.Add('bindings:'); foreach ($b in @($a.bind | Where-Object { $_ })) { $q = ([string]$b -split '\|'); $o.Add('  - ' + (YQ ($q[0] + $(if ($q.Count -gt 1 -and $q[1]) { ' ' + $q[1] } else { '' })))) }
  $o.Add('history:'); foreach ($h in @($a.hist | Where-Object { $_ })) { $o.Add('  - ' + (YQ $h)) }
  ($o -join "`n") + "`n"
}
