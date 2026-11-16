# Build tools

The question bank is embedded as JSON in `index.html` (`<script id="data">`). These scripts rebuild it.

1. `extract.py index.html` – pull the embedded bank out of a page (writes `bank.json`).
2. `build.py <base_bank.json> <out.json>` – take a base bank and re-sync it with the upstream sources
   (`loaders.py` expects clones/packages under `tools/upstream/`), adding explanations, domains and scenario
   text and appending `newsrc/new_questions.json` (converted MIT sources, see `newsrc/SOURCES.md`).
3. `patch.py <built.json> patches.json <final.json>` – apply the review decisions: global wording
   fixes, then per-question `rekey` / `remove` / `set_option` / `edit` / `note`, then drop the `hold`
   list (questions not reviewed yet). Each patch must match exactly, so stale patches fail loudly.
4. `inject.py index.html <final.json> index.html` – write the bank back into the page.

`patches.json` is the audit trail of the November 2026 review against current Anthropic docs.
