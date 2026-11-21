"""Search Library of Congress photos; verify each item's rights statement; keep only
'No known restrictions' / public domain items. usage: python3 -I tools/find_loc.py queries.json outdir"""
import json, sys, os, time, subprocess, urllib.parse

def get(url, out=None):
    args = ["curl", "-sSL", "--max-time", "60", "-A", "MapVideo/1.0 (educational documentary)", url]
    if out: args += ["-o", out]
    return subprocess.run(args, capture_output=True, text=True).stdout

def rights_ok(item_url):
    try: d = json.loads(get(item_url.rstrip("/") + "/?fo=json"))
    except Exception: return None
    it = d.get("item", {})
    r = it.get("rights_advisory") or it.get("rights") or d.get("rights") or []
    r = " ".join(r) if isinstance(r, list) else str(r)
    low = r.lower()
    return r if ("no known restrictions" in low or "public domain" in low) and "rights status not evaluated" not in low else None

if __name__ == "__main__":
    Q = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    meta = json.load(open(f"{out}/meta.json")) if os.path.exists(f"{out}/meta.json") else {}
    for key, spec in Q.items():
        if key in meta and meta[key]: continue
        q, dates = (spec, None) if isinstance(spec, str) else (spec["q"], spec.get("dates"))
        params = {"q": q, "fo": "json", "c": 15}
        if dates: params["dates"] = dates
        try: res = json.loads(get("https://www.loc.gov/photos/?" + urllib.parse.urlencode(params))).get("results", [])
        except Exception as e: print(key, "ERR", e); continue
        meta[key] = []
        for r in res:
            imgs = [u for u in (r.get("image_url") or []) if ".jpg" in u]
            if not imgs or len(meta[key]) >= 4: continue
            rt = rights_ok(r["id"]); time.sleep(0.8)
            if not rt: continue
            big = imgs[-1].split("#")[0]
            f = f"{out}/{key}_{len(meta[key])}.jpg"; get(big, f)
            meta[key].append({"file": f, "title": r.get("title"), "date": r.get("date"), "rights": rt[:200], "source": r["id"], "img": big})
        print(key, len(res), "results,", len(meta[key]), "kept:", [m["title"][:45] for m in meta[key]], flush=True)
        json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
