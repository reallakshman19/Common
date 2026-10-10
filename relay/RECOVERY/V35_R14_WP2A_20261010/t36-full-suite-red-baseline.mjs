/* #294 T36: executable, IMMUTABLE PR323 RED baseline; not a CI waiver.
 * Runs original 283-test full WP2-A suite from pinned PR323 commit, NOT
 * from this diagnostic branch. Exact failures must match; any change is
 * UNVERIFIED, never silently recorded as new acceptance.
 */
import {spawnSync} from 'node:child_process';
import {readdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {pathToFileURL} from 'node:url';

export const PINNED_SOURCE_HEAD='b6b6daabe6defb253bac9dd00ce7ad48081a1000';
const DIR='relay/RECOVERY/V35_R14_WP2A_20261010';
export const FAILURES=Object.freeze({
 T03:Object.freeze([
  'T03 transition supplies exact numeric run id without revealing check name',
  'T03 member arrival remains a refusal, bounded redacted diff',
  'T03 stable second read is not a positive native CI or evidence attestation',
 ]),
 T05:Object.freeze([
  'T05 same PR308 head: genuine U01-U04 source vector consumed by unmodified WP2-B but NEVER E',
  'T05 provider required-CI policy 403 remains UNKNOWN with NO admission',
  'T05 same-source current comment still cannot mint R3 witness/DELP or reviewer',
 ]),
 T14:Object.freeze([
  'T14 original eight physical source blobs proven in two rounds, only read-only',
  'T14 wrong original source byte under unchanged Git metadata refuses',
  'T14 changed actual blob SHA under earlier source manifest refuses',
  'T14 actual PR308 moving after first read prevents old facts admission',
  'T14 PR moves at late GET within first pass',
  'T14 old repository identity denies all source facts',
  'T14 provider failure cannot leak secrets or mint native grade',
 ]),
 PHYSICAL_U01_U04:Object.freeze([
  'physical U01-U04: clean selected and required checks do not admit historical E',
  'green selected check with unreadable required policy is UNKNOWN',
  'failed required check is source fact, not accepted evidence',
  'wrong GitHub App identity cannot satisfy a required status check',
  'edited comment between full U04 cycles invalidates snapshot',
  'CI run id changes between cycles invalidates the snapshot',
  'base branch tip changes between cycles invalidates the snapshot',
  'duplicate selected check names do not count as one required success',
 ]),
});
const NEVER={evidence_admitted:false,required_ci_qualified:false,
 writer_authorized:false,delp_projection:'NOT_CALCULATED',
 parent_acceptance:'AC0/8',release_ready:false};

export function classifyTap(tap,exitCode){
 const lines=String(tap).split(/\r?\n/);
 const names=lines.map(l=>/^not ok\s+\d+\s+-\s+(.+)$/.exec(l)?.[1]).filter(Boolean);
 const summary={};
 for(const l of lines){
  const m=/^# (tests|pass|fail|skipped)\s+(\d+)\s*$/.exec(l);
  if(m)summary[m[1]]=Number(m[2]);
 }
 const expected=Object.values(FAILURES).flat();
 const wanted=new Set(expected),seen=new Set(names);
 const missing=expected.filter(n=>!seen.has(n));
 const unexpected=names.filter(n=>!wanted.has(n));
 const duplicates=names.length!==seen.size;
 const valid=exitCode===1&&summary.tests===283&&summary.pass===262&&
  summary.fail===21&&summary.skipped===0&&
  names.length===21&&expected.length===21&&missing.length===0&&
  unexpected.length===0&&!duplicates;
 return {
  schema:'v35-294-t36-pinned-exact-source-full-suite-red-v1',
  source_head:PINNED_SOURCE_HEAD,
  result:valid?'EXACT_21_FAILURE_RED_BASELINE_REPRODUCED':'BASELINE_UNVERIFIED',
  baseline_is_release_success:false,
  process_exit_code:exitCode??null,totals:summary,
  failures_by_group:Object.fromEntries(Object.entries(FAILURES).map(
   ([group,items])=>[group,items.filter(n=>seen.has(n)).length])),
  observed_failure_names:names,missing_expected_names:missing,
  unexpected_failure_names:unexpected,duplicates,...NEVER
 };
}
export function runPinnedBaseline(root){
 if(typeof root!=='string'||!root)throw Error('PINNED_ROOT_REQUIRED');
 const cwd=resolve(root);
 const rev=spawnSync('git',['rev-parse','HEAD'],{cwd,encoding:'utf8'});
 if(rev.status!==0||rev.stdout.trim()!==PINNED_SOURCE_HEAD)
  throw Error('T36_PINNED_SOURCE_HEAD_MISMATCH');
 const files=readdirSync(join(cwd,DIR)).filter(x=>x.endsWith('.test.mjs')).sort()
   .map(x=>join(DIR,x));
 if(files.length<10)throw Error('T36_TEST_SUITE_INCOMPLETE');
 const run=spawnSync(process.execPath,
  ['--test','--test-reporter=tap',...files],
  {cwd,encoding:'utf8',maxBuffer:16000000,timeout:90000});
 if(run.error)throw Error('T36_NODE_RUN_UNVERIFIED');
 return classifyTap(run.stdout,run.status);
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 try{
  const report=runPinnedBaseline(process.argv[2]);
  console.log(JSON.stringify(report,null,2));
  if(report.result!=='EXACT_21_FAILURE_RED_BASELINE_REPRODUCED')process.exitCode=1;
 }catch(e){
  console.error('T36_PINNED_RED_BASELINE_UNVERIFIED; '+String(e.message).replace(/[^A-Z0-9_ -]/gi,''));
  process.exitCode=1;
 }
}
