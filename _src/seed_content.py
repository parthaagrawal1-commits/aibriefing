"""One-time seed of explainers and glossary. Re-run safe: overwrites the same files."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "data", "explainers"); os.makedirs(EX, exist_ok=True)
D = "2026-11-08"

explainers = [
{
 "slug": "what-is-an-ai-agent",
 "title": "What is an AI agent? A plain-English explanation",
 "summary": "An agent is AI that takes actions, not just answers. Here is what that means, why every company is suddenly announcing one, and what can go wrong.",
 "level": "beginner", "audiences": ["beginners", "executives", "developers"], "published": D, "updated": D,
 "body": """
A chatbot answers a question. An **agent** is given a goal, works out the steps, and carries them out using tools: a browser, a calendar, a payment system, your company's internal software. "Book me a flight to Austin under $400 next Tuesday" is an agent task. "What's the capital of Texas?" is not.

## What is actually inside an agent

Under the hood an agent is a language model running in a loop. On each turn it looks at the goal, what it has done so far and what the tools returned, then decides the next action. The loop ends when the model decides the goal is met or it gives up. Three things make this different from chat:

- **Tools.** The model can call functions: search, read a file, send an email, run code. Each call returns a result the model reads before deciding what to do next.
- **Memory.** The agent keeps a running record of the task so it can recover from a failed step instead of starting over.
- **Autonomy.** Nobody approves each step. That is the point, and it is also the risk.

## Why everyone is announcing agents now

Models got reliable enough at multi-step reasoning that the loop stops breaking after two or three steps. Vendors also discovered that an agent that completes a task is worth far more than a chat answer, so pricing is moving from "per message" to "per task completed". Airbnb, Meta, Amazon and the big labs all shipped or announced consumer agents in 2026.

## What goes wrong

- **Prompt injection.** An agent that reads web pages or emails can be told, by the content it reads, to do something its owner never asked for. See [prompt injection](/learn/prompt-injection-explained/).
- **Over-permissioned tools.** An agent with a company credit card and no spending limit is exactly what it sounds like.
- **Silent failure.** Agents are confident. They will report success on a task they half-finished unless you verify the result.

## What to ask before you deploy one

1. What can it *do*, not just see? List every tool and what the worst misuse of each would cost.
2. Where does it read untrusted content, and is there a human check before it acts on it?
3. How do you know a task actually succeeded?

If you cannot answer all three, run it in a mode where a person approves each action until you can.
""",
 "faqs": [
  ["Is ChatGPT an agent?", "In its basic chat mode, no. Modes that browse, run code or complete tasks on websites on your behalf are agentic features built on the same model."],
  ["Do agents need a special model?", "No. Any capable language model can run an agent loop; the difference is the surrounding software: tools, memory, permissions and verification."],
  ["Are agents safe to give access to my accounts?", "Only with the narrowest permissions that still let the task succeed, and a human approval step for anything irreversible such as payments or sending messages."]
 ]
},
{
 "slug": "llm-api-pricing-explained",
 "title": "LLM API pricing explained: tokens, caching, batch and the cliffs",
 "summary": "How per-million-token pricing works, why output costs more, and the four levers that cut a bill by half or more.",
 "level": "intermediate", "audiences": ["developers", "finance", "executives"], "published": D, "updated": D,
 "body": """
Every major model vendor bills the same way: a price per million **tokens** sent in (input) and a separate, higher price per million tokens the model writes back (output). A token is roughly three-quarters of an English word, so a million tokens is about 750,000 words.

## The basic formula

Cost per request = (input tokens × input price + output tokens × output price) ÷ 1,000,000.

A support bot that reads a 2,000-token conversation and writes a 300-token reply on a $2 / $10 model costs about $0.007 per reply. At 100,000 replies a month that is $700. The same bot on a $10 / $50 flagship costs $3,500. The model choice is the biggest lever you have.

## Why output costs 5x input

Reading a prompt is processed in parallel; writing a reply happens one token at a time and ties up the hardware for the whole generation. Vendors price output at roughly five times input to reflect that. Practical consequence: asking for shorter answers saves more money than trimming prompts.

## The four discounts

- **Prompt caching.** If many requests share the same long prefix (a system prompt, a policy document, a codebase), vendors charge a fraction of the input price for the repeated part, typically 2.5% to 10%. Anthropic charges extra to write the cache the first time; OpenAI charges 1.25x input for cache writes on its flagship. Structure prompts so the stable part comes first.
- **Batch.** Jobs that can wait minutes or hours get about 50% off at all three big vendors. Nightly enrichment, classification backfills and evaluation runs belong here.
- **Smaller tiers.** Flash, Haiku, mini and nano tiers are 5x to 50x cheaper than flagships and handle most classification, extraction and routing tasks well. Route by task difficulty.
- **Shorter outputs.** Cap max tokens and ask for structured output. Verbose prose is the most expensive thing a model produces.

## The cliffs

Some models charge more for long requests, and the surcharge applies to the *whole* request: OpenAI's GPT-6 Astra doubles input above 272K tokens, Gemini Pro steps up above 200K, Claude Haiku 5.5 steps up above 100K. Introductory pricing also expires on published dates; Google's Gemini 4 Argon doubles on December 1, 2026. Check the [pricing tracker](/trackers/api-pricing/) before you forecast.

## Cost per task, not cost per token

Tokenizers differ between models and even between generations of the same family, so the same text can be 30% more tokens on one model than another. Measure what a finished task costs end to end on each candidate model; the per-token rate card alone will mislead you.
""",
 "faqs": [
  ["How many tokens is a page of text?", "Roughly 500 to 700 tokens for a typical page of English prose. Code and non-English text usually tokenise less efficiently."],
  ["Do I pay for the model's hidden reasoning?", "On reasoning models, yes. Thinking or reasoning tokens are billed as output on OpenAI, Google and Anthropic models that expose them."],
  ["Is a subscription like ChatGPT Plus the same as API pricing?", "No. Subscriptions cover the chat app for a person; the API is billed per token for software you build and has no monthly fee."]
 ]
},
{
 "slug": "what-is-a-context-window",
 "title": "What is a context window, and does a million tokens matter?",
 "summary": "The context window is how much a model can read at once. Why it grew from 4K to 1M tokens, what it costs, and when it actually helps.",
 "level": "beginner", "audiences": ["beginners", "developers", "ml"], "published": D, "updated": D,
 "body": """
A model's **context window** is the maximum amount of text it can consider in a single request: your prompt, any documents you include, the conversation so far, and the answer it writes. Everything outside the window does not exist to the model.

## How big is big

In 2023 a typical window was 4,000 to 8,000 tokens, roughly ten pages. Today the flagship tiers from OpenAI, Anthropic and Google all advertise around a million tokens, which is roughly 1,500 pages, or a mid-sized codebase, or every email you sent last year.

## What a bigger window buys you

- **Whole-document questions.** Drop in a 300-page contract and ask what changed from the last version, with no retrieval pipeline.
- **Long conversations.** An agent can keep its full working history instead of summarising and forgetting.
- **Many examples.** You can show the model hundreds of worked examples in the prompt instead of fine-tuning.

## What it costs

Every token in the window is billed as input on every request. A conversation that carries a 500,000-token document costs 500,000 input tokens each turn unless you use prompt caching, and some vendors charge a higher rate above a threshold (see the [pricing tracker](/trackers/api-pricing/)). Latency also rises with context length.

## Where it still breaks

Models do not read a million tokens with uniform attention. Independent tests repeatedly show accuracy drops for facts buried in the middle of very long inputs, and reasoning across many distant parts of a document is harder than reading any one of them. For large, frequently queried corpora, [retrieval (RAG)](/learn/rag-explained-for-business/) that selects the relevant pieces is still cheaper and often more accurate than stuffing the window.

## Rule of thumb

Use the big window when the whole document matters and you ask few questions of it. Use retrieval when the corpus is large, changes often, or you will query it thousands of times.
""",
 "faqs": [
  ["Does a bigger context window make a model smarter?", "No. It lets the model see more at once. Reasoning quality is a separate property, and it tends to degrade somewhat as inputs get very long."],
  ["Does the context window include the model's answer?", "Yes. Input plus output must fit, and most models also cap output separately, commonly at 64K to 128K tokens."],
  ["Can I exceed the context window?", "No. The request is rejected or truncated. Summarise, chunk, or retrieve the relevant parts instead."]
 ]
},
{
 "slug": "rag-explained-for-business",
 "title": "RAG explained for business leaders",
 "summary": "Retrieval-augmented generation is how companies make a general model answer from their own documents without retraining it. What it is, what it costs, and where projects fail.",
 "level": "beginner", "audiences": ["executives", "beginners", "finance"], "published": D, "updated": D,
 "body": """
A language model knows what was on the internet when it was trained. It does not know your contracts, your product manuals or last quarter's support tickets. **Retrieval-augmented generation (RAG)** fixes that without retraining: when a question comes in, software first *retrieves* the most relevant passages from your documents, then hands those passages to the model along with the question, and the model *generates* an answer grounded in them.

## Why it won

- **No training.** Your documents stay in a database you control. Update a policy and the next answer reflects it immediately.
- **Citations.** Because the answer is built from retrieved passages, the system can show which document it came from. That is what makes it auditable.
- **Cost.** Only the relevant few pages go to the model per question, not the whole archive.

## What it costs to build

A pilot over a few thousand documents is weeks, not months, and the running cost is dominated by model calls, typically a fraction of a cent to a few cents per question. The expensive part is not the AI; it is cleaning and permissioning the documents. If your SharePoint is a mess, RAG will answer confidently from the mess.

## Where projects fail

1. **Bad retrieval.** If the right passage is not found, the model answers from general knowledge and sounds just as confident. Most "hallucination" complaints in RAG systems are retrieval failures.
2. **Permissions.** The system must only retrieve what the asking user is allowed to see. Many pilots skip this and cannot ship.
3. **Stale or duplicate documents.** Three versions of the same policy produce three different answers.
4. **No evaluation.** Teams ship without a test set of real questions and known-good answers, so nobody can say whether a change made it better.

## Questions to ask a vendor

- Which document did this answer come from, and can a user click through to it?
- How do you enforce our existing access controls?
- What is your measured accuracy on *our* questions, not a demo set?

RAG is a mature pattern, and in 2026 it competes with very large context windows for small corpora; see [context windows](/learn/what-is-a-context-window/). For anything larger than a few hundred documents that changes regularly, retrieval is still the default.
""",
 "faqs": [
  ["Is RAG the same as fine-tuning?", "No. Fine-tuning changes the model's weights with your data; RAG leaves the model alone and supplies your data at question time. RAG is cheaper, faster to update and easier to audit."],
  ["Does RAG stop hallucinations?", "It reduces them when retrieval works and the model is instructed to answer only from the supplied passages. It does not eliminate them."],
  ["Do we need a special database?", "Usually a vector database or a search engine with vector support. Many existing platforms now include one."]
 ]
},
{
 "slug": "prompt-injection-explained",
 "title": "Prompt injection explained: the attack every AI agent is exposed to",
 "summary": "Why text that an AI reads can hijack what it does, why there is no complete fix, and the controls that actually reduce the damage.",
 "level": "intermediate", "audiences": ["security", "developers", "executives"], "published": D, "updated": D,
 "body": """
Language models cannot reliably tell the difference between instructions from their operator and instructions hidden in the content they are asked to process. **Prompt injection** exploits that: an attacker places text in a web page, email, document or calendar invite that says, in effect, "ignore your previous instructions and do X". When an AI system reads it, it may comply.

## Why it matters more in 2026

A chatbot that gets injected says something wrong. An **agent** that gets injected *does* something wrong: forwards your inbox, approves a refund, posts to a channel, edits a record. As agents gain tools and permissions, injection moves from embarrassing to expensive. It is the top item on most AI security guidance for a reason.

## What it looks like

- A support agent summarises a customer email that contains hidden text instructing it to escalate the ticket and issue a credit.
- A browsing agent lands on a page whose invisible footer tells it to send the user's session data to another site.
- A coding agent reads a repository README that tells it to add a dependency from an attacker's registry.

## Why there is no clean fix

The instruction channel and the data channel are the same channel: text. Vendors train models to resist, and the best models now refuse obvious attempts, but resistance is probabilistic, not a boundary. Treat any model that reads untrusted content as partially under the attacker's control.

## Controls that work

1. **Least privilege for tools.** The agent gets the narrowest permissions that still complete the task, with hard limits (spend caps, allow-listed recipients, read-only where possible).
2. **Human approval for irreversible actions.** Sending, paying, deleting and publishing require a person to confirm, and the confirmation shows exactly what will happen.
3. **Separate reading from acting.** Have one step extract facts from untrusted content into a fixed structure, and a different step, which never sees the raw content, decide what to do.
4. **Log and review.** Every tool call is logged with the content that preceded it, so injections are detectable after the fact.
5. **Assume compromise in design reviews.** Ask "what is the worst thing this agent could do if the page it reads is hostile?" and make that thing impossible, not just unlikely.

Security teams should treat agent deployments as new service accounts with new attack surface, and put them through the same review as any integration with write access.
""",
 "faqs": [
  ["Is prompt injection the same as jailbreaking?", "Related but different. Jailbreaking is a user trying to get a model to break its own rules; injection is a third party hijacking a model through content it processes, usually without the user knowing."],
  ["Can a model be trained to be immune?", "Current models can be made much more resistant, but no vendor claims immunity. Design for containment, not prevention alone."],
  ["Does this affect simple chatbots?", "Less so, because they cannot act. The risk scales with the tools and permissions the AI system has."]
 ]
},
{
 "slug": "how-to-read-an-ai-benchmark",
 "title": "How to read an AI benchmark without being fooled",
 "summary": "Vendor charts always show the vendor winning. The handful of questions that separate a meaningful result from marketing.",
 "level": "intermediate", "audiences": ["ml", "developers", "finance"], "published": D, "updated": D,
 "body": """
Every model launch comes with a bar chart. The vendor's new model is on top. Here is how to decide whether that means anything for you.

## Who ran it

Vendor-run numbers are measured under conditions the vendor chose: prompt format, number of attempts, tool access, reasoning budget. Independent evaluations (academic groups, third-party leaderboards, your own tests) are the only numbers that compare models under the same conditions. If a chart has no independent source, read it as a claim, not a result.

## What was measured

- **Static knowledge tests** (multiple choice over science, law, medicine) saturate: top models score so close to the ceiling that differences are noise, and questions leak into training data over time.
- **Coding and agentic tasks** (fix this real bug, complete this multi-step job) are harder to game and closer to work people pay for. Note whether the score is pass@1 (one attempt) or best-of-many.
- **Preference leaderboards** rank models by which answer humans prefer in blind pairs. They measure likeability and formatting as much as correctness.

## The details that change the answer

- **Reasoning budget.** Many models score higher when allowed more "thinking" tokens. A score at the maximum setting costs several times more per task than the default setting.
- **Tools.** A model allowed to run code or search scores differently from one that cannot. Compare like with like.
- **Contamination.** If the test questions were public before the model was trained, the model may have seen them. New or private test sets are more trustworthy.
- **Error bars.** A two-point lead on a 500-question test is usually within noise. Few vendor charts show confidence intervals.

## What to do instead

Build a small evaluation set from your own work: 50 to 200 real tasks with known-good answers. Run every candidate model on it at the settings you would use in production, and record cost and latency alongside accuracy. That table will disagree with the launch chart more often than you expect, and it is the only one that predicts your results.
""",
 "faqs": [
  ["Which benchmark is the most reliable?", "None is universally reliable. Independent, recently created, task-based evaluations with published methodology are the most informative; your own evaluation set is the most relevant."],
  ["Why do scores differ between sources for the same model?", "Different prompts, attempt counts, reasoning budgets and tool access. Always check the conditions before comparing two numbers."],
  ["Is a higher benchmark score worth a higher price?", "Only if the task you run is the kind the benchmark measures. Many production tasks are handled equally well by models several tiers cheaper."]
 ]
},
{
 "slug": "ai-model-tiers-explained",
 "title": "Flagship, mid-tier, small: which AI model tier should you actually use?",
 "summary": "Every vendor sells three or four sizes. How to match tier to task, and why most production traffic belongs on the middle one.",
 "level": "beginner", "audiences": ["developers", "executives", "beginners"], "published": D, "updated": D,
 "body": """
OpenAI, Anthropic and Google each sell a ladder of models. The names differ (Astra, Fable, Argon at the top; mini, Haiku, Flash-Lite at the bottom) but the shape is the same: each step down is several times cheaper and faster, and somewhat less capable on hard reasoning.

## The tiers

- **Top tier** (GPT-6 Astra, Claude Fable 5.1, Gemini 4 Argon): best at long, multi-step reasoning, agent tasks and hard code. Priced around $10 / $50 per million tokens, or $2–4 / $10–20 at launch promotions. Slowest.
- **Mid tier** (Claude Opus 5.5 and Sonnet 5.5, GPT-5.6 Sol and Terra, Gemini Flash): most production workloads. $2–4 input, $10–20 output. Good reasoning, much faster.
- **Small tier** (Haiku, mini and nano, Flash-Lite): classification, extraction, routing, simple chat. $0.10–0.75 input. Very fast.

Exact prices are on the [pricing tracker](/trackers/api-pricing/).

## How to choose

1. **Start in the middle.** Build and evaluate on a mid-tier model. It is the default recommendation from the vendors themselves for most tasks.
2. **Step up only on measured failures.** If your evaluation set shows the mid tier failing on specific hard cases, route those cases to the top tier rather than moving everything.
3. **Step down aggressively.** Anything that looks like "is this email about billing?" or "pull the invoice number out of this PDF" belongs on the small tier. The accuracy difference is usually nil and the cost difference is 20x.
4. **Route.** A cheap model can classify the request and send it to the right tier. This single pattern typically cuts a bill by more than half.

## The trap

Teams prototype on the flagship because it works first time, then ship on it. Six months later the bill is ten times what a routed system would cost, and nobody has measured whether the flagship was ever needed. Measure on day one.
""",
 "faqs": [
  ["Is the top tier always more accurate?", "On hard reasoning and long agentic tasks, usually. On simple, well-defined tasks the gap is often zero, and the smaller model is faster."],
  ["Can I mix vendors?", "Yes. Many teams route by task to whichever vendor's tier is cheapest for that task. The cost is maintaining prompts for more than one model."],
  ["What about open-weight models?", "Self-hosted open models can be cheapest at very high volume, at the price of running your own inference. For most teams below that scale, API tiers are simpler."]
 ]
},
{
 "slug": "open-weights-vs-closed-models",
 "title": "Open-weight vs closed AI models: what the difference means for you",
 "summary": "Open-weight models can be downloaded and run anywhere; closed models live behind an API. The trade-offs on cost, control, capability and risk.",
 "level": "beginner", "audiences": ["executives", "ml", "security", "beginners"], "published": D, "updated": D,
 "body": """
A **closed** model (GPT-6 Astra, Claude Fable, Gemini) is reachable only through its vendor's API. An **open-weight** model (Meta's Llama family, Mistral's open releases, DeepSeek, Google's Gemma, OpenAI's gpt-oss) publishes the trained parameters so anyone can download, run, modify and redistribute it under a licence.

"Open-weight" is not the same as "open source": the weights are public but the training data and full recipe usually are not.

## Why companies choose open weights

- **Control.** Run it in your own data center or cloud account. No data leaves. No vendor can change or retire the model under you.
- **Cost at scale.** Above a certain volume, renting GPUs and running an open model is cheaper than paying per token.
- **Customisation.** Fine-tune on your own data without restrictions.
- **No rate limits or outages you do not control.**

## Why companies choose closed

- **Capability.** The top closed models still lead on the hardest reasoning and agentic tasks, though the gap narrows every few months.
- **No operations.** No GPUs to provision, no serving stack to maintain, no security patches for inference servers.
- **Features.** Tool use, caching, batch, long context and safety tooling arrive first on the vendor API.

## The security angle

Open weights can be audited and run air-gapped, which regulated industries like. They can also be fine-tuned by anyone to remove safety behaviour, which is why dual-use capability such as advanced cyber-offence tends to ship closed and gated (OpenAI's GPT-6 Cyber is available only to vetted customers).

## A practical rule

Prototype on a closed API for speed. Once a workload is stable and large, price out an open model on your own infrastructure for that specific task. Many companies end up with both: closed for the hard, low-volume tasks and open for the high-volume, well-defined ones.
""",
 "faqs": [
  ["Are open-weight models free?", "The weights are free to download under their licence, but running them costs compute, and some licences restrict commercial use above a size threshold."],
  ["Which open-weight model is best?", "It changes monthly. The model release tracker lists new open releases with links to the vendor's page."],
  ["Is my data safer with open models?", "It never leaves your infrastructure, which removes one class of risk. You then own every other class: access control, patching, and monitoring."]
 ]
},
]

for e in explainers:
    e["body"] = e["body"].strip()
    json.dump(e, open(os.path.join(EX, e["slug"] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

glossary = [
 ("Token", "The unit models read and write; roughly three-quarters of an English word. Pricing and context limits are counted in tokens.", "A token is a chunk of text produced by the model's tokenizer: common words are one token, rare words or code split into several. A million tokens is about 750,000 words of English. Different models tokenise the same text into different counts, so compare cost per task rather than per token.", ["context", "pricing"]),
 ("Context window", "The maximum text a model can consider in one request: prompt, documents, conversation and answer combined.", "Measured in tokens. Flagship models in 2026 advertise around one million tokens. Everything in the window is billed as input on each request, and accuracy on very long inputs is lower than on short ones.", ["token"]),
 ("Large language model (LLM)", "A neural network trained on vast amounts of text to predict the next token, which turns out to be enough to write, summarise, reason and code.", "LLMs are the engines behind ChatGPT, Claude and Gemini. They are trained in two stages: pre-training on general text, then post-training (instruction tuning and reinforcement learning) to make them helpful and safe.", ["model", "transformer"]),
 ("Agent", "An AI system that pursues a goal by taking actions with tools, in a loop, rather than answering a single question.", "See the explainer [What is an AI agent?](/learn/what-is-an-ai-agent/). The risk and value of an agent both come from the tools and permissions it has.", ["tool", "injection"]),
 ("Prompt", "The text sent to a model: instructions, context and the question.", "Prompts usually have a system part (standing instructions from the developer) and a user part. Prompt design strongly affects output quality and cost.", ["system prompt", "token"]),
 ("System prompt", "Standing instructions a developer gives a model that apply to every conversation, such as persona, rules and output format.", "System prompts are a prime candidate for prompt caching because they repeat across requests.", ["prompt", "caching"]),
 ("Prompt injection", "An attack in which text the model reads, such as a web page or email, contains instructions that hijack its behaviour.", "See [Prompt injection explained](/learn/prompt-injection-explained/). The main security concern for agents.", ["agent", "security"]),
 ("Jailbreak", "A user's attempt to make a model ignore its safety rules through crafted prompts.", "Distinct from prompt injection, which is carried out by a third party through content the model processes.", ["injection", "safety"]),
 ("Hallucination", "A confident, fluent model output that is false or unsupported.", "Reduced by grounding (RAG), by instructing the model to cite sources and say when it does not know, and by verification steps. Not eliminated by any current model.", ["RAG", "grounding"]),
 ("Retrieval-augmented generation (RAG)", "Finding the relevant passages from a document store and giving them to the model with the question, so answers are grounded in your data.", "See [RAG explained for business leaders](/learn/rag-explained-for-business/).", ["embedding", "vector", "hallucination"]),
 ("Embedding", "A list of numbers that represents the meaning of a piece of text, so similar texts have similar numbers.", "Embeddings power semantic search and RAG: documents and questions are embedded, and the nearest documents to the question are retrieved.", ["vector", "RAG"]),
 ("Vector database", "A database optimised for storing embeddings and finding the nearest ones to a query.", "Used as the retrieval layer in RAG systems. Many conventional databases now offer vector search.", ["embedding", "RAG"]),
 ("Fine-tuning", "Further training a model on your own examples to change its behaviour or specialise it.", "Useful for consistent style, narrow tasks and reducing prompt length. Compared with RAG it is slower to update and harder to audit, and does not reliably teach new facts.", ["RAG", "training"]),
 ("Inference", "Running a trained model to produce output. What you pay for when you call an API.", "Inference cost scales with tokens processed and model size, which is why smaller tiers and shorter outputs are cheaper.", ["training", "token"]),
 ("Training", "The process of adjusting a model's parameters on data. Pre-training builds general ability; post-training shapes behaviour.", "Frontier training runs cost hundreds of millions to billions of dollars in compute, which is why only a handful of labs train top-tier models.", ["inference", "pre-training"]),
 ("Parameters", "The numbers inside a model that training adjusts; loosely, its size. Frontier models have hundreds of billions to trillions.", "More parameters generally means more capability and higher inference cost, though training data and technique matter as much.", ["model", "weights"]),
 ("Weights", "Another word for a model's parameters, usually in the context of publishing or downloading them.", "See [open-weight vs closed models](/learn/open-weights-vs-closed-models/).", ["parameters", "open"]),
 ("Open-weight model", "A model whose trained parameters are published for anyone to download and run.", "Not the same as open source: training data and code are usually not released. Examples include Llama, Mistral's open releases, Gemma and DeepSeek.", ["weights", "closed"]),
 ("Closed model", "A model reachable only through its vendor's API; the weights are not published.", "GPT-6 Astra, Claude Fable and Gemini are closed. Advantages: capability, features, no operations. Disadvantages: data leaves your environment and the vendor controls availability.", ["open-weight", "API"]),
 ("Transformer", "The neural network architecture behind nearly all current language models, built around a mechanism called attention.", "Introduced in 2017. Its ability to process sequences in parallel made training on internet-scale text practical.", ["LLM", "attention"]),
 ("Attention", "The mechanism that lets a transformer weigh which earlier tokens matter when producing the next one.", "Attention cost grows with sequence length, which is why very long context windows are expensive and were slow to arrive.", ["transformer", "context"]),
 ("Reasoning model", "A model trained to work through a problem step by step, generating intermediate 'thinking' tokens, before answering.", "Reasoning models score higher on maths, code and planning at the cost of more output tokens and latency. Many vendors expose a reasoning budget or effort setting.", ["inference", "token"]),
 ("Reasoning budget", "A setting that controls how many thinking tokens a reasoning model may use before answering.", "Higher budgets raise accuracy on hard tasks and cost. Benchmark scores often quote the maximum setting.", ["reasoning", "benchmark"]),
 ("Prompt caching", "Charging a reduced rate for the repeated prefix of a prompt, such as a system prompt or a document reused across requests.", "Cache reads cost 2.5% to 10% of the input price at the major vendors. Put stable content first in the prompt to benefit.", ["token", "pricing"]),
 ("Batch API", "A way to submit many requests to be processed asynchronously, usually within hours, at about half price.", "Offered by OpenAI, Anthropic and Google. Ideal for backfills, evaluations and nightly jobs.", ["pricing", "inference"]),
 ("Multimodal", "A model that accepts or produces more than one kind of input or output: text, images, audio, video.", "Most flagship models now read images; audio and video are billed at different token rates.", ["model"]),
 ("Benchmark", "A standard test used to compare models, such as a set of coding tasks or exam questions.", "See [How to read an AI benchmark](/learn/how-to-read-an-ai-benchmark/). Vendor-run results are claims; independent runs are evidence.", ["evaluation"]),
 ("Evaluation (eval)", "A test set with known-good answers used to measure a model or system on your own tasks.", "The single most useful artefact an AI team can build. Fifty to two hundred real examples is enough to start.", ["benchmark"]),
 ("Guardrails", "Checks placed around a model to block unwanted inputs or outputs, such as filters for sensitive data or policy violations.", "Guardrails reduce risk but can be bypassed; they complement, rather than replace, careful permissioning of what the system can do.", ["safety", "injection"]),
 ("Alignment", "The broad effort to make models behave as their developers and users intend, including being honest and refusing harmful requests.", "Covers training techniques (such as reinforcement learning from human feedback), evaluations and deployment policies.", ["safety", "RLHF"]),
 ("RLHF", "Reinforcement learning from human feedback: training a model to prefer outputs that human raters rate highly.", "The post-training technique that turned raw language models into usable assistants. Successors use AI feedback and verifiable rewards.", ["alignment", "training"]),
 ("Tool use (function calling)", "A model's ability to request that the surrounding software run a function, such as a search or a database query, and return the result.", "The building block of agents. The model does not execute anything itself; the application does, which is where permissions must be enforced.", ["agent"]),
 ("Model Context Protocol (MCP)", "An open standard for connecting AI applications to tools and data sources through a common interface.", "Lets a tool be written once and used by many AI clients. Security reviews should treat each MCP server as an integration with the permissions it is granted.", ["tool", "agent"]),
 ("Latency", "How long a model takes to respond, usually measured as time to first token and tokens per second.", "Smaller tiers and shorter outputs are faster. Reasoning budgets and long contexts add latency.", ["inference"]),
 ("Rate limit", "The maximum requests or tokens per minute a vendor allows an account, often tiered by spending history.", "A common cause of production failures. Design for retries and consider batch for non-urgent work.", ["API"]),
 ("API", "Application programming interface: the way software calls a model, billed per token, as opposed to a chat app used by a person.", "ChatGPT Plus and Claude Pro are subscriptions for people; the API is what developers build on.", ["pricing", "token"]),
 ("Distillation", "Training a smaller model to imitate a larger one's outputs, capturing much of its capability at lower cost.", "How vendors produce mini, Flash and Haiku tiers, and a point of dispute in vendor terms of service.", ["training", "parameters"]),
 ("Mixture of experts (MoE)", "A model design where only a subset of parameters activates for each token, giving large capacity at lower inference cost.", "Common in frontier and open-weight models. A 'total parameters' figure for an MoE model overstates its per-token compute.", ["parameters", "inference"]),
 ("Synthetic data", "Training data generated by a model rather than collected from humans.", "Used to fill gaps in real data and to train reasoning. Risks include amplifying the generating model's errors.", ["training"]),
 ("Frontier model", "A model at or near the state of the art at the time, typically the newest top tier from a major lab.", "Frontier models are the subject of most safety policies and regulations, which often set capability or compute thresholds.", ["model", "safety"]),
 ("Compute", "The processing power, usually GPU or TPU hours, used to train and run models. The scarce input of the AI industry.", "Data-center capacity, power and chip export controls are compute stories. Most AI infrastructure news is about who can get compute and at what price.", ["training", "inference"]),
 ("GPU", "Graphics processing unit: the chip type, dominated by Nvidia, that performs the parallel arithmetic AI training and inference require.", "GPU supply, pricing and export rules shape which labs and countries can build frontier models.", ["compute"]),
 ("Non-human identity", "A credential used by software, including AI agents, rather than a person, such as a service account or API key.", "Agents multiply non-human identities. Securing their permissions and rotation is an emerging category of security tooling.", ["agent", "security"]),
 ("Deepfake", "Synthetic audio, image or video that convincingly impersonates a real person.", "A fraud and misinformation risk; detection tools exist but lag generation. Verify unusual requests through a second channel.", ["multimodal"]),
 ("Grounding", "Supplying a model with trusted sources (documents, search results) so its answer is tied to evidence rather than memory.", "RAG is one form of grounding; search-augmented answering is another. Grounded answers can cite sources.", ["RAG", "hallucination"]),
]
json.dump([{"term": t, "short": s, "long": l, "related": r} for t, s, l, r in glossary], open(os.path.join(HERE, "data", "glossary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("seeded", len(explainers), "explainers,", len(glossary), "terms")
