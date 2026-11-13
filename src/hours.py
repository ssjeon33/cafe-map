import json,re
D={'일':0,'월':1,'화':2,'수':3,'목':4,'금':5,'토':6}
ORDER=[1,2,3,4,5,6,0]
def days(spec):
    spec=spec.strip()
    if spec in ('매일',''): return list(range(7))
    if spec=='평일': return [1,2,3,4,5]
    if spec=='주말': return [6,0]
    m=re.fullmatch(r'([월화수목금토일])–([월화수목금토일])',spec)
    if m:
        a,b=ORDER.index(D[m.group(1)]),ORDER.index(D[m.group(2)]); return ORDER[a:b+1]
    return [D[x] for x in re.split(r'[·,]',spec)]
def tm(s):
    s=s.strip()
    if ':' in s: h,mm=s.split(':')
    else: h,mm=s,'0'
    return int(h)*60+int(mm)
def span(t, base=None):
    t=t.strip().replace('~','–') if re.fullmatch(r'[\d:]+~[\d:]+',t.strip()) else t.strip()
    if t.endswith('~'): o=tm(t[:-1]); c=base[1] if base else None
    elif t.startswith('~'): o=base[0] if base else None; c=tm(t[1:])
    else:
        a,b=t.split('–'); o,c=tm(a),tm(b)
    if c is not None and c<=o: c+=1440
    return [o,c]
def parse(h):
    h=h.strip()
    if h=='24시간': return [[0,1440]]*7, True
    if '확인 필요' in h: return None, False
    mods=re.findall(r'\(([^)]*)\)',h); body=re.sub(r'\s*\([^)]*\)','',h).strip()
    hs=[None]*7; first=None
    for seg in [s.strip() for s in body.split('/')]:
        m=re.fullmatch(r'(매일|평일|주말|[월화수목금토일](?:–[월화수목금토일])?)?\s*(.+)',seg)
        spec,t=m.group(1) or '',m.group(2)
        sp=span(t,first)
        if first is None: first=sp
        for d in days(spec): hs[d]=sp
    for md in mods:
        md=md.strip()
        m=re.fullmatch(r'(.+?) 휴무',md)
        if m:
            for d in days(m.group(1)): hs[d]=None
            continue
        m=re.fullmatch(r'(매일|평일|주말|[월화수목금토일·]+)\s+(.+)',md)
        for d in days(m.group(1)): hs[d]=span(m.group(2),first)
    return hs, False
d=json.load(open('cafes.json',encoding='utf-8'))
for c in d:
    hs,h24=parse(c['h'])
    c.pop('hs',None); c.pop('h24',None)
    if hs is not None: c['hs']=hs
    if h24: c['h24']=1
json.dump(d,open('cafes.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
fm=lambda x:'휴무' if x is None else f'{x[0]//60:02d}:{x[0]%60:02d}-{x[1]//60:02d}:{x[1]%60:02d}'
seen=set()
for c in d:
    if c['h'] in seen: continue
    seen.add(c['h'])
    print(c['h'],'=>', '?' if 'hs' not in c else ' '.join(k+fm(c['hs'][D[k]]) for k in '월화수목금토일'))
