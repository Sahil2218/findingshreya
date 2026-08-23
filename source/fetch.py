import json, subprocess, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (parent of source/)
os.makedirs(BASE + "/source/scratch/img", exist_ok=True)

# build id -> raw url map from every saved search payload
urls = {}
d = json.load(open(BASE + "/source/scratch/candidates.json"))
for q, rows in d.items():
    for r in rows:
        urls[r["id"]] = r["raw"]
try:
    n = json.load(open(BASE + "/source/scratch/napi.json"))
    for r in n.get("results", []):
        urls[r["id"]] = r["urls"]["raw"]
except Exception:
    pass

WANT = {
    "hero_a": "0HNp87L3SxQ", "hero_b": "0EwU7IWx1S8", "hero_c": "sMsOGnyiFKE", "hero_d": "Z557_ZoaNSw",
    "garden_a": "2Cl39QwsvyQ", "garden_b": "GbkMABgWtKA", "garden_c": "ko5HGtX7daw",
    "garden_d": "Sp9CrJxS3ho", "garden_e": "SbInAjXHKqw",
    "cook_a": "8uJq1W-7QdQ", "cook_b": "OPT2JopTERY", "cook_c": "tFlAl_8x7TQ",
    "tent_a": "_OXXIWoGxIs", "tent_b": "bNDStg4Lu4w", "tent_c": "RlDd6L1lB30",
    "star_a": "To1bws1uOJw", "star_b": "dQPHjk1CHxQ", "star_c": "pPfJN6wfYC0",
    "view_a": "ywnnwzcdR5o", "view_b": "tNDvFkxkBHo",
}

for name, pid in WANT.items():
    if pid not in urls:
        print("MISS", name, pid); continue
    u = urls[pid] + "&w=900&q=65&fm=jpg&fit=max"
    out = "%s/source/scratch/img/%s.jpg" % (BASE, name)
    r = subprocess.run(["curl", "-s", "--max-time", "40", "-o", out, "-w", "%{http_code} %{size_download}", u],
                       capture_output=True, text=True)
    print("%-10s %-14s %s" % (name, pid, r.stdout))
