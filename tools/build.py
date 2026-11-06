#!/usr/bin/env python3
"""Assemble the public GitHub Pages copy of Brief.

Usage (from the repo root): python3 tools/build.py . <brief_json> [...] --stories S --forecasts F --meta M

Each brief_json is one full edition (the same object written to briefs/<id> in the db).
Writes:
  <repo>/data/briefs/<id>.json     (one file per edition)
  <repo>/data/index.json           (meta + light record per edition, rebuilt from every file in data/briefs)
  <repo>/data/stories.json, forecasts.json, people.json (public figures only)
Private data (mine/...) is never read or written here.
"""
import json, os, shutil, sys, argparse

def light(bid, b):
    s = [b.get("title", ""), b.get("bluf", "")]
    for sec in b.get("sections") or []:
        for i in sec.get("items") or []:
            s.append((i.get("headline") or "") + " " + (i.get("summary") or ""))
    for c in b.get("conspiracies") or []:
        s.append(c.get("claim") or "")
    for u in b.get("updates") or []:
        s.append(u.get("update") or "")
    for e in b.get("elections") or []:
        s.append(" ".join(c.get("name") or "" for c in e.get("candidates") or []))
    for n in (b.get("discourse") or {}).get("narratives") or []:
        s.append(n.get("narrative") or "")
    wc = b.get("worldConditions") or {}
    return {"_id": bid, "date": b.get("date"), "edition": b.get("edition"), "type": b.get("type"),
            "title": b.get("title"), "bluf": b.get("bluf"), "generatedAt": b.get("generatedAt"),
            "worldConditions": {"postureLevel": wc.get("postureLevel")},
            "_s": " ".join(s).lower()}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo"); ap.add_argument("briefs", nargs="*")
    ap.add_argument("--stories"); ap.add_argument("--forecasts"); ap.add_argument("--meta"); ap.add_argument("--people")
    a = ap.parse_args()
    data = os.path.join(a.repo, "data"); bdir = os.path.join(data, "briefs")
    os.makedirs(bdir, exist_ok=True)
    for p in a.briefs:
        b = json.load(open(p))
        b.pop("watchlist", None)  # personal watchlist coverage stays private
        b.pop("answers", None)  # answers to her private questions stay private
        bid = b.get("_id") or b["date"]
        b.pop("_id", None)
        json.dump(b, open(os.path.join(bdir, bid + ".json"), "w"), ensure_ascii=False)
    for name, p in (("stories", a.stories), ("forecasts", a.forecasts), ("people", a.people)):
        if p:
            json.dump(json.load(open(p)), open(os.path.join(data, name + ".json"), "w"), ensure_ascii=False)
    recs = []
    for f in sorted(os.listdir(bdir)):
        if f.endswith(".json"):
            recs.append(light(f[:-5], json.load(open(os.path.join(bdir, f)))))
    recs.sort(key=lambda r: (r.get("date") or "", r.get("generatedAt") or ""), reverse=True)
    meta = json.load(open(a.meta)) if a.meta else (json.load(open(os.path.join(data, "index.json"))).get("meta") if os.path.exists(os.path.join(data, "index.json")) else {})
    json.dump({"meta": meta, "briefs": recs}, open(os.path.join(data, "index.json"), "w"), ensure_ascii=False)
    open(os.path.join(a.repo, ".nojekyll"), "w").close()
    print(f"{len(recs)} editions, latest {recs[0]['_id'] if recs else 'none'}")

if __name__ == "__main__":
    main()
