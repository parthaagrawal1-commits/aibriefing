# aibriefing.io — how it is built and deployed

- Source of truth: `_src/data/**` (JSON). Templates and logic: `_src/build.py`.
- Build: `cd _src && python3 build.py` → writes the finished site to the repo root.
- Deploy: push to `main`; Hostinger's GitHub App deploys the repo root into public_html. `.htaccess` blocks `/_src`, `/.git` and `README.md`.
- Validate before pushing: no `{{` in any index.html; every JSON-LD block parses; `feed.xml` and `sitemap.xml` parse as XML.

## Data schema

`data/briefs/YYYY-MM-DD.json`
```
{ "headline": "...", "intro": "...", "one_thing": "...",
  "items": [ { "title", "summary", "why": {"executives"|"finance"|"security"|"ml"|"developers"|"beginners": "..."},
               "source": {"name","url"} | "sources": [{"name","url"}], "tags": [] } ] }
```
`data/trackers/api-pricing.json` rows: vendor, model, input, output, cached, context, note, source, verified, confidence ("primary" = read from vendor page; "secondary" = cited source).
`data/trackers/models.json` rows: vendor, model, released, kind, context, note, source.
`data/explainers/<slug>.json`: title, summary, level, audiences[], published, updated, body (markdown subset: ##, ###, -, 1., **, *, `, [text](url)), faqs [[q,a]].
`data/glossary.json`: [{term, short, long, related[]}].
`data/config.json`: newsletter_form_html (paste the Brevo form), analytics_html (Cloudflare beacon), indexnow_key.

## Editorial rules
- Summaries in our own words, 2–3 sentences, never copied phrasing. Always link the original source.
- "Reportedly" for anything sourced to a single outlet's unnamed sources.
- Never invent prices, dates or figures. Trackers cite the page the number came from.

## v2 (visual edition) notes
- Graphics are generated automatically by `art.py` at build time: one 16:9 WebP per story (`/img/stories/<id>.webp`), one OG PNG per brief, covers for explainers and hubs. Never add photos. Existing images are kept; delete a file to regenerate it.
- Each item may set `"stat": "$11B"` to control the big figure on its graphic; otherwise it is extracted from the title/summary.
- Tags drive /topics/ threads, so use the canonical vocabulary: funding, IPO, M&A, models, pricing, security, policy, regulation, infrastructure, adoption, data, agents, consumer, geopolitics, research, plus vendor names exactly as: OpenAI, Anthropic, Google, Nvidia, Meta, Microsoft, Amazon, Apple, xAI, Mistral, DeepSeek. First non-vendor tag sets the graphic's colour.
- Client features live in build.py (CSS/JS strings): lens selector, Listen (speech synthesis), reading progress, share, theme toggle, search (/search.json), sticky subscribe, PWA (sw.js, manifest).

## v3: sections and dedicated articles
- Sections (beats): security, health, markets, robotics, models, policy, business, tools. Hub at `/<section>/`, feed at `/<section>/feed.xml`.
- Articles live in `data/articles/YYYY-MM-DD-<slug>.json`:
  `{ "slug", "section", "published", "updated", "title", "dek", "stat" (optional), "tags": [], "developing": false,
     "sources": [{"name","url"}], "why": {audience: line} (optional), "body": markdown }`
  Body 300–700 words, own words, with ## sections; always cite 1–3 sources. URL becomes `/<section>/<slug>/`. Cover graphic is generated.
- A brief item may carry `"article": "<slug>"` to link "Full story →" to a dedicated article. Do this whenever an article exists for the item.
- Graphic variants are chosen automatically: M&A → split panel; pricing/funding/adoption/data/markets with a stat → chart; stat → big number; otherwise headline-led.
- Lens: first-visit prompt; stored in localStorage; `[data-forlens]` blocks on the home page show for the chosen lens.
