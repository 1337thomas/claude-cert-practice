"""Answer-length bias check: is the correct option recognisable by its length alone?

Usage: python -I lengthcheck.py <final_bank.json> [patches_length.json] [--list A,C] [--exam CCDV-F]

Prints, per exam and per source, how often the correct option is the longest (base rate without bias:
1/n for single choice, 1/C(n,k) for multiple response) and how many questions fall into each class:
  A  correct option(s) strictly the longest AND >= 1.5x the median wrong option
  B  correct option(s) strictly the longest, < 1.5x
  C  decoy: one wrong option is >= 1.5x the longest correct one and >= 1.3x the next wrong one
If a patches file is given, every question it touches must leave class A and C and keep all option lengths
within +-35 % of the question's mean option length; otherwise the script exits with 1 (use it as a gate after patch.py).
"""
import json, re, sys, statistics as st, collections
from math import comb

sys.stdout.reconfigure(encoding='utf-8')
EXAM = {'associate-foundations': 'CCAO-F', 'developer-foundations': 'CCDV-F',
        'architect-foundations': 'CCAR-F', 'architect-professional': 'CCAR-P'}
SPREAD = 0.35  # max deviation of any option from the mean option length (touched questions only)
L = lambda t: len(re.sub(r'\s+', ' ', t.strip()))


def classify(q):
    ls = [L(o['text']) for o in q['options']]
    cs = [o['correct'] for o in q['options']]
    cl = [l for l, c in zip(ls, cs) if c]
    wl = sorted(l for l, c in zip(ls, cs) if not c)
    ratio = st.mean(cl) / st.median(wl)
    strict = min(cl) > max(wl)
    if strict:
        return ('A' if ratio >= 1.5 else 'B'), ratio, strict, ls
    if len(wl) > 1 and wl[-1] >= 1.5 * max(cl) and wl[-1] >= 1.3 * wl[-2]:
        return 'C', ratio, strict, ls
    return '', ratio, strict, ls


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
            cls, ratio, strict, ls = classify(q)
            rows.append(dict(exam=EXAM.get(e, e), source=q['source'], id=q['id'], cls=cls, ratio=ratio,
                             strict=strict, base=1 / comb(len(ls), k), ls=ls, q=q))
    if opts.get('exam'):
        rows = [r for r in rows if r['exam'] == opts['exam']]

    def line(name, rs):
        n = len(rs); c = collections.Counter(r['cls'] for r in rs)
        print(f"{name:34}{n:6}{sum(r['strict'] for r in rs) / n:9.1%}{sum(r['base'] for r in rs) / n:8.1%}"
              f"{st.median(r['ratio'] for r in rs):8.2f}{c['A']:6}{c['B']:6}{c['C']:6}")

    print(f"{'group':34}{'N':>6}{'longest':>9}{'base':>8}{'med.q':>8}{'A':>6}{'B':>6}{'C':>6}")
    line('ALL', rows)
    for ex in ['CCAO-F', 'CCDV-F', 'CCAR-F', 'CCAR-P']:
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
        for i in sorted(touched):
            r = known.get(i)
            if r is None:
                if not opts.get('exam'): bad.append(f'{i}: not in bank')
                continue
            m = st.mean(r['ls'])
            spread = max(abs(l - m) / m for l in r['ls'])
            if r['cls'] in ('A', 'C') or spread > SPREAD:
                bad.append(f"{i}: class {r['cls'] or '-'}, ratio {r['ratio']:.2f}, spread {spread:.0%}, lengths {r['ls']}")
        print(f"\npatched questions checked: {len(touched)}, failing: {len(bad)}")
        for b in bad: print('  FAIL', b)
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
