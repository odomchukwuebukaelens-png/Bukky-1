"""Search Openverse for openly licensed photos and download thumbnails for review.
usage: python3 -I tools/find_images.py queries.json outdir"""
import json, sys, os, time, subprocess, urllib.parse

OK = {"pdm", "cc0", "by", "by-sa"}

def get(url, out=None):
    args = ["curl", "-sS", "--max-time", "60", "-A", "MapVideo/1.0 (educational documentary)", url]
    if out: args += ["-o", out]
    return subprocess.run(args, capture_output=True, text=True).stdout

if __name__ == "__main__":
    Q = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    meta = {}
    for key, query in Q.items():
        url = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": query, "license": ",".join(sorted(OK)), "page_size": 8})
        try: res = json.loads(get(url)).get("results", [])
        except Exception as e: print(key, "ERR", e); res = []
        meta[key] = []
        for i, r in enumerate(res[:6]):
            f = f"{out}/{key}_{i}.jpg"
            get(f"https://api.openverse.org/v1/images/{r['id']}/thumb/", f)
            meta[key].append({"file": f, "id": r["id"], "title": r.get("title"), "license": r.get("license"), "license_version": r.get("license_version"),
                              "creator": r.get("creator"), "source": r.get("source"), "landing": r.get("foreign_landing_url"), "url": r.get("url"),
                              "w": r.get("width"), "h": r.get("height")})
        print(key, len(meta[key]), [m["title"][:40] for m in meta[key]], flush=True)
        time.sleep(2)
    json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
