# Sources for new_questions.json

Built by `build_new.py` (data parsing only, no upstream code executed). Total imported: 1,436 questions.
Dedup was checked against `bank_final.json` (normalized stem, scenario-prefixed and bare). No near-duplicates were found, either against that bank or between the new sources.

| Source | associate-foundations | developer-foundations | architect-foundations | architect-professional | Total |
|---|---|---|---|---|---|
| rohitg00 | 128 | 123 | 117 | 125 | 493 |
| davidalex89 | 117 | 125 | 102 | 119 | 463 |
| preporato | 30 | 30 | 30 | 30 | 120 |
| utkarsh1agarwal | – | – | 360 | – | 360 |
| **Total** | 275 | 278 | 609 | 274 | 1,436 |

## 1. rohitg00/ai-engineering-from-scratch

- URL: https://github.com/rohitg00/ai-engineering-from-scratch (folder `certifications/claude`)
- Commit: `151fe3f22bca88c665ccaaab3a55e10ed22f804c`
- License: MIT. "Copyright (c) 2026 Rohit Ghumare"
- Files: `assessments/{ccao-f,ccdv-f,ccar-f,ccar-p}/{diagnostic,mock-01}.json` and `lessons/NN-*/quiz.json` (33 lessons, 6 questions each).
- Answer field: `correct` (a list of 0-based indices in assessments, a single int in lesson quizzes). `_select` is the length of that list when it is longer than 1.
- Imported: associate 128 (diagnostic 14, mock 60, lessons 00-07 and 29), developer 123 (16, 53, lessons 08-15 and 30), architect-foundations 117 (15, 60, lessons 16-21 and 31), architect-professional 125 (14, 63, lessons 22-28 and 32).
- Lesson quizzes are shared across tracks upstream. Each lesson was assigned to one home exam (see the list above) to avoid cross-exam copies. The domain is the home track's first mapped domain for that lesson.
- IDs: the upstream question `id` for assessments, and `lesson-NN#i` for lesson quizzes.
- Dropped: 0.
- Note: the Windows checkout failed on one long-path file outside the quiz data. All 203 other `certifications/claude` files were verified against the commit's blob hashes.

## 2. davidalex89/claude-cert-study-path

- URL: https://github.com/davidalex89/claude-cert-study-path
- Commit: `6630604a4bca3a26f559b36d1fffbbff29acd597`
- License: MIT. "Copyright (c) 2026 David Scovetta"
- Files: `js/data/{associate,developer,architect-foundations,architect-professional}.js`. These are JS object literals. Template literals were converted to strings and the result was parsed with json5.
- Questions taken from each domain's `lesson.checks[]` and `quiz[]`. The answer field is `correct` (a list of indices). Lesson "interactive" widgets are not MCQs and were not imported.
- IDs: `<file>/<domain id>/<check|quiz>#i`
- Imported: associate 117, developer 125, architect-foundations 102, architect-professional 119.
- Dropped: 21 items marked `source: "official"` (Anthropic exam-guide samples): 3 associate, 3 developer, 12 architect-foundations, 3 architect-professional.
- Note: the correct answer is at upstream position B in about 83% of single-answer items. The upstream app does not shuffle options. Explanations refer to options by letter, so the order was kept.

## 3. preporato/claude-certification-guide

- URL: https://github.com/preporato/claude-certification-guide
- Commit: `32334487e1441abfd22f0b2ad8d5af79f215c546`
- License: MIT. "Copyright (c) 2026 preporato.com"
- Files: `practice/{ccao-f,ccdv-f,cca-f,ccar-p}.json`. `cca-f` is the older name for CCAR-F.
- Answer field: `answer` (option keys). Upstream authors put the correct option first, and their build applies a seeded shuffle that rewrites `{a}` references in explanations to the final letters. That shuffle was re-implemented. All 120 questions were then verified against the repo's published `*/practice-questions.md` (option order, option text and answer letters): 0 mismatches.
- Scenario text (cca-f, 8 questions) is prepended to the stem with a blank line. One `code` block per bank (cca-f, ccdv-f) is appended to the stem as a fenced block.
- IDs: `<bank>#n`, where n is the question number in the published Markdown.
- Imported: 30 per exam. Dropped: 0.

## 4. utkarsh1agarwal/claude-architect-exam-guide

- URL: https://github.com/utkarsh1agarwal/claude-architect-exam-guide
- Commit: `0a786c7c69822f39e21a7a2f8bd26125d9e18338`
- License: MIT. "Copyright (c) 2026 Claude Architect Exam Guide Contributors"
- Files: `mock-exam/exam-{1..6}-questions.md` with the matching `exam-N-answers.md` (CCAR-F).
- Answer key: read from the key line `**Qn. Answer: X[, Y]** *(Dk)* — rationale` (`**n. Answer: ...**` in exams 2 and 3). The rationale text is never scanned for letters. For every exam, the number of key lines equals the number of questions (60). All 18 "(Select TWO)" stems have exactly two key letters.
- Domain comes from the first `Dk` tag, mapped to the CCAR-F domain names.
- Scenario: each `## Scenario N: <title>` section has no body text, only a title. The title is prepended as `Scenario: <title>` plus a blank line.
- IDs: `exam-N#n`
- Imported: 360 (architect-foundations). Dropped: 0.
- Note: the answer is B in about 59% of single-answer items, which is an upstream position bias.

## Domain naming

Source domain names were matched (ignoring case, "&"/"and", punctuation and `Dn` prefixes) to the names already used in `bank_final.json`. For example, CCAR-P domains became "D1 Solution Design & Architecture" and so on. All source domains matched.
