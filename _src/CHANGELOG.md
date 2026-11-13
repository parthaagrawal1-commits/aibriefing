# Changelog

## 2026-11-09
- Companies index: /companies/ and /companies/<vendor>/ built automatically from the vendor tag vocabulary, each page assembling dedicated articles, brief-item timeline, current API price rows and model releases for that vendor. Linked from footer, mobile menu, sub-nav and the home Trackers band. Structured data: CollectionPage with `about` Organization.
- Pricing tracker: all OpenAI rows now read from vendor model pages (primary); added GPT-6.1 Sol/Terra, GPT-6 Sol/Luna, GPT-6 Cyber, Claude Mythos 5.1, Inkling 2 Small; noted GPT-5.6 Sol promo end (Nov 30).

## 2026-11-10
- Section pages: new "Key numbers" module. Models and Tools pull live figures from the pricing and models trackers (cheapest frontier-class output, cheapest tracked output, latest release); every section fills remaining slots with the `stat` of its latest articles, each linking to the story. No data duplication; renders from existing JSON.
- Pricing tracker: added Claude Fable 5.2 / Mythos 5.2 ($8 / $40), Meta Muse Ember, Meituan LongCat-2.5; Anthropic and Google rows re-verified against vendor pages; Flash promo end dates noted.
- New explainer: what-is-inference-and-why-it-costs-so-much. Glossary +5 (prefill and decode, confidential computing, world action model, LLMjacking, cost per task). Pricing explainer refreshed for the Fable 5.2 price.

## 2026-11-11
- Explainers and articles now auto-link the first mention of each glossary term (dotted underline, `a.gl`) to its /glossary/ page; headings, existing links, code and bold text are skipped, generic words (API, training, compute, prompt) are excluded, max 12 links per page. Implemented in `autolink_glossary()` in build.py; no data changes required.
- Pricing tracker: added Gemini 4 Carbon ($2 / $10 until Nov 30, then $4 / $20, primary source); Anthropic and OpenAI rows re-verified against vendor pricing pages. Models tracker: Gemini 4 Carbon general availability (Nov 10).
- New explainer: ai-incident-response-plan. Glossary +4 (formal verification, sub-processor, lock-up period, physics engine). Pricing explainer updated for the Carbon December 1 step-up.

## 2026-11-12
- Weekly roundup pages: /week/ index and /week/YYYY-WW/ per ISO week, built by `week_pages()` in build.py from existing briefs, articles and the models tracker (day-by-day story tiles linking to dedicated articles where they exist, articles grouped by section, model releases that week, CollectionPage structured data with hasPart). Linked from the home "Earlier this week" band and the brief archive; included in the sitemap at 0.7.
- Pricing tracker: Inkling 2 Small upgraded to primary (Tinker docs, $0.30 / $1.00, 256K); added GPT-6 Rosalind ($15 / $75, primary) and Gemini Decision 1 ($0.10 input, no output charge); Anthropic, OpenAI, Meta and two Google rows re-verified. Models tracker: Gemini Decision 1 (Nov 11).
- New explainer: what-are-non-human-identities. Glossary +5 (decision model, spend cap, frontier AI framework, adjusted operating loss, sandbox escape). CISO agent checklist updated with the Railway $740K figure.

## 2026-11-13
- Email edition of every brief at /brief/YYYY-MM-DD/email/: a self-contained, table-based HTML document with inline CSS, preheader text, absolute links and no scripts or site chrome, built by `brief_email_page()` in build.py for pasting into any newsletter tool; noindex with canonical to the web brief. Linked from the brief toolbar ("Email version"). No data changes required.
- Pricing tracker: added Gemini 4 Hydrogen ($1.50 / $7.50 flat across 1M, primary) and GPT-6 Astra for Law (promo through Dec 31); Anthropic and OpenAI rows re-verified against vendor pricing pages; 3.8 Flash note now points to Hydrogen as its replacement. Models tracker: Gemini 4 Hydrogen (Nov 12); Inkling 2 Small row notes the Nov 12 weights release.
- New explainer: open-source-ai-licenses-explained. Glossary +5 (NVFP4, expert parallelism, thinking level, public nuisance (AI litigation), webshell). Open-weights explainer refreshed for Inkling 2 Small and LongCat-2.5 and linked to the licences explainer.
