#!/usr/bin/env python3
"""Builds share.authentictaiwan.com: static link-preview pages that send people on to authentictaiwan.com."""
import html, json, pathlib, shutil, sys
HOST = "https://share.authentictaiwan.com"
SITE = "https://authentictaiwan.com"
CDN = "https://cdn.shopify.com/s/files/1/0785/8477/4794/files/"
IMG = {
    "d": ("authentic-taiwan-og-share-1200x630.png", 1200, 630),
    "c": ("capital-vision-og-share-1200x627.png", 1200, 627),
    "y": ("you-write-og-share-1200x630.png", 1200, 630),
}
src = pathlib.Path(__file__).parent
out = pathlib.Path(sys.argv[1])
shutil.rmtree(out, ignore_errors=True)
out.mkdir(parents=True)

SCRIPT = """<script>(function(){var u=new URL(%s);var q=new URLSearchParams(location.search);q.forEach(function(v,k){u.searchParams.set(k,v)});if(!u.searchParams.has('utm_source')){u.searchParams.set('utm_source','linkedin');u.searchParams.set('utm_medium','social');u.searchParams.set('utm_campaign',%s)}u.hash=location.hash;location.replace(u.toString())})();</script>"""

PAGE = """<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="noindex,follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Authentic Taiwan">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{share}">
<meta property="og:image" content="{img}">
<meta property="og:image:secure_url" content="{img}">
<meta property="og:image:width" content="{w}">
<meta property="og:image:height" content="{h}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{img}">
<style>body{{margin:0;background:#fff;color:#111;font:17px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans TC",sans-serif}}main{{max-width:640px;margin:0 auto;padding:48px 20px}}h1{{font-size:24px;line-height:1.35;margin:0 0 12px}}a{{color:#b4141e;font-weight:600}}</style>
{script}
</head>
<body><main><h1>{title}</h1><p>{desc}</p><p><a href="{target}">Continue to authentictaiwan.com</a></p></main></body>
</html>
"""

rows = json.loads((src / "pages.json").read_text())
seen = set()
for handle, title, desc, img_key in rows:
    assert handle not in seen, handle
    seen.add(handle)
    home = handle == "__home"
    target = SITE + "/" if home else f"{SITE}/pages/{handle}"
    share = HOST + "/" if home else f"{HOST}/{handle}"
    name, w, h = IMG[img_key]
    campaign = "share_home" if home else "share_" + handle.replace("-", "_")
    script = SCRIPT % (json.dumps(target), json.dumps(campaign))
    (out / ("index.html" if home else handle + ".html")).write_text(PAGE.format(
        title=html.escape(title, quote=True), desc=html.escape(desc, quote=True), share=share,
        img=CDN + name, w=w, h=h, target=target, script=script), encoding="utf-8")

(out / "404.html").write_text(PAGE.format(
    title="Authentic Taiwan", desc="Continue to authentictaiwan.com.", share=HOST + "/",
    img=CDN + IMG["d"][0], w=1200, h=630, target=SITE + "/",
    script="<script>location.replace('" + SITE + "/pages'+location.pathname+location.search+location.hash);</script>"), encoding="utf-8")
(out / "robots.txt").write_text("User-agent: *\nAllow: /\n")
(out / "CNAME").write_text("share.authentictaiwan.com\n")
shutil.copy(src / "pages.json", out / "pages.json")
shutil.copy(__file__, out / "build.py")
print(len(rows), "pages")
