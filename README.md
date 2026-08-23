# Finding Shreya

A scroll-told love letter, in seven movements — from a grey stretch, to a garden brought
back to life, to a fire on the beach under a sky full of stars.

**Live link:** https://claude.ai/code/artifact/57a6d8b8-6a49-4b7b-b749-a74c3ab97a42
(private until you share it from the page's share menu)

---

## Just want to look at it?

Double-click **`finding-shreya.html`**. It opens in any browser and needs no internet —
every photo is baked into the file. You can email it, AirDrop it, or put it on a USB
stick and it still works.

---

## What's in here

```
finding-shreya/
├─ finding-shreya.html      ← THE SITE. one self-contained 3.1 MB file
├─ README.md                ← this
│
├─ photos/                  the 7 original photographs, full quality
│  ├─ hero.jpg              beach campfire under the milky way
│  ├─ garden.jpg            the cosmos meadow (the drag-to-revive one)
│  ├─ fire.jpg              campfire on the sand at sunset
│  ├─ cook.jpg              pot over the flames
│  ├─ camp.jpg              glowing tent by the dark sea
│  ├─ stars.jpg             milky way over a ridge
│  ├─ calm.jpg              long-exposure calm sea at dusk
│  └─ manifest.json         photographer name + Unsplash link for each
│
├─ preview/
│  ├─ desktop/              how each movement looks at 1440×900
│  ├─ mobile/               how each movement looks at 390×844 (iPhone)
│  └─ intermediate/         earlier renders, kept for comparison
│
└─ source/
   ├─ template.html         ← EDIT THIS ONE, not finding-shreya.html
   ├─ build.py              inlines the photos → finding-shreya.html
   ├─ final.py              re-downloads the 7 photos from Unsplash
   ├─ shoot.js              screenshots every movement (needs `npm i`)
   ├─ search.py / refind.py / fetch.py    photo-hunting helpers
   ├─ page-script.reference.js            copy of the page's JS, for reading
   └─ scratch/              every photo considered and rejected along the way
```

## Changing something

1. Edit `source/template.html` — that's the real source. It has `__IMG_hero__`-style
   placeholders where the photos get slotted in.
2. Run the build:

   ```bash
   python3 ~/Desktop/finding-shreya/source/build.py
   ```

   That rewrites `finding-shreya.html`. Refresh the browser and you'll see it.

**Never hand-edit `finding-shreya.html`** — it's generated, and the next build overwrites it.

### Swapping a photo

Drop a new JPG into `photos/` under the same name (`garden.jpg`, etc.) and re-run
`build.py`. Or edit the `PICKS` list at the top of `source/final.py` with a different
Unsplash ID and run `python3 source/final.py` first.

### Re-taking the screenshots

```bash
cd ~/Desktop/finding-shreya/source
npm install                          # pulls puppeteer-core, ~29 MB
node shoot.js 1440 900 desktop
node shoot.js 390 844 mobile
```

## Photo credits

All seven are free-licence Unsplash photographs — you can use them anywhere, including
commercially, no attribution legally required. The site credits them anyway in the
footer: **Marc James, Leslie Cross, Jasper Gronewold, SAM sokkolinmony, Mahyar Yeganeh,
Dns Dgn and Jonathan Bean**. Names and links are in `photos/manifest.json`.

## Notes

- `node_modules/` was left out (29 MB of re-downloadable npm packages). `npm install`
  inside `source/` brings it back if you want to run `shoot.js`.
- The garden slider deliberately has **alive on the left, dead on the right** — so
  dragging *rightward* floods the frame with life rather than killing it.
- **श्रेया** under her name in the hero was a grace note, not a requirement. Delete that
  line from `template.html` and rebuild if you'd rather it wasn't there.
