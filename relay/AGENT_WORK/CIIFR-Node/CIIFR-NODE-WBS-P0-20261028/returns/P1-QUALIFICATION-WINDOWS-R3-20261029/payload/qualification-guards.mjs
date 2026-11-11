import assert from 'node:assert/strict';

const elementHeaders = ['Element #','FROM → TO','Branch','T1 stored raw','P1 stored raw','Fluid density stored raw','Qualification'];
const nodeHeaders = ['Family','Owning element #','Occurrence','Evidence / HOLD'];
const qualification = 'HOLD: effective process semantics / identity not qualified';
export function verifyElementSection(section, expected) {
  assert.ok(section, 'SOURCE element section is missing');
  assert.equal(section.title, `SOURCE · FROM ${expected.fromNode} → TO ${expected.toNode} · 1 element(s)`);
  assert.equal(section.tables.length, 1);
  const table = section.tables[0];
  assert.deepEqual(table.headers, elementHeaders);
  assert.equal(table.rows.length, 1, 'Exactly one selected oriented element is required');
  const row = table.rows[0];
  assert.equal(row.length, 7);
  assert.equal(row[0], String(expected.ordinal));
  assert.equal(row[1], `${expected.fromNode} → ${expected.toNode}`);
  assert.equal(row[2], expected.branch);
  const rawFields = expected.fields.map((field, i) => {
    const text = row[3+i];
    // Match the complete field cell, including its independently derived span.
    assert.equal(text, `${field.identity}: ${field.lexeme} [bytes ${field.byteStart}–${field.byteEnd}]`, field.identity);
    const match = /^([A-Z0-9_]+): ([^ ]+) \[bytes (\d+)–(\d+)\]$/.exec(text);
    assert.ok(match, 'Malformed stored-field evidence');
    return {identity:match[1],lexeme:match[2],byteStart:Number(match[3]),byteEnd:Number(match[4]),storedNumber:Number(match[2].replace(/[dD]/g,'E'))};
  });
  assert.equal(row[6], qualification);
  return {t1:rawFields[0].storedNumber,p1:rawFields[1].storedNumber,density:rawFields[2].storedNumber,qual:'HOLD',rawFields};
}

export function verifyNodeSection(section, expected) {
  assert.ok(section, 'SOURCE node section is missing');
  assert.equal(section.title, `SOURCE · Numeric Node ${expected.number}`);
  assert.equal(section.tables.length, 1);
  assert.deepEqual(section.tables[0].headers, nodeHeaders);
  const sort = rows => rows.map(row => JSON.stringify(row)).sort();
  assert.deepEqual(sort(section.tables[0].rows), sort(expected.rows), 'Exact incidents, attachment ownership and occurrences must match');
  const find = family => section.tables[0].rows.find(row => row[0] === family);
  return {restrant:find('RESTRANT'),displmnt:find('DISPLMNT'),forcmnt:find('FORCMNT'),rigid:find('RIGID')};
}

export function verifyReverseSection(section) {
  assert.ok(section, 'SOURCE reverse section is missing');
  assert.equal(section.title, 'SOURCE · FROM 500 → TO 400 · 0 element(s)');
  assert.equal(section.tables.length, 1);
  assert.deepEqual(section.tables[0].headers, elementHeaders);
  assert.equal(section.tables[0].rows.length, 0);
}
