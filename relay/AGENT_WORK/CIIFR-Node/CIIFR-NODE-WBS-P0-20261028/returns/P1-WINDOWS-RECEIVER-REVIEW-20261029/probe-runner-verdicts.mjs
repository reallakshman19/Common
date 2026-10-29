import fs from 'node:fs';
import vm from 'node:vm';
import crypto from 'node:crypto';
if(!process.argv[2])throw Error('Usage: node probe-runner-verdicts.mjs <received runner path>');
const source=fs.readFileSync(process.argv[2],'utf8');
if(crypto.createHash('sha256').update(source).digest('hex')!=='8934bb53c0e8a4ca09abe598d8f8140cc088e554ece438ea060e10b989cad5db')throw Error('Unexpected runner bytes');
function block(from,to){const a=source.indexOf(from),b=source.indexOf(to,a);if(a<0||b<0)throw Error('Pinned source block absent');return source.slice(a,b);}
const case5=block('  results.cases.case5_negative_zero_dormant_challenges = {','\n  // ==========================================\n  // CASE 6');
const box5={results:{cases:{}},uiSearchNegStatus:'ACCEPTED',uiSearchZeroStatus:'ACCEPTED',fileNegStatus:'ACCEPTED',fileZeroStatus:'ACCEPTED',pointerBeyondControl:'ACCEPTED',dormantStatus:{results:''},ptApplyButton:null,ptExportButton:null};
vm.runInNewContext(case5,box5);
const fieldGuard=block("  if (!fwd400_500.includes('200')",'\n  // Inspect node 500');
let case4MissingPressuresAccepted=false;
try{vm.runInNewContext(fieldGuard,{fwd400_500:'TEMPERATURE_1_STORED 200; PRESSURE_1_STORED WRONG',fwd500_600:'TEMPERATURE_1_STORED 180; PRESSURE_1_STORED WRONG',rev500_400:'0 element(s)'});case4MissingPressuresAccepted=true;}catch{}
const case6=block('  results.cases.case6_integrity_immutability = {','\n  await session.screenshot');
const box6={results:{cases:{}},session:{pageErrors:[{text:'late exception'}]}};
vm.runInNewContext(case6,box6);
const result={scope:'Review of extracted verdict/guard blocks only; no browser execution or product failure claimed',case5FailedChallengesStillPass:box5.results.cases.case5_negative_zero_dormant_challenges,case4WrongPressureNotRejected:case4MissingPressuresAccepted,case6LateExceptionStillPass:box6.results.cases.case6_integrity_immutability};
console.log(JSON.stringify(result,null,2));
