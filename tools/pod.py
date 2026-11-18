"""Drive a RunPod pod through its JupyterLab (HTTPS only; SSH is blocked here).
Auth: the session proxy injects `Authorization: token <JUPYTER_PASSWORD>` for the pod host.
Usage:  POD=<pod_id> python3 pod.py run "nvidia-smi"
        POD=<pod_id> python3 pod.py put local_file /workspace/remote_file
        POD=<pod_id> python3 pod.py get /workspace/remote_file local_file
"""
import base64, json, os, sys, time, uuid, urllib.request, urllib.parse, urllib.error
import websocket  # websocket-client

POD = os.environ.get("POD", "")
BASE = f"https://{POD}-8888.proxy.runpod.net"
HDR = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) pod-client"}  # the session proxy adds "Authorization: Token <JUPYTER_PASSWORD>"

def api(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    h = dict(HDR, **({"Content-Type": "application/json"} if data else {}))
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=600) as r:
        b = r.read(); return json.loads(b) if b else {}

def put(local, remote, chunk=8 << 20):
    remote = remote.lstrip("/"); size = os.path.getsize(local); n = 0
    with open(local, "rb") as f:
        while True:
            b = f.read(chunk); n += 1; last = f.tell() >= size
            body = {"type": "file", "format": "base64", "name": os.path.basename(remote), "path": remote,
                    "content": base64.b64encode(b).decode(), "chunk": -1 if last else n}
            api("PUT", "/api/contents/" + urllib.parse.quote(remote), body)
            if last: break
    return remote

def get(remote, local):
    r = api("GET", "/api/contents/" + urllib.parse.quote(remote.lstrip("/")) + "?content=1&format=base64&type=file")
    open(local, "wb").write(base64.b64decode(r["content"])); return local

def run(cmd, timeout=7200, echo=True):
    """Run a shell command on the pod via a Python kernel; streams output; returns (exit_code, output)."""
    k = api("POST", "/api/kernels", {"name": "python3"})
    ws_url = BASE.replace("https://", "wss://") + f"/api/kernels/{k['id']}/channels"
    px = urllib.parse.urlparse(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy") or "")
    ca = "/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else None
    ws = websocket.create_connection(ws_url, header=[f"{a}: {b}" for a, b in HDR.items() if a != "User-Agent"], timeout=timeout,
                                     http_proxy_host=px.hostname, http_proxy_port=px.port, proxy_type="http",
                                     sslopt={"ca_certs": ca} if ca else {})
    code = ("import subprocess,sys\n"
            f"p=subprocess.Popen({cmd!r},shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)\n"
            "for l in p.stdout: print(l,end='',flush=True)\n"
            "print('__EXIT__',p.wait())\n")
    mid = uuid.uuid4().hex
    ws.send(json.dumps({"header": {"msg_id": mid, "username": "c", "session": uuid.uuid4().hex, "msg_type": "execute_request",
                                   "version": "5.3"}, "parent_header": {}, "metadata": {}, "channel": "shell",
                        "content": {"code": code, "silent": False, "store_history": False, "user_expressions": {},
                                    "allow_stdin": False, "stop_on_error": True}}))
    out, rc, t0 = [], None, time.time()
    while time.time() - t0 < timeout:
        m = json.loads(ws.recv())
        if m.get("parent_header", {}).get("msg_id") != mid: continue
        if m["msg_type"] == "stream":
            t = m["content"]["text"]; out.append(t)
            for ln in t.splitlines():
                if ln.startswith("__EXIT__"): rc = int(ln.split()[1])
            if echo: sys.stdout.write(t); sys.stdout.flush()
        elif m["msg_type"] == "error":
            out.append("\n".join(m["content"]["traceback"])); rc = rc if rc is not None else 1
        elif m["msg_type"] == "status" and m["content"]["execution_state"] == "idle" and (rc is not None or out):
            break
    ws.close(); api("DELETE", f"/api/kernels/{k['id']}")
    return rc, "".join(out)

if __name__ == "__main__":
    op = sys.argv[1]
    if op == "run": sys.exit(run(" ".join(sys.argv[2:]))[0] or 0)
    if op == "put": print(put(sys.argv[2], sys.argv[3]))
    if op == "get": print(get(sys.argv[2], sys.argv[3]))

# ---- websocket-free job API (this session's proxy blocks websockets) ----
def start_runner():
    """Start the 'runner' kernel once; its launch command starts /workspace/runner.sh (flock-guarded)."""
    k = api("POST", "/api/kernels", {"name": "runner"}); return k["id"]

def job(name, script, wait=True, poll=10, timeout=14400, echo=True):
    """Upload /workspace/jobs/<name>.sh; the runner executes it. Returns (rc, log)."""
    import tempfile
    tf = tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False); tf.write(script); tf.close()
    put(tf.name, f"workspace/jobs/{name}.sh")
    if not wait: return None, ""
    t0, shown = time.time(), 0
    while time.time() - t0 < timeout:
        time.sleep(poll)
        log = text(f"workspace/jobs/{name}.log") or ""
        if echo and len(log) > shown: sys.stdout.write(log[shown:]); sys.stdout.flush(); shown = len(log)
        rc = text(f"workspace/jobs/{name}.rc")
        if rc is not None: return int(rc.strip() or 1), log
    raise TimeoutError(name)

def text(remote):
    try:
        r = api("GET", "/api/contents/" + urllib.parse.quote(remote) + "?content=1&format=text&type=file"); return r["content"]
    except urllib.error.HTTPError as e:
        if e.code == 404: return None
        raise
