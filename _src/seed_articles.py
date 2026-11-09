"""Launch articles for the beat sections. Re-run safe."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "data", "articles"); os.makedirs(D, exist_ok=True)
DATE = "2026-11-08"
A = [
{
 "slug": "gpt-6-cyber-critical-what-defenders-should-do", "section": "security", "published": DATE,
 "title": "OpenAI's GPT-6 Cyber is rated 'Critical'. Here is what that means for defenders",
 "dek": "The first model OpenAI has put in its highest cyber-capability tier is gated to vetted customers. The capability itself is not gated anywhere.",
 "stat": "81+", "tags": ["security", "models", "OpenAI"],
 "sources": [{"name": "Fortune", "url": "https://fortune.com/2026/11/05/openai-debuts-new-cybersecurity-focused-ai-model-amid-growing-alarm-about-ai-driven-cyber-attacks/"}, {"name": "CyberScoop", "url": "https://cyberscoop.com/openai-gpt-6-cyber-security-model/"}],
 "why": {"security": "Assume adversaries have equivalent tooling within months. Measure and shrink your time-to-patch; that is now the control that matters.", "executives": "Ask for one number from your security lead: median days from public disclosure to fix. Fund whatever shortens it.", "developers": "Expect more automated vulnerability reports against your dependencies. Pin versions and budget upgrade time every sprint."},
 "body": """
On November 5 OpenAI released GPT-6 Cyber, a version of its GPT-6 Astra flagship tuned for authorised security work: finding vulnerabilities, developing exploits to prove them, and penetration-testing web applications. The company classified it as "Critical" under its Preparedness Framework, the first time it has used the top tier for cyber capability. Its predecessor, GPT-5.6 Cyber, was rated "High".

## What is actually new

Three things, according to the launch coverage:

- **Capability.** OpenAI says the model outperforms GPT-6 Astra on its internal exploit benchmarks and found more than 80 previously unknown vulnerabilities in Firefox during testing. The company has not published independent evaluations.
- **Scope adherence.** OpenAI says the model stayed within its authorised target scope in more than 99% of test runs. That matters because an offensive model that wanders off-scope is a liability for the customer running it, not just the target.
- **Access.** The model is available only to approved customers in OpenAI's Daybreak Red programme, initially a small group, widening over the following weeks. There is no public API tier.

## Why gating does not settle it

Gated release reduces casual misuse; it does not change the underlying trend. Open-weight models are a generation behind and improving, and the same month saw reports of hundreds of AI-driven hacking toolkits exposed on the open web. The practical assumption for a defender is that vulnerability discovery is becoming cheap and fast for everyone, approved or not.

That shifts the economics. Historically, the gap between a bug's existence and its discovery protected most organisations most of the time. When discovery is automated, the only gap that protects you is the one between public disclosure and your patch.

## What to do this quarter

1. **Measure time-to-patch** for internet-facing systems and critical dependencies. If you cannot produce the number, that is the first finding.
2. **Automate dependency updates** with tests good enough to merge them without a human reading every diff.
3. **Reduce attack surface** rather than racing on patches: fewer exposed services, fewer stale integrations, fewer forgotten subdomains.
4. **Use the same tools defensively.** Vetted access to offensive models is available to defenders; run them against your own estate before someone else does.
5. **Brief the board in one sentence:** vulnerability discovery is now automated; our defence is patch speed and surface reduction, and here is our number.

GPT-6 Cyber is one data point in a year that has produced four OpenAI security models and similar efforts from rivals. The direction is not in doubt; the question is whether your patch cadence is.
"""
},
{
 "slug": "biobasicsbench-ai-agents-wet-lab", "section": "health", "published": DATE,
 "title": "OpenAI's BioBasicsBench: AI agents score 66.7% on routine lab work, and the failures are the story",
 "dek": "A new 100-task benchmark tests whether AI can read gels, plates and microscopy like a bench scientist. The headline score is decent; the error cases show why nobody should hand it a pipette yet.",
 "stat": "66.7%", "tags": ["health", "research", "OpenAI"],
 "sources": [{"name": "R&D World", "url": "https://www.rdworldonline.com/openai-unveils-biobasicsbench-a-benchmark-to-gauge-how-well-ai-agents-read-raw-experimental-data-across-100-routine-wet-lab-tasks/"}, {"name": "Unite.AI", "url": "https://www.unite.ai/?p=507300"}],
 "why": {"ml": "A benchmark built from raw bench evidence, not publication figures, with partial-credit rubrics. Worth reading for the rubric design alone.", "executives": "If a vendor pitches an autonomous lab agent, ask what it scores on evidence like this and how it handles 'insufficient evidence' cases.", "beginners": "AI can now read many lab results reasonably well, but it still makes confident mistakes a trained technician would catch."},
 "body": """
On November 6 OpenAI published BioBasicsBench, a benchmark built with the enzyme-design company Ligo Biosciences to test one narrow, important skill: can an AI agent look at the raw output of an everyday laboratory experiment and draw the right conclusion?

## What it tests

The benchmark contains 100 tasks across five areas of routine wet-lab work: protein methods, imaging and cytometry, quantification and assays, nucleic acid methods, and molecular cloning. Instead of the clean figures that appear in published papers, the inputs are the messy artefacts a technician actually sees: gel images, colony plates, microscope fields, instrument readouts, including failed and ambiguous experiments.

Agents must return a structured conclusion, measurement or recommendation. A rubric awards partial credit for the numerical result, the reasoning, and, notably, for recognising when the evidence is not sufficient to support a conclusion at all.

## The scores

OpenAI reports that GPT-6 Astra, at its highest reasoning setting, earned 66.7% of available credit, versus 43.8% for the earlier GPT-5.6 Sol. The post compares only OpenAI models and gives no human baseline, so the number says how far OpenAI's own models have moved, not how they compare with a trained technician.

## The failures matter more

OpenAI's own write-up is unusually frank about error cases, and they are the useful part. In one colony-counting task the model merged neighbouring colonies, missed visible ones and marked empty agar, overcounting by about 12%, which would inflate a downstream efficiency estimate by the same amount. The pattern across failures is a correct observation paired with a wrong call. OpenAI's own summary: higher scores do not yet mean reliable judgement in the lab.

## What this means for healthcare and life sciences

- **For lab teams:** these agents are approaching usefulness as a second reader that flags anomalies, not as a decision-maker. Deploy them where a wrong call is cheap and visible.
- **For regulated environments:** a model that can say "insufficient evidence" is the behaviour regulators will want to see documented. Ask vendors for their rate of appropriate abstention, not just accuracy.
- **For the broader AI-for-science push:** benchmarks built from raw evidence rather than curated figures are the right direction. Expect rivals to publish comparable tests, and expect the gap between reading data and making sound decisions to be the thing that closes last.
"""
},
{
 "slug": "openai-anthropic-repriced-same-week", "section": "markets", "published": DATE,
 "title": "OpenAI at $1.25T, Anthropic talked down to $1.2–1.3T: the week AI's two giants got repriced",
 "dek": "Both labs are still worth more than almost any company on earth. What changed is that investors started setting the price instead of accepting it.",
 "stat": "$1.25T", "tags": ["markets", "funding", "IPO", "OpenAI", "Anthropic"],
 "sources": [{"name": "TechCrunch", "url": "https://techcrunch.com/2026/11/06/openai-reportedly-raises-an-additional-11-billion-at-a-1-25-trillion-valuation/"}, {"name": "The Information", "url": "https://www.theinformation.com/"}, {"name": "TechCrunch (Ramp data)", "url": "https://techcrunch.com/2026/11/06/ramp-data-shows-ai-spending-stalling-just-as-anthropic-nears-its-ipo/"}],
 "why": {"finance": "Private marks across the sector key off these two. A clearing price below the October whisper numbers resets every secondary and every late-stage round.", "executives": "Your vendors' cost of capital just went up. Expect firmer pricing, longer contracts and more pressure to expand usage.", "beginners": "The two best-known AI companies are still enormously valuable, but for the first time investors are negotiating the price down rather than bidding it up."},
 "body": """
Two numbers landed within days of each other. On November 6 Reuters reported, and TechCrunch relayed, that OpenAI had closed about $11 billion as the first part of a larger round, at a valuation of roughly $1.25 trillion, with SoftBank and MGX among the participants. The company had reportedly been seeking $1.5 trillion. The same week, reports from Bloomberg and The Information described investors preparing for Anthropic's IPO roadshow, due to start the week of November 9, discussing a valuation around $1.2–1.3 trillion, below figures floated in October, with a smaller raise or a short delay both on the table if AI stocks stay volatile.

## What is driving the discount

Three things converged.

**Public-market volatility.** AI-related stocks had a rough week, and public comparables are what IPO investors price against. A private round closed in a drawdown prices the drawdown in.

**Capital intensity in plain view.** Anthropic's S-1, filed October 26, put first-half 2026 revenue at roughly $16.3 billion alongside a very large net loss and multi-year compute commitments, including a reported ~$19 billion, 20-year data-centre lease. OpenAI has made comparable infrastructure pledges, including a November 5 commitment to pay the full cost of power and grid upgrades for its sites. Investors can now see the bills, not just the growth.

**Adoption data.** Ramp's spending index, reported by TechCrunch the same day as the OpenAI round, shows the share of US businesses paying for AI tools flattening after two years of growth. Plateauing adoption is survivable; plateauing adoption during an IPO roadshow is awkward.

## What has not changed

Revenue growth at both companies remains extraordinary by any historical standard, and both rounds are still being filled. A $1.25 trillion valuation is a discount to a wish, not a crisis. The IPO itself is the first chance for the public market to price a frontier lab directly, and every private AI valuation on the street will be re-marked against where it trades in the first month.

## What to watch

- The amended S-1 with a price range: that is the moment the roadshow is real.
- First-month trading in ANT, and whether OpenAI's remaining round closes at the same $1.25 trillion or lower.
- Enterprise pricing moves from both labs over the next two quarters; pressure on valuation tends to show up as pressure on list prices.
"""
},
{
 "slug": "physicl-10m-robot-simulation-humanoid-funding", "section": "robotics", "published": DATE,
 "title": "Physicl raises $10M to make simulations real enough to train robots, as humanoid funding hits a record",
 "dek": "The bottleneck in robotics is no longer the model or the hardware. It is believable practice environments, and a new wave of startups is selling exactly that.",
 "stat": "$10M", "tags": ["robotics", "funding"],
 "sources": [{"name": "TechCrunch", "url": "https://techcrunch.com/2026/11/06/physicl-raises-10m-to-make-the-digital-world-real-enough-for-robots/"}, {"name": "Dealroom", "url": "https://dealroom.co/charts/humanoid-robotics"}, {"name": "Robotics 24/7", "url": "https://www.robotics247.com/topic/tag/Humanoid"}],
 "why": {"ml": "Sim-to-real is where robotics compute is going. Expect the same data-engine dynamics that drove LLMs: whoever owns the richest environments trains the best policies.", "finance": "Humanoid funding is at an all-time high and increasingly concentrated in China. The picks-and-shovels layer (simulation, data, safety) is where Western capital is finding entry points.", "executives": "If you run warehouses or plants, humanoid pilots are now a procurement question, not a research one. Start with a narrow task and a safety partner."},
 "body": """
Physicl, a startup building high-fidelity simulated environments for training robots, has raised $10 million, TechCrunch reported on November 6. The pitch is simple: robots learn by practising, practising in the physical world is slow and expensive, and today's simulators are not realistic enough for skills learned there to survive contact with reality. Make the digital world "real enough" and you can train millions of hours overnight.

## Why simulation is the bottleneck

Language models had the internet to learn from. Robots have nothing comparable: there is no trillion-token archive of a hand picking up a cup. The industry's answer is to manufacture experience, either by teleoperating real robots and recording them, or by simulating. Simulation scales, but the gap between simulated and real physics (friction, deformable objects, lighting, sensor noise) has historically wasted much of what was learned. Closing that gap is now a product category, and Physicl is one of several companies selling into it alongside the simulation stacks offered by the large chip and cloud vendors.

## The money around it

The context is a funding boom. Dealroom's tracker put venture investment in humanoid robotics at $8.7 billion for 2026 by late July, already an all-time high, and noted that China accounts for roughly two-thirds of that total, with the US share down to about 15%. Earlier in the year Apptronik's $520 million round pushed its total raised to nearly $1 billion.

Deployments are following the money, cautiously. In October, agricultural-equipment maker AGCO announced a pilot of Agility Robotics' Digit humanoid at its Hesston, Kansas plant, and Agility signed a safety partnership covering its newest robot. The pattern across announcements is narrow tasks, defined zones and a safety vendor in the loop.

## What to watch

- **Sim-to-real benchmarks.** Expect simulation vendors to publish transfer rates (how much a sim-trained skill degrades in the real world) the way model labs publish benchmarks.
- **Who owns the environments.** The large platforms are bundling simulation with chips and cloud; independents like Physicl bet that fidelity wins over bundling.
- **The China gap.** Two-thirds of humanoid capital is now there. Western policy on robotics exports and supply chains is the next place this shows up.
"""
},
{
 "slug": "data-center-politics-after-the-midterms", "section": "policy", "published": DATE,
 "title": "After the midterms, the data-center backlash has votes behind it",
 "dek": "Local measures against new AI data centers won across several states this week. The industry's response, from paying for its own power to warning of slower expansion, tells you how seriously it is taking the result.",
 "stat": None, "tags": ["policy", "infrastructure"],
 "sources": [{"name": "TechCrunch", "url": "https://techcrunch.com/2026/11/07/after-the-midterms-things-are-looking-rocky-for-elon-musk-and-data-centers/"}, {"name": "TechCrunch (Crusoe/Google)", "url": "https://techcrunch.com/2026/11/06/crusoe-sells-troubled-wyoming-data-center-project-to-google/"}],
 "why": {"executives": "Compute availability in 2027–28 is now a political variable. Lock in capacity commitments and diversify regions.", "finance": "Permitting and power risk now attach to every data-center REIT, neocloud and AI-infrastructure credit. Price the delay, not just the demand.", "beginners": "The buildings that run AI need enormous amounts of electricity and water, and the people who live near them are starting to vote against them."},
 "body": """
The November 3 midterms were not an AI election, but AI infrastructure was on the ballot in dozens of places, directly through local measures and indirectly through candidates who campaigned against new data centers. TechCrunch's post-election analysis describes a rougher road for several planned projects, Elon Musk's among them, and Meta has publicly warned that the backlash could slow AI expansion.

## What voters objected to

The complaints are consistent across regions: electricity demand that raises local rates or delays other grid connections, water consumption, noise, tax abatements for facilities that employ few people, and non-disclosure agreements that kept communities from knowing what was being built until it was approved.

## How the industry is responding

The responses arrived fast, which is itself a signal.

- **OpenAI** pledged on November 5 to pay the full cost of power and grid upgrades for its sites and to stop requiring non-disclosure agreements in negotiations with local communities.
- **Google** took over a struggling data-center project in Wyoming from the developer Crusoe, a pattern in which hyperscalers absorb projects that smaller builders cannot finance or permit.
- **Meta** warned investors that community opposition could become a constraint on capacity, language companies use when they expect analysts to ask about it.

## Why it matters beyond the US

The US is where the largest share of frontier compute is being built, and where local permitting is most fragmented. Delays here raise the value of capacity everywhere else, and shift some building toward jurisdictions with centralised approval. Expect more announcements of sites in the Gulf, parts of Europe with surplus power, and Asia, and more deals in which a hyperscaler buys a half-finished project rather than starting one.

## What to watch

1. State-level bills on data-center rate structures and water reporting in the 2027 sessions; several candidates ran on them.
2. Whether OpenAI's "pay our own way" terms become the template other builders are forced to match.
3. Capacity guidance in the next round of hyperscaler earnings: the first time "community opposition" appears as a named risk factor will move the infrastructure trade.
"""
},
{
 "slug": "gemini-4-argon-pricing-doubles-december-1", "section": "tools", "published": DATE,
 "title": "Gemini 4 Argon's launch price ends November 30. Plan for $4 / $20",
 "dek": "Google's pricing page now carries an expiry date on its flagship's introductory rate, and the Flash tiers follow in January. Here is the math for anyone who built on launch pricing.",
 "stat": "Dec 1", "tags": ["pricing", "tools", "Google"],
 "sources": [{"name": "Google AI for Developers (pricing)", "url": "https://ai.google.dev/pricing"}],
 "why": {"developers": "Re-run your cost model today. If Argon was chosen on price, a mid-tier model from any vendor at $2–4 / $10–20 is now the comparison.", "finance": "Introductory API pricing with a published end date is becoming standard. Any AI cost forecast built on launch rates needs a vendor-pricing-change line.", "executives": "Build price-review dates into AI contracts. Vendors are using time-limited rates to win workloads and then stepping up."},
 "body": """
Google's official Gemini API pricing page, checked on November 8, lists Gemini 4 Argon at $2 per million input tokens and $10 per million output tokens through November 30, 2026, rising to $4 and $20 from December 1. Cached-input pricing doubles on the same schedule, from $0.10 to $0.20. The Flash tiers follow a month later: Gemini 3.8 Flash and 3.6 Flash are $0.75 / $3.75 through December 31 and $1.50 / $7.50 from January 1, 2027.

## What this costs you

Take a typical assistant workload: 2,000 input tokens and 400 output tokens per request, 2 million requests a month.

- At launch pricing: input $8,000 + output $8,000 = **$16,000 / month**.
- From December 1: **$32,000 / month**.

Caching and batch discounts still apply, and the ratio is the same either way: the bill doubles.

## How the new rate compares

At $4 / $20, Argon lands at the same list price as Anthropic's Claude Opus 5.5 and OpenAI's GPT-5.6 Sol, and remains well below the $10 / $50 of the top tiers (GPT-6 Astra, Claude Fable 5.1). Below it, Anthropic's Sonnet 5.5 at $2 / $10 becomes the cheapest current frontier-class list price once the Argon promotion ends. The full table is on the [pricing tracker](/trackers/api-pricing/).

## What to do before December 1

1. **Measure, do not assume.** Tokenisers differ; cost per completed task on each candidate model is the only number that matters.
2. **Route by difficulty.** Most traffic in most products is routine. Keep Argon for the hard cases and send the rest to a Flash-class model; the Flash promotion runs a month longer.
3. **Cache aggressively.** Stable prefixes (system prompts, documents) at the cached rate are 5% of input price. Reorder prompts so the stable part comes first.
4. **Check your contract.** Committed-use or enterprise pricing may not follow the public schedule. Ask.

## The wider pattern

Google is not alone. Anthropic launched Sonnet 5 at an introductory rate that reverted on a fixed date, and OpenAI has used promotional pricing on new tiers. Launch prices are now marketing, not cost; the nightly check of vendor pages that feeds our tracker exists because of exactly this.
"""
},
{
 "slug": "ramp-ai-spending-plateau-what-it-means", "section": "business", "published": DATE,
 "title": "Ramp's data says business AI spending has flattened. Here is how to read it",
 "dek": "A plateau in the share of companies paying for AI tools is not the end of adoption. It is the end of buying everything.",
 "stat": None, "tags": ["adoption", "business", "data"],
 "sources": [{"name": "TechCrunch", "url": "https://techcrunch.com/2026/11/06/ramp-data-shows-ai-spending-stalling-just-as-anthropic-nears-its-ipo/"}],
 "why": {"executives": "Boards will cite this. Have your own numbers ready: which AI tools you pay for, what each replaced or sped up, and what you cancelled.", "finance": "Breadth of adoption is flattening while depth (spend per adopter) is the open question. Model the two separately.", "beginners": "Companies tried a lot of AI tools over two years. Now they are keeping the ones that pay for themselves and dropping the rest."},
 "body": """
Ramp, the corporate card and bill-pay company, publishes an index built from what its customers actually pay for. TechCrunch reported on November 6 that the latest reading shows the share of US businesses paying for AI tools has flattened in recent months after two years of steady growth. The timing, days before Anthropic's IPO marketing begins, guaranteed attention.

## What the data measures, and what it does not

Ramp's index measures breadth: the fraction of businesses with at least one AI subscription or usage charge. It is a good proxy for "has tried AI," and that number saturating was always going to happen; most companies that were going to buy a ChatGPT or Claude seat have done so.

It does not measure depth: how much each adopter spends, how many seats, how much API usage. Breadth can flatten while depth rises, which is the pattern in most enterprise software categories after the trial phase. It also undercounts spend that flows through cloud bills (Azure, AWS, Google Cloud), where most API usage is invoiced.

## The pilot cull

What is almost certainly happening underneath is consolidation. Two years of experimentation produced, in many companies, five or six overlapping subscriptions and several pilots with no owner. Finance teams are now cancelling what did not produce measurable results and standardising on one or two platforms. That shows up as flat breadth and, often, higher spend per surviving vendor.

## Why it matters for the IPO

Investors underwriting Anthropic, and OpenAI's next round, are paying for growth that depends on enterprise expansion. Flat adoption breadth is not fatal to that story, but it moves the burden of proof to depth: usage per customer, net revenue retention and API growth, numbers the S-1 and the roadshow will be pushed to disclose.

## What to do with it

- **If you run a company:** make the consolidation deliberate. List every AI line item, assign an owner and an outcome, and cancel the rest. The survivors will get better terms if you consolidate volume.
- **If you sell AI software:** the land-grab phase is over. Expansion now comes from proving outcomes inside existing accounts, not from logos.
- **If you invest:** ask every AI company for net revenue retention. It is the number this data makes unavoidable.
"""
},
]
for a in A:
    a["body"] = a["body"].strip(); a.setdefault("updated", a["published"])
    json.dump(a, open(os.path.join(D, a["published"] + "-" + a["slug"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("seeded", len(A), "articles")
