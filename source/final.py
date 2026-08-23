import json, subprocess, os, base64

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (parent of source/)
os.makedirs(BASE + "/photos", exist_ok=True)

# slug -> (unsplash id, width)
PICKS = [
    ("hero",   "Z557_ZoaNSw", 2000),  # beach + campfire + milky way
    ("garden", "HkEHZZA5jwU", 1600),  # cosmos meadow, edge to edge (the wipe)
    ("fire",   "0EwU7IWx1S8", 1500),  # campfire on beach at sunset
    ("cook",   "tFlAl_8x7TQ", 1500),  # pot over flames
    ("camp",   "_OXXIWoGxIs", 1600),  # glowing tent on beach under stars
    ("stars",  "9wH624ALFQA", 1600),  # milky way over a dark ridge
    ("calm",   "ywnnwzcdR5o", 1600),  # long-exposure calm sea at dusk
]

manifest = {}
for slug, pid, w in PICKS:
    # photo metadata -> raw url + photographer
    meta_raw = subprocess.run(
        ["curl", "-s", "--max-time", "30", "-H", "Accept: application/json",
         "https://unsplash.com/napi/photos/" + pid],
        capture_output=True, text=True).stdout
    try:
        m = json.loads(meta_raw)
        raw_url = m["urls"]["raw"]
        who = m["user"]["name"]
        link = m["links"]["html"]
    except Exception as e:
        print("META FAIL", slug, pid, e, meta_raw[:120]); continue

    # Unsplash+ images come back watermarked for unauthenticated fetches.
    if m.get("premium") or m.get("plus") or "plus.unsplash.com" in raw_url:
        print("REJECT %s (%s): premium/watermarked" % (slug, pid)); continue

    out = "%s/photos/%s.jpg" % (BASE, slug)
    u = "%s&w=%d&q=68&fm=jpg&fit=max" % (raw_url, w)
    r = subprocess.run(["curl", "-s", "--max-time", "60", "-o", out, "-w", "%{http_code}"],
                       capture_output=True, text=True)
    r = subprocess.run(["curl", "-s", "--max-time", "60", "-o", out, "-w", "%{http_code}", u],
                       capture_output=True, text=True)
    size = os.path.getsize(out) if os.path.exists(out) else 0
    manifest[slug] = {"id": pid, "who": who, "link": link, "bytes": size}
    print("%-8s %-14s http=%s  %6.1f KB  by %s" % (slug, pid, r.stdout, size / 1024.0, who))

json.dump(manifest, open(BASE + "/photos/manifest.json", "w"), indent=1)
total = sum(v["bytes"] for v in manifest.values())
print("\nRAW TOTAL %.2f MB   -> base64 approx %.2f MB" % (total / 1048576.0, total * 1.34 / 1048576.0))
