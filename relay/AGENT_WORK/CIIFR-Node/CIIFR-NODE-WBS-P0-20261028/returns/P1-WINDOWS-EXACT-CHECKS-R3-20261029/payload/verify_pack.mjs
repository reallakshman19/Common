import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'ARTIFACT_MANIFEST.json'),'utf8'));
for(const item of manifest.files){
  assert.ok(!item.path.split('/').includes('..')&&!path.isAbsolute(item.path),'Invalid package member path');
  const bytes=fs.readFileSync(path.join(root,item.path));
  const sha=crypto.createHash('sha256').update(bytes).digest('hex');
  const blob=crypto.createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${bytes.length}\0`),bytes])).digest('hex');
  assert.equal(bytes.length,item.bytes,item.path+' byte length');
  assert.equal(sha,item.sha256,item.path+' SHA-256');
  assert.equal(blob,item.gitBlob,item.path+' Git blob');
}
console.log(JSON.stringify({candidate:manifest.candidate,verifiedMembers:manifest.files.length,status:'BYTES_VERIFIED'},null,2));
