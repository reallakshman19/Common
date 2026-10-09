/* Manual/CI read-only public provider currentness check. No GitHub mutations. */
import {readFileSync} from 'node:fs';
import {auditNativeProvider,nativeGithubGet} from './audit-native-provider-v1.mjs';

const manifest = JSON.parse(readFileSync(new URL('./migration-manifest-v1.json',import.meta.url),'utf8'));
const audit = await auditNativeProvider(manifest,
  (slug,path)=>nativeGithubGet(slug,path,{token:process.env.GITHUB_TOKEN||''}));
console.log(JSON.stringify({
  schema:audit.schema,current:audit.current,errors:audit.errors,
  provider_identity:audit.provider_identity,owner_authenticated:audit.owner_authenticated,
  reviewed:audit.reviewed,evidence_accepted:audit.evidence_accepted,
  writer_authorized:audit.writer_authorized,
  programme_acceptance:audit.programme_acceptance,
},null,2));
if(!audit.current) process.exitCode=1; // stale/paginated/rate-limited source = HOLD
