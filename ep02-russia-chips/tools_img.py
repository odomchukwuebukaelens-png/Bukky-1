"""Generate cartoon art via ai33 v3/image (Imagen 3). usage: python3 -I tools_img.py out.png "prompt" [aspect] [ref1.png ...]"""
import json, subprocess, sys, time
STYLE = ("2D hand-drawn cartoon illustration, thick clean dark outlines, warm saturated colors, expressive exaggerated faces with big round "
         "white eyes and small pupils, slightly chunky stylized proportions, detailed painterly background, soft cinematic lighting, "
         "storybook animated-film look, no text, no letters, no logos, no watermark. Scene: ")
def curl(*a): return subprocess.run(["curl", "-sS", "--max-time", "120", *a], capture_output=True, text=True).stdout
out, prompt = sys.argv[1], sys.argv[2]
aspect = sys.argv[3] if len(sys.argv) > 3 else "16:9"
refs = sys.argv[4:]
args = ["-X", "POST", "https://api.ai33.pro/v3/image", "-H", "xi-api-key: injected",
        "--form-string", "prompt=" + STYLE + prompt, "--form-string", "resolution=1K", "--form-string", "aspect_ratio=" + aspect,
        "--form-string", "generations_count=1", "--form-string", 'model_parameters={"output_format":"png"}']
for r in refs: args += ["-F", f"assets=@{r};type=image/png"]
r = json.loads(curl(*args))
if not r.get("success"): sys.exit(f"submit failed: {r}")
tid = r["task_id"]
for _ in range(100):
    d = json.loads(curl(f"https://api.ai33.pro/v3/task/{tid}", "-H", "xi-api-key: injected"))["data"]
    if d["status"] == "done":
        url = d["metadata"]["result_images"][0]["imageUrl"]; curl("-o", out, url); print(out, "ok"); break
    if d["status"] == "error": sys.exit(f"failed: {d}")
    time.sleep(3)
