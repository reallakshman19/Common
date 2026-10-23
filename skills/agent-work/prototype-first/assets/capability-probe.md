# Capability probe (first message to a builder)

Send this before the card is final. Record the answers as the card's `probe`
(yes, no or unknown each). Shape the step to what the builder can actually do.

```text
Before any task, answer in two lines, yes / no / unknown for each, from what you
can actually do in this session (try it if unsure; do not guess):
1 code: can you run code and tests here?
2 downloads: can you give me files to download (a ZIP with a launcher)?
3 read_attachments: can you read files I attach in this chat?
4 browser: can you open web pages, and is localhost reachable for you?
5 repo_push: can you clone, push a branch and open a pull request on GitHub?
6 links: can you open a Google Drive or OneDrive folder link?
Then one line: anything else that limits you (time, size, blocked sites).
```

Rules for using the answers:

- `read_attachments: no` and `links: no`: this builder cannot receive private files;
  choose another builder or a local one.
- `browser: no` or localhost blocked: browser witnesses run on the user's machine;
  the builder ships the launcher and the demo steps.
- `repo_push: no`: hardening needs another route (the coordinator commits the pack's
  code without private data, or a local builder does).
