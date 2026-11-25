# Original questions (`original_*.json`)

Questions written for this site, not taken from a community repository. Licensed MIT like the rest of the repo.
Currently: `original_ccdv-p.json` for CCDV-P (Claude Certified Developer – Professional, exam guide v1.0, Nov 2026).

## Format

Same item shape as the rest of the bank, plus these fields:

- `why` on every option: one or two sentences on why the option is right or wrong. The page shows them in the
  order the options were displayed, so they must not refer to option letters.
- `_claims` (optional): the product facts an item relies on, each with its doc source. Kept in the source file as review evidence; `build.py` drops it from the published bank.
- `mock`: the fixed mock-exam set (1–3). Each set follows the blueprint weights for 70 items:
  D1 12 · D2 14 · D3 8 · D4 7 · D5 8 · D6 6 · D7 8 · D8 7.

Multi-response items have five options, `_select` set to the number of correct options, and the stem ends with
`(Select TWO.)` or `(Select THREE.)`.

## Writing rules

- Scenario-based, Professional level: operating Claude systems in production, not definitions.
- One defensible answer. Distractors are plausible and partly right (a real practice applied to the wrong
  problem, or a weaker control), never absurd. No "all/none of the above".
- All options about the same length and equally specific. `lint_original.py` fails a file when the correct
  option is clearly the longest in an item, or the longest in more than 35% of items.
- Every product fact (API, Agent SDK, Managed Agents, Claude Code, MCP, platform differences) is checked against
  the current Anthropic documentation before the item goes live. Unchecked items go to `hold` in `patches.json`.
- Anthropic's sample questions from the exam guides are not copied or paraphrased.
