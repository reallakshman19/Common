# Manual file-return: validator on an uncopyable UI

Synthetic worked transport example, not a completed live agent run. The sender
records the issued packet bytes and SHA-256, then sends this short pointer:

> Read `examples/nlm-validator/packet.md` (UTF-8; SHA-256
> `a6d75c9b26655b6abebe98cb373b6d7fa3ff527460aaaee83a66940f2c52f06b`).
> Use `sample-items.txt` (UTF-8). Follow the packet without regenerating it.
> Write exactly ONE result file, `nlm-p3-result.md` (UTF-8), then reply with
> exactly ONE `SAVED-P3 · rows=<n> · file=nlm-p3-result.md · sha256=<digest>` line.

The illustrative [packet](packet.md) is the exact immutable file identified in
that pointer; the [input](sample-items.txt) and [result](nlm-p3-result.md) show
the evidence format. A sample one-line reply for the included result file is:

`SAVED-P3 · rows=3 · file=nlm-p3-result.md · sha256=4c937a98f038d63156f3ea7ae8dcc24202769b833b95c8b7e90293e317e93870`

In a real send, compare the file bytes against the recorded issued packet and
verify the returned file's digest and row count yourself. This is a transport
pattern, not proof that any model independently checked the claims.
