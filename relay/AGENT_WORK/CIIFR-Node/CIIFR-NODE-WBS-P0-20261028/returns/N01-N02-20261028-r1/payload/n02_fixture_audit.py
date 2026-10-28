"""Bounded independent physical audit of public synthetic fixtures; no product imports."""
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import re


def numeric(row, field):
    value = row[2 + 13 * field:15 + 13 * field].strip()
    assert value, 'missing numeric field'
    return Decimal(value.decode('ascii').replace('D', 'E').replace('d', 'E'))


def integer(row, field):
    value = numeric(row, field)
    assert value == int(value), 'noninteger field'
    return int(value)


def audit(data):
    assert all(c < 128 for c in data), 'not ASCII'
    assert data.count(b'\n') == data.count(b'\r\n') == data.count(b'\r'), 'not CRLF'
    sections = {}
    active = None
    for row in data.split(b'\r\n'):
        if row.startswith(b'#$'):
            assert re.fullmatch(rb'#\$ [A-Z0-9_&]+ *', row), 'marker grammar'
            active = row[3:].strip().decode()
            assert active not in sections, 'duplicate section'
            sections[active] = []
        elif row.strip():
            assert active, 'unowned row'
            sections[active].append(row)
    assert integer(sections['VERSION'][0], 1) == 14, 'not V14'
    control = sections['CONTROL']
    first = [integer(control[0], i) for i in range(6)]
    assert all(x >= 0 for x in first), 'negative primary count'
    numelt = first[0]
    aux = [integer(control[1], i) for i in range(6)]
    aux += [integer(control[2], i) for i in range(6)]
    assert all(x >= 0 for i, x in enumerate(aux) if i != 11), 'negative auxiliary count'
    assert aux[11] in (0, 1), 'invalid axis'
    element_rows = sections['ELEMENTS']
    assert len(element_rows) == 15 * numelt, 'element cardinality'
    elements = []
    for i in range(numelt):
        rows = element_rows[i * 15:(i + 1) * 15]
        elements.append({'ordinal': i + 1, 'from': integer(rows[0], 0),
                         'to': integer(rows[0], 1), 'T1': float(numeric(rows[1], 3)),
                         'P1': float(numeric(rows[3], 0)),
                         'density': float(numeric(rows[5], 1)),
                         'pointers': [integer(rows[12], j) for j in range(6)]})
    families = [('RIGID', 1, 1), ('RESTRANT', 3, 24),
                ('DISPLMNT', 4, 20), ('FORCMNT', 5, 20)]
    observations = {}
    for name, field, rows_per in families:
        rows = sections.get(name, [])
        count = aux[field]
        assert len(rows) == rows_per * count, name + ' cardinality'
        owners = {}
        for element in elements:
            pointer = element['pointers'][field]
            assert 0 <= pointer <= count, name + ' pointer range'
            if pointer:
                assert pointer not in owners, name + ' shared pointer'
                owners[pointer] = element
        assert len(owners) == count, name + ' orphan'
        populated = []
        for pointer, owner in owners.items():
            block = rows[(pointer - 1) * rows_per:pointer * rows_per]
            if name == 'RIGID':
                populated.append({'owner': owner['ordinal'], 'pointer': pointer,
                                  'weight': float(numeric(block[0], 0))})
                continue
            slots, stride = (6, 4) if name == 'RESTRANT' else (2, 10)
            for slot in range(slots):
                node = integer(block[slot * stride], 0)
                assert node >= 0, name + ' negative node'
                if name == 'RESTRANT':
                    kind = integer(block[slot * stride], 1)
                    cnode = integer(block[slot * stride], 5)
                    assert cnode >= 0, 'negative CNode'
                    assert (node > 0 and 1 <= kind <= 62) or (node == kind == cnode == 0), 'restraint identity'
                if node:
                    populated.append({'owner': owner['ordinal'], 'pointer': pointer,
                                      'slot': slot + 1, 'node': node})
        observations[name] = {'blocks': count, 'records': populated}
    misc = sections['MISCEL_1']
    material = [integer(misc[i // 6], i % 6) for i in range(numelt)]
    assert all(1 <= x <= 699 for x in material), 'material range'
    return {'elements': elements, 'auxiliary': observations, 'materials': material,
            'numnoz': first[1], 'nohgrs': first[2], 'izup': aux[11],
            'trailingMiscRowsUnqualified': len(misc) - (numelt + 5) // 6}


if __name__ == '__main__':
    catalog = json.loads((Path('n02-fixtures') / 'FIXTURE_CATALOG.json').read_text())
    results = {}
    for side, name in [('source', 'SYNTH_V14_SOURCE.cii'), ('target', 'SYNTH_V14_TARGET0.cii')]:
        data = (Path('n02-fixtures') / name).read_bytes()
        result = audit(data)
        for actual, expected in zip(result['elements'], catalog['families'][1][side], strict=True):
            assert all(actual[key] == value for key, value in expected.items()), 'catalog mismatch'
        assert result['materials'] == [1, 1]
        assert all(x['blocks'] == 1 and len(x['records']) == 1 for x in result['auxiliary'].values())
        results[name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), **result}
    original = (Path('n02-fixtures') / 'SYNTH_V14_SOURCE.cii').read_bytes()
    rows = original.split(b'\r\n')
    at = rows.index(b'#$ CONTROL') + 1
    changed = rows.copy()
    changed[at] = b'  ' + b'3'.rjust(13) + changed[at][15:]
    rejected = False
    try:
        audit(b'\r\n'.join(changed))
    except AssertionError as exc:
        rejected = str(exc) == 'element cardinality'
    assert rejected, 'seeded NUMELT defect not detected'
    output = {'publicFixtureAudit': results, 'seededWrongNumeltRejected': rejected,
              'originalProtectedFile': 'NOT_RECEIVED / NOT_RUN',
              'oracleExposure': 'catalog author-exposed; raw fields independently decoded; no vendor acceptance'}
    Path('n02-public-audit-results.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
