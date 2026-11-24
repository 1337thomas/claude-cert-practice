# Build tools

The question bank is embedded as JSON in `index.html` (`<script id="data">`). These scripts rebuild it.

1. `extract.py index.html` – pull the embedded bank out of a page (writes `bank.json`).
2. `build.py <base_bank.json> <out.json>` – take a base bank and re-sync it with the upstream sources
   (`loaders.py` expects clones/packages under `tools/upstream/`), adding explanations, domains and scenario
   text and appending `newsrc/new_questions.json` (converted MIT sources, see `newsrc/SOURCES.md`).
3. `patch.py <built.json> patches.json <final.json>` – apply the review decisions: global wording
   fixes, then per-question `rekey` / `remove` / `set_option` / `edit` / `note`, then drop the `hold`
   list (questions not reviewed yet). Each patch must match exactly, so stale patches fail loudly.
3b. `patch.py <final.json> patches_length.json <final2.json>` – apply the answer-length rework (option texts
   rewritten so the correct answer is no longer recognisable by its length; same patch format, no `global`/`hold`).
3c. `lengthcheck.py <final2.json> patches_length.json` – gate: prints the length-bias table per exam and source
   and exits 1 if a reworked question is still class A (correct option clearly the longest) or C (long decoy),
   or has an option more than 35 % off the question's mean option length.
4. `inject.py index.html <final2.json> index.html` – write the bank back into the page.

`patches.json` is the audit trail of the November 2026 review against current Anthropic docs.
