"""Audit only the pinned public synthetic SOURCE; imports no product reader."""
import hashlib
import json
import pathlib
import sys
from decimal import Decimal

path = pathlib.Path(sys.argv[1])
data = path.read_bytes()
assert len(data) == 8276
assert hashlib.sha256(data).hexdigest() == 'c8de516c54767c7cf7d5239d404810be891ed3d56ec2111db3dc4c2b07dcdb0b'
lines = data.splitlines(keepends=True)
sections = {}
offset = 0
active = None
for physical in lines:
    text = physical.rstrip(b'\r\n').decode('ascii')
    if text.startswith('#$ '):
        active = text[3:].strip()
        sections[active] = []
    elif text.strip():
        sections[active].append((offset, text))
    offset += len(physical)

def integer(text, a, b):
    value = Decimal(text[a:b].strip())
    assert value == value.to_integral_value()
    return int(value)

cards = sections['ELEMENTS']
assert len(cards) == 30
assert integer(sections['CONTROL'][0][1], 2, 15) == 2
elements = []
for ordinal in (1, 2):
    cs = cards[(ordinal - 1) * 15:ordinal * 15]
    first = cs[0][1]
    start_node, end_node = integer(first, 0, 15), integer(first, 15, 28)
    fields = []
    for identity, card, a, b in [('TEMPERATURE_1_STORED', 1, 41, 54), ('PRESSURE_1_STORED', 3, 2, 15), ('FLUID_DENSITY_STORED', 5, 15, 28)]:
        start, text = cs[card]
        fields.append(dict(identity=identity, lexeme=text[a:b].strip(), byteStart=start+a, byteEnd=start+b))
    elements.append(dict(ordinal=ordinal, fromNode=start_node, toNode=end_node, branch='(none)', fields=fields))

owner = cards[:15]
ptr_card = owner[12][1]
assert [integer(ptr_card, 2+13*i, 15+13*i) for i in range(6)] == [0, 1, 0, 1, 1, 1]
rs = sections['RESTRANT'][0][1]
assert (integer(rs, 2, 15), integer(rs, 15, 28), integer(rs, 67, 80)) == (500, 1, 0)
assert integer(sections['DISPLMNT'][0][1], 2, 15) == 500
assert integer(sections['FORCMNT'][0][1], 2, 15) == 500
assert Decimal(sections['RIGID'][0][1][2:15].strip()) == 100
rows = [['ELEMENT', str(e['ordinal']), f"{e['fromNode']} → {e['toNode']}", 'Incident endpoint; element-owned properties'] for e in elements]
rows += [
    ['RESTRANT', '1', 'Pointer 1 · Slot 1', 'Type 1 · CNode 0 · semantics partial'],
    ['DISPLMNT', '1', 'Pointer 1 · Specification 1', 'Vectors/cases not yet qualified'],
    ['FORCMNT', '1', 'Pointer 1 · Specification 1', 'Input loads only; not computed reactions'],
    ['RIGID', '1', 'Pointer 1', 'Weight raw 100 · element-owned, semantics partial']
]
print(json.dumps(dict(scope='Pinned public synthetic SOURCE only; physical raw fields and ownership, no effective engineering semantics', sha256=hashlib.sha256(data).hexdigest(), elements=elements, node=dict(number=500, rows=rows)), indent=2, ensure_ascii=False))
