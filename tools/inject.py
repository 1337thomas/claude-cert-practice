import json,sys,re
html,bank,out=sys.argv[1:4]
t=open(html,encoding='utf-8').read()
data=json.dumps(json.load(open(bank,encoding='utf-8')),ensure_ascii=False,separators=(',',':')).replace('</','<'+chr(92)+'/')
t2,n=re.subn(r'(<script id="data" type="application/json">\n).*?(\n</script>)',lambda m:m.group(1)+data+m.group(2),t,count=1,flags=re.S)
assert n==1
open(out,'w',encoding='utf-8',newline='\n').write(t2); print('ok',len(t2))
