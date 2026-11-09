#!/usr/bin/env python3
"""aibriefing.io static site generator.

Reads _src/data/** and writes the finished site to the repo root (../).
Run:  cd _src && python3 build.py
"""
import json, os, re, html, datetime, shutil, glob
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = "https://aibriefing.io"
BRAND = "AI Briefing"
TAGLINE = "The daily AI brief, written for your job."

CFG = json.load(open(os.path.join(DATA, "config.json"), encoding="utf-8"))

AUDIENCES = [
    ("executives", "Executives", "Leaders & decision-makers", "What changed, what it costs, what to do about it. No jargon."),
    ("finance", "Finance", "Investors, analysts & CFOs", "Capital, valuations, unit economics and the numbers behind the headlines."),
    ("security", "Security", "CISOs & security engineers", "New attack surfaces, vendor incidents, defensive tooling and policy."),
    ("ml", "ML engineers", "Researchers & model builders", "Model releases, benchmarks, training and inference techniques."),
    ("developers", "Developers", "Software engineers shipping with AI", "APIs, pricing changes, tooling, agents and what to build with."),
    ("beginners", "Beginners", "Curious, non-technical readers", "Plain-English explanations of what matters and why."),
]
AUD = {a[0]: a for a in AUDIENCES}

# ---------- helpers ----------
def esc(s): return html.escape(str(s), quote=True)
def money(v):
    if v is None: return "—"
    return ("$%.2f" % v) if v < 10 else ("$%g" % v)
def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
def jd(o): return json.dumps(o, ensure_ascii=False)
def md_inline(s):
    """Tiny markdown: **bold**, *em*, `code`, [text](url)."""
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<em>\1</em>", s)
    return s
def md_block(text):
    """Paragraph/heading/list markdown subset -> HTML."""
    out, buf, lst = [], [], None
    def flush():
        nonlocal buf
        if buf: out.append("<p>" + md_inline(" ".join(buf)) + "</p>"); buf = []
    for line in text.strip().split("\n"):
        l = line.rstrip()
        if not l:
            flush()
            if lst: out.append(f"</{lst}>"); lst = None
            continue
        if l.startswith("### "): flush(); out.append(f"<h3>{md_inline(l[4:])}</h3>"); continue
        if l.startswith("## "): flush(); out.append(f"<h2>{md_inline(l[3:])}</h2>"); continue
        if l.startswith("- "):
            flush()
            if lst != "ul":
                if lst: out.append(f"</{lst}>")
                out.append("<ul>"); lst = "ul"
            out.append(f"<li>{md_inline(l[2:])}</li>"); continue
        if re.match(r"^\d+\. ", l):
            flush()
            if lst != "ol":
                if lst: out.append(f"</{lst}>")
                out.append("<ol>"); lst = "ol"
            out.append(f"<li>{md_inline(re.sub(r'^\d+\. ', '', l))}</li>"); continue
        buf.append(l)
    flush()
    if lst: out.append(f"</{lst}>")
    return "\n".join(out)
def fmt_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%A, %B %-d, %Y")
def short_date(iso):
    d = datetime.date.fromisoformat(iso)
    return d.strftime("%b %-d, %Y")
def write(path, content):
    p = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)

# ---------- data ----------
def load_briefs():
    briefs = []
    for p in sorted(glob.glob(os.path.join(DATA, "briefs", "*.json"))):
        b = json.load(open(p, encoding="utf-8"))
        b["date"] = os.path.basename(p)[:-5]
        for i, it in enumerate(b["items"]):
            it.setdefault("id", f"{b['date']}-{i+1}")
            it.setdefault("audiences", list(it.get("why", {}).keys()))
            it.setdefault("tags", [])
        briefs.append(b)
    briefs.sort(key=lambda b: b["date"], reverse=True)
    return briefs

def load_explainers():
    ex = []
    for p in sorted(glob.glob(os.path.join(DATA, "explainers", "*.json"))):
        e = json.load(open(p, encoding="utf-8"))
        e.setdefault("slug", os.path.basename(p)[:-5])
        ex.append(e)
    ex.sort(key=lambda e: e.get("updated", ""), reverse=True)
    return ex

GLOSSARY = json.load(open(os.path.join(DATA, "glossary.json"), encoding="utf-8"))
TRACKERS = {}
for p in glob.glob(os.path.join(DATA, "trackers", "*.json")):
    TRACKERS[os.path.basename(p)[:-5]] = json.load(open(p, encoding="utf-8"))

# ---------- layout ----------
CSS = r"""
:root{--paper:#faf8f4;--paper2:#f1ede6;--ink:#141311;--ink2:#4a463f;--mute:#857f74;--line:#e2dcd1;--acc:#1f4bff;--acc2:#e8edff;--ok:#1d7a4a;--warn:#b7791f;--max:1120px}
@media(prefers-color-scheme:dark){:root{--paper:#121110;--paper2:#1b1917;--ink:#f1ede6;--ink2:#c9c2b5;--mute:#8d8678;--line:#2b2825;--acc:#7a93ff;--acc2:#1b2240}}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}
h1,h2,h3,.serif{font-family:Newsreader,Georgia,"Times New Roman",serif;font-weight:600;letter-spacing:-.01em;line-height:1.15}
h1{font-size:clamp(30px,5vw,46px);margin:.2em 0 .4em}h2{font-size:clamp(23px,3.2vw,30px);margin:1.6em 0 .5em}h3{font-size:21px;margin:1.2em 0 .4em}
p{margin:0 0 1em}code{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--paper2);padding:1px 5px;border-radius:5px}
.wrap{max-width:var(--max);margin:0 auto;padding:0 20px}
header.top{border-bottom:1px solid var(--line);background:var(--paper);position:sticky;top:0;z-index:5}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:60px}
.logo{font-family:Newsreader,Georgia,serif;font-weight:700;font-size:24px;color:var(--ink);letter-spacing:-.02em}.logo b{color:var(--acc)}
nav.main{display:flex;gap:4px;flex-wrap:wrap}nav.main a{color:var(--ink2);padding:6px 10px;border-radius:8px;font-size:15px;font-weight:500}nav.main a:hover,nav.main a.on{background:var(--paper2);color:var(--ink);text-decoration:none}
@media(max-width:720px){nav.main{display:none}header.top .wrap{min-height:54px}}
.sub{border-bottom:1px solid var(--line);background:var(--paper2)}.sub .wrap{display:flex;gap:6px;overflow-x:auto;padding:8px 20px;scrollbar-width:none}.sub a{white-space:nowrap;font-size:14px;color:var(--ink2);padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:var(--paper)}.sub a.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
main{padding:28px 0 60px}
.kicker{color:var(--acc);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase}
.lede{font-size:20px;color:var(--ink2);max-width:760px}
.grid{display:grid;gap:18px}.g2{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}.g3{grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.card{background:var(--paper2);border:1px solid var(--line);border-radius:14px;padding:18px 20px}
.card h3{margin:0 0 6px}.card p{margin:0;color:var(--ink2);font-size:15px}
.tile{display:block;color:inherit}.tile:hover{text-decoration:none;border-color:var(--acc)}
.item{border-top:1px solid var(--line);padding:22px 0}.item:first-of-type{border-top:0}
.item h3{margin:0 0 8px;font-size:24px}.item .sum{max-width:760px}
.why{display:grid;gap:8px;margin:12px 0 10px}.why div{display:flex;gap:10px;align-items:flex-start;font-size:15px;color:var(--ink2)}
.chip{flex:0 0 auto;display:inline-block;font-size:12px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;padding:3px 8px;border-radius:6px;background:var(--acc2);color:var(--acc);margin-top:2px}
.src{font-size:14px;color:var(--mute)}.src a{color:var(--mute);text-decoration:underline}
.btn{display:inline-block;background:var(--acc);color:#fff;padding:11px 18px;border-radius:10px;font-weight:600}.btn:hover{text-decoration:none;filter:brightness(1.08)}
.nl{background:var(--ink);color:var(--paper);border-radius:16px;padding:26px 24px;margin:36px 0}.nl h2{margin:0 0 6px;color:var(--paper)}.nl p{color:#cfc9bd;margin:0 0 14px}
.nl form{display:flex;gap:8px;flex-wrap:wrap}.nl input[type=email]{flex:1 1 220px;padding:12px 14px;border-radius:10px;border:1px solid #555;background:#fff;color:#111;font-size:16px}.nl button{padding:12px 18px;border-radius:10px;border:0;background:var(--acc);color:#fff;font-weight:600;font-size:16px;cursor:pointer}
.nl small{color:#9b958a}
table{border-collapse:collapse;width:100%;font-size:15px;margin:10px 0 18px}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:13px;letter-spacing:.05em;text-transform:uppercase;color:var(--mute)}td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.meta{color:var(--mute);font-size:14px}
.toc a{display:block;padding:6px 0;border-bottom:1px solid var(--line)}
footer{border-top:1px solid var(--line);padding:28px 0 40px;color:var(--mute);font-size:14px}footer a{color:var(--ink2)}footer .cols{display:flex;gap:28px;flex-wrap:wrap;margin-bottom:12px}
.pill{display:inline-block;font-size:12px;padding:2px 8px;border-radius:999px;border:1px solid var(--line);color:var(--mute);margin-right:6px}
.faq details{border-top:1px solid var(--line);padding:10px 0}.faq summary{cursor:pointer;font-weight:600}
.article{max-width:760px}.article p,.article li{font-size:18px}
.conf-primary{color:var(--ok)}.conf-secondary{color:var(--warn)}
.hero{padding:10px 0 20px}.hero h1{max-width:900px}
.dateline{font-size:15px;color:var(--mute)}
.list a{display:block;padding:12px 0;border-bottom:1px solid var(--line);color:inherit}.list a:hover{text-decoration:none;color:var(--acc)}.list small{display:block;color:var(--mute)}
"""

HEAD_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:ital,wght@0,500;0,600;0,700;1,500&display=swap" rel="stylesheet">'

def nav_html(section=""):
    links = [("/brief/", "brief", "Daily brief"), ("/for/", "for", "For you"), ("/trackers/", "trackers", "Trackers"), ("/learn/", "learn", "Learn"), ("/glossary/", "glossary", "Glossary"), ("/newsletter/", "newsletter", "Newsletter")]
    return "".join(f'<a href="{h}"{" class=on" if k == section else ""}>{t}</a>' for h, k, t in links)

def sub_html(section=""):
    links = [("/", "home", "Home"), ("/brief/", "brief", "Brief"), ("/for/", "for", "For you"), ("/trackers/api-pricing/", "trackers", "Pricing"), ("/trackers/models/", "trackers2", "Models"), ("/learn/", "learn", "Learn"), ("/glossary/", "glossary", "Glossary"), ("/newsletter/", "newsletter", "Newsletter")]
    return "".join(f'<a href="{h}"{" class=on" if k == section else ""}>{t}</a>' for h, k, t in links)

def newsletter_box(compact=False):
    form = CFG.get("newsletter_form_html", "").strip()
    if not form:
        form = ('<form action="/newsletter/" method="get" onsubmit="try{localStorage.setItem(\'nl_pending\',this.email.value)}catch(e){}">'
                '<input type="email" name="email" placeholder="you@company.com" required aria-label="Email address">'
                '<button type="submit">Subscribe free</button></form>')
    return (f'<section class="nl" id="subscribe"><h2>Get the brief in your inbox</h2>'
            f'<p>One email every morning: the 8 things that mattered in AI, each with a one-line "why it matters" for your role. Free, no ads, unsubscribe any time.</p>{form}'
            f'<small>Published daily by {BRAND}. We never share your address.</small></section>')

def layout(*, title, desc, path, body, section="", jsonld=None, og_type="website", published=None, modified=None, noindex=False):
    url = ROOT + path
    ld = [{"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": ROOT + "/", "logo": ROOT + "/og.png"},
          {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": ROOT + "/"}]
    if jsonld: ld += jsonld if isinstance(jsonld, list) else [jsonld]
    ldtags = "".join(f'<script type="application/ld+json">{jd(x)}</script>' for x in ld)
    meta_dates = ""
    if published: meta_dates += f'<meta property="article:published_time" content="{published}">'
    if modified: meta_dates += f'<meta property="article:modified_time" content="{modified}">'
    robots = '<meta name="robots" content="noindex">' if noindex else '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
{robots}
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{ROOT}/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{ROOT}/og.png">
{meta_dates}
<link rel="alternate" type="application/rss+xml" title="{BRAND} daily" href="{ROOT}/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{HEAD_FONTS}
<style>{CSS}</style>
{ldtags}
{CFG.get("analytics_html", "")}
</head>
<body>
<header class="top"><div class="wrap"><a class="logo" href="/">AI<b>Briefing</b></a><nav class="main" aria-label="Main">{nav_html(section)}</nav><a class="btn" href="/newsletter/" style="padding:8px 14px;font-size:14px">Subscribe</a></div></header>
<div class="sub"><div class="wrap">{sub_html(section)}</div></div>
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
<div class="cols"><a href="/brief/">Daily brief</a><a href="/for/">By role</a><a href="/trackers/">Trackers</a><a href="/learn/">Learn</a><a href="/glossary/">Glossary</a><a href="/newsletter/">Newsletter</a><a href="/about/">About</a><a href="/privacy/">Privacy</a><a href="/feed.xml">RSS</a></div>
<div>{BRAND} is an independent publication. Every item links to its original source; summaries are written in our own words and are not affiliated with the companies covered. &copy; {datetime.date.today().year} aibriefing.io</div>
</div></footer>
</body>
</html>"""

# ---------- renderers ----------
def item_html(it, aud_filter=None, date=None, with_date=False):
    why = it.get("why", {})
    keys = [aud_filter] if aud_filter and aud_filter in why else [k for k in why if k in AUD]
    whys = "".join(f'<div><span class="chip">{esc(AUD[k][1])}</span><span>{md_inline(why[k])}</span></div>' for k in keys)
    src = it.get("source", {})
    srcs = it.get("sources") or ([src] if src else [])
    srcl = " · ".join(f'<a href="{esc(s["url"])}" rel="noopener">{esc(s["name"])}</a>' for s in srcs if s.get("url"))
    dl = f'<span class="meta">{short_date(date)} · </span>' if with_date and date else ""
    tags = "".join(f'<span class="pill">{esc(t)}</span>' for t in it.get("tags", []))
    return (f'<article class="item" id="{esc(it["id"])}"><h3>{dl}{md_inline(it["title"])}</h3>'
            f'<p class="sum">{md_inline(it["summary"])}</p><div class="why">{whys}</div>'
            f'<div class="src">Source: {srcl}</div><div style="margin-top:8px">{tags}</div></article>')

def brief_page(b, prev_b=None, next_b=None):
    date = b["date"]; title = b.get("headline") or f"AI news for {short_date(date)}"
    path = f"/brief/{date}/"
    items = "".join(item_html(it) for it in b["items"])
    one = f'<div class="card" style="margin:14px 0 22px"><div class="kicker">The one thing to know</div><p style="font-size:18px;color:var(--ink)">{md_inline(b["one_thing"])}</p></div>' if b.get("one_thing") else ""
    navl = ""
    if prev_b: navl += f'<a href="/brief/{prev_b["date"]}/">&larr; {short_date(prev_b["date"])}</a>'
    if next_b: navl += f' &nbsp;·&nbsp; <a href="/brief/{next_b["date"]}/">{short_date(next_b["date"])} &rarr;</a>'
    aud_links = " ".join(f'<a class="pill" href="/for/{k}/">{esc(AUD[k][1])} view</a>' for k in AUD)
    body = (f'<div class="hero"><div class="kicker">Daily brief</div><h1>{esc(title)}</h1>'
            f'<div class="dateline">{fmt_date(date)} · {len(b["items"])} items · read in 4 minutes</div>'
            f'<p class="lede" style="margin-top:10px">{md_inline(b.get("intro", ""))}</p><div style="margin:8px 0 0">{aud_links}</div></div>'
            f'{one}<section>{items}</section><p class="meta" style="margin-top:18px">{navl}</p>{newsletter_box()}')
    desc = b.get("intro", "")[:155] or f"The {len(b['items'])} AI stories that mattered on {short_date(date)}, with a one-line why-it-matters for executives, finance, security, ML and developers."
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": title, "datePublished": date, "dateModified": b.get("updated", date),
          "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": ROOT + "/og.png"}},
          "mainEntityOfPage": ROOT + path, "image": ROOT + "/og.png", "description": desc,
          "citation": [s["url"] for it in b["items"] for s in (it.get("sources") or [it.get("source", {})]) if s.get("url")]}
    bc = breadcrumbs([("Brief", "/brief/"), (short_date(date), path)])
    return layout(title=f"{title} — AI Briefing, {short_date(date)}", desc=desc, path=path, body=body, section="brief", jsonld=[ld, bc], og_type="article", published=date, modified=b.get("updated", date))

def breadcrumbs(items):
    el = [{"@type": "ListItem", "position": 1, "name": "Home", "item": ROOT + "/"}]
    for i, (n, p) in enumerate(items, start=2): el.append({"@type": "ListItem", "position": i, "name": n, "item": ROOT + p})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": el}

def brief_index(briefs):
    rows = "".join(f'<a href="/brief/{b["date"]}/"><strong>{esc(b.get("headline") or short_date(b["date"]))}</strong><small>{fmt_date(b["date"])} · {len(b["items"])} items</small></a>' for b in briefs)
    body = (f'<div class="hero"><div class="kicker">Archive</div><h1>Every daily brief</h1><p class="lede">One page per day. Each item is summarised in our own words with a why-it-matters line for your role, and links to the original reporting.</p></div><div class="list">{rows}</div>{newsletter_box()}')
    return layout(title="Daily AI brief archive — AI Briefing", desc="Every daily AI news brief, one page per day, with role-specific why-it-matters lines and links to original sources.", path="/brief/", body=body, section="brief", jsonld=breadcrumbs([("Brief", "/brief/")]))

def hub_page(key, briefs, explainers):
    k, name, who, blurb = AUD[key]
    recent = []
    for b in briefs[:10]:
        for it in b["items"]:
            if key in it.get("why", {}): recent.append((b["date"], it))
    recent = recent[:18]
    items = "".join(item_html(it, aud_filter=key, date=d, with_date=True) for d, it in recent)
    ex = [e for e in explainers if key in e.get("audiences", [])][:6]
    exh = "".join(f'<a class="card tile" href="/learn/{e["slug"]}/"><h3>{esc(e["title"])}</h3><p>{esc(e["summary"])}</p></a>' for e in ex)
    others = " ".join(f'<a class="pill" href="/for/{a[0]}/">{esc(a[1])}</a>' for a in AUDIENCES if a[0] != key)
    body = (f'<div class="hero"><div class="kicker">AI briefing for</div><h1>{esc(name)}</h1><p class="lede">{esc(blurb)} Updated every morning.</p><div>{others}</div></div>'
            f'<h2>This week, for {esc(who.lower())}</h2><section>{items or "<p>First edition publishes tomorrow morning.</p>"}</section>'
            f'<h2>Start here</h2><div class="grid g3">{exh}</div>{newsletter_box()}')
    path = f"/for/{key}/"
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"AI news for {name}", "url": ROOT + path, "description": blurb, "isPartOf": {"@type": "WebSite", "url": ROOT + "/", "name": BRAND}}
    return layout(title=f"AI news for {name} — daily, in plain language | AI Briefing", desc=f"Daily AI news for {who.lower()}: {blurb} Updated every morning with sources.", path=path, body=body, section="for", jsonld=[ld, breadcrumbs([("For you", "/for/"), (name, path)])])

def for_index():
    tiles = "".join(f'<a class="card tile" href="/for/{k}/"><div class="kicker">{esc(who)}</div><h3>{esc(name)}</h3><p>{esc(blurb)}</p></a>' for k, name, who, blurb in AUDIENCES)
    body = f'<div class="hero"><div class="kicker">Pick your lens</div><h1>The same news, explained for your job</h1><p class="lede">Every story in the daily brief carries a one-line "why it matters" written for each of these readers. Choose yours.</p></div><div class="grid g3">{tiles}</div>{newsletter_box()}'
    return layout(title="AI news by role: executives, finance, security, ML, developers, beginners | AI Briefing", desc="Choose your lens: daily AI news explained for executives, finance professionals, security teams, ML engineers, developers and beginners.", path="/for/", body=body, section="for", jsonld=breadcrumbs([("For you", "/for/")]))

def conf_badge(c):
    return '<span class="conf-primary">● primary source</span>' if c == "primary" else '<span class="conf-secondary">● secondary source, pending re-check</span>'

def tracker_pricing(t):
    rows = ""
    for r in t["rows"]:
        rows += (f'<tr><td><strong>{esc(r["model"])}</strong><br><span class="meta">{esc(r["vendor"])}{(" · " + esc(r["note"])) if r.get("note") else ""}</span></td>'
                 f'<td class="num">{money(r["input"])}</td><td class="num">{money(r["output"])}</td><td class="num">{money(r.get("cached"))}</td>'
                 f'<td class="num">{esc(r.get("context", "—"))}</td><td class="meta"><a href="{esc(r["source"])}" rel="noopener">{esc(r.get("verified", ""))}</a><br>{conf_badge(r.get("confidence", "secondary"))}</td></tr>')
    table = f'<div class="tscroll"><table><thead><tr><th>Model</th><th>Input / 1M</th><th>Output / 1M</th><th>Cached input</th><th>Context</th><th>Verified</th></tr></thead><tbody>{rows}</tbody></table></div>'
    notes = md_block(t.get("notes", ""))
    faq = faq_html(t.get("faqs", []))
    body = (f'<div class="hero"><div class="kicker">Tracker</div><h1>{esc(t["title"])}</h1><p class="lede">{esc(t["intro"])}</p><p class="meta">Last checked {esc(t["updated"])}. Prices in USD per million tokens, standard tier, as published by each vendor. Rows marked "secondary" were taken from sources that cite the vendor page and are re-verified nightly.</p></div>'
            f'{table}<h2>How to read this</h2>{notes}{faq}{newsletter_box()}')
    path = "/trackers/api-pricing/"
    ld = [{"@context": "https://schema.org", "@type": "Dataset", "name": t["title"], "description": t["intro"], "url": ROOT + path, "dateModified": t["updated"], "creator": {"@type": "Organization", "name": BRAND}, "license": "https://creativecommons.org/licenses/by/4.0/"}, breadcrumbs([("Trackers", "/trackers/"), (t["title"], path)])]
    if t.get("faqs"): ld.append(faq_ld(t["faqs"]))
    return layout(title=f'{t["title"]} ({datetime.date.fromisoformat(t["updated"]).strftime("%B %Y")}) | AI Briefing', desc=t["intro"][:155], path=path, body=body, section="trackers", jsonld=ld, modified=t["updated"])

def tracker_models(t):
    rows = "".join(f'<tr><td><strong>{esc(r["model"])}</strong><br><span class="meta">{esc(r["vendor"])}</span></td><td class="num">{esc(r["released"])}</td><td>{esc(r["kind"])}</td><td class="num">{esc(r.get("context", "—"))}</td><td>{md_inline(r.get("note", ""))}</td><td class="meta"><a href="{esc(r["source"])}" rel="noopener">source</a></td></tr>' for r in t["rows"])
    table = f'<div class="tscroll"><table><thead><tr><th>Model</th><th>Released</th><th>Type</th><th>Context</th><th>What it is</th><th></th></tr></thead><tbody>{rows}</tbody></table></div>'
    body = f'<div class="hero"><div class="kicker">Tracker</div><h1>{esc(t["title"])}</h1><p class="lede">{esc(t["intro"])}</p><p class="meta">Last updated {esc(t["updated"])}. Newest first. Each row links to the vendor announcement or model page.</p></div>{table}{md_block(t.get("notes", ""))}{faq_html(t.get("faqs", []))}{newsletter_box()}'
    path = "/trackers/models/"
    ld = [{"@context": "https://schema.org", "@type": "Dataset", "name": t["title"], "description": t["intro"], "url": ROOT + path, "dateModified": t["updated"], "creator": {"@type": "Organization", "name": BRAND}}, breadcrumbs([("Trackers", "/trackers/"), (t["title"], path)])]
    if t.get("faqs"): ld.append(faq_ld(t["faqs"]))
    return layout(title=f'{t["title"]} ({datetime.date.fromisoformat(t["updated"]).strftime("%B %Y")}) | AI Briefing', desc=t["intro"][:155], path=path, body=body, section="trackers", jsonld=ld, modified=t["updated"])

def trackers_index():
    tiles = "".join(f'<a class="card tile" href="/trackers/{k}/"><h3>{esc(t["title"])}</h3><p>{esc(t["intro"])}</p><p class="meta" style="margin-top:8px">Updated {esc(t["updated"])}</p></a>' for k, t in sorted(TRACKERS.items()))
    body = f'<div class="hero"><div class="kicker">Reference</div><h1>Trackers: the numbers that keep changing</h1><p class="lede">Living tables, checked against vendor pages every night. Bookmark these instead of re-googling.</p></div><div class="grid g2">{tiles}</div>{newsletter_box()}'
    return layout(title="AI trackers: API pricing, model releases, context windows | AI Briefing", desc="Living reference tables for AI: API prices per million tokens, model releases and context windows, re-checked against vendor pages nightly.", path="/trackers/", body=body, section="trackers", jsonld=breadcrumbs([("Trackers", "/trackers/")]))

def faq_html(faqs):
    if not faqs: return ""
    return '<section class="faq"><h2>Common questions</h2>' + "".join(f'<details><summary>{esc(q)}</summary><p>{md_inline(a)}</p></details>' for q, a in faqs) + "</section>"
def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"[*`]", "", a)}} for q, a in faqs]}

def explainer_page(e, explainers):
    path = f"/learn/{e['slug']}/"
    aud = " ".join(f'<a class="pill" href="/for/{k}/">{esc(AUD[k][1])}</a>' for k in e.get("audiences", []) if k in AUD)
    related = [x for x in explainers if x["slug"] != e["slug"] and set(x.get("audiences", [])) & set(e.get("audiences", []))][:3]
    rel = "".join(f'<a class="card tile" href="/learn/{x["slug"]}/"><h3>{esc(x["title"])}</h3><p>{esc(x["summary"])}</p></a>' for x in related)
    body = (f'<div class="hero"><div class="kicker">Explainer · {esc(e.get("level", "all levels"))}</div><h1>{esc(e["title"])}</h1><p class="lede">{esc(e["summary"])}</p><p class="meta">Updated {esc(e.get("updated", ""))} · For: {aud}</p></div>'
            f'<div class="article">{md_block(e["body"])}</div>{faq_html(e.get("faqs", []))}'
            f'{"<h2>Related</h2><div class=\"grid g3\">" + rel + "</div>" if rel else ""}{newsletter_box()}')
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": e["title"], "description": e["summary"], "datePublished": e.get("published", e.get("updated")), "dateModified": e.get("updated"), "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": ROOT + "/og.png"}}, "mainEntityOfPage": ROOT + path, "image": ROOT + "/og.png"}, breadcrumbs([("Learn", "/learn/"), (e["title"], path)])]
    if e.get("faqs"): ld.append(faq_ld(e["faqs"]))
    return layout(title=f'{e["title"]} | AI Briefing', desc=e["summary"][:155], path=path, body=body, section="learn", jsonld=ld, og_type="article", published=e.get("published"), modified=e.get("updated"))

def learn_index(explainers):
    by = defaultdict(list)
    for e in explainers:
        for k in e.get("audiences", []): by[k].append(e)
    secs = ""
    for k, name, who, _ in AUDIENCES:
        if not by[k]: continue
        secs += f'<h2>For {esc(name.lower())}</h2><div class="grid g3">' + "".join(f'<a class="card tile" href="/learn/{e["slug"]}/"><h3>{esc(e["title"])}</h3><p>{esc(e["summary"])}</p></a>' for e in by[k]) + "</div>"
    body = f'<div class="hero"><div class="kicker">Learn</div><h1>Explainers that stay current</h1><p class="lede">Short, plain-English guides to the ideas behind the news. Each is revisited when the facts change.</p></div>{secs}{newsletter_box()}'
    return layout(title="Learn AI: plain-English explainers for every role | AI Briefing", desc="Short explainers on agents, pricing, context windows, RAG, prompt injection, benchmarks and more, written for executives, developers, security and beginners.", path="/learn/", body=body, section="learn", jsonld=breadcrumbs([("Learn", "/learn/")]))

def glossary_pages():
    terms = sorted(GLOSSARY, key=lambda t: t["term"].lower())
    out = {}
    letters = defaultdict(list)
    for t in terms: letters[t["term"][0].upper()].append(t)
    idx = "".join(f'<h2 id="{L}">{L}</h2><div class="list">' + "".join(f'<a href="/glossary/{slugify(t["term"])}/"><strong>{esc(t["term"])}</strong><small>{esc(t["short"])}</small></a>' for t in ts) + "</div>" for L, ts in sorted(letters.items()))
    body = f'<div class="hero"><div class="kicker">Glossary</div><h1>AI terms, defined in one breath</h1><p class="lede">{len(terms)} terms. Each definition is short enough to read in a meeting and precise enough to use in one.</p></div>{idx}{newsletter_box()}'
    ld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "AI Briefing glossary", "url": ROOT + "/glossary/", "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t["term"], "description": t["short"], "url": ROOT + f"/glossary/{slugify(t['term'])}/"} for t in terms]}
    out["/glossary/"] = layout(title="AI glossary: plain-English definitions of every term that matters | AI Briefing", desc=f"{len(terms)} AI terms defined in plain English: tokens, context window, RAG, agents, prompt injection, fine-tuning and more.", path="/glossary/", body=body, section="glossary", jsonld=[ld, breadcrumbs([("Glossary", "/glossary/")])])
    for t in terms:
        path = f"/glossary/{slugify(t['term'])}/"
        rel = [x for x in terms if x["term"] != t["term"] and any(w in x["term"].lower() or w in x["short"].lower() for w in t.get("related", []))][:5]
        relh = "".join(f'<a class="pill" href="/glossary/{slugify(x["term"])}/">{esc(x["term"])}</a>' for x in rel)
        body = (f'<div class="hero"><div class="kicker">Glossary</div><h1>{esc(t["term"])}</h1><p class="lede">{esc(t["short"])}</p></div><div class="article">{md_block(t.get("long", ""))}</div>'
                f'{("<h2>Related terms</h2><p>" + relh + "</p>") if relh else ""}<p><a href="/glossary/">&larr; All terms</a></p>{newsletter_box()}')
        ld = {"@context": "https://schema.org", "@type": "DefinedTerm", "name": t["term"], "description": t["short"], "url": ROOT + path, "inDefinedTermSet": ROOT + "/glossary/"}
        out[path] = layout(title=f'What is {t["term"]}? Definition in plain English | AI Briefing', desc=t["short"][:155], path=path, body=body, section="glossary", jsonld=[ld, breadcrumbs([("Glossary", "/glossary/"), (t["term"], path)])])
    return out

def home(briefs, explainers):
    b = briefs[0]
    top = "".join(f'<a class="card tile" href="/brief/{b["date"]}/#{esc(it["id"])}"><h3 style="font-size:19px">{md_inline(it["title"])}</h3><p>{md_inline(it["summary"][:160])}…</p></a>' for it in b["items"][:6])
    tiles = "".join(f'<a class="card tile" href="/for/{k}/"><div class="kicker">{esc(who)}</div><h3>{esc(name)}</h3><p>{esc(blurb)}</p></a>' for k, name, who, blurb in AUDIENCES)
    tr = "".join(f'<a class="card tile" href="/trackers/{k}/"><h3>{esc(t["title"])}</h3><p>{esc(t["intro"])}</p><p class="meta" style="margin-top:8px">Checked {esc(t["updated"])}</p></a>' for k, t in sorted(TRACKERS.items()))
    ex = "".join(f'<a class="card tile" href="/learn/{e["slug"]}/"><h3>{esc(e["title"])}</h3><p>{esc(e["summary"])}</p></a>' for e in explainers[:3])
    one = f'<div class="card" style="margin:14px 0 6px"><div class="kicker">The one thing to know today</div><p style="font-size:18px;color:var(--ink)">{md_inline(b["one_thing"])}</p></div>' if b.get("one_thing") else ""
    body = (f'<div class="hero"><div class="kicker">{fmt_date(b["date"])}</div><h1>{esc(b.get("headline") or TAGLINE)}</h1><p class="lede">{md_inline(b.get("intro", ""))}</p>'
            f'<p><a class="btn" href="/brief/{b["date"]}/">Read today\'s brief</a> &nbsp; <a href="/for/">or pick your role &rarr;</a></p></div>{one}'
            f'<h2>Today\'s top stories</h2><div class="grid g3">{top}</div>'
            f'<h2>Written for your job</h2><div class="grid g3">{tiles}</div>'
            f'<h2>Trackers</h2><div class="grid g2">{tr}</div>'
            f'<h2>Learn</h2><div class="grid g3">{ex}</div>{newsletter_box()}')
    desc = "Daily AI news in 4 minutes, with a one-line why-it-matters for executives, finance, security, ML engineers, developers and beginners. Plus live trackers for API pricing and model releases."
    return layout(title="AI Briefing — daily AI news, explained for your job", desc=desc, path="/", body=body, section="home")

def newsletter_page():
    form = newsletter_box()
    body = (f'<div class="hero"><div class="kicker">Newsletter</div><h1>The AI Briefing, every morning</h1><p class="lede">The 8 things that mattered in AI yesterday, each in two sentences, each with a why-it-matters line for your role. Four minutes. Free.</p></div>'
            f'{form}<h2>What you get</h2><ul><li>One email per day, sent around 7am US Eastern / 12pm London / 5:30pm India.</li><li>Every item links to the original reporting or announcement.</li><li>Role lenses: executives, finance, security, ML, developers, beginners.</li><li>No ads, no sponsored placements, unsubscribe in one click.</li></ul>'
            f'<p class="meta">Prefer RSS? <a href="/feed.xml">Subscribe to the feed</a>.</p>')
    return layout(title="Subscribe to the daily AI Briefing newsletter (free)", desc="A free daily email with the 8 AI stories that mattered, each with a one-line why-it-matters for your role. Four minutes, no ads.", path="/newsletter/", body=body, section="newsletter", jsonld=breadcrumbs([("Newsletter", "/newsletter/")]))

def static_page(path, title, desc, h1, md):
    return layout(title=f"{title} | AI Briefing", desc=desc, path=path, body=f'<div class="hero"><h1>{esc(h1)}</h1></div><div class="article">{md_block(md)}</div>', jsonld=breadcrumbs([(h1, path)]))

ABOUT = """
AI Briefing is a daily publication that explains what happened in artificial intelligence and, more importantly, what it means for the person reading.

## How it works

Every morning an editorial pipeline reads the day's announcements, filings, papers and reporting, selects the handful of items that actually change something, and writes a short summary in our own words. Each item then gets a one-line "why it matters" for six kinds of readers: executives, finance professionals, security teams, ML engineers, developers and beginners. Every item links to its original source so you can go deeper.

The pipeline is operated with AI assistance and reviewed for accuracy against primary sources (vendor pricing pages, SEC filings, official announcements). Our trackers show, row by row, which source was used and when it was last checked.

## What we don't do

- We do not republish other outlets' articles. Summaries are short and original, and we always link out.
- We do not run sponsored placements or affiliate links in the brief.
- We do not collect personal data beyond an email address if you subscribe. See the [privacy policy](/privacy/).

## Corrections

If something is wrong, email corrections@aibriefing.io. Corrections are noted on the affected page.
"""
PRIVACY = """
AI Briefing (aibriefing.io) collects as little as possible.

- **Analytics.** We use privacy-preserving, cookie-free analytics (Cloudflare Web Analytics) to count page views. No personal profile is built and no data is sold.
- **Newsletter.** If you subscribe, your email address is stored with our email provider solely to send the daily brief. Every email has an unsubscribe link; unsubscribing deletes you from the list.
- **Cookies.** The site sets no tracking cookies.
- **Third parties.** Pages load fonts from Google Fonts. Links to external sites are governed by those sites' policies.

Questions: privacy@aibriefing.io.
"""

def feed(briefs):
    items = ""
    for b in briefs[:20]:
        url = f"{ROOT}/brief/{b['date']}/"
        content = ""
        if b.get("one_thing"): content += f"<p><strong>The one thing to know:</strong> {md_inline(b['one_thing'])}</p>"
        for it in b["items"]:
            whys = "".join(f"<li><strong>{esc(AUD[k][1])}:</strong> {md_inline(v)}</li>" for k, v in it.get("why", {}).items() if k in AUD)
            srcs = it.get("sources") or [it.get("source", {})]
            srcl = " · ".join(f'<a href="{esc(s["url"])}">{esc(s["name"])}</a>' for s in srcs if s.get("url"))
            content += f"<h3>{md_inline(it['title'])}</h3><p>{md_inline(it['summary'])}</p><ul>{whys}</ul><p><small>Source: {srcl}</small></p>"
        content += f'<p><a href="{url}">Read on aibriefing.io</a> · <a href="{ROOT}/for/">Pick your role</a></p>'
        pub = datetime.datetime.fromisoformat(b["date"] + "T11:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
        items += (f"<item><title>{esc(b.get('headline') or 'AI Briefing for ' + short_date(b['date']))}</title><link>{url}</link><guid isPermaLink=\"true\">{url}</guid><pubDate>{pub}</pubDate>"
                  f"<description>{esc(b.get('intro', ''))}</description><content:encoded><![CDATA[{content}]]></content:encoded></item>")
    return f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{BRAND}</title><link>{ROOT}/</link><description>{esc(TAGLINE)}</description><language>en</language><atom:link href="{ROOT}/feed.xml" rel="self" type="application/rss+xml"/>{items}</channel></rss>'

HTACCESS = r"""RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^ https://aibriefing.io%{REQUEST_URI} [R=301,L]
RewriteCond %{HTTP_HOST} !^aibriefing[.]io$ [NC]
RewriteRule ^ https://aibriefing.io%{REQUEST_URI} [R=301,L]
RedirectMatch 404 ^/_src(/|$)
RedirectMatch 404 ^/[.]git
RedirectMatch 404 ^/README[.]md$
ErrorDocument 404 /404.html
AddDefaultCharset UTF-8
<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
Header set X-Frame-Options "SAMEORIGIN"
<FilesMatch "\.(html)$">
Header set Cache-Control "public, max-age=600"
</FilesMatch>
<FilesMatch "\.(png|svg|xml|txt)$">
Header set Cache-Control "public, max-age=86400"
</FilesMatch>
</IfModule>
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml application/xml text/xml
</IfModule>
"""

FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#141311"/><text x="32" y="44" text-anchor="middle" font-family="Georgia,serif" font-weight="700" font-size="36" fill="#faf8f4">A<tspan fill="#7a93ff">I</tspan></text></svg>'

def og_image():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (20, 19, 17)); d = ImageDraw.Draw(img)
    def f(p, s):
        try: return ImageFont.truetype(p, s)
        except Exception: return ImageFont.load_default()
    serif = f("/usr/share/fonts/truetype/google-fonts/Lora-Variable.ttf", 86)
    sans = f("/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf", 30)
    d.text((80, 170), "AI", font=serif, fill=(250, 248, 244)); w = d.textlength("AI", font=serif)
    d.text((80 + w, 170), "Briefing", font=serif, fill=(122, 147, 255))
    d.text((82, 300), "Daily AI news, explained for your job.", font=sans, fill=(201, 194, 181))
    d.text((82, 350), "Executives · Finance · Security · ML · Developers · Beginners", font=f("/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf", 24), fill=(141, 134, 120))
    d.rectangle([80, 520, 1120, 524], fill=(122, 147, 255))
    d.text((82, 545), "aibriefing.io", font=sans, fill=(250, 248, 244))
    img.save(os.path.join(OUT, "og.png"), optimize=True)

# ---------- main ----------
def main():
    briefs = load_briefs(); explainers = load_explainers()
    assert briefs, "need at least one brief"
    pages = {}
    pages["/"] = home(briefs, explainers)
    pages["/brief/"] = brief_index(briefs)
    for i, b in enumerate(briefs):
        pages[f"/brief/{b['date']}/"] = brief_page(b, prev_b=briefs[i + 1] if i + 1 < len(briefs) else None, next_b=briefs[i - 1] if i > 0 else None)
    pages["/for/"] = for_index()
    for k in AUD: pages[f"/for/{k}/"] = hub_page(k, briefs, explainers)
    pages["/trackers/"] = trackers_index()
    if "api-pricing" in TRACKERS: pages["/trackers/api-pricing/"] = tracker_pricing(TRACKERS["api-pricing"])
    if "models" in TRACKERS: pages["/trackers/models/"] = tracker_models(TRACKERS["models"])
    pages["/learn/"] = learn_index(explainers)
    for e in explainers: pages[f"/learn/{e['slug']}/"] = explainer_page(e, explainers)
    pages.update(glossary_pages())
    pages["/newsletter/"] = newsletter_page()
    pages["/about/"] = static_page("/about/", "About", "What AI Briefing is, how the daily brief is produced and checked, and what we don't do.", "About AI Briefing", ABOUT)
    pages["/privacy/"] = static_page("/privacy/", "Privacy", "AI Briefing's privacy policy: cookie-free analytics, newsletter email handling, no data sales.", "Privacy policy", PRIVACY)

    # clean previous build outputs (keep _src, .git, README)
    for name in os.listdir(OUT):
        if name in ("_src", ".git", "README.md", ".gitignore"): continue
        p = os.path.join(OUT, name)
        shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)

    for path, html_ in pages.items():
        assert "{{" not in html_, path
        write(path.lstrip("/") + "index.html", html_)
    write("404.html", layout(title="Page not found | AI Briefing", desc="That page does not exist.", path="/404.html", body='<div class="hero"><h1>Not found</h1><p class="lede">That page moved or never existed. Try <a href="/brief/">the daily brief</a> or <a href="/">the home page</a>.</p></div>', noindex=True))
    write("feed.xml", feed(briefs))
    today = datetime.date.today().isoformat()
    def lastmod(path):
        m = re.match(r"/brief/(\d{4}-\d{2}-\d{2})/", path)
        if m: return m.group(1)
        if path.startswith("/trackers/") and len(path) > 10:
            k = path.strip("/").split("/")[1]; return TRACKERS.get(k, {}).get("updated", today)
        return today
    def prio(path):
        if path == "/": return "1.0"
        if path.startswith("/trackers/") or path.startswith("/for/"): return "0.9"
        if path.startswith("/brief/") and len(path) > 7: return "0.8"
        if path.startswith("/learn/"): return "0.7"
        if path.startswith("/glossary/") and len(path) > 10: return "0.4"
        return "0.6"
    urls = "".join(f"<url><loc>{ROOT}{p}</loc><lastmod>{lastmod(p)}</lastmod><priority>{prio(p)}</priority></url>" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.w3.org/sitemaps/schema/0.9">{urls}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {ROOT}/sitemap.xml\n")
    write(".htaccess", HTACCESS)
    write("favicon.svg", FAVICON)
    if CFG.get("indexnow_key"): write(CFG["indexnow_key"] + ".txt", CFG["indexnow_key"])
    og_image()
    print(f"built {len(pages)} pages → {OUT}")

if __name__ == "__main__":
    main()
