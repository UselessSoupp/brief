#!/usr/bin/env python3
"""Plain language check for a Brief edition.

Usage: python3 tools/plaincheck.py data/briefs/<date>.json
Flags long sentences, semicolons, jargon and unexplained acronyms in the text
fields readers see. Fix what it flags before publishing.
"""
import json, re, sys

FIELDS = {"title", "bluf", "headline", "summary", "assessment", "update", "argument",
          "whyNonObvious", "counter", "what", "soWhat", "claim", "caseFor", "caseAgainst",
          "whyBelieved", "unknowns", "overall", "change", "answer", "support", "against",
          "description", "reason", "note"}
JARGON = ["posture", "kinetic", "littoral", "signpost", "overhang", "base case", "tempo",
          "second order", "third order", "decapitation", "lawfare", "gray network",
          "threat inflation", "sequencing", "de facto", "in practice", "modalities",
          "force posture", "theater", "ISR", "C2", "ICD 203", "Admiralty"]
COMMON = {"US", "UK", "EU", "UN", "NATO", "AP", "BBC", "CNN", "FBI", "CIA", "DOJ", "AI",
          "GDP", "TV", "OK", "ET", "UTC", "WHO", "NPR", "NYT", "PM", "MP", "MPs", "LNG",
          "ID", "CEO", "COVID", "DC", "USA", "AM", "PM", "II", "III"}

def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, str) and k in FIELDS:
                yield f"{path}.{k}", v
            else:
                yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, f"{path}[{i}]")

def main(p):
    b = json.load(open(p))
    long_s, semis, jar, acr = [], 0, {}, {}
    for where, t in walk(b):
        semis += t.count(";")
        for s in re.split(r"(?<=[.!?])\s+", t):
            n = len(s.split())
            if n > 28:
                long_s.append((n, where, s[:140]))
        low = t.lower()
        for j in JARGON:
            if re.search(r"\b"+re.escape(j.lower())+r"\b", low):
                jar.setdefault(j, []).append(where)
        for a in re.findall(r"\b[A-Z]{2,6}s?\b", t):
            if a not in COMMON:
                acr[a] = acr.get(a, 0) + 1
    print(f"Sentences over 28 words: {len(long_s)}")
    for n, w, s in sorted(long_s, reverse=True)[:25]:
        print(f"  {n:>3}w {w}: {s}")
    print(f"Semicolons: {semis} (aim for zero; split into two sentences)")
    print("Jargon found:", {k: len(v) for k, v in jar.items()} or "none")
    print("Acronyms to spell out on first use:", dict(sorted(acr.items(), key=lambda x: -x[1])) or "none")

if __name__ == "__main__":
    main(sys.argv[1])
