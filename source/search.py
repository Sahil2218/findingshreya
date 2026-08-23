import json, os, subprocess, sys, urllib.parse

QUERIES = [
    "wilted dry dead flowers garden",
    "lush green garden blooming flowers sunlight",
    "starry night sky milky way tent camping",
    "cooking pot over campfire",
    "beach sunset calm dusk ocean",
    "dew drops green leaf macro",
    "tent under stars night mountain",
    "campfire sparks night beach",
]

out = {}
for q in QUERIES:
    url = "https://unsplash.com/napi/search/photos?query=%s&per_page=12&orientation=landscape" % urllib.parse.quote(q)
    try:
        raw = subprocess.run(["curl", "-s", "--max-time", "25", "-H", "Accept: application/json", url],
                             capture_output=True, text=True, timeout=40).stdout
        d = json.loads(raw)
    except Exception as e:
        print("FAIL", q, e); continue
    print("\n=== %s ===" % q)
    rows = []
    for r in d.get("results", []):
        rid = r["id"]
        alt = (r.get("alt_description") or "")[:75]
        raw_url = r["urls"]["raw"]
        likes = r.get("likes", 0)
        rows.append({"id": rid, "alt": alt, "raw": raw_url})
        print("  %-14s %5d  %s" % (rid, likes, alt))
    out[q] = rows

json.dump(out, open("" + os.path.dirname(os.path.abspath(__file__)) + "/scratch/candidates.json", "w"), indent=1)
