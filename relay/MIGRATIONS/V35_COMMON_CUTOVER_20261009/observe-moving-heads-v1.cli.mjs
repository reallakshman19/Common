/* Read-only live current-source observation across moving PRs.
 * No GitHub write, reviewers, acceptance, custody or Owner authentication.
 */
import {readFileSync} from 'node:fs';
import {observeLiveMovingHeads} from './observe-moving-heads-v1.mjs';

const manifest=JSON.parse(readFileSync(new URL('./migration-manifest-v1.json',import.meta.url),'utf8'));
const result=await observeLiveMovingHeads(manifest,{token:process.env.GITHUB_TOKEN||''});
console.log(JSON.stringify(result,null,2));
if(!result.current) process.exitCode=1;
