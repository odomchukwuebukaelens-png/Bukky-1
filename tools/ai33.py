"""Minimal client for api.ai33.pro (auth is injected by the session proxy)."""
import json, sys, time, urllib.request, urllib.parse, uuid, mimetypes, os

BASE = "https://api.ai33.pro"
HDR = {"xi-api-key": "proxy-injected"}

def _req(method, path, data=None, headers=None, raw=False, tries=8):
    import random, urllib.error
    h = dict(HDR); h.update(headers or {})
    for k in range(tries):
        r = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(r, timeout=300) as resp:
                b = resp.read()
            return b if raw else json.loads(b)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 502, 503, 504) or k == tries - 1:
                raise
            wait_s = float(e.headers.get("Retry-After") or 0) or min(60, 2 ** k)
            time.sleep(wait_s + random.random())

def get(path): return _req("GET", path)
def post_json(path, obj):
    return _req("POST", path, json.dumps(obj).encode(), {"Content-Type": "application/json"})
def post_form(path, fields, files=()):
    bnd = uuid.uuid4().hex; out = []
    for k, v in fields.items():
        out.append(f'--{bnd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
    for k, p in files:
        ct = mimetypes.guess_type(p)[0] or "application/octet-stream"
        out.append(f'--{bnd}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(p)}"\r\nContent-Type: {ct}\r\n\r\n'.encode())
        out.append(open(p, "rb").read() + b"\r\n")
    out.append(f"--{bnd}--\r\n".encode())
    return _req("POST", path, b"".join(out), {"Content-Type": f"multipart/form-data; boundary={bnd}"})

def wait(task_id, every=8, limit=1800):
    t0 = time.time()
    while True:
        t = get(f"/v1/task/{task_id}")
        if t.get("status") in ("done", "error", "failed"):
            return t
        if time.time() - t0 > limit:
            raise TimeoutError(task_id)
        time.sleep(every)

def download(url, dest):
    import subprocess
    subprocess.run(["curl", "-sSfL", "-A", "Mozilla/5.0", "-o", dest, url], check=True)
    return dest

if __name__ == "__main__":
    print(json.dumps(get(sys.argv[1]), indent=1)[:4000])
