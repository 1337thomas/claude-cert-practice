import json,sys,re,collections
html=open(sys.argv[1],encoding='utf-8').read().split('\n')
line=html[175]
start=line.index('{'); 
dec=json.JSONDecoder(); obj,end=dec.raw_decode(line[start:])
print(repr(line[:start]), repr(line[start+end:start+end+80]))
json.dump(obj,open('bank.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
for k,v in obj.items():
    c=collections.Counter(q['source'] for q in v)
    print(k,len(v),dict(c))
print(json.dumps(obj['developer-foundations'][0],ensure_ascii=False)[:1500])
print(set(k for v in obj.values() for q in v for k in q))
