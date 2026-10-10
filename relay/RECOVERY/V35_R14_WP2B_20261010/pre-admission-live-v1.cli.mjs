/* WP2-B native GET-only smoke. Default stale-history; explicit current author
 * claim mode is also diagnostic-only, never evidence admission or DELP credit.
 */
import {inspectLivePreAdmission} from './pre-admission-boundary-v1.mjs';
import {observeNativeWithUnknownRetry} from './native-read-retry-v1.mjs';
import {buildNativeSmokeConfig,qualifiesNegativeSmoke} from './native-smoke-config-v1.mjs';

const {locator,mode}=buildNativeSmokeConfig(process.env);
const result=await observeNativeWithUnknownRetry(locator,inspectLivePreAdmission);
if(!qualifiesNegativeSmoke(result,mode))process.exitCode=1;
