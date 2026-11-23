"""Downloads real, freely licensed sound recordings from Wikimedia Commons.

Usage:  python3 citystudio/fetch_sfx.py OUT_DIR
For each sound kind it searches Commons, keeps only Public domain / CC0 /
CC BY files (no share-alike, no non-commercial), picks a suitable one and
saves it as OUT_DIR/<kind>.<ext>. Writes OUT_DIR/CREDITS.txt with the
attribution lines to paste into the YouTube description.
Requests are paced slowly to respect Wikimedia's rate limits.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

UA = "city-studio/1.0 (educational history videos; contact via repository)"
API = "https://commons.wikimedia.org/w/api.php"
SEARCHES = {
    "birds": ["birdsong forest", "birds singing"], "water": ["river water flowing", "stream water"],
    "hammer": ["hammering wood", "carpentry hammer"], "chisel": ["stone chisel", "stonemason"],
    "saw": ["hand saw wood", "sawing wood"], "chatter": ["crowd talking", "market crowd"],
    "hooves": ["horse hooves", "horse walking"], "cart": ["horse carriage", "horse cart"],
    "bells": ["church bells"], "traffic": ["city traffic", "street traffic"], "carhorn": ["car horn"],
    "scooter": ["moped", "motor scooter"], "siren": ["police siren", "ambulance siren"], "tram": ["tram", "streetcar"],
    "cheer": ["crowd cheering", "applause crowd"], "fireworks": ["fireworks"], "wind": ["wind howling", "strong wind"],
    "rain": ["rain falling", "rain"], "horn": ["ship horn", "foghorn"], "sword": ["sword clash", "swords fighting"],
    "shouts": ["battle cry", "crowd shouting"], "march": ["marching soldiers", "soldiers marching"],
    "drums": ["war drum", "military drum"], "cannon": ["cannon fire", "cannon shot"], "gunfire": ["musket fire", "gunshots"],
    "bomb": ["explosion"], "fire": ["fire crackling", "fire burning"], "rumble": ["thunder rumble", "building collapse"],
}
OK = re.compile(r"^(public domain|pd|cc0|cc by( \d\.\d)?( [a-z]{2})?)$", re.I)


def api(params, tries=6):
    url = API + "?" + urllib.parse.urlencode(dict(params, format="json"))
    for k in range(tries):
        r = subprocess.run(["curl", "-sS", "-m", "60", "-A", UA, url], capture_output=True, text=True)
        try:
            return json.loads(r.stdout)
        except ValueError:
            print("[city-studio] Wikimedia asked us to slow down - waiting %d s" % (30 * (k + 1)), flush=True)
            time.sleep(30 * (k + 1))
    return {}


def candidates(query):
    d = api({"action": "query", "generator": "search", "gsrsearch": query + " filetype:audio", "gsrnamespace": 6,
             "gsrlimit": 15, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mediatype",
             "iiextmetadatafilter": "LicenseShortName|Artist|LicenseUrl"})
    out = []
    for p in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        m = ii.get("extmetadata", {})
        lic = re.sub("<[^>]+>", "", m.get("LicenseShortName", {}).get("value", "")).strip()
        artist = re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip()
        url = ii.get("url", "")
        size = ii.get("size", 0)
        ext = url.rsplit(".", 1)[-1].lower()
        if not OK.match(lic) or ext not in ("ogg", "oga", "mp3", "wav", "flac", "opus") or not 20_000 < size < 25_000_000:
            continue
        title = p["title"][5:]
        if re.search(r"(^LL-|pronunc|spoken|voice of|\bword\b|\.mid$)", title, re.I):
            continue
        out.append({"title": title, "license": lic, "artist": artist or "unknown", "url": url, "size": size,
                    "ext": ext, "page": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(p["title"].replace(" ", "_"))})
    out.sort(key=lambda c: (0 if re.match("public|pd|cc0", c["license"], re.I) else 1, -min(c["size"], 3_000_000)))
    return out


def duration(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def main():
    out = sys.argv[1]
    only = set(sys.argv[2:])
    os.makedirs(out, exist_ok=True)
    credits = []
    for kind, queries in SEARCHES.items():
        if only and kind not in only:
            continue
        if any(f.startswith(kind + ".") for f in os.listdir(out)):
            print("[city-studio] %-9s already have it" % kind)
            continue
        got = None
        for q in queries:
            for c in candidates(q):
                tmp = os.path.join(out, "_dl." + c["ext"])
                r = subprocess.run(["curl", "-sS", "-m", "300", "-L", "-A", UA, "-o", tmp, c["url"]])
                if r.returncode or duration(tmp) < 1.5:
                    continue
                dest = os.path.join(out, kind + ".wav")
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-t", "90", "-ac", "2", "-ar", "44100",
                                "-af", "loudnorm=I=-18:TP=-2", dest], check=True)
                os.remove(tmp)
                got = c
                break
            time.sleep(4)
            if got:
                break
        if got:
            print("[city-studio] %-9s %s (%s)" % (kind, got["title"], got["license"]), flush=True)
            if not re.match("public|pd|cc0", got["license"], re.I):
                credits.append('"%s" by %s, %s, via Wikimedia Commons' % (got["title"], got["artist"], got["license"]))
            with open(os.path.join(out, "SOURCES.txt"), "a") as f:
                f.write("%s\t%s\t%s\t%s\n" % (kind, got["title"], got["license"], got["page"]))
        else:
            print("[city-studio] %-9s nothing suitable found - the generated sound will be used" % kind, flush=True)
        time.sleep(4)
    if credits:
        with open(os.path.join(out, "CREDITS.txt"), "a") as f:
            f.write("\n".join(credits) + "\n")


if __name__ == "__main__":
    main()
