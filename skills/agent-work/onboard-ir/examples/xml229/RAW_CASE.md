# OBIR-G01 — raw synthetic XML229 source task (show to cold IR)

**Fixture:** a deliberately small *fictional* source story for assessing the IR method, not an actual production model. No private Owner coordinates, input files or identities are included. **Keep the golden expected interpretation withheld until the reviewer has recorded its own source-derived model and candidate comparison.**

## Original user outcome and constraints

Convert source piping XML + optional JSON Trace into a governed EnrichedXML and CAESAR II 2019 CII. Node rows, physical vertices, restraint members, component owners and output node IDs must remain distinct identities. Do not change original XYZ, attach unsupported restraints, weld disconnected pipes or duplicate physical mass.

A previous real but **unavailable** Owner V6 execution reported 21 row-level position ambiguities. This fixture cannot establish their cause or resolve any of them.

## Tiny source representation

~~~xml
<PipeStressExport><Pipe>
  <Branch>
    <Branchname>/A/B1</Branchname>
    <Node><NodeNumber>10</NodeNumber><Position>0 0 0</Position><ComponentType>PIPE</ComponentType></Node>
    <Node><NodeNumber>-1</NodeNumber><Position>100 0 0</Position><ComponentType>ATTA</ComponentType></Node>
    <Node><NodeNumber>-1</NodeNumber><Position>100.000 0 0</Position><ComponentType>ATTA</ComponentType></Node>
    <Node><NodeNumber>20</NodeNumber><Position>200 0 0</Position><ComponentType>PIPE</ComponentType></Node>
  </Branch>
  <Branch>
    <Branchname>/B/B1</Branchname>
    <Node><NodeNumber>30</NodeNumber><Position>100 0 0</Position><ComponentType>PIPE</ComponentType></Node>
    <Node><NodeNumber>40</NodeNumber><Position>100 100 0</Position><ComponentType>PIPE</ComponentType></Node>
  </Branch>
</Pipe></PipeStressExport>
~~~

The original JSON Trace describes **two distinct GUIDE support members** at the /A support station, with 5 mm and 8 mm gaps. Their source member occurrences and source branch names are distinct evidence. No source-declared /A-to-/B junction exists. Do not assume a candidate's use of these facts is correct merely from the problem description.

## Cold IR task

1. Identify exact source occurrence IDs, source branch edges, physical-vertex identity candidates and disconnected same-XYZ line.
2. State whether the original two adjacent -1 rows create a meaningful graph complication if assigned one positive native node number. Derive your own test, not an author's patch.
3. Specify what original-source proof is required to place both GUIDE members, and what losing one would look like in the native file.
4. Distinguish a correct six-slot serializer test on unrelated positive IDs from a real solution for the zero-span source graph.
5. Identify how accepted mass owner identity and split-before-Final would be verified independently.
6. Explicitly mark the actual 21 production claims **NOT_RECEIVED / NOT_RUN**, regardless of success on this tiny fixture.

Use the project's one real native task if actually assigned. No standalone authority, permission to edit, or Owner decision is implied by this exercise. The case is intentionally not pre-labeled as PASS.
