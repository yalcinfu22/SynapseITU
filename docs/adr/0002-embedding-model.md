# ADR-0002: Embedding model

## Decision

Use **Qwen3-Embedding-0.6B** with 1024 dimensions. Use **bge-m3** as the fallback model.

- Staging and production send requests to DeepInfra. This is the same provider as the LLM (ADR-0001).
- Developers can run the same model on their own computer. A GPU is not necessary.

| Status | Date | Activity | Owners |
|---|---|---|---|
| Proposed | 2026-11-13 | WBS-14.1 (issue #25) | Options and test calls: Ahmed Said. This record: Furkan |
| Accepted | 2026-11-15 | WBS-14.1 (issue #25) | Furkan and Ahmed Said |

This decision replaces Voyage AI, which the Project Plan specifies. We report the change to the TA and record it in the change log of the Project Plan.

Terms:

- **Embedding**: a list of numbers that shows the meaning of a text. Texts with similar meanings have similar lists. The search uses embeddings to find opportunities that match a CV. The CV and the opportunity can be in different languages.
- **Dimensions**: the length of the list. The database column has 1024 (WBS-14.3).

## Reasons

### 1. It found the correct results in Turkish and English

We tested 5 models on a laptop GPU (RTX 4080). The test set had 40 opportunities and 32 CV summaries. Half of them were in Turkish and half in English. Some CVs were in a different language from their correct opportunities.

| Model | Score (0–1) | Wrong language first |
|---|---|---|
| Qwen3-Embedding-0.6B | 0.97 | 0% |
| arctic-embed-l-v2.0 | 0.96 | 0% |
| bge-m3 | 0.96 | 0% |
| multilingual-e5-small | 0.85 | 38% |
| multilingual-e5-large-instruct | 0.81 | 56% |
| Keyword search (no model) | 0.69 | – |

- **Score** is nDCG@10. A score of 1 means that the correct opportunities are at the top of the list.
- **Wrong language first** applies to tests where the CV and its correct opportunities are in different languages. It is the share of these tests where the first result was in the language of the CV. The e5 models often did this. The first three models never did it.
- The first three models have almost the same score. The test set is small, so the test cannot show which of the three is best.

### 2. Qwen3 has more functions than the other two

| | Qwen3-Embedding-0.6B | bge-m3 |
|---|---|---|
| Fits the 1024 column | Yes | Yes |
| Can make shorter vectors | Yes | No |
| Maximum text length (tokens) | 32,000 | 8,000 |
| Price for each 1M tokens | $0.01 | $0.01 |
| Licence | Apache-2.0 | MIT |

arctic-embed-l-v2.0 has no hosted provider with a published price. Thus we did not select it.

### 3. Our servers cannot run the model

The servers are `t3.small` (2 CPUs, 2 GB memory, no GPU). On a laptop CPU, which is faster than the server CPU, one query took 1.9–3.5 s. The limit is 4 s (MC-12). Thus we use a hosted provider.

### 4. The plan's Voyage model has disadvantages

- We did not test it. We had no API key.
- Voyage uses customer data for training. To stop this, the account must give a payment method.
- It adds one more data provider to the CV consent text.

### 5. Spike on a developer computer (issue #25)

`backend/spikes/ai_spike.py` (see ADR-0001) embedded one made-up CV summary, with the query text below, and 5 made-up opportunities. It ran with Ollama and `qwen3-embedding:0.6b` on a laptop without a GPU.

- 6 texts in 2.9 s, 1024 dimensions.
- The opportunities that match the CV came first. A mechanical design internship and a pastry course came last.
- Ollama uses a compressed copy of the model. Its vectors differ a little from the vectors of DeepInfra, so each environment makes its own vectors. Do not copy stored vectors between them.

## Results of this decision

| Result | Action | Owner |
|---|---|---|
| The consent text names Voyage AI (NFR-06, FR-19). | Change the name to DeepInfra. Do this with ADR-0001. | Team |
| No hosted test call yet (issue #25) | Send one embedding request to DeepInfra when staging is ready. Measure the time. | Ahmed Said (WBS-14.6) |
| The baseline scores (WBS-15.4) use no real model yet. | Run the harness with this model on the labelled set. | Amr, Furkan |
| If we change the model later | Calculate all stored embeddings again. The `embedding_model` column shows which model made each row. | Owner of the change |

**How to use the model:** add this text before each query: `Instruct: Given a student's CV summary, retrieve matching academic opportunities\nQuery: `. Do not add text before the documents.
