# <code style="background: transparent;">Summoner<b>.gpt_guardrails</b></code>

This page documents the **Python utility interface** for budgeting OpenAI calls using `gpt_guardrails`. It focuses on how to install it in an extension-template workflow, how to use it to estimate tokens and cost before a call, and how to compute actual cost after a call when usage is available.

`gpt_guardrails` is intentionally small. It does not wrap the OpenAI SDK. It does not retry, split batches, truncate inputs, or filter content. It gives you a consistent way to do two things:

* **Pre-call budgeting:** count tokens and estimate cost, then decide whether to skip the request.
* **Post-call accounting:** extract usage from the response and compute the actual cost.

The typical usage pattern is:

1. Count tokens for the payload you are about to send.
2. Estimate cost using the local pricing tables in `gpt_guardrails`.
3. Enforce a token ceiling and optionally a cost ceiling.
4. Call the OpenAI SDK.
5. Extract usage from the response and compute actual cost.

### Public entry points

The public symbols exported by this extension are:

* `count_chat_tokens`
* `estimate_chat_request_cost`
* `actual_chat_request_cost`
* `get_usage_from_response`
* `count_embedding_tokens`
* `estimate_embedding_request_cost`
* `actual_embedding_request_cost`

All of them are implemented in `gpt_guardrails/cost.py`.

## Installation in an extension-template workflow

`gpt_guardrails` is shipped as an extension module hosted in the `extension-utilities` repository. In an extension-template project, you add it to your SDK build list so it is included during composition.

### Add `gpt_guardrails` to `build.txt`

Add the following entry to your SDK builder list:

```text
https://github.com/Summoner-Network/extension-utilities.git:
gpt_guardrails
```

This tells the SDK composition step to pull the `gpt_guardrails` module from `extension-utilities` and merge it into the composed SDK.

### Import path

Import the utilities from the SDK like any other public module:

```python
from summoner.gpt_guardrails import (
    count_chat_tokens,
    estimate_chat_request_cost,
    actual_chat_request_cost,
    get_usage_from_response,
    count_embedding_tokens,
    estimate_embedding_request_cost,
    actual_embedding_request_cost,
)
```

> [!NOTE]
> In the `extension-utilities` repository, local test scripts may import `gpt_guardrails` directly from the repo layout as `from tooling.gpt_guardrails import ...` (that is, without SDK composition). For normal SDK usage, always use the `summoner.gpt_guardrails` import.

## What this module counts and what it estimates

### Chat calls

For chat-style calls, the module provides:

* a prompt token estimator (`count_chat_tokens(messages, model=...)`)
* a worst-case cost estimator (`estimate_chat_request_cost(model, prompt_tokens, max_completion_tokens)`)
* an actual cost computation once you know usage (`actual_chat_request_cost(model, prompt_tokens, completion_tokens)`)

The estimate is conservative because it assumes the model generates the full `max_completion_tokens`.

### Embeddings calls

For embeddings, the module provides:

* an input token counter for a list of texts (`count_embedding_tokens(texts, model_name=...)`)
* a cost estimate (`estimate_embedding_request_cost(model_name, input_tokens)`)
* an actual cost computation (`actual_embedding_request_cost(...)`)

In this module, estimate and actual are the same for embeddings because embeddings are treated as input-only billing.

### Usage extraction

For post-call accounting, the module provides a unified usage view that works for:

* Chat Completions usage (`prompt_tokens`, `completion_tokens`, `total_tokens`)
* Responses API usage (`input_tokens`, `output_tokens`, `total_tokens`)

The extractor returns a single `Usage(prompt_tokens, completion_tokens, total_tokens)` or `None` if usage is absent.

## `count_chat_tokens`

```python
def count_chat_tokens(
    messages: list[dict[str, str]],
    model: str = "gpt-4o",
) -> int
```

### Behavior

Returns the token count intended to approximate what will be sent as `prompt_tokens` for a `chat.completions` call.

Tokenizer selection:

* Tries `tiktoken.encoding_for_model(model)`.
* If `tiktoken` does not recognize the model name, falls back to `tiktoken.get_encoding("cl100k_base")`.

Overhead rules:

* If `model.startswith("gpt-3.5-turbo-0301")`:

  * `tokens_per_message = 4`
  * `tokens_per_name = -1`

* Else if `model.startswith("gpt-3.5-turbo")`:

  * `tokens_per_message = 4`
  * `tokens_per_name = -1`

* Else if `model.startswith("gpt-4")`:

  * `tokens_per_message = 3`
  * `tokens_per_name = 1`

* Else:

  * default for newer families (4o, 5, etc.)
  * `tokens_per_message = 3`
  * `tokens_per_name = 1`

Counting rule:

* For each message dict:

  * add `tokens_per_message`
  * for each `(key, val)` in the dict:

    * add `len(encoding.encode(val))`
    * if `key == "name"`, add `tokens_per_name`

Final priming:

* After processing all messages, add `+3` tokens to account for assistant role priming.

### Inputs

#### `messages`

* **Type:** `list[dict[str, str]]`
* **Meaning:** Chat messages. Every field value is encoded and counted (including `role`, `content`, and optional `name`).

#### `model`

* **Type:** `str`
* **Meaning:** Model id used for tokenizer selection and overhead selection.
* **Default:** `"gpt-4o"`

### Outputs

Returns an integer token count.

### Examples

#### Count tokens for a single user message

```python
messages = [{"role": "user", "content": "Say this is a test"}]
prompt_tokens = count_chat_tokens(messages, model="gpt-4o-mini")
```

#### Count tokens with a `name` field

```python
messages = [{"role": "user", "name": "alice", "content": "hi"}]
prompt_tokens = count_chat_tokens(messages, model="gpt-3.5-turbo")
```

## Chat pricing: `PRICING` (not exposed)

```python
PRICING: dict[str, dict[str, float]] = {
    "gpt-3.5-turbo":     {"prompt": 0.0005,  "completion": 0.0015},
    "gpt-3.5-turbo-16k": {"prompt": 0.003,   "completion": 0.004},
    "gpt-4.1":           {"prompt": 0.002,   "completion": 0.008},
    "gpt-4.1-mini":      {"prompt": 0.0004,  "completion": 0.0016},
    "o3":                {"prompt": 0.002,   "completion": 0.008},
    "o4-mini":           {"prompt": 0.0011,  "completion": 0.0044},
    "gpt-4o":            {"prompt": 0.0050,  "completion": 0.0200},
    "gpt-4o-mini":       {"prompt": 0.00015, "completion": 0.00060},
    "gpt-5":             {"prompt": 0.00125, "completion": 0.01000},
    "gpt-5-mini":        {"prompt": 0.00025, "completion": 0.00200},
    "gpt-5-nano":        {"prompt": 0.00005, "completion": 0.00040},
}
```

### Behavior

This is a local pricing table expressed as USD per 1k tokens:

* `prompt`: USD per 1k prompt tokens
* `completion`: USD per 1k completion tokens

If a model id is not present in `PRICING`, chat cost functions raise a `ValueError`.

## `estimate_chat_request_cost`

```python
def estimate_chat_request_cost(
    model_name: str,
    prompt_tokens: int,
    max_completion_tokens: int
) -> float
```

### Behavior

Estimates the USD cost for a chat call assuming the model uses:

* `prompt_tokens` prompt tokens, and
* `max_completion_tokens` completion tokens

Computation:

```python
(prompt_tokens / 1_000) * rates["prompt"]
+ (max_completion_tokens / 1_000) * rates["completion"]
```

If `model_name` is not in `PRICING`, raises:

```text
ValueError: No pricing info for model '<model_name>'
```

### Inputs

#### `model_name`

* **Type:** `str`
* **Meaning:** Key into `PRICING`.

#### `prompt_tokens`

* **Type:** `int`
* **Meaning:** Estimated or measured prompt token count.

#### `max_completion_tokens`

* **Type:** `int`
* **Meaning:** Output token budget you plan to pass to the API.

### Outputs

Returns a float USD estimate.

### Examples

```python
prompt_tokens = count_chat_tokens([{"role": "user", "content": "hi"}], model="gpt-4o-mini")
est_cost = estimate_chat_request_cost("gpt-4o-mini", prompt_tokens, max_completion_tokens=1000)
```

## `actual_chat_request_cost`

```python
def actual_chat_request_cost(
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int
) -> float
```

### Behavior

Computes the USD cost once you know actual usage tokens:

* `prompt_tokens` used
* `completion_tokens` generated

Computation:

```python
(prompt_tokens / 1_000) * rates["prompt"]
+ (completion_tokens / 1_000) * rates["completion"]
```

If `model_name` is not in `PRICING`, raises:

```text
ValueError: No pricing info for model '<model_name>'
```

### Inputs

#### `model_name`

* **Type:** `str`
* **Meaning:** Key into `PRICING`.

#### `prompt_tokens`

* **Type:** `int`
* **Meaning:** Actual prompt tokens from usage.

#### `completion_tokens`

* **Type:** `int`
* **Meaning:** Actual completion tokens from usage.

### Outputs

Returns a float USD cost.

### Examples

```python
usage = get_usage_from_response(response)
if usage:
    cost = actual_chat_request_cost("gpt-4o-mini", usage.prompt_tokens, usage.completion_tokens)
```

## `normalize_usage` (not exposed)

```python
def normalize_usage(usage_obj: Any) -> Optional[dict[str, int]]
```

### Behavior

Normalizes usage from OpenAI SDK responses into:

```python
{"prompt_tokens": int, "completion_tokens": int, "total_tokens": int}
```

This function returns `None` if usage is unavailable or cannot be interpreted.

Conversion to dict:

* If `usage_obj is None`, return `None`.
* Tries to call one of these methods in order, stopping at the first that succeeds:

  * `usage_obj.to_dict()`
  * `usage_obj.model_dump()`
  * `usage_obj.dict()`
* If none worked:

  * if `usage_obj` is already a dict, use it
  * else try `dict(usage_obj)` as a last resort
  * if that fails, return `None`

Key normalization:

* If `"prompt_tokens"` in the dict or `"completion_tokens"` in the dict:

  * `prompt = int(d.get("prompt_tokens", 0))`
  * `comp = int(d.get("completion_tokens", 0))`
  * `total = int(d.get("total_tokens", prompt + comp))`

* Else if `"input_tokens"` in the dict or `"output_tokens"` in the dict:

  * `prompt = int(d.get("input_tokens", 0))`
  * `comp = int(d.get("output_tokens", 0))`
  * `total = int(d.get("total_tokens", prompt + comp))`

* Else return `None`.

### Inputs

#### `usage_obj`

* **Type:** `Any`
* **Meaning:** A usage object attached to a response, or a dict-like payload.

### Outputs

Returns a dict of integers or `None`.

### Examples

```python
norm = normalize_usage(response.usage)
if norm is not None:
    print(norm)
```

## `Usage` (not exposed)

```python
@dataclass(frozen=True)
class Usage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def to_dict(self) -> dict[str, int]: ...
```

### Behavior

Immutable unified usage view for both Chat Completions and Responses API. The `to_dict()` method returns:

```python
{
    "prompt_tokens": ...,
    "completion_tokens": ...,
    "total_tokens": ...,
}
```

### Examples

```python
usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
print(usage.to_dict())
```

## `get_usage_from_response`

```python
def get_usage_from_response(response: Any) -> Optional[Usage]
```

### Behavior

Extracts a unified `Usage` object from an OpenAI SDK response.

* Reads `usage_obj = getattr(response, "usage", None)`.
* If `usage_obj` is missing, returns `None`.
* Normalizes `usage_obj` using `normalize_usage`.
* If normalization fails, returns `None`.
* Constructs `Usage` using:

  * `prompt = int(norm.get("prompt_tokens", 0))`
  * `comp = int(norm.get("completion_tokens", 0))`
  * `total = int(norm.get("total_tokens", prompt + comp))`

### Inputs

#### `response`

* **Type:** `Any`
* **Meaning:** OpenAI SDK response object.

### Outputs

Returns `Usage` or `None`.

### Examples

```python
usage = get_usage_from_response(response)
if usage is None:
    # budget checks still worked pre-call, but actual usage is unavailable
    pass
```

## Embedding pricing: `EMBEDDING_PRICING` (not exposed)

```python
EMBEDDING_PRICING: dict[str, float] = {
    "text-embedding-3-small":  0.00002,
    "text-embedding-3-large":  0.00013,
    "text-embedding-ada-002":  0.00010,
}
```

### Behavior

Local pricing table for embeddings expressed as USD per 1k input tokens (input-only billing). If a model id is not present, embedding cost functions raise a `ValueError`.

## `count_embedding_tokens`

```python
def count_embedding_tokens(
    texts: list[str],
    model_name: str = "text-embedding-ada-002",
) -> int
```

### Behavior

Returns the total number of tokens for a list of input strings when sent to the embeddings endpoint.

Tokenizer selection:

* Tries `tiktoken.encoding_for_model(model_name)`.
* Falls back to `tiktoken.get_encoding("cl100k_base")` if the model is not mapped in `tiktoken`.

Counting rule:

* Returns:

```python
sum(len(enc.encode(text)) for text in texts)
```

This is a batch total, not per-text counts.

### Inputs

#### `texts`

* **Type:** `list[str]`
* **Meaning:** List of input strings to embed.

#### `model_name`

* **Type:** `str`
* **Meaning:** Model id used for tokenizer selection.
* **Default:** `"text-embedding-ada-002"`

### Outputs

Returns an integer token count.

### Examples

```python
tokens = count_embedding_tokens(
    ["The quick brown fox", "jumps over the lazy dog"],
    model_name="text-embedding-3-small",
)
```

## `estimate_embedding_request_cost`

```python
def estimate_embedding_request_cost(
    model_name: str,
    input_tokens: int,
) -> float
```

### Behavior

Estimates the USD cost for an embeddings call given an input token count.

* Looks up `rate_per_1k = EMBEDDING_PRICING.get(model_name)`.
* If missing, raises:

```text
ValueError: No embedding pricing on record for '<model_name>'
```

* Computes:

```python
input_tokens / 1_000 * rate_per_1k
```

### Inputs

#### `model_name`

* **Type:** `str`
* **Meaning:** Key into `EMBEDDING_PRICING`.

#### `input_tokens`

* **Type:** `int`
* **Meaning:** Input tokens used or expected.

### Outputs

Returns a float USD cost.

### Examples

```python
tokens = count_embedding_tokens(["hello"], model_name="text-embedding-3-small")
est = estimate_embedding_request_cost("text-embedding-3-small", tokens)
```

## `actual_embedding_request_cost`

```python
def actual_embedding_request_cost(
    model_name: str,
    input_tokens: int,
) -> float
```

### Behavior

Computes the USD cost once you know the actual tokens used for an embeddings call.

This is implemented as:

```python
return estimate_embedding_request_cost(model_name, input_tokens)
```

because embeddings are treated as input-only billing in this module.

### Inputs

Same as `estimate_embedding_request_cost`.

### Outputs

Returns a float USD cost.

## Running it in your OpenAI wrappers

`gpt_guardrails` is designed to be embedded in your call sites, not to run as a standalone tool. A minimal pattern for each API family is shown below.

### Example: guarded chat call

```python
import os
from typing import Optional, Any
from openai import AsyncOpenAI

from summoner.gpt_guardrails import (
    count_chat_tokens,
    estimate_chat_request_cost,
    actual_chat_request_cost,
    get_usage_from_response,
)

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

MAX_CHAT_INPUT_TOKENS = 100
MAX_CHAT_OUTPUT_TOKENS = 1000

async def chat_with_budget(
    message: str,
    model_name: str = "gpt-4o-mini",
    cost_limit: Optional[float] = None,
) -> dict[str, Any]:
    messages = [{"role": "user", "content": message}]

    prompt_tokens = count_chat_tokens(messages, model=model_name)
    est_cost = estimate_chat_request_cost(model_name, prompt_tokens, MAX_CHAT_OUTPUT_TOKENS)

    if prompt_tokens >= MAX_CHAT_INPUT_TOKENS:
        return {"output": None, "cost": None}

    if cost_limit is not None and est_cost > cost_limit:
        return {"output": None, "cost": None}

    response = await client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_completion_tokens=MAX_CHAT_OUTPUT_TOKENS,
    )

    usage = get_usage_from_response(response)
    act_cost = None
    if usage:
        act_cost = actual_chat_request_cost(model_name, usage.prompt_tokens, usage.completion_tokens)

    return {"output": response.choices[0].message.content, "cost": act_cost}
```

### Example: guarded embeddings call

```python
import os
from typing import Optional, Any
from openai import AsyncOpenAI

from summoner.gpt_guardrails import (
    count_embedding_tokens,
    estimate_embedding_request_cost,
    actual_embedding_request_cost,
    get_usage_from_response,
)

client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

MAX_EMBED_INPUT_TOKENS = 500

async def embed_with_budget(
    texts: list[str],
    model_name: str = "text-embedding-3-small",
    cost_limit: Optional[float] = None,
) -> dict[str, Any]:
    input_tokens = count_embedding_tokens(texts, model_name=model_name)
    est_cost = estimate_embedding_request_cost(model_name, input_tokens)

    if input_tokens > MAX_EMBED_INPUT_TOKENS:
        return {"output": None, "cost": None}

    if cost_limit is not None and est_cost > cost_limit:
        return {"output": None, "cost": None}

    response = await client.embeddings.create(model=model_name, input=texts)

    usage = get_usage_from_response(response)
    act_cost = None
    if usage:
        act_cost = actual_embedding_request_cost(model_name, usage.total_tokens)

    return {"output": [r.embedding for r in response.data], "cost": act_cost}
```

## OpenAI API prerequisites

`gpt_guardrails` assumes you already have the OpenAI Python SDK installed and an API key available as `OPENAI_API_KEY`.

References:

* OpenAI Python SDK: [https://github.com/openai/openai-python](https://github.com/openai/openai-python)
* API reference: [https://platform.openai.com/docs/api-reference/introduction](https://platform.openai.com/docs/api-reference/introduction)
* API keys: [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
* Pricing: [https://openai.com/api/pricing/](https://openai.com/api/pricing/)

## Troubleshooting

* **`ValueError: No pricing info for model ...`**
  The model name is not present in `PRICING` (chat) or `EMBEDDING_PRICING` (embeddings). Add a table entry or normalize model names before computing cost.

* **Token counts look wrong**
  If `tiktoken` does not recognize the model name, token counting falls back to `cl100k_base`. Update `tiktoken` or use a model id that `tiktoken` maps correctly.

* **`get_usage_from_response(...)` returns `None`**
  The response object did not expose `.usage`, or the usage dict did not include recognizable keys (`prompt_tokens` / `completion_tokens` or `input_tokens` / `output_tokens`). Pre-call budgeting still works, but actual cost is unavailable.

* **Embeddings token ceilings block batches**
  `count_embedding_tokens` returns a batch total across the input list. If you want per-text ceilings or automatic request splitting, implement that above this module.


<p align="center">
  <a href="curl_tools.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.curl_tools</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="crypto_utils.md">Next: <code style="background: transparent;">Summoner<b>.crypto_utils</b></code> &raquo;</a>
</p>