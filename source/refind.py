import json, subprocess, urllib.parse, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (parent of source/)
os.makedirs(BASE + "/source/scratch/alt", exist_ok=True)

JOBS = {
    "garden": ["wildflower meadow pink flowers summer", "flower garden full bloom colourful",
               "cosmos flower field bloom"],
    "stars":  ["milky way night sky stars landscape", "starry night sky galaxy",
               "night sky stars silhouette horizon"],
}

picked = {}
for slug, queries in JOBS.items():
    seen, free = set(), []
    for q in queries:
        u = ("https://unsplash.com/napi/search/photos?query=%s&per_page=20&orientation=landscape"
             % urllib.parse.quote(q))
        try:
            d = json.loads(subprocess.run(["curl", "-s", "--max-time", "30",
                                           "-H", "Accept: application/json", u],
                                          capture_output=True, text=True).stdout)
        except Exception as e:
            print("fail", q, e); continue
        for r in d.get("results", []):
            if r["id"] in seen:
                continue
            seen.add(r["id"])
            if r.get("premium") or r.get("plus"):
                continue
            if "plus.unsplash.com" in r["urls"]["raw"]:
                continue
            free.append({"id": r["id"], "raw": r["urls"]["raw"],
                         "alt": (r.get("alt_description") or "")[:64],
                         "likes": r.get("likes", 0)})
    free.sort(key=lambda x: -x["likes"])
    picked[slug] = free[:8]
    print("\n=== %s : %d free candidates ===" % (slug, len(free)))
    for i, r in enumerate(picked[slug]):
        out = "%s/source/scratch/alt/%s%d.jpg" % (BASE, slug, i)
        subprocess.run(["curl", "-s", "--max-time", "40", "-o", out,
                        r["raw"] + "&w=760&q=62&fm=jpg&fit=max"], capture_output=True)
        r["file"] = out
        print("  %d %-14s %5d  %s" % (i, r["id"], r["likes"], r["alt"]))

json.dump(picked, open(BASE + "/source/scratch/alt/picks.json", "w"), indent=1)
