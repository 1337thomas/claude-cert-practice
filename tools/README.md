# Build tools

The question bank is embedded as JSON in `index.html` (`<script id="data">`). These scripts rebuild it.
Never edit the embedded bank by hand: every content decision lives in `patches.json` or in a source file.

1. `extract.py index.html` – pull the embedded bank out of a page (writes `bank.json`).
2. `build.py <base_bank.json> <out.json>` – take a base bank and re-sync it with the upstream sources
   (`loaders.py` expects clones/packages under `tools/upstream/`), adding explanations, domains and scenario
   text, appending `newsrc/new_questions.json` (converted MIT sources, see `newsrc/SOURCES.md`) and the
   original questions in `newsrc/original_*.json` (see `newsrc/ORIGINAL.md`).
3. `patch.py <built.json> patches.json <final.json>` – apply the review decisions: blueprint domain renames
   (`domains`), global wording fixes, then per-question `rekey` / `remove` / `set_option` / `edit` / `note` /
   `set_domain`, then drop the `hold` list (questions not reviewed yet). Each patch must match exactly, so stale
   patches fail loudly.
3b. `patch.py <final.json> patches_length.json <final2.json>` – apply the answer-length rework (option texts
   rewritten so the correct answer is no longer recognisable by its length; same patch format, no `global`/`hold`).
3c. `lengthcheck.py <final2.json> patches_length.json` – gate: prints the length-bias table per exam and source
   and exits 1 if a reworked question is still class A (correct option clearly the longest), C (long decoy) or
   S (correct option clearly the shortest), has an option more than 35 % off the question's mean option length,
   or if across the reworked questions of an exam the correct option is the longest or the shortest in more than
   35 % of items (same limits as `lint_original.py`).
4. `inject.py index.html <final2.json> index.html` – write the bank back into the page.

`lint_original.py newsrc/original_<exam>.json --hold patches.json` checks the original questions (schema,
per-option rationale, multi-response wording, answer-length bias, mock sets against the blueprint weights).
Run it before every build that touches those files.

`patches.json` is the audit trail of the reviews against current Anthropic docs.

## Reproducing the published bank

Base bank: the page from commit `afaefec` (`git show afaefec:index.html > old.html`, then `extract.py old.html`).
Run all scripts from `tools/` with `python -I`. Upstream state used for v2026.11 (clone into `tools/upstream/`,
which is git-ignored; `json5` goes into `tools/pylib/`):

| Folder under `tools/upstream/` | Source | Pin |
|---|---|---|
| `CLAUDE-CERTIFICATIONS` | github.com/Amey-Thakur/CLAUDE-CERTIFICATIONS | `a21808e` |
| `ccar-p-revision` | github.com/Aliquanto3/ccar-p-revision | `9137338` (later commits moved the data to `data/ccar-p/`) |
| `CCDVFTrainer` | github.com/DaNiELChIoRo/CCDVFTrainer | `9fcb7aa` |
| `claude-architect-quiz` | github.com/MilindGaharwar/claude-architect-quiz | `270e920` |
| `claude-certified-developer` | github.com/mrKindly/claude-certified-developer | `8f67393` |
| `connectry-npm/package` | npm `connectry-architect-mcp` 0.1.13 (tarball, extracted) | 0.1.13 |

With these pins the pipeline reproduces the v2026.11 bank exactly, except one fallback ID that used Python's
salted `hash()`; `build.py` now derives fallback IDs from an MD5 of the stem, so they are stable across runs.
