#!/usr/bin/env python3
"""Split sentences over 28 words at a natural joint near the middle. Usage: splitlong.py file.json"""
import json, re, sys
sys.path.insert(0, __file__.rsplit('/',1)[0]); import plaincheck as pc
JOINTS=[(", and ",". "),(", but ",". But "),(", while ",". "),(", so ",". So "),(", though ",". Still, "),(", as ",". "),(", after ",". This came after "),(", with ",". It comes with ")]
def fix(s):
    w=len(s.split())
    if w<=28: return s
    best=None
    for j,rep in JOINTS:
        for m in re.finditer(re.escape(j), s):
            left=len(s[:m.start()].split()); right=w-left
            if left>=7 and right>=7:
                score=abs(left-right)
                if best is None or score<best[0]: best=(score,m.start(),j,rep)
    if not best: return s
    _,i,j,rep=best
    rest=s[i+len(j):]
    if rep==". ": rest=rest[:1].upper()+rest[1:]
    return fix(s[:i]+rep+rest)
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str) and k in pc.FIELDS:
                parts=re.split(r"(?<=[.!?])\s+", v); o[k]=" ".join(fix(p) for p in parts)
            else: walk(v)
    elif isinstance(o,list):
        for v in o: walk(v)
p=sys.argv[1]; b=json.load(open(p)); walk(b); json.dump(b,open(p,'w'),ensure_ascii=False)
