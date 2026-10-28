/* RELAY RESET G2c #829: one real GitHub read -> actual R2-B1 -> actual
 * G1 journal provenance bridge. No independent Owner authentication or writers.
 */
import {createHash} from 'node:crypto';
import {canonicalJSON} from './provenance-v1.mjs';
import {readCommittedPortableJournalForLineage} from './github-bundle-custody-v1.mjs';
import {projectVerifiedPortableReplay} from './journal-provenance-bridge-v1.mjs';

export class GitHubLineageError extends Error {
  constructor(code,message){super(code+': '+message);this.name='GitHubLineageError';this.code=code;}
}
const fail=(code,message)=>{throw new GitHubLineageError(code,message);};
const equal=(a,b)=>canonicalJSON(a)===canonicalJSON(b);
const sha256=x=>createHash('sha256').update(x).digest('hex');

/**
 * A single fixed GitHub GET produces native content witness and real B1 replay.
 * Replay flows IN MEMORY to the actual G1 bridge: never re-download, synthesize
 * a parallel journal or join two unrelated caller-provided hash-only summaries.
 * The R1 structural OwnerIntent seed and event IDs are caller-supplied claims;
 * they remain unverified even when the bytes are genuinely committed.
 */
export async function projectCommittedGithubLineage(spec,seed,bindings,options={}) {
  const {custody,replay}=await readCommittedPortableJournalForLineage(spec,options);
  if(!replay||custody.bundle_sha256!==replay.bundle_sha256
    ||custody.source_sha!==replay.source_sha||custody.parent_issue!==replay.parent_issue
    ||custody.repository!==replay.repository
    ||!equal(custody.tip,replay.tip)||!equal(custody.session_ids,replay.session_ids))
    fail('SOURCE_REPLAY_MISMATCH','native custody witness differs from same-read R2-B1 replay');
  const lineage=projectVerifiedPortableReplay(replay,seed,bindings);
  if(lineage.document.parent_issue!==custody.parent_issue
    ||!equal(lineage.journal_tip,custody.tip)
    ||!equal(lineage.document.sessions.map(s=>s.id).sort(),custody.session_ids.slice().sort()))
    fail('SOURCE_LINEAGE_MISMATCH','GitHub source identity differs from derived R1 lineage');
  const digest=sha256(canonicalJSON({
    repository:custody.repository,parent_issue:custody.parent_issue,
    commit_sha:custody.commit_sha,path:custody.path,
    git_blob_sha1:custody.git_blob_sha1,bundle_sha256:custody.bundle_sha256,
    tip_sha256:custody.tip.sha256,policy_sha256:custody.policy_sha256,
    lineage_sha256:lineage.projection_sha256
  }));
  return Object.freeze({
    schema:'relay-github-to-r1-lineage-v1',
    status:custody.provider_bytes_observed?'GITHUB_BYTES_TO_STRUCTURAL_LINEAGE':'INJECTED_UNVERIFIED_STRUCTURAL_LINEAGE',
    custody,lineage,source_lineage_sha256:digest,
    original_chat_source:'UNKNOWN',
    owner_message_authenticated:false,externally_anchored:false,
    authorization_granted:false,independently_accepted:false,
    live_writer_enabled:false
  });
}
