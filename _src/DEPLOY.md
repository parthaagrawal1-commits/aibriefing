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
