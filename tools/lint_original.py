"""Quality gate for the original question files (newsrc/original_*.json).

Usage: python -I lint_original.py newsrc/original_ccdv-p.json [--hold patches.json]

Checks every item for: schema, per-option rationale (`why`), multi-response stems that state how many
answers to pick, and answer-length bias (the correct option must not stand out by length). Then prints the
per-mock domain counts against the blueprint weights. Exit code 1 on any error.
"""
import json, re, sys, collections, statistics
sys.stdout.reconfigure(encoding='utf-8')

BLUEPRINTS = {  # exam -> (items per mock, {domain label: weight %})
    'developer-professional': (70, {
        'D1 Advanced Agent Architecture & Orchestration': 17,
        'D2 Production Integration, Reliability & Knowledge Grounding': 20,
        'D3 Observability & Production Monitoring': 12,
        'D4 Advanced Debugging & Incident Response': 10,
        'D5 Evaluation Engineering & Quality Assurance': 12,
        'D6 Cost & Latency Optimization at Scale': 8,
        'D7 Runtime Guardrails & Production Security': 11,
        'D8 Agent Fleet Operations for Software Delivery': 10}),
}
WORDS = {2: 'TWO', 3: 'THREE'}
RATIO = (0.85, 1.15)      # mean correct length / mean distractor length
LONGEST_MARGIN = 1.10     # correct option may not beat the next-longest option by more than this
MAX_LONGEST_SHARE = 0.35 # across a file: correct option is the longest in at most this share of items


def targets(n, weights):
    """Largest-remainder apportionment of n items to the domain weights."""
    raw = {d: n * w / sum(weights.values()) for d, w in weights.items()}
    t = {d: int(v) for d, v in raw.items()}
    for d in sorted(raw, key=lambda d: raw[d] - t[d], reverse=True)[:n - sum(t.values())]:
        t[d] += 1
    return t


def main(path, hold=()):
    bank = json.load(open(path, encoding='utf-8'))
    errors, warns, longest = [], [], 0
    ids, stems = set(), set()
    for exam, items in bank.items():
        per_mock, weights = BLUEPRINTS[exam]
        for q in items:
            qid = q.get('id', '?')
            err = lambda m: errors.append(f'{qid}: {m}')
            if qid in ids: err('duplicate id')
            ids.add(qid)
            stem = re.sub(r'\W+', ' ', q['q']).lower().strip()
            if stem in stems: err('duplicate stem')
            stems.add(stem)
            if q.get('domain') not in weights: err(f"unknown domain {q.get('domain')!r}")
            if q.get('mock') not in (1, 2, 3): err('mock must be 1, 2 or 3')
            if not q.get('explanation'): err('missing explanation')
            opts = q['options']
            k = sum(o['correct'] for o in opts)
            sel = q.get('_select') or 1
            if k != sel: err(f'{k} correct options but _select={sel}')
            if len(opts) != (4 if k == 1 else 5): err(f'{len(opts)} options for {k} correct (want 4 single / 5 multi)')
            if k > 1 and f'(Select {WORDS[k]}.)' not in q['q']: err(f'multi-response stem must contain "(Select {WORDS[k]}.)"')
            for o in opts:
                if not o.get('why'): err(f"option without why: {o['text'][:40]}")
                if re.search(r'\b(all|none) of the above\b', o['text'], re.I): err('all/none of the above')
            L = [len(o['text']) for o in opts]
            c = [l for l, o in zip(L, opts) if o['correct']]
            d = [l for l, o in zip(L, opts) if not o['correct']]
            ratio = statistics.mean(c) / statistics.mean(d)
            if not RATIO[0] <= ratio <= RATIO[1]: err(f'length ratio {ratio:.2f} (lengths {L})')
            top = sorted(L, reverse=True)
            if max(c) == top[0]:
                longest += 1
                if top[0] > LONGEST_MARGIN * top[1] and k == 1: err(f'correct option clearly longest {L}')
            if max(L) > 1.6 * min(L): warns.append(f'{qid}: option lengths spread {L}')
        # blueprint coverage per mock
        live = [q for q in items if q['id'] not in hold]
        print(f'{exam}: {len(items)} items ({len(live)} live, {len(items) - len(live)} on hold)')
        t = targets(per_mock, weights)
        for m in sorted({q.get('mock') for q in items}):
            cnt = collections.Counter(q['domain'] for q in live if q.get('mock') == m)
            row = '  '.join(f"{d.split()[0]} {cnt[d]}/{t[d]}" for d in weights)
            print(f'  mock {m}: {sum(cnt.values()):>3}/{per_mock}  {row}')
        n = len(items)
        print(f'  correct option is the longest in {longest}/{n} items ({longest / n:.0%}; chance ≈ 25%)')
        if longest / n > MAX_LONGEST_SHARE: errors.append(f'{exam}: correct option is the longest in {longest / n:.0%} of items (max {MAX_LONGEST_SHARE:.0%})')
        pos = collections.Counter(next(i for i, o in enumerate(q['options']) if o['correct']) for q in items)
        print('  first correct option at source position:', dict(sorted(pos.items())), '(options are shuffled at runtime)')
    for w in warns: print('WARN', w)
    for e in errors: print('ERROR', e)
    print('errors:', len(errors))
    return 1 if errors else 0


if __name__ == '__main__':
    args = sys.argv[1:]
    hold = set()
    if '--hold' in args:
        i = args.index('--hold'); hold = set(json.load(open(args[i + 1], encoding='utf-8')).get('hold', [])); del args[i:i + 2]
    sys.exit(main(args[0], hold))
