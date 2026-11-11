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
