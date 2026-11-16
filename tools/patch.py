"""Apply review decisions (patches.json) to a built bank.

Usage: python -I patch.py bank_new.json patches.json bank_final.json

patches.json:
  {"global": [{"exams": [...], "pattern": regex, "repl": str, "first_repl": str?}],
   "items": [{"id", "action": "remove"} |
             {"id", "action": "rekey", "correct": "<option text prefix>" | [prefixes]} |
             {"id", "action": "edit", "field": "q|explanation|opt", "find": str, "replace": str} |
             {"id", "action": "set_option", "match": "<old option prefix>", "text": str} |
             {"id", "action": "set_explanation", "text": str} |
             {"id", "action": "note", "text": str}   # appended to explanation as a correction note
  ]}
Every patch must hit exactly once, otherwise the script fails (so stale patches can't silently no-op).
"""
import json, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
src, pfile, dst = sys.argv[1:4]
bank = json.load(open(src, encoding='utf-8'))
P = json.load(open(pfile, encoding='utf-8'))
Q = {q['id']: (e, q) for e, v in bank.items() for q in v}
norm = lambda s: re.sub(r'\W+', ' ', s or '').strip().lower()
stats = collections.Counter()
removed = set()


def opt(q, prefix):
    hits = [o for o in q['options'] if norm(o['text']).startswith(norm(prefix))]
    assert len(hits) == 1, (q['id'], prefix, [o['text'][:60] for o in q['options']])
    return hits[0]


for g in P.get('global', []):
    rx = re.compile(g['pattern'])
    for e in g['exams']:
        for q in bank[e]:
            if g.get('ids') and q['id'] not in g['ids']: continue
            first = [True]
            def sub(m):
                r = g['first_repl'] if first[0] and g.get('first_repl') else g['repl']
                first[0] = False
                return m.expand(r)
            n0 = 0
            for fld in ('q', 'explanation'):
                if q.get(fld):
                    new, n = rx.subn(sub, q[fld]); q[fld] = new; n0 += n
            for o in q['options']:
                new, n = rx.subn(sub, o['text']); o['text'] = new; n0 += n
            if n0: stats['global:' + g['pattern'][:20]] += 1

for p in P['items']:
    assert p['id'] in Q, ('unknown id', p['id'])
    e, q = Q[p['id']]
    a = p['action']
    if a == 'remove':
        removed.add(p['id'])
    elif a == 'rekey':
        want = p['correct'] if isinstance(p['correct'], list) else [p['correct']]
        hits = [opt(q, w) for w in want]
        for o in q['options']: o['correct'] = any(o is h for h in hits)
    elif a == 'set_option':
        opt(q, p['match'])['text'] = p['text']
    elif a == 'set_explanation':
        q['explanation'] = p['text']
    elif a == 'note':
        q['explanation'] = (q.get('explanation', '') + f"\n\n**Correction (per current docs):** {p['text']}").strip()
    elif a == 'edit':
        fields = {'q': [q], 'explanation': [q]}
        if p['field'] == 'opt':
            targets = [o for o in q['options'] if p['find'] in o['text']]
            assert len(targets) == 1, (p['id'], p['find'])
            targets[0]['text'] = targets[0]['text'].replace(p['find'], p['replace'])
        else:
            assert p['find'] in q.get(p['field'], ''), (p['id'], p['field'], p['find'])
            q[p['field']] = q[p['field']].replace(p['find'], p['replace'])
    else:
        raise ValueError(a)
    if a != 'remove': q['_reviewed'] = '2026-11'
    stats[a] += 1

removed |= set(P.get('hold', []))  # not yet reviewed
for e in bank:
    bank[e] = [q for q in bank[e] if q['id'] not in removed]
    for q in bank[e]:
        assert sum(o['correct'] for o in q['options']) >= 1, q['id']
json.dump(bank, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({e: len(v) for e, v in bank.items()}, dict(stats))
