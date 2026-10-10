/* WP2-B native GET-only smoke. Default stale-history; explicit current author
 * claim mode is also diagnostic-only, never evidence admission or DELP credit.
 */
import {inspectLivePreAdmission} from './pre-admission-boundary-v1.mjs';
import {observeNativeWithUnknownRetry} from './native-read-retry-v1.mjs';
import {buildNativeSmokeConfig,qualifiesNegativeSmoke} from './native-smoke-config-v1.mjs';

const {locator,mode}=buildNativeSmokeConfig(process.env);
const result=await observeNativeWithUnknownRetry(locator,inspectLivePreAdmission);
if(result.source_status==='UNKNOWN'){
  // Additional native GETs explain source stages; do not alter the original
  // UNKNOWN result or convert this non-atomic post-failure read into evidence.
  try{
    const {diagnoseLiveNativeSourceStages}=await import('./native-source-stage-diagnostic-v1.mjs');
    const diagnostic=await diagnoseLiveNativeSourceStages(locator);
    console.log(JSON.stringify(diagnostic,null,2));
  }catch{
    console.log(JSON.stringify({schema:'common-wp2b-postfailure-stages-v1',
      basis:'INDEPENDENT_POST_FAILURE_NON_ATOMIC_READS',
      diagnostic_status:'UNAVAILABLE',admission:'NOT_ADMITTED',
      evidence_admitted:false,writer_authorized:false}));
  }
}
if(!qualifiesNegativeSmoke(result,mode))process.exitCode=1;
