# ADR-0001: LLM for the AI features

## Decision

Use **Qwen3.5 9B** as the LLM. Use **Gemma 4 12B** as the fallback model.

- Staging and production send requests to a hosted provider (DeepInfra).
- Developers can run the same model on their own computer.
- All code calls the LLM through one interface. To change the model or the provider, change the configuration only.

| Status | Date | Activity | Owners |
|---|---|---|---|
| Proposed | 2026-11-13 | WBS-14.1 (issue #25) | Options and test calls: Ahmed Said. This record: Furkan |
| Accepted | 2026-11-15 | WBS-14.1 (issue #25) | Furkan and Ahmed Said |

This decision replaces the Claude API that the Project Plan specifies. We report the change to the TA and record it in the change log of the Project Plan.

## Reasons

| Criterion | Qwen3.5 9B | Gemma 4 12B | Claude Sonnet 5.5 (plan) |
|---|---|---|---|
| Our tests | Passed | Passed | Not tested |
| Invented items in a poor CV scan | 0 | 4 | Not tested |
| Cost for each month (estimate) | $1.1 | $1.2 | $36 |
| Licence | Open (Apache-2.0) | Open (Apache-2.0) | Closed |
| Runs on a team computer | Yes | Yes | No |

Terms:

- **LLM** (large language model): the AI model that writes text. It makes the CV summary, the search ranking and the chatbot answers.
- **Invented item**: a skill in the output that is not in the CV. The requirements do not allow this (NFR-23).
- **Cost for each month**: price × 10 million tokens (8 million in, 2 million out). This is the demo load in the plan. A **token** is a part of a word.

### Our tests

The team ran both open models on a laptop GPU (RTX 4080, 12 GB). The tests used the prompts of the project:

1. Change a CV (English and Turkish) to the JSON format of the platform.
2. Rank 4 opportunities for one student.
3. Answer 6 Turkish questions from opportunity records.
4. Write 1 Turkish sentence about an opportunity.
5. Call a search tool.

Both models passed all 5 tests. The tests did not find a difference, except for the poor scan. On the poor scan, Qwen added no invented items and Gemma added 4.

### Claude Haiku 5.5

Claude Haiku 5.5 costs approximately $1.8 for each month. This cost is near the cost of Qwen. We did not test it. We keep it as an alternative.

### Spike on a developer computer (issue #25)

The script `backend/spikes/ai_spike.py` sends one request to any OpenAI-compatible server. The address, the model and the API key come from environment variables, so the same script runs against Ollama or DeepInfra.

We ran it on a laptop without a GPU (Intel i7-9750H, 16 GB memory) with Ollama and `qwen3.5:4b-q4_K_M`, the smaller model of the same family. The CV was made up.

| Check | Result |
|---|---|
| The answer matches the JSON schema | Yes |
| Invented items | 0 |
| Time | 8–23 s for about 60 output tokens (23 s includes loading the model) |
| Writing speed | About 7 tokens per second |

- Turn off Qwen "thinking" (`reasoning_effort: "none"`). With thinking on, the model writes many extra tokens before the answer.
- The 4B model is for development only. Staging and production use Qwen3.5 9B through DeepInfra.
- We did not send a request to DeepInfra yet. We do this when staging is ready (WBS-14.6).

### Data terms of DeepInfra

From the [data privacy page](https://docs.deepinfra.com/account/data-privacy) and the [terms](https://deepinfra.com/terms) (Section 7(b), checked on 2026-11-15):

- DeepInfra does not store the requests on disk and does not log their content. It deletes the output after it returns it.
- It does not use the data to train models. This does not apply to Google and Anthropic models; we use neither through DeepInfra.
- The pages do not state the data region. DeepInfra's blog states that it runs in data centers in the US.

## Results of this decision

| Result | Action | Owner |
|---|---|---|
| The CV consent text names Anthropic (NFR-06, FR-19). | Change the name to DeepInfra. Get TA approval. | Team |
| DeepInfra processes the data in the US. This is a transfer of personal data abroad (KVKK). | Ask for explicit consent in the CV consent text and name the US. Remove the name, the e-mail and the phone number from a CV before we send it. | Team (consent text), Ahmed Said (WBS-14.5) |
| No request to DeepInfra yet | Send one request when staging is ready. Measure the time. | Ahmed Said (WBS-14.6) |
| An answer took 10–37 s on the laptop. The limit is 20 s (MC-04, MC-06). | Measure the time on staging. | Furkan (WBS-15.5) |
| The servers have no GPU. | Use the hosted provider in staging and production. | Ahmed Said (WBS-14.5) |
| If Qwen fails the time limit or the "no invented items" check | Test Claude Haiku 5.5 next. | Ahmed Said |

API keys are GitHub secrets. They are not in the repository.
