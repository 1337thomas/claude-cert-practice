"""Answer-length bias check: is the correct option recognisable by its length alone (either direction)?

Usage: python -I lengthcheck.py <final_bank.json> [patches_length.json] [--list A,C,S] [--exam CCAR-F]

Prints, per exam and per source, how often the correct option is strictly the longest (base rate without bias:
1/n for single choice, 1/C(n,k) for multiple response) and, for single-answer items, strictly the shortest
(base rate 1/n), plus how many questions fall into each class:
  A  correct option(s) strictly the longest AND >= 1.5x the median wrong option
  B  correct option(s) strictly the longest, < 1.5x
  C  decoy: one wrong option is >= 1.5x the longest correct one and >= 1.3x the next wrong one
  S  single answer: correct option strictly the shortest AND <= 0.67x the median wrong option (reverse tell)
If a patches file is given, it is used as a gate for the questions it touches (exit 1 on failure):
  - no touched question may be in class A, C or S,
  - all option lengths within +-35 % of the question's mean option length,
  - across the touched questions of each exam, the correct option may be the longest (ties count) in at most
    35 % of items and the shortest (ties count, single answer) in at most 35 % -- same limits as lint_original.py.
"""
import json, re, sys, statistics as st, collections
from math import comb

sys.stdout.reconfigure(encoding='utf-8')
EXAM = {'associate-foundations': 'CCAO-F', 'developer-foundations': 'CCDV-F',
        'architect-foundations': 'CCAR-F', 'architect-professional': 'CCAR-P',
        'developer-professional': 'CCDV-P'}
SPREAD = 0.35             # max deviation of any option from the mean option length (touched questions only)
MAX_LONGEST_SHARE = 0.35  # touched questions per exam: correct option is (one of) the longest
MAX_SHORTEST_SHARE = 0.35  # touched single-answer questions per exam: correct option is (one of) the shortest
L = lambda t: len(re.sub(r'\s+', ' ', t.strip()))


def classify(q):
    ls = [L(o['text']) for o in q['options']]
    cs = [o['correct'] for o in q['options']]
    cl = [l for l, c in zip(ls, cs) if c]
    wl = sorted(l for l, c in zip(ls, cs) if not c)
    ratio = st.mean(cl) / st.median(wl)
    strict = min(cl) > max(wl)
    short = len(cl) == 1 and cl[0] < min(wl)
    if strict:
        return ('A' if ratio >= 1.5 else 'B'), ratio, strict, short, ls
    if len(wl) > 1 and wl[-1] >= 1.5 * max(cl) and wl[-1] >= 1.3 * wl[-2]:
        return 'C', ratio, strict, short, ls
    if short and ratio <= 1 / 1.5:
        return 'S', ratio, strict, short, ls
    return '', ratio, strict, short, ls


def main(argv):
    args = [a for a in argv if not a.startswith('--')]
    opts = dict(a[2:].split('=', 1) if '=' in a else (a[2:], '') for a in argv if a.startswith('--'))
    bank = json.load(open(args[0], encoding='utf-8'))
    touched = set()
    if len(args) > 1:
        touched = {p['id'] for p in json.load(open(args[1], encoding='utf-8'))['items']}
    rows = []
    for e, items in bank.items():
        for q in items:
            k = sum(o['correct'] for o in q['options'])
            cls, ratio, strict, short, ls = classify(q)
            cl = [l for l, o in zip(ls, q['options']) if o['correct']]
            rows.append(dict(exam=EXAM.get(e, e), source=q['source'], id=q['id'], cls=cls, ratio=ratio, k=k,
                             strict=strict, short=short, base=1 / comb(len(ls), k), ls=ls,
                             tie_long=max(cl) == max(ls), tie_short=k == 1 and cl[0] == min(ls)))
    if opts.get('exam'):
        rows = [r for r in rows if r['exam'] == opts['exam']]

    def line(name, rs):
        n = len(rs); c = collections.Counter(r['cls'] for r in rs)
        singles = [r for r in rs if r['k'] == 1] or [None]
        sh = sum(r['short'] for r in singles if r) / len(singles)
        print(f"{name:34}{n:6}{sum(r['strict'] for r in rs) / n:9.1%}{sh:9.1%}{sum(r['base'] for r in rs) / n:7.1%}"
              f"{st.median(r['ratio'] for r in rs):7.2f}{c['A']:6}{c['B']:6}{c['C']:6}{c['S']:6}")

    print(f"{'group':34}{'N':>6}{'longest':>9}{'shortest':>9}{'base':>7}{'med.q':>7}{'A':>6}{'B':>6}{'C':>6}{'S':>6}")
    line('ALL', rows)
    for ex in ['CCAO-F', 'CCDV-F', 'CCAR-F', 'CCAR-P', 'CCDV-P']:
        if any(r['exam'] == ex for r in rows): line(ex, [r for r in rows if r['exam'] == ex])
    for (ex, s) in sorted({(r['exam'], r['source']) for r in rows}):
        line(f'  {ex} / {s}', [r for r in rows if r['exam'] == ex and r['source'] == s])

    if 'list' in opts:
        want = set(opts['list'].split(','))
        for r in sorted(rows, key=lambda r: -r['ratio']):
            if r['cls'] in want: print(f"{r['cls']} {r['ratio']:5.2f} {r['exam']} {r['id']}  {r['ls']}")

    if touched:
        bad = []
        known = {r['id']: r for r in rows}
        hit = []
        for i in sorted(touched):
            r = known.get(i)
            if r is None:
                if not opts.get('exam'): bad.append(f'{i}: not in bank')
                continue
            hit.append(r)
            m = st.mean(r['ls'])
            spread = max(abs(l - m) / m for l in r['ls'])
            if r['cls'] in ('A', 'C', 'S') or spread > SPREAD:
                bad.append(f"{i}: class {r['cls'] or '-'}, ratio {r['ratio']:.2f}, spread {spread:.0%}, lengths {r['ls']}")
        print(f"\npatched questions checked: {len(touched)}")
        for ex in sorted({r['exam'] for r in hit}):
            g = [r for r in hit if r['exam'] == ex]; s1 = [r for r in g if r['k'] == 1]
            lo = sum(r['tie_long'] for r in g) / len(g)
            sh = sum(r['tie_short'] for r in s1) / max(len(s1), 1)
            print(f"  {ex}: {len(g)} patched, correct longest (ties count) {lo:.0%}, shortest {sh:.0%} (max {MAX_LONGEST_SHARE:.0%} each)")
            if lo > MAX_LONGEST_SHARE: bad.append(f'{ex}: correct option is the longest in {lo:.0%} of patched items')
            if sh > MAX_SHORTEST_SHARE: bad.append(f'{ex}: correct option is the shortest in {sh:.0%} of patched single-answer items')
        print(f"failing: {len(bad)}")
        for b in bad: print('  FAIL', b)
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
