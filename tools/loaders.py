import json,re,glob,sys,os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'pylib'))
import json5
UP=os.path.join(os.path.dirname(os.path.abspath(__file__)),'upstream')
def js_array(path,var=None):
    t=open(path,encoding='utf-8').read()
    out=[]
    # find assignments / concat([...])
    for m in re.finditer(r'(?:=\s*|concat\()\s*(\[)',t):
        i=m.start(1); depth=0; instr=None; esc=False
        for j in range(i,len(t)):
            c=t[j]
            if instr:
                if esc: esc=False
                elif c==chr(92): esc=True
                elif c==instr: instr=None
            elif c in '"\'`': instr=c
            elif c=='[': depth+=1
            elif c==']':
                depth-=1
                if depth==0: break
        try: out.append(json5.loads(t[i:j+1]))
        except Exception as e: print('parse fail',path,e,file=sys.stderr)
    return out
def amey():
    return json.load(open(f'{UP}/CLAUDE-CERTIFICATIONS/question-bank.json',encoding='utf-8'))['questions']
def connectry():
    qs=[]
    for f in sorted(glob.glob(f'{UP}/connectry-npm/package/dist/data/questions/*.json')):
        d=json.load(open(f,encoding='utf-8')); qs+= d if isinstance(d,list) else d['questions']
    return qs
def ccdvf_quiz():
    a=js_array(f'{UP}/CCDVFTrainer/assets/js/questions.js'); return [q for arr in a for q in arr if isinstance(q,dict) and 'prompt' in q]
def ccdvf_sim():
    a=js_array(f'{UP}/CCDVFTrainer/simulator/questions.js'); return [q for arr in a for q in arr if isinstance(q,dict)]
def aliquanto():
    qs=[]
    for f in sorted(glob.glob(f'{UP}/ccar-p-revision/data/questions-*.js')):
        for arr in js_array(f): qs+=arr
    return qs
def milind():
    t=open(f'{UP}/claude-architect-quiz/claude_architect_quiz.html',encoding='utf-8').read()
    i=t.index('const QUESTIONS = ')+len('const QUESTIONS = ')
    return json.JSONDecoder().raw_decode(t[i:])[0]
def mrkindly():
    t=open(f'{UP}/claude-certified-developer/README.md',encoding='utf-8').read()
    out=[]
    for blk in re.split(r'\n### Question \d+ of \d+\n',t)[1:]:
        q=re.search(r'\*\*Question:\*\*\s*(.*?)\n\s*\n\*\*Options',blk,re.S).group(1).strip()
        opts=re.findall(r'^- \*\*([A-E])\.\*\*\s*(.*)$',blk,re.M)
        ca=re.search(r'\*\*Correct Answers?:\*\*\s*(.*)',blk).group(1)
        letters=re.findall(r'\*\*([A-E])\.\*\*',ca)
        ex=re.search(r'\*\*Explanation:\*\*\s*(.*?)(?:\n---|\Z)',blk,re.S)
        out.append(dict(q=q,options=[o[1].strip() for o in opts],letters=[o[0] for o in opts],correct=letters,explanation=ex.group(1).strip() if ex else ''))
    return out
