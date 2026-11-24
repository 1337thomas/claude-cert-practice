"""Rebuild the question catalog from the current bank (keeps prior manual repairs) + upstream sources.

Usage: python -I build.py <in_bank.json> <out_bank.json>
"""
import sys, os, json, re, collections, hashlib, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loaders as L

sys.stdout.reconfigure(encoding='utf-8')
src_path, out_path = sys.argv[1], sys.argv[2]
bank = json.load(open(src_path, encoding='utf-8'))
LET = 'ABCDE'
norm = lambda s: re.sub(r'\W+', ' ', s or '').strip().lower()

CCARF = {1: 'Agentic Architecture & Orchestration', 2: 'Tool Design & MCP Integration',
         3: 'Claude Code Configuration & Workflows', 4: 'Prompt Engineering & Structured Output',
         5: 'Context Management & Reliability'}
CCARP = {1: 'Solution Design & Architecture', 2: 'Claude Models, Prompting & Context Engineering',
         3: 'Integration', 4: 'Evaluation, Testing & Optimization', 5: 'Governance, Safety & Risk Management',
         6: 'Stakeholder Communication & Lifecycle Management',
         7: 'Developer Productivity & Operational Enablement'}
CCDVF = {'agents': 'Agents and Workflows', 'integration': 'Applications and Integration',
         'modelopt': 'Model Selection and Optimization', 'promptcontext': 'Prompt and Context Engineering',
         'toolsmcp': 'Tools and MCPs', 'security': 'Security and Safety', 'claudecode': 'Claude Code',
         'evaldebug': 'Eval, Testing, and Debugging'}
CCDVF_ALIAS = {v.replace(' and ', ' & ').replace(', & ', ' & ').replace('Testing &', 'Testing &'): v for v in CCDVF.values()}
CCDVF_ALIAS['Eval, Testing & Debugging'] = 'Eval, Testing, and Debugging'

# Answer-key corrections confirmed by review: key = (exam, normalized stem prefix) -> correct option text prefix
OVERRIDES = {
    ('associate-foundations', norm('Your team drafts hundreds of short, routine customer replies daily')):
        'Use the fastest, lowest-cost model for routine replies',
}
if os.path.exists('overrides.json'):  # filled during the one-by-one review
    for o in json.load(open('overrides.json', encoding='utf-8')):
        OVERRIDES[(o['exam'], norm(o['stem']))] = o['correct']

REMOVE = set()
if os.path.exists('remove.json'):
    REMOVE = {(r['exam'], norm(r['stem'])) for r in json.load(open('remove.json', encoding='utf-8'))}


def mk(q, domain, source, options, correct_idx, explanation='', uid='', select=None, difficulty=None):
    item = {'id': uid, 'q': q.strip(), 'domain': domain, 'source': source,
            'options': [{'text': t.strip(), 'correct': i in correct_idx} for i, t in enumerate(options)]}
    if explanation: item['explanation'] = explanation.strip()
    if select: item['_select'] = select
    if difficulty: item['_difficulty'] = difficulty
    return item


out = {k: [] for k in bank}
index = {k: {} for k in bank}           # exam -> normalized stem -> item
stats = collections.Counter()

# 1) carry over current bank, keyed by stem
for exam, items in bank.items():
    for q in items:
        q = dict(q)
        if not q['source']: q['source'] = 'Amey-Thakur'
        if q['source'].startswith('Aliquanto3'): q['source'] = 'Aliquanto3'
        index[exam][norm(q['q'])] = q
        out[exam].append(q)


def find(exam, *stems):
    for s in stems:
        if norm(s) in index[exam]: return index[exam][norm(s)]
    return None


def add(exam, item, *alt_stems):
    """Enrich an existing entry (matched by stem) or append as new."""
    cur = find(exam, item['q'], *alt_stems)
    if cur is None:
        # also dedup against near-identical stems from other sources
        out[exam].append(item); index[exam][norm(item['q'])] = item; stats[f'new:{exam}:{item["source"]}'] += 1
        return item
    # keep current options/answers (prior repairs), refresh metadata
    if item.get('explanation') and not cur.get('explanation'): cur['explanation'] = item['explanation']
    if item['domain'] and cur['domain'] in ('General', '') or re.match(r'^D\d$', cur['domain'] or ''):
        cur['domain'] = item['domain']
    if len(item['q']) > len(cur['q']) and norm(cur['q']) in norm(item['q']):  # restored scenario
        index[exam][norm(item['q'])] = cur; cur['q'] = item['q']; stats[f'context-restored:{exam}'] += 1
    cur['id'] = item['id']
    stats[f'enriched:{exam}:{item["source"]}'] += 1
    return cur


# 2) Amey-Thakur (all four exams)
for q in L.amey():
    keys = sorted(q['options'])
    item = mk(q['question'], q['domain'], 'Amey-Thakur', [q['options'][k] for k in keys],
              [keys.index(q['answer'])], q['rationale'], 'amey:' + q['id'])
    add(q['exam'], item)

# 3) Connectry (CCAR-F) — restore scenario
for q in L.connectry():
    keys = sorted(q['options'])
    expl = q['explanation']
    item = mk(q['scenario'].strip() + '\n\n' + q['text'].strip(), CCARF[q['domainId']], 'Connectry-io',
              [q['options'][k] for k in keys], [keys.index(q['correctAnswer'])], expl,
              'connectry:' + q['id'], difficulty=q.get('difficulty'))
    add('architect-foundations', item, q['text'])

# 4) MilindGaharwar (CCAR-F)
for q in L.milind():
    keys = sorted(q['choices']); ans = q['answer']
    dom = q['domain_name'] if q['domain'] != 'SQ' else 'Official exam-guide sample'
    item = mk(q['question'], dom, 'MilindGaharwar', [q['choices'][k] for k in keys],
              [keys.index(a) for a in ans if a in keys], q.get('explanation', ''), 'milind:' + q['id'])
    add('architect-foundations', item)

# 5) mrKindly (CCDV-F)
for i, q in enumerate(L.mrkindly()):
    item = mk(q['q'], 'General', 'mrKindly', q['options'], [q['letters'].index(c) for c in q['correct']],
              q['explanation'], f'mrkindly:{i + 1}')
    add('developer-foundations', item)

# 6) CCDVFTrainer quiz + simulator (CCDV-F)
for q in L.ccdvf_quiz():
    item = mk(q['prompt'], CCDVF.get(q['topic'], q['topic']), 'CCDVFTrainer', [o['text'] for o in q['options']],
              [i for i, o in enumerate(q['options']) if o['correct']], q.get('explanation', ''), 'ccdvf:' + str(q['id']))
    add('developer-foundations', item)
sim_new = 0
for q in (L.ccdvf_sim() if os.environ.get('WITH_SIM') else []):  # simulator dropped after review (quality)
    if q.get('dupOf') is not None: continue
    stem = q['ctx'].strip() + '\n\n' + q['q'].strip()
    # dedup vs mrKindly etc. by option overlap (sim items are often reworded mrKindly items)
    opts_n = {norm(o) for o in q['opts']}
    if any(len(opts_n & {norm(o['text']) for o in x['options']}) >= 2 for x in out['developer-foundations']):
        stats['sim-dup-skipped'] += 1; continue
    import difflib
    if any(difflib.SequenceMatcher(None, stem.lower(), x['q'].lower()).ratio() > 0.6 for x in out['developer-foundations']):
        stats['sim-dup-skipped'] += 1; continue
    item = mk(stem, 'General', 'CCDVFTrainer', q['opts'], [q['ans']], '', f'ccdvf-sim:{q["n"]}')
    add('developer-foundations', item)

# 7) Aliquanto3 (CCAR-P)
for q in L.aliquanto():
    item = mk(q['question'], f"D{q['domain']} {CCARP[q['domain']]}", 'Aliquanto3', q['options'], q['correct'],
              q.get('explanation', ''), 'aliquanto:' + q['id'], select=q.get('select') if q.get('select', 1) > 1 else None)
    add('architect-professional', item)

# 7b) MIT sources added 2026-11 (converted by newsrc/build_new.py, see newsrc/SOURCES.md)
if os.path.exists('newsrc/new_questions.json'):
    for exam, items in json.load(open('newsrc/new_questions.json', encoding='utf-8')).items():
        for item in items:
            add(exam, item)

# 7c) Original questions written for this site (one file per exam, see newsrc/ORIGINAL.md).
#     Unlike upstream items they carry per-option rationale (`why`) and a fixed mock-set number (`mock`).
for path in sorted(glob.glob('newsrc/original_*.json')):
    for exam, items in json.load(open(path, encoding='utf-8')).items():
        out.setdefault(exam, []); index.setdefault(exam, {})
        for item in items:
            add(exam, item)

# 8) normalize domains, flags, overrides, removals
REF_OPT = re.compile(r'^(both [A-E] and [A-E]|[A-E] and [A-E] (are|both)|all of the above|none of the above|neither [A-E] nor [A-E]|either [A-E] or [A-E])', re.I)
for exam, items in out.items():
    kept = []
    for q in items:
        if exam == 'developer-foundations': q['domain'] = CCDVF_ALIAS.get(q['domain'], q['domain'])
        if exam == 'architect-professional' and not re.match(r'^D\d ', q['domain']):
            inv = {v: k for k, v in CCARP.items()}
            if q['domain'] in inv: q['domain'] = f"D{inv[q['domain']]} {q['domain']}"
        if any(REF_OPT.search(o['text']) for o in q['options']): q['_fixed'] = True
        k = (exam, norm(q['q']))
        if any(k[0] == e and k[1].startswith(s) for (e, s) in REMOVE): stats['removed'] += 1; continue
        for (e, s), ctext in OVERRIDES.items():
            if e == exam and norm(q['q']).startswith(s):
                hit = [o for o in q['options'] if norm(o['text']).startswith(norm(ctext))]
                assert len(hit) == 1, (s, ctext)
                for o in q['options']: o['correct'] = o is hit[0]
                q['_reviewed'] = 'answer-corrected'; stats['override'] += 1
        n_correct = sum(o['correct'] for o in q['options'])
        assert n_correct >= 1, q['q'][:80]
        if not q.get('id'):  # stable across runs (built-in hash() is salted per process)
            q['id'] = f"{q['source'].lower()}:{int(hashlib.md5(norm(q['q']).encode()).hexdigest(), 16) % 10**8}"
        kept.append(q)
    out[exam] = kept

for exam, items in out.items():
    print(exam, len(items), dict(collections.Counter(q['source'] for q in items)))
for k, v in sorted(stats.items()): print(' ', k, v)
print('no explanation:', {e: sum(1 for q in v if not q.get('explanation')) for e, v in out.items()})
print('fixed-order:', sum(1 for v in out.values() for q in v if q.get('_fixed')))
json.dump(out, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
