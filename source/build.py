import base64, json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (parent of source/)
SRC  = BASE + "/source/template.html"
OUT  = BASE + "/finding-shreya.html"

html = open(SRC, encoding="utf-8").read()
manifest = json.load(open(BASE + "/photos/manifest.json"))

SLUGS = ["hero", "garden", "fire", "cook", "camp", "stars", "calm"]

for slug in SLUGS:
    path = "%s/photos/%s.jpg" % (BASE, slug)
    with open(path, "rb") as f:
        uri = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("ascii")
    token = "__IMG_%s__" % slug
    n = html.count(token)
    if n == 0:
        print("WARN: token %s not found" % token)
    html = html.replace(token, uri)
    print("%-8s inlined %dx  (%.0f KB raw)" % (slug, n, os.path.getsize(path) / 1024.0))

# photographer credits, in page order, de-duplicated
seen, names = set(), []
for slug in SLUGS:
    who = manifest[slug]["who"]
    if who not in seen:
        seen.add(who)
        names.append('<a href="%s" target="_blank" rel="noopener">%s</a>' % (manifest[slug]["link"], who))
credits = ", ".join(names[:-1]) + " and " + names[-1]
html = html.replace("__CREDITS__", credits)

# nothing may be left behind
leftover = re.findall(r"__[A-Z_]+__", html)
if leftover:
    print("ERROR unresolved tokens:", set(leftover)); sys.exit(1)

open(OUT, "w", encoding="utf-8").write(html)
mb = os.path.getsize(OUT) / 1048576.0
print("\n%s  ->  %.2f MB  (limit 16 MB)" % (OUT, mb))
if mb > 15:
    print("TOO BIG"); sys.exit(1)
