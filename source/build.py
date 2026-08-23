import base64, json, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # project root (parent of source/)
SRC  = BASE + "/source/template.html"
OUT  = BASE + "/index.html"   # index.html so GitHub Pages serves it at the site root

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

# template.html is an artifact-shaped fragment: the artifact platform supplies the
# <!doctype>/<head>/<body> skeleton around it. GitHub Pages serves the file raw, so
# without a prologue the page lands in quirks mode and — with no viewport meta — lays
# out at 980px on a phone, which switches off every mobile rule in the stylesheet.
# The parser closes <head> and opens <body> by itself at the first flow content.
SITE = "https://sahil2218.github.io/findingshreya"
FAVICON = ("data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
           "<text y='.9em' font-size='90'>%F0%9F%8C%BF</text></svg>")
DESC = ("A scroll-told love letter, in seven movements — from a grey stretch, to a garden "
        "brought back to life, to a fire on the beach under a sky full of stars.")

prologue = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{desc}">
<meta name="theme-color" content="#070C11">
<meta name="color-scheme" content="dark">
<link rel="icon" href="{icon}">
<meta property="og:type" content="website">
<meta property="og:title" content="Finding Shreya">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}/photos/hero.jpg">
<meta property="og:url" content="{site}/">
<meta name="twitter:card" content="summary_large_image">
""".format(desc=DESC, icon=FAVICON, site=SITE)

html = prologue + html + "\n</body>\n</html>\n"

open(OUT, "w", encoding="utf-8").write(html)
mb = os.path.getsize(OUT) / 1048576.0
print("\n%s  ->  %.2f MB  (limit 16 MB)" % (OUT, mb))
if mb > 15:
    print("TOO BIG"); sys.exit(1)
