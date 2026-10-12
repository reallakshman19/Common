# Shared state-file writes (v3.27, Owner 11 Oct 21:0x: "my records move to their own file"; review finding 4: read-modify-write without a lock loses updates).
# Every coordinator script dot-sources this file and saves with Commit-Diff instead of WriteAllText:
#   . ([scriptblock]::Create([IO.File]::ReadAllText('C:\Users\reall\.claude\skills\coordinator-protocol\scripts\state-io.ps1')))
#   $saved = Commit-Diff $StateFile $text $new     # $text = what this script read and changed, $new = its changed copy
# Under ONE named lock (all coordinator sessions share it) it re-reads the file, applies only the claude_code_* lines this script added, changed or
# removed, checks the JSON and swaps the file in atomically (write a temp file, then File.Replace). Another session's lines written meanwhile survive.
# It returns the merged text (assign it to $text), or $null when nothing could be written (the caller reports it).
$CoordStateDefault = 'C:\Users\reall\.claude\coordinator-state.json'
function Get-StateLines($t) {
  $d = [ordered]@{}
  foreach ($m in [regex]::Matches([string]$t, '(?m)^[ \t]*"(claude_code_[^"]+)":[^\r\n]*')) { if ($m.Groups[1].Value -ne 'claude_code_log_anchor') { $d[$m.Groups[1].Value] = $m.Value.Trim() } }
  $d
}
function Commit-Diff($path, $old, $new) {
  $anc = '"claude_code_log_anchor": 0,'; $enc = New-Object System.Text.UTF8Encoding($false)
  $a = Get-StateLines $old; $b = Get-StateLines $new
  $chg = [ordered]@{}
  foreach ($k in $b.Keys) { if (-not $a.Contains($k) -or $a[$k] -ne $b[$k]) { $chg[$k] = $b[$k] } }
  foreach ($k in $a.Keys) { if (-not $b.Contains($k)) { $chg[$k] = '' } }
  $mx = New-Object System.Threading.Mutex($false, 'Global\ClaudeCoordinatorState'); $got = $false
  try { $got = $mx.WaitOne(15000) } catch [System.Threading.AbandonedMutexException] { $got = $true }
  if (-not $got) { $mx.Dispose(); return $null }
  try {
    $t = $null; for ($i = 0; $i -lt 5 -and $null -eq $t; $i++) { try { $t = [IO.File]::ReadAllText($path, $enc) } catch { Start-Sleep -Milliseconds 200 } }
    if ($null -eq $t -or -not $t.Contains($anc)) { return $null }
    foreach ($k in $chg.Keys) {
      $m = [regex]::Match($t, '(?m)^[ \t]*"' + [regex]::Escape($k) + '":[^\r\n]*\r?\n?')
      if ($m.Success) { $t = $t.Remove($m.Index, $m.Length) }
      if ($chg[$k]) { $ln = $chg[$k]; if (-not $ln.EndsWith(',')) { $ln += ',' }; $t = $t.Replace($anc, $ln + "`n  " + $anc) }
    }
    try { [void]($t | ConvertFrom-Json) } catch { return $null }
    $tmp = $path + '.' + [guid]::NewGuid().ToString('N').Substring(0, 8) + '.tmp'
    [IO.File]::WriteAllText($tmp, $t, $enc)
    $ok = $false; for ($i = 0; $i -lt 5 -and -not $ok; $i++) { try { [IO.File]::Replace($tmp, $path, [NullString]::Value); $ok = $true } catch { Start-Sleep -Milliseconds 200 } }
    if (-not $ok) { Remove-Item $tmp -ErrorAction SilentlyContinue; return $null }
    return $t
  }
  finally { $mx.ReleaseMutex(); $mx.Dispose() }
}
