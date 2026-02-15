# <code style="background: transparent;">Summoner<b>.curl_tools</b></code>

This page documents the **Python utility interface** for turning an HTTP request description into a callable async tool using `curl_tools`.

The mental model is as follows:

* you start with a request description (often a `curl ...` snippet copied from docs),
* you compile it into a Python object (`HttpTool`),
* and later you run the request by calling that object with inputs: `await tool.call(...)`.

`curl_tools` is intentionally small. It does not implement retries, batching, rate limiting, backoff, or provider-specific SDK wrappers. It focuses on one job: represent an HTTP request in a deterministic way, execute it when you ask, and return a structured report of what happened.

This reference covers three things:

* how to compile a tool from either a cURL snippet or an explicit schema,
* how runtime placeholders work when you execute the tool (env secrets and input variables),
* how to freeze a tool spec as JSON and reload it later without changing its meaning.

The typical usage pattern is:

1. Compile a tool via deterministic cURL parsing (`compiler.parse(...)`) or an explicit schema (`compiler.request_schema(...)`):

    ```python
    compiler = CurlToolCompiler()
    tool = compiler.parse(curl_text)  # or: compiler.request_schema(...)
    ```

2. Optionally snapshot the tool spec via `tool.to_dict()` for deterministic persistence:

    ```python
    spec_dict = tool.to_dict()
    ```

3. Execute the request by calling the tool with runtime inputs:

    ```python
    report = await tool.call({"response_id": "resp_..."})
    ```

4. Inspect the report to decide what to do next:

    ```python
    if report.ok:
        data = report.response_json
    else:
        raise RuntimeError(f"{report.status_code}: {report.response_text}")
    ```

5. If you persisted the spec, rehydrate it later and run it the same way:

    ```python
    tool2 = compiler.request_schema_from_dict(spec_dict)
    ```

### Public entry points

The public symbols exported by this extension are:

* `CurlToolCompiler`
* `SecretResolver`
* `BasicAuthSpec`
* `parse_curl_command`

## Installation in an extension-template workflow

`curl_tools` is shipped as an extension module hosted in the `extension-utilities` repository. In an extension-template project, you add it to your SDK build list so it is included during composition.

### Add `curl_tools` to `build.txt`

Add the following entry to your SDK builder list:

```text
https://github.com/Summoner-Network/extension-utilities.git:
curl_tools
```

This tells the SDK composition step to pull the `curl_tools` module from `extension-utilities` and merge it into the composed SDK.

### Import path

Import the compiler from the SDK like any other public module:

```python
from summoner.curl_tools import (
    CurlToolCompiler,
    SecretResolver,
    BasicAuthSpec,
    parse_curl_command,
)
```

> [!NOTE]
> In the `extension-utilities` repository, local tests may import this module directly as `from tooling.curl_tools import ...` (that is, without SDK composition). For normal SDK usage, always use the `summoner.curl_tools` import.

## What this module compiles and what it executes

`curl_tools` compiles to one runtime object:

* `HttpTool`: an async callable wrapper around `HttpRequestSpec`.

When you run `await tool.call(inputs)`, the tool executes a well-defined sequence:

* it renders templates in the URL, headers, params, and body
* it resolves `{{env:NAME}}` using `SecretResolver`
* it resolves `{{var}}` using the `inputs` dict passed to `call(...)`
* it sends the HTTP request via `httpx.AsyncClient`
* it parses JSON when response content-type indicates JSON
* it can validate JSON responses against an optional Pydantic `output_model`
* it returns a `ToolCallReport` describing what happened

## Templating model

Two placeholder syntaxes exist:

* `{{env:NAME}}`: resolved via `SecretResolver.require(NAME)`
* `{{var}}`: resolved via `inputs["var"]`

Rendering happens in:

* `spec.url` (string)
* `spec.headers` and `spec.params` (dict-like)
* `spec.body` (string/dict/list, recursively)

Fail-fast behavior:

* missing env var raises `KeyError("Missing required secret: ...")`
* missing runtime input raises `KeyError("Missing required input variable: ...")`

This prevents partially-formed requests from silently executing.

## `SecretResolver`

```python
class SecretResolver:
    def __init__(
        self,
        mapping: Optional[Mapping[str, str]] = None,
        fallback: Optional[Callable[[str], Optional[str]]] = None,
        auto_dotenv: bool = False,
        dotenv_path: Optional[str] = None,
        dotenv_override: bool = False,
    ):
        ...
```

### Behavior

Resolves secrets using the following order:

1. explicit `mapping` passed at construction time
2. `os.environ`
3. optional `fallback(name)` callable

If `auto_dotenv=True`, it loads environment variables via `dotenv.load_dotenv(...)` during initialization.

### `SecretResolver.get`

```python
def get(self, name: str) -> Optional[str]
```

Returns the secret value or `None` if unavailable.

### `SecretResolver.require`

```python
def require(self, name: str) -> str
```

Returns the secret value or raises a `KeyError` if unavailable.

### Example

```python
secrets = SecretResolver(auto_dotenv=True)
token = secrets.require("HUBSPOT_TOKEN")
```

## `HttpRequestSpec`

```python
@dataclass
class HttpRequestSpec:
    method: HttpMethod
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None

    body_mode: BodyMode = "json"
    auth: Optional[BasicAuthSpec] = None

    timeout_s: Optional[float] = 30.0
    follow_redirects: bool = False
    verify_tls: bool = True

    description: Optional[str] = None

    input_model: Optional[Type[BaseModel]] = None
    output_model: Optional[Type[BaseModel]] = None
```

### Behavior

`HttpRequestSpec` is the full, deterministic request description consumed by `HttpTool`. It is intentionally close to the inputs of `httpx.AsyncClient.request(...)`, but keeps a stable structure that can be persisted and reloaded.

It describes:

* how to reach the endpoint (`method`, `url`, `params`)
* how to authenticate or identify the caller (`headers`, optional `auth`)
* how to encode the request body (`body`, `body_mode`)
* how to control transport behavior (`timeout_s`, `follow_redirects`, `verify_tls`)
* optional metadata and validation (`description`, `input_model`, `output_model`)

**Body conventions:**

The meaning of `body` depends on `body_mode`:

* `body_mode="json"`

  * If `body` is a `dict` or `list`, it is sent via `httpx` as JSON (`json=...`).
  * If `body` is a `str`, it is sent as raw `content` (useful when you already have a JSON string).

* `body_mode="form"`

  * `body` may be a `dict`, a `list[tuple[str, str]]`, or a raw string like `"a=1&b=2"`.
  * The runtime encodes the body as `application/x-www-form-urlencoded`.

* `body_mode="raw"`

  * `body` is sent as raw `content`.
  * If `body` is a `dict` or `list`, it is stringified using `json.dumps(...)` first.

### `HttpRequestSpec.to_dict`

```python
def to_dict(self, *, include_models: bool = False) -> dict[str, Any]
```

#### Behavior

Returns a JSON-safe snapshot of the spec. This is the representation intended for persistence (for example, writing to disk), and it is the format that `CurlToolCompiler.request_schema_from_dict(...)` expects.

Serialization rules are best-effort:

* tuples become lists (JSON cannot represent tuples)
* dataclasses become dict-like structures
* objects that are not JSON-friendly are stringified
* `input_model` and `output_model` are omitted by default

If `include_models=True`, the function stores best-effort import paths for `input_model` and `output_model`. Rehydration of models is intentionally not automatic.

#### Outputs

Returns a JSON-safe `dict[str, Any]`.

### `HttpRequestSpec.to_request_schema_kwargs` (not exposed)

```python
def to_request_schema_kwargs(self) -> dict[str, Any]
```

#### Behavior

Returns a Python-native kwargs dict suitable for rebuilding the tool through:

```python
compiler.request_schema(**kwargs)
```

This is a convenience when you want to "round-trip" a spec without going through JSON serialization (so tuples, dataclasses, and model types can remain intact).

Important distinction:

* `to_request_schema_kwargs()` returns Python-native values (may include `BasicAuthSpec`, tuple pairs in form bodies, and Pydantic model types).
* `to_dict()` returns JSON-safe values (tuples become lists, models are omitted by default).

The returned dict includes all fields accepted by `CurlToolCompiler.request_schema(...)`:

* `method`, `url`
* `headers`, `params`
* `body`, `body_mode`
* `auth`
* `timeout_s`, `follow_redirects`, `verify_tls`
* `description`
* `input_model`, `output_model`

#### Outputs

Returns a `dict[str, Any]` intended to be passed directly into `CurlToolCompiler.request_schema(...)`.

#### Example

```python
compiler = CurlToolCompiler()

tool = compiler.request_schema(
    method="POST",
    url="https://api.example.com/oauth/token",
    body=[("grant_type", "client_credentials"), ("client_id", "{{env:CLIENT_ID}}")],
    body_mode="form",
    auth=BasicAuthSpec(username="{{env:USER}}", password="{{env:PASS}}"),
)

kwargs = tool.spec.to_request_schema_kwargs()

tool2 = compiler.request_schema(**kwargs)
report = await tool2.call({})
```


## `HttpTool`

```python
class HttpTool:
    def __init__(self, spec: HttpRequestSpec, secrets: Optional[SecretResolver] = None): ...
    def to_dict(self, *, include_models: bool = False) -> dict[str, Any]: ...
    async def call(self, inputs: Optional[dict[str, Any]] = None) -> ToolCallReport: ...
```

### `HttpTool.call`

```python
async def call(self, inputs: Optional[dict[str, Any]] = None) -> ToolCallReport
```

#### Behavior

Executes the request and returns a `ToolCallReport`.

Steps:

1. If `spec.input_model` exists, validates `inputs` via Pydantic and replaces `inputs` with the validated dump.
2. Renders templates in URL, headers, params, and body.
3. Applies Basic Auth if `spec.auth` is set (after template rendering).
4. Applies default `Content-Type` based on `body_mode` if missing.
5. Sends the HTTP request via `httpx.AsyncClient`.
6. Attempts JSON parsing if `content-type` includes `application/json`.
7. If `spec.output_model` exists, validates `response_json` and sets validation fields.
8. Returns a report with `ok`, `status_code`, `elapsed_ms`, and parsed response fields.

Request error behavior:

* On network or client exceptions, returns a report with:

  * `ok=False`
  * `status_code=0`
  * `response_text="Request error: ..."`

#### Inputs

`inputs` is used only for templating and optional input model validation.

#### Outputs

Returns a `ToolCallReport`:

```python
@dataclass
class ToolCallReport:
    ok: bool
    status_code: int
    elapsed_ms: int
    request: dict[str, Any]
    response_text: Optional[str] = None
    response_json: Optional[Any] = None
    output_validation_ok: Optional[bool] = None
    output_validation_error: Optional[str] = None
```

### Example

#### Call a JSON tool

```python
tool = compiler.request_schema(
    method="POST",
    url="https://api.example.com/v1/items",
    headers={"Authorization": "Bearer {{env:API_TOKEN}}"},
    body={"name": "{{name}}"},
    body_mode="json",
)

report = await tool.call({"name": "demo"})
assert report.ok
assert report.response_json is not None
```

#### Call a form tool

```python
tool = compiler.request_schema(
    method="POST",
    url="https://api.example.com/oauth/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    body=[("grant_type", "client_credentials"), ("client_id", "{{env:CLIENT_ID}}")],
    body_mode="form",
)

report = await tool.call({})
assert report.status_code in (200, 400)
```

## `CurlToolCompiler`

`CurlToolCompiler` is the main entry point for building `HttpTool` instances. It supports three construction paths:

* deterministic compilation from cURL (`parse(...)`)
* fully explicit compilation (`request_schema(...)`)
* GPT-assisted extraction from docs (`gpt_parse(...)`)

### `CurlToolCompiler.set_budget`

```python
def set_budget(
    self,
    *,
    max_chat_input_tokens: Optional[int] = None,
    max_chat_output_tokens: Optional[int] = None,
    default_cost_limit: Optional[float] = None,
) -> None
```

#### Behavior

Updates the budgeting parameters used by `CurlToolCompiler.gpt_parse(...)`.

This method does not affect deterministic compilation (`parse(...)`, `request_schema(...)`) or runtime execution (`HttpTool.call(...)`). It only changes the ceilings enforced before making an OpenAI call inside `gpt_parse(...)`.

Fields updated:

* `max_chat_input_tokens`: prompt token ceiling (measured with `count_chat_tokens(...)`)
* `max_chat_output_tokens`: output token budget passed to the API and used for worst-case cost estimation
* `default_cost_limit`: default USD cost ceiling used when `gpt_parse(..., cost_limit=None)`

Any argument left as `None` leaves the existing value unchanged.

#### Inputs

* `max_chat_input_tokens`

    * **Type:** `Optional[int]`
    * **Meaning:** Maximum allowed prompt tokens for the `gpt_parse` request.
    * **Default:** `None` (do not change)

* `max_chat_output_tokens`

    * **Type:** `Optional[int]`
    * **Meaning:** Output token budget used when calling OpenAI and when estimating worst-case cost.
    * **Default:** `None` (do not change)

* `default_cost_limit`

    * **Type:** `Optional[float]`
    * **Meaning:** Default USD cost ceiling used by `gpt_parse` when `cost_limit` is not explicitly provided.
    * **Default:** `None` (do not change)

#### Outputs

Returns `None`.

#### Example

```python
compiler = CurlToolCompiler()

# Tighten ceilings for docs-heavy parsing sessions.
compiler.set_budget(
    max_chat_input_tokens=400,
    max_chat_output_tokens=800,
    default_cost_limit=0.01,
)

tool = await compiler.gpt_parse(docs_text, model_name="gpt-4o-mini")
```

### `CurlToolCompiler.parse`

```python
def parse(
    self,
    curl_text: str,
    *,
    description: Optional[str] = None,
    input_model: Optional[Type[BaseModel]] = None,
    output_model: Optional[Type[BaseModel]] = None,
) -> HttpTool
```

#### Behavior

Parses a practical subset of `curl` into an `HttpRequestSpec` and returns an `HttpTool`.

This method is deterministic. It delegates curl parsing to `parse_curl_command(...)`, then optionally attaches:

* `description` (stored on the spec)
* `input_model` (validated against `inputs` before sending the request)
* `output_model` (validated against JSON responses when possible)

#### Example

```python
compiler = CurlToolCompiler(secrets=SecretResolver(auto_dotenv=True))

curl_text = r"""
curl https://api.hubapi.com/crm/v3/objects/companies?limit={{limit}} \
  -H "Authorization: Bearer $HUBSPOT_TOKEN"
""".strip()

tool = compiler.parse(curl_text, description="HubSpot: list companies")
report = await tool.call({"limit": 10})
assert report.ok
```

### `CurlToolCompiler.request_schema`

```python
def request_schema(
    self,
    *,
    method: HttpMethod,
    url: str,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, str]] = None,
    body: Optional[Any] = None,
    body_mode: BodyMode = "json",
    auth: Optional[BasicAuthSpec] = None,
    timeout_s: Optional[float] = 30.0,
    follow_redirects: bool = False,
    verify_tls: bool = True,
    description: Optional[str] = None,
    input_model: Optional[Type[BaseModel]] = None,
    output_model: Optional[Type[BaseModel]] = None,
) -> HttpTool
```

#### Behavior

Constructs an `HttpRequestSpec` with no inference and returns an `HttpTool`.

Use this when you want full control over:

* method selection
* body encoding (`json`, `form`, `raw`)
* TLS verification and redirect policy
* timeouts
* optional Pydantic input/output validation

#### Example

```python
tool = compiler.request_schema(
    method="GET",
    url="https://api.hubapi.com/crm/v3/objects/companies",
    headers={"Authorization": "Bearer {{env:HUBSPOT_TOKEN}}"},
    params={"limit": "{{limit}}"},
    body=None,
    body_mode="json",
    description="HubSpot: list companies",
)

report = await tool.call({"limit": 10})
assert report.status_code == 200
```

### `CurlToolCompiler.request_schema_from_dict`

```python
def request_schema_from_dict(self, d: Mapping[str, Any]) -> HttpTool
```

#### Behavior

Deterministically rehydrates a tool spec produced by `HttpTool.to_dict()`.

Special fixup:

* if `body_mode == "form"`, it converts stored list pairs back into tuple pairs so form encoding works after JSON reload.

#### Example

```python
tool = compiler.parse(curl_text)
spec_dict = tool.to_dict()

tool2 = compiler.request_schema_from_dict(spec_dict)
report2 = await tool2.call({"limit": 10})
```

### `CurlToolCompiler.gpt_parse`

```python
async def gpt_parse(
    self,
    docs: str,
    *,
    model_name: str = "gpt-4o-mini",
    cost_limit: Optional[float] = None,
    debug: bool = False,
) -> HttpTool
```

#### Behavior

Extracts a request description from documentation text using OpenAI structured outputs, then compiles it into an `HttpTool`.

1. Requires `OPENAI_API_KEY` (or `openai_api_key` passed at compiler init). If missing, raises `RuntimeError`.
2. Optionally validates `model_name` by listing available OpenAI models (fail-open if listing fails).
3. Redacts probable secrets in `docs` before sending them to the model.
4. Enforces token and cost ceilings using `gpt_guardrails` (`count_chat_tokens`, `estimate_chat_request_cost`).
5. Calls `AsyncOpenAI.responses.parse(..., text_format=CurlToolBlueprint)`.
6. Converts the resulting `CurlToolBlueprint` into an `HttpRequestSpec` and returns an `HttpTool`.

The returned tool is no different from tools built via `parse(...)` or `request_schema(...)`.

#### Example

```python
compiler = CurlToolCompiler(
    secrets=SecretResolver(auto_dotenv=True),
    max_chat_input_tokens=600,
    max_chat_output_tokens=1200,
    default_cost_limit=0.02,
)

tool = await compiler.gpt_parse(docs_text, model_name="gpt-4o-mini")
spec_dict = tool.to_dict()
```

> [!NOTE]
> A common workflow is to run `gpt_parse` once, persist `tool.to_dict()`, and then use `request_schema_from_dict(...)` in production paths so the runtime is deterministic and does not depend on GPT.

## `parse_curl_command`

```python
def parse_curl_command(curl_text: str) -> HttpRequestSpec
```

### Behavior

Parses a practical subset of `curl` into an `HttpRequestSpec`. It is deterministic.

Supported curl features:

* URL: positional `https://...` or `--url`
* Method: `-X/--request`, or `-G/--get` (forces GET)
* Headers: `-H/--header "Key: Value"`
* Body:

  * `-d/--data/--data-raw/--data-binary/--data-ascii`
  * `--data-urlencode` (produces `body_mode="form"` and list of pairs)
* Basic auth: `-u user:pass`
* Redirects: `-L/--location`
* TLS verify disable: `-k/--insecure`
* Timeout: `--connect-timeout`, `-m/--max-time`

Environment variables:

* `$FOO` and `${FOO}` are converted to `{{env:FOO}}`
* escaped dollars are preserved (`\$FOO` stays `$FOO`)

Body inference:

* JSON is selected if Content-Type is JSON or payload looks like JSON
* form is selected if Content-Type is urlencoded or payload parses as `k=v&...`
* raw is selected otherwise

Special case:

* `-G/--get` plus `-d` treats the `-d` payload as query params (best-effort)

## Troubleshooting

* **My tool output is not a dict**
  `tool.call(...)` returns a `ToolCallReport`. Read `report.response_json` or `report.response_text` rather than assuming a dict return value.

* **Why is `response_json` missing?**
  JSON parsing is only attempted when the response content-type includes `application/json`. Otherwise the response is stored in `response_text`.

* **Form tools fail after reload**
  Reload via `request_schema_from_dict(...)`, not by manually feeding the dict into `request_schema(...)`. The rehydrator converts list pairs back to tuple pairs.

* **Template variables do not render**
  Missing env vars raise `KeyError` via `SecretResolver.require(...)`. Missing runtime variables raise `KeyError` in `_render_template_str(...)`.

* **`gpt_parse` fails with token/cost ceiling errors**
  Reduce the docs text, increase `max_chat_input_tokens`, reduce `max_chat_output_tokens`, or raise the cost limit.

<p align="center">
  <a href="code_tools.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.code_tools</b></code></a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="gpt_guardrails.md">Next: <code style="background: transparent;">Summoner<b>.gpt_guardrails</b></code> &raquo;</a>
</p>
