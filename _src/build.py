#!/usr/bin/env python3
"""aibriefing.io static site generator (v2: visual edition).

Reads _src/data/** and writes the finished site to the repo root (../).
Run:  cd _src && python3 build.py
"""
import json, os, re, html, datetime, shutil, glob, hashlib
from collections import defaultdict
import art

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = "https://aibriefing.io"
BRAND = "AI Briefing"
TAGLINE = "Daily AI news, explained for your job."
TODAY = datetime.date.today().isoformat()
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
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)\*(?!\*)", r"<em>\1</em>", s)
    return s
def strip_md(s): return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", re.sub(r"[*`]", "", s))
def md_block(text):
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
def fmt_date(iso): return datetime.date.fromisoformat(iso).strftime("%A, %B %-d, %Y")
def short_date(iso): return datetime.date.fromisoformat(iso).strftime("%b %-d, %Y")
def read_time(words): return max(1, round(words / 230))
def write(path, content):
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
def ensure_dir(path): os.makedirs(os.path.join(OUT, path), exist_ok=True)

# ---------- data ----------
def load_briefs():
    briefs = []
    for p in sorted(glob.glob(os.path.join(DATA, "briefs", "*.json"))):
        b = json.load(open(p, encoding="utf-8")); b["date"] = os.path.basename(p)[:-5]
        for i, it in enumerate(b["items"]):
            it.setdefault("id", f"{b['date']}-{i+1}")
            it.setdefault("audiences", list(it.get("why", {}).keys()))
            it.setdefault("tags", [])
            it["sources"] = it.get("sources") or ([it["source"]] if it.get("source") else [])
            it["stat"] = it.get("stat") or art.key_stat(it["title"]) or art.key_stat(it["summary"])
            it["img"] = f"/img/stories/{it['id']}.webp"
            it["words"] = len((it["title"] + " " + it["summary"] + " " + " ".join(it.get("why", {}).values())).split())
        b["words"] = sum(it["words"] for it in b["items"]) + len(b.get("intro", "").split()) + len(b.get("one_thing", "").split())
        briefs.append(b)
    briefs.sort(key=lambda b: b["date"], reverse=True)
    return briefs
def load_explainers():
    ex = []
    for p in sorted(glob.glob(os.path.join(DATA, "explainers", "*.json"))):
        e = json.load(open(p, encoding="utf-8")); e.setdefault("slug", os.path.basename(p)[:-5])
        e["img"] = f"/img/learn/{e['slug']}.webp"; e["words"] = len(e["body"].split()); ex.append(e)
    ex.sort(key=lambda e: e.get("updated", ""), reverse=True)
    return ex
GLOSSARY = json.load(open(os.path.join(DATA, "glossary.json"), encoding="utf-8"))
TRACKERS = {os.path.basename(p)[:-5]: json.load(open(p, encoding="utf-8")) for p in glob.glob(os.path.join(DATA, "trackers", "*.json"))}

# ---------- assets ----------
CSS = r"""
:root{--paper:#faf8f4;--paper2:#f1ede6;--paper3:#e9e4da;--ink:#141311;--ink2:#4a463f;--mute:#857f74;--line:#e2dcd1;--acc:#1f4bff;--acc2:#e8edff;--ok:#1d7a4a;--warn:#b7791f;--max:1180px;--r:14px}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--paper:#111110;--paper2:#1a1917;--paper3:#242220;--ink:#f1ede6;--ink2:#c9c2b5;--mute:#8d8678;--line:#2b2825;--acc:#7a93ff;--acc2:#1b2240}}
:root[data-theme=dark]{--paper:#111110;--paper2:#1a1917;--paper3:#242220;--ink:#f1ede6;--ink2:#c9c2b5;--mute:#8d8678;--line:#2b2825;--acc:#7a93ff;--acc2:#1b2240}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
a{color:var(--acc);text-decoration:none}a:hover{text-decoration:underline}img{max-width:100%;height:auto;display:block}
h1,h2,h3,h4,.serif{font-family:Newsreader,Georgia,"Times New Roman",serif;font-weight:600;letter-spacing:-.01em;line-height:1.12}
h1{font-size:clamp(30px,5vw,50px);margin:.2em 0 .4em}h2{font-size:clamp(23px,3.2vw,30px);margin:1.5em 0 .5em}h3{font-size:21px;margin:1em 0 .4em}
p{margin:0 0 1em}code{font:14px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--paper2);padding:1px 5px;border-radius:5px}
.wrap{max-width:var(--max);margin:0 auto;padding:0 20px}
#prog{position:fixed;top:0;left:0;height:3px;width:0;background:var(--acc);z-index:50;transition:width .15s linear}
header.top{border-bottom:1px solid var(--line);background:var(--paper);position:sticky;top:0;z-index:20}
header.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:14px;min-height:62px}
.logo{font-family:Newsreader,Georgia,serif;font-weight:700;font-size:26px;color:var(--ink);letter-spacing:-.02em;white-space:nowrap}.logo b{color:var(--acc)}
nav.main{display:flex;gap:2px;flex-wrap:wrap}nav.main a{color:var(--ink2);padding:6px 10px;border-radius:8px;font-size:15px;font-weight:500}nav.main a:hover,nav.main a.on{background:var(--paper2);color:var(--ink);text-decoration:none}
.tools{display:flex;gap:6px;align-items:center}.ibtn{border:1px solid var(--line);background:var(--paper2);color:var(--ink);border-radius:9px;padding:7px 10px;font-size:14px;cursor:pointer;font-weight:500;line-height:1}.ibtn:hover{border-color:var(--acc);text-decoration:none}
@media(max-width:860px){nav.main{display:none}header.top .wrap{min-height:56px}.logo{font-size:23px}}
.sub{border-bottom:1px solid var(--line);background:var(--paper2)}.sub .wrap{display:flex;gap:6px;overflow-x:auto;padding:8px 20px;scrollbar-width:none;align-items:center}.sub a{white-space:nowrap;font-size:14px;color:var(--ink2);padding:5px 11px;border-radius:999px;border:1px solid var(--line);background:var(--paper)}.sub a.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.ticker{background:var(--ink);color:var(--paper);font-size:14px;overflow:hidden;white-space:nowrap}.ticker .wrap{display:flex;gap:28px;padding:7px 20px;overflow-x:auto;scrollbar-width:none}.ticker a{color:var(--paper);opacity:.92}.ticker b{color:var(--acc)}.ticker .dot{opacity:.4}
main{padding:22px 0 60px}
.kicker{color:var(--acc);font-weight:600;font-size:13px;letter-spacing:.08em;text-transform:uppercase}
.lede{font-size:20px;color:var(--ink2);max-width:760px}
.grid{display:grid;gap:18px}.g2{grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}.g3{grid-template-columns:repeat(auto-fit,minmax(250px,1fr))}.g4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.card{background:var(--paper2);border:1px solid var(--line);border-radius:var(--r);padding:18px 20px}.card h3{margin:0 0 6px}.card p{margin:0;color:var(--ink2);font-size:15px}
.tile{display:block;color:inherit;transition:transform .15s,border-color .15s}.tile:hover{text-decoration:none;border-color:var(--acc);transform:translateY(-2px)}
.story{background:var(--paper2);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;display:flex;flex-direction:column;color:inherit}.story img{aspect-ratio:16/9;object-fit:cover;width:100%}.story .b{padding:14px 16px 16px}.story h3{font-size:20px;margin:0 0 6px}.story p{color:var(--ink2);font-size:15px;margin:0}.story .m{font-size:12px;color:var(--mute);margin-top:10px;display:flex;gap:8px;align-items:center}
.lead{display:grid;grid-template-columns:1.25fr 1fr;gap:28px;align-items:center;margin:8px 0 10px}.lead img{border-radius:var(--r);border:1px solid var(--line);aspect-ratio:16/9;object-fit:cover;width:100%}.lead h1{margin:.1em 0 .3em}
@media(max-width:860px){.lead{grid-template-columns:1fr}}
.band{margin:34px 0 0}.band .hd{display:flex;align-items:baseline;justify-content:space-between;gap:12px;border-bottom:2px solid var(--ink);margin-bottom:16px}.band .hd h2{margin:0 0 8px}.band .hd a{font-size:14px;white-space:nowrap}
.item{border-top:1px solid var(--line);padding:26px 0;display:grid;grid-template-columns:300px 1fr;gap:22px}.item:first-of-type{border-top:0}.item img{border-radius:12px;border:1px solid var(--line);aspect-ratio:16/9;object-fit:cover;width:100%}
@media(max-width:760px){.item{grid-template-columns:1fr;gap:12px}}
.item h3{margin:0 0 8px;font-size:25px}.item .sum{max-width:760px;font-size:17px}
.why{display:grid;gap:8px;margin:12px 0 10px}.why div{display:flex;gap:10px;align-items:flex-start;font-size:15px;color:var(--ink2)}.why div.me{background:var(--acc2);border-radius:10px;padding:8px 10px;color:var(--ink)}
.chip{flex:0 0 auto;display:inline-block;font-size:11px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;padding:3px 8px;border-radius:6px;background:var(--acc2);color:var(--acc);margin-top:2px}
.src{font-size:14px;color:var(--mute)}.src a{color:var(--mute);text-decoration:underline}
.btn{display:inline-block;background:var(--acc);color:#fff;padding:11px 18px;border-radius:10px;font-weight:600;border:0;cursor:pointer;font-size:16px}.btn:hover{text-decoration:none;filter:brightness(1.08)}.btn.ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:14px 0 8px}.toolbar select{padding:9px 12px;border-radius:9px;border:1px solid var(--line);background:var(--paper2);color:var(--ink);font-size:14px}
.nl{background:var(--ink);color:var(--paper);border-radius:16px;padding:26px 24px;margin:36px 0}.nl h2{margin:0 0 6px;color:var(--paper)}.nl p{color:#cfc9bd;margin:0 0 14px}
.nl form{display:flex;gap:8px;flex-wrap:wrap}.nl input[type=email]{flex:1 1 220px;padding:12px 14px;border-radius:10px;border:1px solid #555;background:#fff;color:#111;font-size:16px}.nl button{padding:12px 18px;border-radius:10px;border:0;background:var(--acc);color:#fff;font-weight:600;font-size:16px;cursor:pointer}.nl small{color:#9b958a}
#stick{position:fixed;left:0;right:0;bottom:-140px;background:var(--ink);color:var(--paper);padding:12px 16px;z-index:30;transition:bottom .3s;box-shadow:0 -6px 24px rgba(0,0,0,.25)}#stick.on{bottom:0}#stick .wrap{display:flex;gap:10px;align-items:center;flex-wrap:wrap;justify-content:space-between}#stick form{display:flex;gap:6px;flex:1 1 300px}#stick input{flex:1;padding:10px 12px;border-radius:9px;border:0;font-size:15px}#stick button{padding:10px 14px;border-radius:9px;border:0;background:var(--acc);color:#fff;font-weight:600}#stick .x{background:none;border:0;color:#aaa;font-size:22px;cursor:pointer}
table{border-collapse:collapse;width:100%;font-size:15px;margin:10px 0 18px}th,td{text-align:left;padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:13px;letter-spacing:.05em;text-transform:uppercase;color:var(--mute)}td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.tscroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
.meta{color:var(--mute);font-size:14px}
footer{border-top:1px solid var(--line);padding:28px 0 60px;color:var(--mute);font-size:14px}footer a{color:var(--ink2)}footer .cols{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:12px}
.pill{display:inline-block;font-size:12px;padding:2px 9px;border-radius:999px;border:1px solid var(--line);color:var(--mute);margin:0 6px 6px 0}a.pill:hover{border-color:var(--acc);color:var(--acc);text-decoration:none}
.faq details{border-top:1px solid var(--line);padding:10px 0}.faq summary{cursor:pointer;font-weight:600}
.article{max-width:760px}.article p,.article li{font-size:18px}.cover{border-radius:var(--r);border:1px solid var(--line);margin:0 0 22px;max-width:900px}
.conf-primary{color:var(--ok)}.conf-secondary{color:var(--warn)}
.hero{padding:10px 0 16px}.hero h1{max-width:900px}.dateline{font-size:15px;color:var(--mute)}
.list a{display:block;padding:12px 0;border-bottom:1px solid var(--line);color:inherit}.list a:hover{text-decoration:none;color:var(--acc)}.list small{display:block;color:var(--mute)}
.chart{width:100%;height:auto;margin:6px 0 18px}.chart text{font-family:Inter,system-ui,sans-serif}
.tl{border-left:2px solid var(--line);margin:10px 0 0 8px;padding-left:22px}.tl .ev{position:relative;padding:0 0 22px}.tl .ev:before{content:"";position:absolute;left:-29px;top:6px;width:12px;height:12px;border-radius:50%;background:var(--acc);border:2px solid var(--paper)}.tl .d{font-size:13px;color:var(--mute)}
.badge{background:var(--acc);color:#fff;border-radius:999px;font-size:11px;padding:2px 7px;margin-left:6px;font-weight:700;display:none}
#q{width:100%;padding:14px 16px;font-size:18px;border-radius:12px;border:1px solid var(--line);background:var(--paper2);color:var(--ink)}
.share{display:flex;gap:6px;flex-wrap:wrap}.share button,.share a{font-size:13px;padding:6px 10px;border-radius:8px;border:1px solid var(--line);background:var(--paper);color:var(--ink2);cursor:pointer}
.statbig{font-family:Newsreader,Georgia,serif;font-size:44px;font-weight:700;color:var(--acc);line-height:1}
"""

JS = r"""
(function(){
var d=document,ls=window.localStorage,root=d.documentElement;function g(k){try{return ls.getItem(k)}catch(e){return null}}function s(k,v){try{ls.setItem(k,v)}catch(e){}}
var t=g('theme');if(t)root.setAttribute('data-theme',t);var tb=d.getElementById('themeBtn');if(tb){tb.onclick=function(){var cur=root.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');var n=cur==='dark'?'light':'dark';root.setAttribute('data-theme',n);s('theme',n)}}
var pr=d.getElementById('prog');if(pr){addEventListener('scroll',function(){var h=d.documentElement.scrollHeight-innerHeight;pr.style.width=(h>0?Math.min(100,scrollY/h*100):0)+'%'},{passive:true})}
var AUD={executives:'Executives',finance:'Finance',security:'Security',ml:'ML engineers',developers:'Developers',beginners:'Beginners'};
function applyLens(k){d.querySelectorAll('.why').forEach(function(w){var rows=[].slice.call(w.children);rows.forEach(function(r){r.classList.toggle('me',!!k&&r.getAttribute('data-aud')===k)});if(k){rows.filter(function(r){return r.getAttribute('data-aud')===k}).forEach(function(r){w.insertBefore(r,w.firstChild)})}});d.querySelectorAll('.lensName').forEach(function(e){e.textContent=k?AUD[k]:'everyone'})}
var lens=g('lens');d.querySelectorAll('select.lens').forEach(function(sel){if(lens)sel.value=lens;sel.onchange=function(){s('lens',sel.value);applyLens(sel.value);d.querySelectorAll('select.lens').forEach(function(o){o.value=sel.value})}});if(lens)applyLens(lens);
var lb=d.getElementById('listenBtn');if(lb){if(!('speechSynthesis' in window)){lb.style.display='none'}else{var speaking=false;lb.onclick=function(){if(speaking){speechSynthesis.cancel();speaking=false;lb.textContent='▶ Listen';return}var txt=[].map.call(d.querySelectorAll('[data-speak]'),function(e){return e.textContent}).join('. ');var u=new SpeechSynthesisUtterance(txt);u.rate=1.02;u.onend=function(){speaking=false;lb.textContent='▶ Listen'};speechSynthesis.cancel();speechSynthesis.speak(u);speaking=true;lb.textContent='■ Stop'}}}
d.querySelectorAll('[data-share]').forEach(function(b){b.onclick=function(){var url=b.getAttribute('data-share'),ti=b.getAttribute('data-title')||d.title;if(navigator.share){navigator.share({title:ti,url:url}).catch(function(){})}else{if(navigator.clipboard)navigator.clipboard.writeText(url);b.textContent='Link copied'}}});
var last=g('lastSeen'),cur=d.body.getAttribute('data-latest');if(cur){if(last&&last<cur){d.querySelectorAll('.badge').forEach(function(b){b.style.display='inline-block';b.textContent='New'})}s('lastSeen',cur)}
var st=d.getElementById('stick');if(st&&!g('nl_dismissed')&&!g('nl_pending')){var shown=false;addEventListener('scroll',function(){if(!shown){var h=d.documentElement.scrollHeight-innerHeight;if(h>0&&scrollY/h>0.45){st.classList.add('on');shown=true}}},{passive:true});var x=st.querySelector('.x');if(x)x.onclick=function(){st.classList.remove('on');s('nl_dismissed','1')}}
d.querySelectorAll('form.nlf').forEach(function(f){f.addEventListener('submit',function(){var e=f.querySelector('input[type=email]');if(e)s('nl_pending',e.value)})});
var q=d.getElementById('q');if(q){var idx=null,res=d.getElementById('res');var run=function(){var v=q.value.trim().toLowerCase();if(!idx||v.length<2){res.innerHTML='';return}var terms=v.split(/\s+/);var hits=idx.map(function(it){var h=(it.t+' '+it.s).toLowerCase(),sc=0;terms.forEach(function(w){if(it.t.toLowerCase().indexOf(w)>=0)sc+=3;if(h.indexOf(w)>=0)sc+=1});return[sc,it]}).filter(function(x){return x[0]>0}).sort(function(a,b){return b[0]-a[0]}).slice(0,30);res.innerHTML=hits.map(function(x){var it=x[1];return'<a href="'+it.u+'"><strong>'+it.t+'</strong><small>'+it.k+' · '+it.s.slice(0,140)+'</small></a>'}).join('')||'<p class="meta">No matches.</p>'};q.oninput=run;var qs=new URLSearchParams(location.search).get('q');if(qs)q.value=qs;fetch('/search.json').then(function(r){return r.json()}).then(function(j){idx=j;run()});q.focus()}
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(function(){})}
})();
"""

SW = r"""
const C='aib-v2';self.addEventListener('install',e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(['/','/brief/','/assets/site.css','/assets/site.js'])).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET'||!r.url.startsWith(self.location.origin))return;e.respondWith(fetch(r).then(res=>{const cp=res.clone();caches.open(C).then(c=>c.put(r,cp));return res}).catch(()=>caches.match(r).then(m=>m||caches.match('/'))))});
"""
ASSET_V = hashlib.md5((CSS + JS).encode()).hexdigest()[:8]
HEAD_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:ital,wght@0,500;0,600;0,700;1,500&display=swap" rel="stylesheet">'

def nav_html(section=""):
    links = [("/brief/", "brief", "Daily brief"), ("/for/", "for", "For you"), ("/trackers/", "trackers", "Trackers"), ("/topics/", "topics", "Topics"), ("/learn/", "learn", "Learn"), ("/glossary/", "glossary", "Glossary")]
    return "".join(f'<a href="{h}"{" class=on" if k == section else ""}>{t}</a>' for h, k, t in links)
def sub_html(section=""):
    links = [("/", "home", "Home"), ("/brief/", "brief", "Brief"), ("/for/", "for", "For you"), ("/trackers/api-pricing/", "pricing", "Pricing"), ("/trackers/models/", "models", "Models"), ("/topics/", "topics", "Topics"), ("/learn/", "learn", "Learn"), ("/glossary/", "glossary", "Glossary"), ("/newsletter/", "newsletter", "Newsletter")]
    return "".join(f'<a href="{h}"{" class=on" if k == section else ""}>{t}</a>' for h, k, t in links)

def nl_form(cls="nlf"):
    form = CFG.get("newsletter_form_html", "").strip()
    if form: return form
    return f'<form class="{cls}" action="/newsletter/thanks/" method="get"><input type="email" name="email" placeholder="you@company.com" required aria-label="Email address"><button type="submit">Subscribe free</button></form>'
def newsletter_box():
    return (f'<section class="nl" id="subscribe"><h2>Get the brief in your inbox</h2>'
            f'<p>One email every morning: the stories that mattered in AI, each with a one-line "why it matters" for your role. Free, no ads, unsubscribe any time.</p>{nl_form()}'
            f'<small>Published daily by {BRAND}. We never share your address.</small></section>')
def sticky_bar():
    return f'<div id="stick"><div class="wrap"><strong>Like this? Get tomorrow\'s brief by email, free.</strong>{nl_form("nlf")}<button class="x" aria-label="Dismiss">×</button></div></div>'
def ticker_html(briefs):
    b = briefs[0]
    items = "".join(f'<a href="/brief/{b["date"]}/#{esc(it["id"])}">{esc(strip_md(it["title"]))}</a><span class="dot">•</span>' for it in b["items"][:8])
    return f'<div class="ticker"><div class="wrap"><b>Latest</b>{items}</div></div>'

def layout(*, title, desc, path, body, section="", jsonld=None, og_type="website", og_image=None, published=None, modified=None, noindex=False, latest=None, ticker=""):
    url = ROOT + path; og_image = og_image or (ROOT + "/og.png")
    ld = [{"@context": "https://schema.org", "@type": "NewsMediaOrganization", "name": BRAND, "url": ROOT + "/", "logo": ROOT + "/og.png"},
          {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": ROOT + "/", "potentialAction": {"@type": "SearchAction", "target": ROOT + "/search/?q={search_term_string}", "query-input": "required name=search_term_string"}}]
    if jsonld: ld += jsonld if isinstance(jsonld, list) else [jsonld]
    ldtags = "".join(f'<script type="application/ld+json">{jd(x)}</script>' for x in ld)
    meta_dates = (f'<meta property="article:published_time" content="{published}">' if published else "") + (f'<meta property="article:modified_time" content="{modified}">' if modified else "")
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
<meta name="theme-color" content="#141311">
<meta property="og:type" content="{og_type}"><meta property="og:site_name" content="{BRAND}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}"><meta property="og:image" content="{og_image}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{og_image}">
{meta_dates}
<link rel="alternate" type="application/rss+xml" title="{BRAND} daily" href="{ROOT}/feed.xml">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/icon-192.png"><link rel="manifest" href="/manifest.webmanifest">
{HEAD_FONTS}
<link rel="stylesheet" href="/assets/site.css?v={ASSET_V}">
{ldtags}
{CFG.get("analytics_html", "")}
</head>
<body{(' data-latest="' + latest + '"') if latest else ''}>
<div id="prog"></div>
<header class="top"><div class="wrap"><a class="logo" href="/">AI<b>Briefing</b></a><nav class="main" aria-label="Main">{nav_html(section)}</nav><div class="tools"><a class="ibtn" href="/search/" aria-label="Search">⌕</a><button class="ibtn" id="themeBtn" aria-label="Toggle dark mode">◐</button><a class="btn" href="/newsletter/" style="padding:8px 14px;font-size:14px">Subscribe</a></div></div></header>
<div class="sub"><div class="wrap">{sub_html(section)}</div></div>
{ticker}
<main><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
<div class="cols"><a href="/brief/">Daily brief</a><a href="/for/">By role</a><a href="/trackers/">Trackers</a><a href="/topics/">Topics</a><a href="/learn/">Learn</a><a href="/glossary/">Glossary</a><a href="/newsletter/">Newsletter</a><a href="/search/">Search</a><a href="/about/">About</a><a href="/privacy/">Privacy</a><a href="/feed.xml">RSS</a></div>
<div>{BRAND} is an independent publication. Every item links to its original source; summaries are written in our own words. Graphics are generated in-house. Not affiliated with the companies covered. &copy; {datetime.date.today().year} aibriefing.io</div>
</div></footer>
{sticky_bar()}
<script src="/assets/site.js?v={ASSET_V}" defer></script>
</body>
</html>"""

# ---------- components ----------
def breadcrumbs(items):
    el = [{"@type": "ListItem", "position": 1, "name": "Home", "item": ROOT + "/"}]
    for i, (n, p) in enumerate(items, start=2): el.append({"@type": "ListItem", "position": i, "name": n, "item": ROOT + p})
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": el}
def faq_html(faqs):
    if not faqs: return ""
    return '<section class="faq"><h2>Common questions</h2>' + "".join(f'<details><summary>{esc(q)}</summary><p>{md_inline(a)}</p></details>' for q, a in faqs) + "</section>"
def faq_ld(faqs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_md(a)}} for q, a in faqs]}
def story_tile(it, date, href=None):
    href = href or f"/brief/{date}/#{it['id']}"
    return (f'<a class="story tile" href="{href}"><img src="{it["img"]}" alt="" width="1200" height="675" loading="lazy">'
            f'<div class="b"><h3>{md_inline(it["title"])}</h3><p>{md_inline(it["summary"][:150])}…</p><div class="m"><span>{short_date(date)}</span><span>·</span><span>{esc(it["sources"][0]["name"]) if it["sources"] else ""}</span></div></div></a>')
def item_html(it, date, aud_filter=None, with_date=False):
    why = it.get("why", {})
    keys = [aud_filter] if aud_filter and aud_filter in why else [k for k in why if k in AUD]
    whys = "".join(f'<div data-aud="{k}"><span class="chip">{esc(AUD[k][1])}</span><span>{md_inline(why[k])}</span></div>' for k in keys)
    srcl = " · ".join(f'<a href="{esc(s["url"])}" rel="noopener">{esc(s["name"])}</a>' for s in it["sources"] if s.get("url"))
    dl = f'<span class="meta">{short_date(date)} · </span>' if with_date else ""
    tags = "".join(f'<a class="pill" href="/topics/{slugify(t)}/">{esc(t)}</a>' for t in it.get("tags", []))
    url = f"{ROOT}/brief/{date}/#{it['id']}"
    return (f'<article class="item" id="{esc(it["id"])}"><a href="/brief/{date}/#{it["id"]}"><img src="{it["img"]}" alt="" width="1200" height="675" loading="lazy"></a><div>'
            f'<h3 data-speak>{dl}{md_inline(it["title"])}</h3><p class="sum" data-speak>{md_inline(it["summary"])}</p><div class="why">{whys}</div>'
            f'<div class="src">Source: {srcl}</div><div style="margin-top:10px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap"><div>{tags}</div><div class="share"><button data-share="{url}" data-title="{esc(strip_md(it["title"]))}">Share</button></div></div></div></article>')
def lens_select():
    opts = '<option value="">Everyone</option>' + "".join(f'<option value="{k}">{esc(n)}</option>' for k, n, _, _ in AUDIENCES)
    return f'<label class="meta">Read as&nbsp;<select class="lens" aria-label="Choose your lens">{opts}</select></label>'

# ---------- pages ----------
def brief_page(b, prev_b=None, next_b=None):
    date = b["date"]; title = b.get("headline") or f"AI news for {short_date(date)}"; path = f"/brief/{date}/"
    items = "".join(item_html(it, date) for it in b["items"])
    one = f'<div class="card" style="margin:14px 0 22px"><div class="kicker">The one thing to know</div><p style="font-size:18px;color:var(--ink)" data-speak>{md_inline(b["one_thing"])}</p></div>' if b.get("one_thing") else ""
    navl = (f'<a href="/brief/{prev_b["date"]}/">&larr; {short_date(prev_b["date"])}</a>' if prev_b else "") + (f' &nbsp;·&nbsp; <a href="/brief/{next_b["date"]}/">{short_date(next_b["date"])} &rarr;</a>' if next_b else "")
    og = f"{ROOT}/img/briefs/{date}.png"
    body = (f'<div class="hero"><div class="kicker">Daily brief</div><h1 data-speak>{esc(title)}</h1>'
            f'<div class="dateline">{fmt_date(date)} · {len(b["items"])} stories · {read_time(b["words"])} min read</div>'
            f'<p class="lede" style="margin-top:10px" data-speak>{md_inline(b.get("intro", ""))}</p>'
            f'<div class="toolbar">{lens_select()}<button class="btn ghost" id="listenBtn">▶ Listen</button><div class="share"><button data-share="{ROOT}{path}" data-title="{esc(title)}">Share</button></div></div></div>'
            f'{one}<section>{items}</section><p class="meta" style="margin-top:18px">{navl}</p>{newsletter_box()}')
    desc = (b.get("intro", "")[:155]) or f"The {len(b['items'])} AI stories that mattered on {short_date(date)}."
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": title, "datePublished": date + "T11:00:00Z", "dateModified": (b.get("updated", date)) + "T11:00:00Z",
          "author": {"@type": "Organization", "name": BRAND, "url": ROOT + "/about/"}, "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": ROOT + "/og.png"}},
          "mainEntityOfPage": ROOT + path, "image": [og], "description": desc, "wordCount": b["words"],
          "citation": [s["url"] for it in b["items"] for s in it["sources"] if s.get("url")]}
    return layout(title=f"{title} — AI Briefing, {short_date(date)}", desc=desc, path=path, body=body, section="brief", jsonld=[ld, breadcrumbs([("Brief", "/brief/"), (short_date(date), path)])], og_type="article", og_image=og, published=date, modified=b.get("updated", date))

def brief_index(briefs):
    rows = "".join(f'<a class="story tile" href="/brief/{b["date"]}/"><img src="/img/briefs/{b["date"]}.png" alt="" width="1200" height="630" loading="lazy"><div class="b"><h3>{esc(b.get("headline") or short_date(b["date"]))}</h3><p>{esc(strip_md(b.get("intro", ""))[:140])}…</p><div class="m">{fmt_date(b["date"])} · {len(b["items"])} stories</div></div></a>' for b in briefs)
    body = f'<div class="hero"><div class="kicker">Archive</div><h1>Every daily brief</h1><p class="lede">One page per day. Each story is summarised in our own words with a why-it-matters line for your role, and links to the original reporting.</p></div><div class="grid g3">{rows}</div>{newsletter_box()}'
    return layout(title="Daily AI brief archive — AI Briefing", desc="Every daily AI news brief, one page per day, with role-specific why-it-matters lines and links to original sources.", path="/brief/", body=body, section="brief", jsonld=breadcrumbs([("Brief", "/brief/")]))

def hub_page(key, briefs, explainers):
    k, name, who, blurb = AUD[key]
    recent = [(b["date"], it) for b in briefs[:10] for it in b["items"] if key in it.get("why", {})][:18]
    items = "".join(item_html(it, d, aud_filter=key, with_date=True) for d, it in recent)
    ex = [e for e in explainers if key in e.get("audiences", [])][:6]
    exh = "".join(f'<a class="story tile" href="/learn/{e["slug"]}/"><img src="{e["img"]}" alt="" width="1200" height="675" loading="lazy"><div class="b"><h3>{esc(e["title"])}</h3><p>{esc(e["summary"][:120])}…</p></div></a>' for e in ex)
    others = " ".join(f'<a class="pill" href="/for/{a[0]}/">{esc(a[1])}</a>' for a in AUDIENCES if a[0] != key)
    body = (f'<div class="lead"><div><div class="kicker">AI briefing for</div><h1>{esc(name)}</h1><p class="lede">{esc(blurb)} Updated every morning.</p><div>{others}</div></div><img src="/img/for/{key}.webp" alt="" width="1200" height="675"></div>'
            f'<div class="band"><div class="hd"><h2>This week, for {esc(who.lower())}</h2><a href="/brief/">All briefs →</a></div><section>{items or "<p>First edition publishes tomorrow morning.</p>"}</section></div>'
            f'<div class="band"><div class="hd"><h2>Start here</h2><a href="/learn/">All explainers →</a></div><div class="grid g3">{exh}</div></div>{newsletter_box()}')
    path = f"/for/{key}/"
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"AI news for {name}", "url": ROOT + path, "description": blurb, "isPartOf": {"@type": "WebSite", "url": ROOT + "/", "name": BRAND}}
    return layout(title=f"AI news for {name} — daily, in plain language | AI Briefing", desc=f"Daily AI news for {who.lower()}: {blurb} Updated every morning with sources.", path=path, body=body, section="for", jsonld=[ld, breadcrumbs([("For you", "/for/"), (name, path)])], og_image=f"{ROOT}/img/for/{key}.webp")

def for_index():
    tiles = "".join(f'<a class="story tile" href="/for/{k}/"><img src="/img/for/{k}.webp" alt="" width="1200" height="675" loading="lazy"><div class="b"><div class="kicker">{esc(who)}</div><h3>{esc(name)}</h3><p>{esc(blurb)}</p></div></a>' for k, name, who, blurb in AUDIENCES)
    body = f'<div class="hero"><div class="kicker">Pick your lens</div><h1>The same news, explained for your job</h1><p class="lede">Every story in the daily brief carries a one-line "why it matters" written for each of these readers. Choose yours; the site remembers.</p></div><div class="grid g3">{tiles}</div>{newsletter_box()}'
    return layout(title="AI news by role: executives, finance, security, ML, developers, beginners | AI Briefing", desc="Choose your lens: daily AI news explained for executives, finance professionals, security teams, ML engineers, developers and beginners.", path="/for/", body=body, section="for", jsonld=breadcrumbs([("For you", "/for/")]))

def conf_badge(c): return '<span class="conf-primary">● primary source</span>' if c == "primary" else '<span class="conf-secondary">● secondary, pending re-check</span>'

def pricing_chart(rows):
    rows = [r for r in rows if r.get("output") and "/" not in r["model"]][:14]
    rows = sorted(rows, key=lambda r: -r["output"])
    W, rh, lw = 900, 26, 250; H = 40 + rh * len(rows) + 30; mx = max(r["output"] for r in rows)
    svg = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Output price per million tokens by model">']
    svg.append(f'<text x="{lw}" y="18" font-size="12" fill="#857f74">Price per 1M tokens · dark bar = output, light bar = input</text>')
    for i, r in enumerate(rows):
        y = 34 + i * rh; wo = (W - lw - 110) * r["output"] / mx; wi = (W - lw - 110) * r["input"] / mx
        svg.append(f'<text x="{lw - 10}" y="{y + 14}" text-anchor="end" font-size="12" fill="currentColor">{esc(r["model"][:30])}</text>')
        svg.append(f'<rect x="{lw}" y="{y + 2}" width="{wo:.1f}" height="10" rx="3" fill="#1f4bff" opacity=".9"/><rect x="{lw}" y="{y + 13}" width="{wi:.1f}" height="6" rx="3" fill="#1f4bff" opacity=".35"/>')
        svg.append(f'<text x="{lw + wo + 6:.1f}" y="{y + 12}" font-size="11" fill="#857f74">{money(r["output"])} / {money(r["input"])}</text>')
    svg.append("</svg>"); return "".join(svg)

def tracker_pricing(t):
    rows = "".join(f'<tr><td><strong>{esc(r["model"])}</strong><br><span class="meta">{esc(r["vendor"])}{(" · " + esc(r["note"])) if r.get("note") else ""}</span></td><td class="num">{money(r["input"])}</td><td class="num">{money(r["output"])}</td><td class="num">{money(r.get("cached"))}</td><td class="num">{esc(r.get("context", "—"))}</td><td class="meta"><a href="{esc(r["source"])}" rel="noopener">{esc(r.get("verified", ""))}</a><br>{conf_badge(r.get("confidence", "secondary"))}</td></tr>' for r in t["rows"])
    table = f'<div class="tscroll"><table><thead><tr><th>Model</th><th>Input / 1M</th><th>Output / 1M</th><th>Cached input</th><th>Context</th><th>Verified</th></tr></thead><tbody>{rows}</tbody></table></div>'
    top = max(t["rows"], key=lambda r: r["output"]); cheapest = min((r for r in t["rows"] if r["output"] >= 10), key=lambda r: r["output"], default=top)
    stats = (f'<div class="grid g3" style="margin:6px 0 10px"><div class="card"><div class="statbig">{money(top["output"])}</div><p>Highest output price per 1M ({esc(top["model"])})</p></div>'
             f'<div class="card"><div class="statbig">{money(cheapest["output"])}</div><p>Cheapest frontier-class output ({esc(cheapest["model"])})</p></div>'
             f'<div class="card"><div class="statbig">{len(t["rows"])}</div><p>Models tracked · {sum(1 for r in t["rows"] if r.get("confidence") == "primary")} read from vendor pages</p></div></div>')
    body = (f'<div class="hero"><div class="kicker">Tracker</div><h1>{esc(t["title"])}</h1><p class="lede">{esc(t["intro"])}</p><p class="meta">Last checked {esc(t["updated"])}. USD per million tokens, standard tier, as published by each vendor.</p></div>'
            f'{stats}{pricing_chart(t["rows"])}{table}<h2>How to read this</h2>{md_block(t.get("notes", ""))}{faq_html(t.get("faqs", []))}{newsletter_box()}')
    path = "/trackers/api-pricing/"
    ld = [{"@context": "https://schema.org", "@type": "Dataset", "name": t["title"], "description": t["intro"], "url": ROOT + path, "dateModified": t["updated"], "creator": {"@type": "Organization", "name": BRAND}, "license": "https://creativecommons.org/licenses/by/4.0/"}, breadcrumbs([("Trackers", "/trackers/"), (t["title"], path)])]
    if t.get("faqs"): ld.append(faq_ld(t["faqs"]))
    return layout(title=f'{t["title"]} ({datetime.date.fromisoformat(t["updated"]).strftime("%B %Y")}) | AI Briefing', desc=t["intro"][:155], path=path, body=body, section="trackers", jsonld=ld, modified=t["updated"])

def tracker_models(t):
    tl = "".join(f'<div class="ev"><div class="d">{esc(r["released"])} · {esc(r["vendor"])}</div><strong>{esc(r["model"])}</strong> <span class="pill">{esc(r["kind"])}</span><div class="meta">{md_inline(r.get("note", ""))} <a href="{esc(r["source"])}" rel="noopener">source</a></div></div>' for r in t["rows"])
    body = f'<div class="hero"><div class="kicker">Tracker</div><h1>{esc(t["title"])}</h1><p class="lede">{esc(t["intro"])}</p><p class="meta">Last updated {esc(t["updated"])}. Newest first; each entry links to the vendor page.</p></div><div class="tl">{tl}</div>{md_block(t.get("notes", ""))}{faq_html(t.get("faqs", []))}{newsletter_box()}'
    path = "/trackers/models/"
    ld = [{"@context": "https://schema.org", "@type": "Dataset", "name": t["title"], "description": t["intro"], "url": ROOT + path, "dateModified": t["updated"], "creator": {"@type": "Organization", "name": BRAND}}, breadcrumbs([("Trackers", "/trackers/"), (t["title"], path)])]
    if t.get("faqs"): ld.append(faq_ld(t["faqs"]))
    return layout(title=f'{t["title"]} ({datetime.date.fromisoformat(t["updated"]).strftime("%B %Y")}) | AI Briefing', desc=t["intro"][:155], path=path, body=body, section="trackers", jsonld=ld, modified=t["updated"])

def trackers_index():
    tiles = "".join(f'<a class="card tile" href="/trackers/{k}/"><h3>{esc(t["title"])}</h3><p>{esc(t["intro"])}</p><p class="meta" style="margin-top:8px">Updated {esc(t["updated"])}</p></a>' for k, t in sorted(TRACKERS.items()))
    body = f'<div class="hero"><div class="kicker">Reference</div><h1>Trackers: the numbers that keep changing</h1><p class="lede">Living tables and charts, checked against vendor pages every night. Bookmark these instead of re-googling.</p></div><div class="grid g2">{tiles}</div>{newsletter_box()}'
    return layout(title="AI trackers: API pricing, model releases | AI Briefing", desc="Living reference tables for AI: API prices per million tokens and model releases, re-checked against vendor pages nightly.", path="/trackers/", body=body, section="trackers", jsonld=breadcrumbs([("Trackers", "/trackers/")]))

def topic_pages(briefs):
    by = defaultdict(list)
    for b in briefs:
        for it in b["items"]:
            for t in it.get("tags", []): by[t].append((b["date"], it))
    out = {}
    tiles = "".join(f'<a class="card tile" href="/topics/{slugify(t)}/"><h3>{esc(t)}</h3><p>{len(v)} stor{"y" if len(v) == 1 else "ies"} · latest {short_date(v[0][0])}</p></a>' for t, v in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])))
    out["/topics/"] = layout(title="AI topics: story threads by company and theme | AI Briefing", desc="Follow the story so far on every AI company and theme: funding, models, security, pricing, regulation and more, as a timeline.", path="/topics/", body=f'<div class="hero"><div class="kicker">Threads</div><h1>The story so far, by topic</h1><p class="lede">Every story we publish is tagged. Pick a thread to read it as a timeline.</p></div><div class="grid g3">{tiles}</div>{newsletter_box()}', section="topics", jsonld=breadcrumbs([("Topics", "/topics/")]))
    for t, v in by.items():
        path = f"/topics/{slugify(t)}/"
        tl = "".join(f'<div class="ev"><div class="d">{short_date(d)}</div><a href="/brief/{d}/#{it["id"]}"><strong>{md_inline(it["title"])}</strong></a><div class="meta">{md_inline(it["summary"][:220])}…</div></div>' for d, it in v)
        cards = "".join(story_tile(it, d) for d, it in v[:6])
        body = f'<div class="hero"><div class="kicker">Topic</div><h1>{esc(t)}: the story so far</h1><p class="lede">{len(v)} stor{"y" if len(v) == 1 else "ies"}, newest first, each linking to the original reporting.</p></div><div class="grid g3">{cards}</div><h2>Timeline</h2><div class="tl">{tl}</div>{newsletter_box()}'
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{t}: AI news timeline", "url": ROOT + path}
        out[path] = layout(title=f"{t} — AI news timeline and story thread | AI Briefing", desc=f"Everything we have covered on {t}, as a timeline with sources. Updated daily.", path=path, body=body, section="topics", jsonld=[ld, breadcrumbs([("Topics", "/topics/"), (t, path)])])
    return out

def explainer_page(e, explainers):
    path = f"/learn/{e['slug']}/"
    aud = " ".join(f'<a class="pill" href="/for/{k}/">{esc(AUD[k][1])}</a>' for k in e.get("audiences", []) if k in AUD)
    related = [x for x in explainers if x["slug"] != e["slug"] and set(x.get("audiences", [])) & set(e.get("audiences", []))][:3]
    rel = "".join(f'<a class="story tile" href="/learn/{x["slug"]}/"><img src="{x["img"]}" alt="" width="1200" height="675" loading="lazy"><div class="b"><h3>{esc(x["title"])}</h3><p>{esc(x["summary"][:120])}…</p></div></a>' for x in related)
    relh = f'<div class="band"><div class="hd"><h2>Related</h2></div><div class="grid g3">{rel}</div></div>' if rel else ""
    body = (f'<div class="hero"><div class="kicker">Explainer · {esc(e.get("level", "all levels"))} · {read_time(e["words"])} min read</div><h1>{esc(e["title"])}</h1><p class="lede">{esc(e["summary"])}</p><p class="meta">Updated {esc(e.get("updated", ""))} · For: {aud}</p></div>'
            f'<img class="cover" src="{e["img"]}" alt="" width="1200" height="675"><div class="article">{md_block(e["body"])}</div>{faq_html(e.get("faqs", []))}{relh}{newsletter_box()}')
    ld = [{"@context": "https://schema.org", "@type": "Article", "headline": e["title"], "description": e["summary"], "datePublished": e.get("published", e.get("updated")), "dateModified": e.get("updated"), "author": {"@type": "Organization", "name": BRAND}, "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": ROOT + "/og.png"}}, "mainEntityOfPage": ROOT + path, "image": ROOT + e["img"], "wordCount": e["words"]}, breadcrumbs([("Learn", "/learn/"), (e["title"], path)])]
    if e.get("faqs"): ld.append(faq_ld(e["faqs"]))
    return layout(title=f'{e["title"]} | AI Briefing', desc=e["summary"][:155], path=path, body=body, section="learn", jsonld=ld, og_type="article", og_image=ROOT + e["img"], published=e.get("published"), modified=e.get("updated"))

def learn_index(explainers):
    by = defaultdict(list)
    for e in explainers:
        for k in e.get("audiences", []): by[k].append(e)
    secs = ""
    for k, name, who, _ in AUDIENCES:
        if not by[k]: continue
        secs += f'<div class="band"><div class="hd"><h2>For {esc(name.lower())}</h2><a href="/for/{k}/">{esc(name)} brief →</a></div><div class="grid g3">' + "".join(f'<a class="story tile" href="/learn/{e["slug"]}/"><img src="{e["img"]}" alt="" width="1200" height="675" loading="lazy"><div class="b"><h3>{esc(e["title"])}</h3><p>{esc(e["summary"][:130])}…</p></div></a>' for e in by[k]) + "</div></div>"
    body = f'<div class="hero"><div class="kicker">Learn</div><h1>Explainers that stay current</h1><p class="lede">Short, plain-English guides to the ideas behind the news. Each is revisited when the facts change.</p></div>{secs}{newsletter_box()}'
    return layout(title="Learn AI: plain-English explainers for every role | AI Briefing", desc="Short explainers on agents, pricing, context windows, RAG, prompt injection, benchmarks and more, written for executives, developers, security and beginners.", path="/learn/", body=body, section="learn", jsonld=breadcrumbs([("Learn", "/learn/")]))

def glossary_pages():
    terms = sorted(GLOSSARY, key=lambda t: t["term"].lower()); out = {}
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
    b = briefs[0]; lead = b["items"][0]
    rest = "".join(story_tile(it, b["date"]) for it in b["items"][1:7])
    tiles = "".join(f'<a class="story tile" href="/for/{k}/"><img src="/img/for/{k}.webp" alt="" width="1200" height="675" loading="lazy"><div class="b"><h3>{esc(name)}</h3><p>{esc(blurb)}</p></div></a>' for k, name, who, blurb in AUDIENCES)
    pt = TRACKERS.get("api-pricing"); mt = TRACKERS.get("models", {})
    tr = (f'<div class="grid g2"><a class="card tile" href="/trackers/api-pricing/"><div class="kicker">Pricing tracker</div><h3>{esc(pt["title"]) if pt else ""}</h3>{pricing_chart(pt["rows"]) if pt else ""}<p class="meta">Checked {esc(pt["updated"]) if pt else ""} · {len(pt["rows"]) if pt else 0} models</p></a>'
          f'<a class="card tile" href="/trackers/models/"><div class="kicker">Release tracker</div><h3>{esc(mt.get("title", ""))}</h3><div class="tl">' + "".join(f'<div class="ev"><div class="d">{esc(r["released"])} · {esc(r["vendor"])}</div><strong>{esc(r["model"])}</strong></div>' for r in mt.get("rows", [])[:5]) + '</div></a></div>')
    ex = "".join(f'<a class="story tile" href="/learn/{e["slug"]}/"><img src="{e["img"]}" alt="" width="1200" height="675" loading="lazy"><div class="b"><h3>{esc(e["title"])}</h3><p>{esc(e["summary"][:120])}…</p></div></a>' for e in explainers[:3])
    older = "".join(story_tile(it, ob["date"]) for ob in briefs[1:3] for it in ob["items"][:3])
    one = f'<div class="card"><div class="kicker">The one thing to know today</div><p style="font-size:18px;color:var(--ink);margin:0">{md_inline(b["one_thing"])}</p></div>' if b.get("one_thing") else ""
    older_band = f'<div class="band"><div class="hd"><h2>Earlier this week</h2><a href="/brief/">Archive →</a></div><div class="grid g3">{older}</div></div>' if older else ""
    body = (f'<div class="lead"><div><div class="kicker">{fmt_date(b["date"])} · Today\'s brief<span class="badge"></span></div><h1>{esc(b.get("headline") or TAGLINE)}</h1><p class="lede">{md_inline(b.get("intro", ""))}</p>'
            f'<p><a class="btn" href="/brief/{b["date"]}/">Read the brief · {read_time(b["words"])} min</a> &nbsp; <a href="/for/">or pick your role &rarr;</a></p></div>'
            f'<a href="/brief/{b["date"]}/#{lead["id"]}"><img src="{lead["img"]}" alt="" width="1200" height="675" fetchpriority="high"></a></div>{one}'
            f'<div class="band"><div class="hd"><h2>Today\'s stories</h2><a href="/brief/{b["date"]}/">Full brief →</a></div><div class="grid g3">{rest}</div></div>'
            f'<div class="band"><div class="hd"><h2>Written for your job</h2><a href="/for/">All lenses →</a></div><div class="grid g3">{tiles}</div></div>'
            f'<div class="band"><div class="hd"><h2>Trackers</h2><a href="/trackers/">All trackers →</a></div>{tr}</div>{older_band}'
            f'<div class="band"><div class="hd"><h2>Learn</h2><a href="/learn/">All explainers →</a></div><div class="grid g3">{ex}</div></div>{newsletter_box()}')
    desc = "Daily AI news in 4 minutes, with a one-line why-it-matters for executives, finance, security, ML engineers, developers and beginners. Plus live trackers for API pricing and model releases."
    return layout(title="AI Briefing — daily AI news, explained for your job", desc=desc, path="/", body=body, section="home", latest=b["date"], ticker=ticker_html(briefs), og_image=f"{ROOT}/img/briefs/{b['date']}.png")

def newsletter_page():
    body = (f'<div class="hero"><div class="kicker">Newsletter</div><h1>The AI Briefing, every morning</h1><p class="lede">The stories that mattered in AI yesterday, each in two sentences, each with a why-it-matters line for your role. Four minutes. Free.</p></div>'
            f'{newsletter_box()}<h2>What you get</h2><ul><li>One email per day, sent around 7am US Eastern / 12pm London / 5:30pm India.</li><li>Every item links to the original reporting or announcement.</li><li>Role lenses: executives, finance, security, ML, developers, beginners.</li><li>No ads, no sponsored placements, unsubscribe in one click.</li></ul>'
            f'<p class="meta">Prefer RSS? <a href="/feed.xml">Subscribe to the feed</a>. Prefer an app? Add this site to your home screen; it works offline.</p>')
    return layout(title="Subscribe to the daily AI Briefing newsletter (free)", desc="A free daily email with the AI stories that mattered, each with a one-line why-it-matters for your role. Four minutes, no ads.", path="/newsletter/", body=body, section="newsletter", jsonld=breadcrumbs([("Newsletter", "/newsletter/")]))
def thanks_page():
    return layout(title="Almost there | AI Briefing", desc="Confirm your subscription.", path="/newsletter/thanks/", body='<div class="hero"><h1>Thanks — one more step</h1><p class="lede">Daily email delivery is being switched on this week. We saved your request in this browser; the first email will arrive as soon as sending is live. Meanwhile, <a href="/brief/">today\'s brief is here</a>.</p></div>', noindex=True)
def search_page():
    return layout(title="Search | AI Briefing", desc="Search every brief, explainer and glossary term.", path="/search/", body='<div class="hero"><h1>Search</h1></div><input id="q" type="search" placeholder="Search stories, explainers, terms…" aria-label="Search"><div id="res" class="list" style="margin-top:14px"></div>', noindex=True)
def static_page(path, title, desc, h1, md):
    return layout(title=f"{title} | AI Briefing", desc=desc, path=path, body=f'<div class="hero"><h1>{esc(h1)}</h1></div><div class="article">{md_block(md)}</div>', jsonld=breadcrumbs([(h1, path)]))

ABOUT = """
AI Briefing is a daily publication that explains what happened in artificial intelligence and, more importantly, what it means for the person reading.

## How it works

Every morning an editorial pipeline reads the day's announcements, filings, papers and reporting, selects the handful of items that actually change something, and writes a short summary in our own words. Each item then gets a one-line "why it matters" for six kinds of readers: executives, finance professionals, security teams, ML engineers, developers and beginners. Every item links to its original source so you can go deeper.

The pipeline is operated with AI assistance and checked against primary sources (vendor pricing pages, SEC filings, official announcements). Our trackers show, row by row, which source was used and when it was last checked.

## Graphics

We do not use news photographs. Every story graphic on this site is generated in-house from the story's own facts: the key figure, the category and the headline.

## What we don't do

- We do not republish other outlets' articles. Summaries are short and original, and we always link out.
- We do not run sponsored placements or affiliate links in the brief.
- We do not collect personal data beyond an email address if you subscribe. See the [privacy policy](/privacy/).

## Corrections

If something is wrong, email corrections@aibriefing.io. Corrections are noted on the affected page.
"""
PRIVACY = """
AI Briefing (aibriefing.io) collects as little as possible.

- **Analytics.** We use privacy-preserving, cookie-free analytics to count page views. No personal profile is built and no data is sold.
- **Newsletter.** If you subscribe, your email address is stored with our email provider solely to send the daily brief. Every email has an unsubscribe link; unsubscribing deletes you from the list.
- **Preferences.** Your chosen reading lens, theme and dismissed prompts are stored in your own browser (localStorage), never sent to us.
- **Cookies.** The site sets no tracking cookies.
- **Third parties.** Pages load fonts from Google Fonts. Links to external sites are governed by those sites' policies.

Questions: privacy@aibriefing.io.
"""

def feed(briefs):
    items = ""
    for b in briefs[:20]:
        url = f"{ROOT}/brief/{b['date']}/"; content = f'<p><img src="{ROOT}/img/briefs/{b["date"]}.png" alt="" width="600"></p>'
        if b.get("one_thing"): content += f"<p><strong>The one thing to know:</strong> {md_inline(b['one_thing'])}</p>"
        for it in b["items"]:
            whys = "".join(f"<li><strong>{esc(AUD[k][1])}:</strong> {md_inline(v)}</li>" for k, v in it.get("why", {}).items() if k in AUD)
            srcl = " · ".join(f'<a href="{esc(s["url"])}">{esc(s["name"])}</a>' for s in it["sources"] if s.get("url"))
            content += f'<h3><a href="{url}#{it["id"]}">{md_inline(it["title"])}</a></h3><p>{md_inline(it["summary"])}</p><ul>{whys}</ul><p><small>Source: {srcl}</small></p>'
        content += f'<p><a href="{url}">Read on aibriefing.io</a> · <a href="{ROOT}/for/">Pick your role</a></p>'
        pub = datetime.datetime.fromisoformat(b["date"] + "T11:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
        items += (f'<item><title>{esc(b.get("headline") or "AI Briefing for " + short_date(b["date"]))}</title><link>{url}</link><guid isPermaLink="true">{url}</guid><pubDate>{pub}</pubDate>'
                  f'<description>{esc(b.get("intro", ""))}</description><enclosure url="{ROOT}/img/briefs/{b["date"]}.png" type="image/png" length="0"/><content:encoded><![CDATA[{content}]]></content:encoded></item>')
    return f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{BRAND}</title><link>{ROOT}/</link><description>{esc(TAGLINE)}</description><language>en</language><image><url>{ROOT}/og.png</url><title>{BRAND}</title><link>{ROOT}/</link></image><atom:link href="{ROOT}/feed.xml" rel="self" type="application/rss+xml"/>{items}</channel></rss>'

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
AddType image/webp .webp
AddType application/manifest+json .webmanifest
<IfModule mod_headers.c>
Header set X-Content-Type-Options "nosniff"
Header set Referrer-Policy "strict-origin-when-cross-origin"
Header set X-Frame-Options "SAMEORIGIN"
<FilesMatch "\.(html)$">
Header set Cache-Control "public, max-age=600"
</FilesMatch>
<FilesMatch "\.(png|webp|svg|xml|txt|css|js|json|webmanifest)$">
Header set Cache-Control "public, max-age=86400"
</FilesMatch>
<FilesMatch "sw\.js$">
Header set Cache-Control "no-cache"
</FilesMatch>
</IfModule>
<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml application/xml text/xml
</IfModule>
"""
FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#141311"/><text x="32" y="44" text-anchor="middle" font-family="Georgia,serif" font-weight="700" font-size="36" fill="#faf8f4">A<tspan fill="#7a93ff">I</tspan></text></svg>'
MANIFEST = {"name": "AI Briefing", "short_name": "AI Briefing", "start_url": "/", "display": "standalone", "background_color": "#141311", "theme_color": "#141311", "description": TAGLINE, "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}

def og_image():
    from PIL import Image, ImageDraw
    W, H = 1200, 630; img = Image.new("RGB", (W, H), (20, 19, 17)); d = ImageDraw.Draw(img)
    serif = art.font(art.SERIF, 86); sans = art.font(art.SANS, 30)
    d.text((80, 170), "AI", font=serif, fill=(250, 248, 244)); w = d.textlength("AI", font=serif)
    d.text((80 + w, 170), "Briefing", font=serif, fill=(122, 147, 255))
    d.text((82, 300), "Daily AI news, explained for your job.", font=sans, fill=(201, 194, 181))
    d.text((82, 350), "Executives · Finance · Security · ML · Developers · Beginners", font=art.font(art.SANSR, 24), fill=(141, 134, 120))
    d.rectangle([80, 520, 1120, 524], fill=(122, 147, 255)); d.text((82, 545), "aibriefing.io", font=sans, fill=(250, 248, 244))
    img.save(os.path.join(OUT, "og.png"), optimize=True)
    for s in (192, 512):
        ic = Image.new("RGB", (s, s), (20, 19, 17)); dd = ImageDraw.Draw(ic); f = art.font(art.SERIF, int(s * 0.5))
        dd.text((s * 0.5, s * 0.52), "AI", font=f, fill=(250, 248, 244), anchor="mm"); ic.save(os.path.join(OUT, f"icon-{s}.png"))

def generate_images(briefs, explainers):
    for d in ("img/stories", "img/briefs", "img/learn", "img/for"): ensure_dir(d)
    n = 0
    for b in briefs:
        p = os.path.join(OUT, "img", "briefs", f"{b['date']}.png")
        if not os.path.exists(p): art.brief_og(p, b.get("headline") or f"AI Briefing for {short_date(b['date'])}", fmt_date(b["date"]), len(b["items"])); n += 1
        for it in b["items"]:
            p = os.path.join(OUT, it["img"].lstrip("/"))
            if not os.path.exists(p): art.story_card(p, strip_md(it["title"]), it.get("tags", []), short_date(b["date"]), it["sources"][0]["name"] if it["sources"] else BRAND, it.get("stat")); n += 1
    for e in explainers:
        p = os.path.join(OUT, e["img"].lstrip("/"))
        if not os.path.exists(p): art.explainer_cover(p, e["title"], e.get("level", "all levels")); n += 1
    for k, name, who, _ in AUDIENCES:
        p = os.path.join(OUT, "img", "for", f"{k}.webp")
        if not os.path.exists(p): art.hub_cover(p, name, who, k); n += 1
    return n

def main():
    briefs = load_briefs(); explainers = load_explainers(); assert briefs
    for name in os.listdir(OUT):
        if name in ("_src", ".git", "README.md", ".gitignore", "img"): continue
        p = os.path.join(OUT, name); shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
    nimg = generate_images(briefs, explainers)
    topics = topic_pages(briefs)
    pages = {"/": home(briefs, explainers), "/brief/": brief_index(briefs)}
    for i, b in enumerate(briefs):
        pages[f"/brief/{b['date']}/"] = brief_page(b, prev_b=briefs[i + 1] if i + 1 < len(briefs) else None, next_b=briefs[i - 1] if i > 0 else None)
    pages["/for/"] = for_index()
    for k in AUD: pages[f"/for/{k}/"] = hub_page(k, briefs, explainers)
    pages["/trackers/"] = trackers_index()
    if "api-pricing" in TRACKERS: pages["/trackers/api-pricing/"] = tracker_pricing(TRACKERS["api-pricing"])
    if "models" in TRACKERS: pages["/trackers/models/"] = tracker_models(TRACKERS["models"])
    pages.update(topics)
    pages["/learn/"] = learn_index(explainers)
    for e in explainers: pages[f"/learn/{e['slug']}/"] = explainer_page(e, explainers)
    pages.update(glossary_pages())
    pages["/newsletter/"] = newsletter_page(); pages["/newsletter/thanks/"] = thanks_page(); pages["/search/"] = search_page()
    pages["/about/"] = static_page("/about/", "About", "What AI Briefing is, how the daily brief is produced and checked, and what we don't do.", "About AI Briefing", ABOUT)
    pages["/privacy/"] = static_page("/privacy/", "Privacy", "AI Briefing's privacy policy: cookie-free analytics, newsletter email handling, no data sales.", "Privacy policy", PRIVACY)
    for path, h in pages.items():
        assert "{{" not in h, path; write(path.lstrip("/") + "index.html", h)
    write("404.html", layout(title="Page not found | AI Briefing", desc="That page does not exist.", path="/404.html", body='<div class="hero"><h1>Not found</h1><p class="lede">That page moved or never existed. Try <a href="/brief/">the daily brief</a>, <a href="/search/">search</a>, or <a href="/">the home page</a>.</p></div>', noindex=True))
    write("assets/site.css", CSS); write("assets/site.js", JS); write("sw.js", SW); write("manifest.webmanifest", jd(MANIFEST))
    write("feed.xml", feed(briefs))
    idx = [{"t": strip_md(it["title"]), "s": strip_md(it["summary"]), "u": f"/brief/{b['date']}/#{it['id']}", "k": short_date(b["date"])} for b in briefs for it in b["items"]]
    idx += [{"t": e["title"], "s": e["summary"], "u": f"/learn/{e['slug']}/", "k": "Explainer"} for e in explainers]
    idx += [{"t": t["term"], "s": t["short"], "u": f"/glossary/{slugify(t['term'])}/", "k": "Glossary"} for t in GLOSSARY]
    write("search.json", jd(idx))
    noindex = {"/newsletter/thanks/", "/search/"}
    def lastmod(path):
        m = re.match(r"/brief/(\d{4}-\d{2}-\d{2})/", path)
        if m: return m.group(1)
        if path.startswith("/trackers/") and len(path) > 10: return TRACKERS.get(path.strip("/").split("/")[1], {}).get("updated", TODAY)
        return TODAY
    def prio(path):
        if path == "/": return "1.0"
        if path.startswith("/trackers/") or path.startswith("/for/"): return "0.9"
        if path.startswith("/brief/") and len(path) > 7: return "0.8"
        if path.startswith("/learn/") or path.startswith("/topics/"): return "0.7"
        if path.startswith("/glossary/") and len(path) > 10: return "0.4"
        return "0.6"
    def img_for(path):
        m = re.match(r"/brief/(\d{4}-\d{2}-\d{2})/", path)
        return f'<image:image><image:loc>{ROOT}/img/briefs/{m.group(1)}.png</image:loc></image:image>' if m else ""
    urls = "".join(f"<url><loc>{ROOT}{p}</loc><lastmod>{lastmod(p)}</lastmod><priority>{prio(p)}</priority>{img_for(p)}</url>" for p in pages if p not in noindex)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">{urls}</urlset>')
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /search/\nSitemap: {ROOT}/sitemap.xml\n")
    write(".htaccess", HTACCESS); write("favicon.svg", FAVICON)
    if CFG.get("indexnow_key"): write(CFG["indexnow_key"] + ".txt", CFG["indexnow_key"])
    og_image()
    print(f"built {len(pages)} pages, {nimg} new images → {OUT}")

if __name__ == "__main__":
    main()
