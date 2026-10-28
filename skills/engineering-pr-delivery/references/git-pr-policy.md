# Git / PR Policy

Use one PR per coherent assignment unless the owner changes scope or a safety/recovery boundary requires supersession.

Before PR allocation use a unique WIP ID. After allocation migrate WIP report/status/claim records to the PR number.

Keep commits logical and recoverable. Update recovery artifacts around meaningful state changes; metadata-only sync commits are acceptable.

Do not silently force-push, rewrite validated history, or resolve engineering-significant rebase conflicts by guessing intent.

Do not modify `.github/workflows/*` unless explicitly authorized.

Default to draft PR during active implementation/recovery.

Never merge without explicit owner authorization.

When superseding a PR, preserve predecessor lineage, reason, salvaged evidence/commits, rejected work, and fresh current-main grounding in the replacement PR.
