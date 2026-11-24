# Claude Certification — Practice Exams

Unofficial practice exams for Anthropic Claude certifications. Single-file static HTML — no backend, no tracking, works offline.

**Supported exams:** CCAO-F (Associate – Foundations), CCDV-F (Developer – Foundations), CCDV-P (Developer – Professional), CCAR-F (Architect – Foundations), CCAR-P (Architect – Professional)

CCAO-F, CCDV-F and CCAR-P follow the exam guides v1.1 effective 7 December 2026 (70 items, 60 scored, new domain weights). CCDV-P follows exam guide v1.0 (November 2026).

**[Start practicing](https://1337thomas.github.io/claude-cert-practice/)**

## Features

- Exam mode (timed, scored at the end) and learning mode (answer and explanation after each question)
- Random exams are drawn in the official domain weights; results show percent correct by domain, like the real score report
- CCDV-P: original scenario questions with a rationale for every option, grouped into fixed mock exams
- Explanations from the original authors for nearly every question
- "Report a problem" link on every question opens a pre-filled GitHub issue with the question ID

## Quality

In November 2026 every answer key was audited against the current Anthropic documentation
(Claude API, Claude Code, Agent SDK, MCP). Questions with wrong keys were re-keyed, outdated
facts corrected, and questions without a single defensible answer removed. If you still find
a wrong answer, please use the report link — it includes the question ID.

## Sources

Questions collected from community repositories:

- Amey-Thakur/CLAUDE-CERTIFICATIONS (all exams, MIT)
- rohitg00/ai-engineering-from-scratch (all exams, MIT)
- davidalex89/claude-cert-study-path (all exams, MIT; Anthropic's official sample questions excluded)
- preporato/claude-certification-guide (all exams, MIT)
- utkarsh1agarwal/claude-architect-exam-guide (CCAR-F, MIT)
- Aliquanto3/ccar-p-revision (CCAR-P, CC BY-SA 4.0)
- Connectry LABS connectry-architect-mcp on npm (CCAR-F, MIT)
- MilindGaharwar/claude-architect-quiz (CCAR-F)
- mrKindly/claude-certified-developer (CCDV-F)
- DaNiELChIoRo/CCDVFTrainer (CCDV-F)

The CCDV-P questions are original to this repo (MIT), see `tools/newsrc/ORIGINAL.md`. All other questions are collected:
question content © respective authors under original licenses.

## License

MIT for the exam shell (HTML/CSS/JS). Question rights remain with original authors.
