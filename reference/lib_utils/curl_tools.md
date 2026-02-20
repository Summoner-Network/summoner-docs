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

## Installation in a summoner-sdk workflow

`curl_tools` is shipped as an extension module hosted in the `extension-utilities` repository. In a project based on the [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk) template, you add it to your SDK build list so it is included during composition.

### Add `curl_tools` to `build.txt`

Add the following entry to your SDK builder list (in the `build.txt` file):

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

## `SecretResolver.__init__`

```python
def __init__(
    self,
    mapping: Optional[Mapping[str, str]] = None,
    fallback: Optional[Callable[[str], Optional[str]]] = None,
    auto_dotenv: bool = False,
    dotenv_path: Optional[str] = None,
    dotenv_override: bool = False,
) -> None
```

### Behavior

Creates a secret resolver with a fixed resolution order:

1. explicit `mapping` passed at construction time
2. `os.environ`
3. optional `fallback(name)` callable

If `auto_dotenv=True`, the constructor loads environment variables via `dotenv.load_dotenv(...)`.

### Inputs

#### `mapping`

* **Type:** `Optional[Mapping[str, str]]`
* **Meaning:** Explicit secret mapping used as the highest-precedence source.
* **Default:** `None` (treated as empty)

#### `fallback`

* **Type:** `Optional[Callable[[str], Optional[str]]]`
* **Meaning:** Optional callable used when a name is missing from both `mapping` and `os.environ`.
* **Default:** `None`

#### `auto_dotenv`

* **Type:** `bool`
* **Meaning:** If `True`, loads `.env` variables during initialization.
* **Default:** `False`

#### `dotenv_path`

* **Type:** `Optional[str]`
* **Meaning:** Optional path passed to `load_dotenv(...)`.
* **Default:** `None`

#### `dotenv_override`

* **Type:** `bool`
* **Meaning:** Whether `.env` values override existing `os.environ`.
* **Default:** `False`

### Outputs

This constructor returns a `SecretResolver` instance.

### Examples

#### Load `.env` and require a token

```python
secrets = SecretResolver(auto_dotenv=True)
token = secrets.require("HUBSPOT_TOKEN")
```

## `SecretResolver.get`

```python
def get(self, name: str) -> Optional[str]
```

### Behavior

Returns the resolved secret value, or `None` if no source provides it.

Resolution order:

1. `mapping`
2. `os.environ`
3. `fallback(name)` if provided

### Inputs

#### `name`

* **Type:** `str`
* **Meaning:** Secret name to resolve.

### Outputs

Returns `Optional[str]`.

### Examples

```python
token = secrets.get("HUBSPOT_TOKEN")
if token is None:
    raise RuntimeError("Missing token")
```

## `SecretResolver.require`

```python
def require(self, name: str) -> str
```

### Behavior

Returns the resolved secret value.

If the secret is unavailable, raises:

* `KeyError(f"Missing required secret: {name}")`

### Inputs

#### `name`

* **Type:** `str`
* **Meaning:** Secret name to resolve.

### Outputs

Returns `str`.

### Examples

```python
token = secrets.require("HUBSPOT_TOKEN")
```

## `HttpRequestSpec.__init__`

```python
def __init__(
    self,
    method: HttpMethod,
    url: str,
    headers: dict[str, str] = ...,
    params: dict[str, str] = ...,
    body: Optional[Any] = None,
    body_mode: BodyMode = "json",
    auth: Optional[BasicAuthSpec] = None,
    timeout_s: Optional[float] = 30.0,
    follow_redirects: bool = False,
    verify_tls: bool = True,
    description: Optional[str] = None,
    input_model: Optional[Type[BaseModel]] = None,
    output_model: Optional[Type[BaseModel]] = None,
) -> None
```

### Behavior

Creates a deterministic HTTP request specification consumed by `HttpTool`.

The spec is intentionally close to the arguments accepted by `httpx.AsyncClient.request(...)`, but keeps a stable structure that can be persisted and reloaded.

It describes:

* how to reach the endpoint (`method`, `url`, `params`)
* how to authenticate or identify the caller (`headers`, optional `auth`)
* how to encode the request body (`body`, `body_mode`)
* how to control transport behavior (`timeout_s`, `follow_redirects`, `verify_tls`)
* optional metadata and validation (`description`, `input_model`, `output_model`)

Body conventions:

* `body_mode="json"`

  * if `body` is a `dict` or `list`, it is sent as JSON
  * if `body` is a `str`, it is sent as raw `content`

* `body_mode="form"`

  * `body` may be a `dict`, a `list[tuple[str, str]]`, or a raw string like `"a=1&b=2"`
  * the runtime encodes the body as `application/x-www-form-urlencoded`

* `body_mode="raw"`

  * `body` is sent as raw `content`
  * if `body` is a `dict` or `list`, it is stringified using `json.dumps(...)` first

### Inputs

#### `method`

* **Type:** `HttpMethod`
* **Meaning:** HTTP method used for the request.

#### `url`

* **Type:** `str`
* **Meaning:** Endpoint URL. May include `{{env:...}}` and `{{var}}` placeholders.

#### `headers`

* **Type:** `dict[str, str]`
* **Meaning:** Request headers after templating.
* **Default:** `{}`

#### `params`

* **Type:** `dict[str, str]`
* **Meaning:** Query parameters after templating.
* **Default:** `{}`

#### `body`

* **Type:** `Optional[Any]`
* **Meaning:** Request body payload. Interpreted according to `body_mode`.
* **Default:** `None`

#### `body_mode`

* **Type:** `BodyMode`
* **Meaning:** Body encoding mode (`"json"`, `"form"`, `"raw"`).
* **Default:** `"json"`

#### `auth`

* **Type:** `Optional[BasicAuthSpec]`
* **Meaning:** Optional basic auth credentials.
* **Default:** `None`

#### `timeout_s`

* **Type:** `Optional[float]`
* **Meaning:** Timeout in seconds passed to `httpx`.
* **Default:** `30.0`

#### `follow_redirects`

* **Type:** `bool`
* **Meaning:** Whether redirects are followed by `httpx`.
* **Default:** `False`

#### `verify_tls`

* **Type:** `bool`
* **Meaning:** Whether TLS certificates are verified by `httpx`.
* **Default:** `True`

#### `description`

* **Type:** `Optional[str]`
* **Meaning:** Optional human-readable description stored on the spec.
* **Default:** `None`

#### `input_model`

* **Type:** `Optional[Type[BaseModel]]`
* **Meaning:** Optional Pydantic model used to validate inputs before templating.
* **Default:** `None`

#### `output_model`

* **Type:** `Optional[Type[BaseModel]]`
* **Meaning:** Optional Pydantic model used to validate JSON responses when possible.
* **Default:** `None`

### Outputs

This constructor returns an `HttpRequestSpec` instance.

## `HttpRequestSpec.to_dict`

```python
def to_dict(self, *, include_models: bool = False) -> dict[str, Any]
```

### Behavior

Returns a JSON-safe snapshot of the spec intended for persistence and later rehydration via `CurlToolCompiler.request_schema_from_dict(...)`.

Serialization is best-effort:

* tuples become lists
* dataclasses become dict-like structures
* objects that are not JSON-friendly are stringified
* `input_model` and `output_model` are omitted by default

If `include_models=True`, the snapshot includes best-effort import paths for `input_model` and `output_model`. Model rehydration is intentionally not automatic.

### Inputs

#### `include_models`

* **Type:** `bool`
* **Meaning:** Whether to include best-effort model import paths in the snapshot.
* **Default:** `False`

### Outputs

Returns a JSON-safe `dict[str, Any]`.

## `HttpRequestSpec.to_request_schema_kwargs`

```python
def to_request_schema_kwargs(self) -> dict[str, Any]
```

### Behavior

Returns Python-native kwargs suitable for rebuilding a tool through:

```python
tool2 = compiler.request_schema(**kwargs)
```

This is a round-trip convenience when you do not want JSON serialization to coerce types. For example, tuple pairs in form bodies and Pydantic model types remain intact.

Important distinction:

* `to_request_schema_kwargs()` returns Python-native values
* `to_dict()` returns JSON-safe values

### Outputs

Returns a `dict[str, Any]` intended to be passed directly into `CurlToolCompiler.request_schema(...)`.

### Examples

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

## `HttpTool.__init__`

```python
def __init__(self, spec: HttpRequestSpec, secrets: Optional[SecretResolver] = None) -> None
```

### Behavior

Creates an async callable tool around a fixed `HttpRequestSpec`.

* Stores the request spec on `self.spec`.
* Stores a `SecretResolver` on `self.secrets`. If none is provided, a default resolver is created.

This constructor does not execute any request. Execution happens only when you call `await tool.call(...)`.

### Inputs

#### `spec`

* **Type:** `HttpRequestSpec`
* **Meaning:** Deterministic request description executed by this tool.

#### `secrets`

* **Type:** `Optional[SecretResolver]`
* **Meaning:** Resolver used to satisfy `{{env:NAME}}` placeholders at runtime.
* **Default behavior:** If not provided, a default `SecretResolver()` is created.

### Outputs

This constructor returns an `HttpTool` instance.

### Examples

```python
compiler = CurlToolCompiler()
tool = compiler.parse(curl_text)
```

## `HttpTool.call`

```python
async def call(self, inputs: Optional[dict[str, Any]] = None) -> ToolCallReport
```

### Behavior

Executes the request and returns a `ToolCallReport`.

Steps:

1. If `spec.input_model` exists, validates `inputs` via Pydantic and replaces `inputs` with the validated dump.
2. Renders templates in URL, headers, params, and body.
3. Applies Basic Auth if `spec.auth` is set, after template rendering.
4. Applies default `Content-Type` based on `body_mode` if missing.
5. Sends the HTTP request via `httpx.AsyncClient`.
6. Attempts JSON parsing when the response `content-type` includes `application/json`.
7. If `spec.output_model` exists, validates `response_json` and fills validation fields.
8. Returns a report with request summary, status, timing, and parsed response fields.

Request error behavior:

* On network or client exceptions, returns a report with:

  * `ok=False`
  * `status_code=0`
  * `response_text="Request error: ..."`

### Inputs

#### `inputs`

* **Type:** `Optional[dict[str, Any]]`
* **Meaning:** Runtime values used to render `{{var}}` placeholders, and optionally validated by `spec.input_model`.
* **Default:** `None` (treated as empty dict)

### Outputs

Returns a `ToolCallReport` instance.

### Examples

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

## `HttpTool.to_dict`

```python
def to_dict(self, *, include_models: bool = False) -> dict[str, Any]
```

### Behavior

Returns a JSON-safe snapshot of the underlying `HttpRequestSpec`.

This is a convenience wrapper around:

```python
tool.spec.to_dict(include_models=include_models)
```

The snapshot is intended for deterministic persistence and later rehydration using:

```python
tool2 = compiler.request_schema_from_dict(spec_dict)
```

Model handling:

* `input_model` and `output_model` are omitted by default
* if `include_models=True`, the snapshot includes best-effort import paths for `input_model` and `output_model`
* model rehydration is intentionally not automatic

### Inputs

#### `include_models`

* **Type:** `bool`
* **Meaning:** Whether to include best-effort model import paths.
* **Default:** `False`

### Outputs

Returns a JSON-safe `dict[str, Any]`.

### Examples

```python
spec_dict = tool.to_dict()
tool2 = compiler.request_schema_from_dict(spec_dict)
report = await tool2.call({"response_id": "resp_..."})
```

## `CurlToolCompiler.__init__`

```python
def __init__(
    self,
    *,
    secrets: Optional[SecretResolver] = None,
    openai_api_key: Optional[str] = None,
    auto_dotenv: bool = True,
    dotenv_path: Optional[str] = None,
    dotenv_override: bool = False,
    max_chat_input_tokens: int = 600,
    max_chat_output_tokens: int = 1200,
    default_cost_limit: Optional[float] = None,
    validate_model_name: bool = True,
) -> None
```

### Behavior

Creates a compiler used to build `HttpTool` instances from either deterministic inputs or GPT-assisted extraction.

Constructor responsibilities:

* Optionally loads `.env` via `load_dotenv(...)` when `auto_dotenv=True`.
* Stores a `SecretResolver` on `self.secrets`. If none is provided, a default resolver is created.
* Configures budgeting parameters used by `gpt_parse(...)`.
* If an OpenAI API key is available, initializes an `AsyncOpenAI` client for `gpt_parse(...)`.
* If `validate_model_name=True`, it may attempt to list available model IDs. If model listing fails, it fails open and continues without blocking `gpt_parse(...)`.

### Inputs

#### `secrets`

* **Type:** `Optional[SecretResolver]`
* **Meaning:** Secret resolver used for `{{env:...}}` placeholders at runtime.
* **Default behavior:** If not provided, a default resolver is created.

#### `openai_api_key`

* **Type:** `Optional[str]`
* **Meaning:** Optional API key used for `gpt_parse(...)`.
* **Default behavior:** If omitted, the constructor reads `OPENAI_API_KEY` from the environment.

#### `auto_dotenv`

* **Type:** `bool`
* **Meaning:** Whether to load `.env` variables during initialization.
* **Default:** `True`

#### `dotenv_path`

* **Type:** `Optional[str]`
* **Meaning:** Optional path passed to `load_dotenv(...)`.
* **Default:** `None`

#### `dotenv_override`

* **Type:** `bool`
* **Meaning:** Whether `.env` values override existing `os.environ`.
* **Default:** `False`

#### `max_chat_input_tokens`

* **Type:** `int`
* **Meaning:** Prompt token ceiling enforced by `gpt_parse(...)`.
* **Default:** `600`

#### `max_chat_output_tokens`

* **Type:** `int`
* **Meaning:** Output token budget used for API calls and worst-case cost estimation.
* **Default:** `1200`

#### `default_cost_limit`

* **Type:** `Optional[float]`
* **Meaning:** Default USD cost ceiling used when `gpt_parse(..., cost_limit=None)`.
* **Default:** `None`

#### `validate_model_name`

* **Type:** `bool`
* **Meaning:** Whether `gpt_parse(...)` validates `model_name` against a best-effort model list.
* **Default:** `True`

### Outputs

This constructor returns a `CurlToolCompiler` instance.

### Examples

```python
compiler = CurlToolCompiler(secrets=SecretResolver(auto_dotenv=True))
tool = compiler.parse(curl_text)
```

## `CurlToolCompiler.set_budget`

```python
def set_budget(
    self,
    *,
    max_chat_input_tokens: Optional[int] = None,
    max_chat_output_tokens: Optional[int] = None,
    default_cost_limit: Optional[float] = None,
) -> None
```

### Behavior

Updates the budgeting parameters used by `CurlToolCompiler.gpt_parse(...)`.

This method does not affect deterministic compilation (`parse(...)`, `request_schema(...)`) or runtime execution (`HttpTool.call(...)`). It only changes the ceilings enforced before making an OpenAI call inside `gpt_parse(...)`.

Fields updated:

* `max_chat_input_tokens`: prompt token ceiling (measured with `count_chat_tokens(...)`)
* `max_chat_output_tokens`: output token budget passed to the API and used for worst-case cost estimation
* `default_cost_limit`: default USD cost ceiling used when `gpt_parse(..., cost_limit=None)`

Any argument left as `None` leaves the existing value unchanged.

### Inputs

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

### Outputs

Returns `None`.

### Example

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

## `CurlToolCompiler.parse`

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

### Behavior

Parses a practical subset of `curl` into an `HttpRequestSpec` and returns an `HttpTool`.

This method is deterministic. It delegates curl parsing to `parse_curl_command(...)`, then optionally attaches:

* `description` (stored on the spec)
* `input_model` (validated against `inputs` before sending the request)
* `output_model` (validated against JSON responses when possible)

### Example

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

## `CurlToolCompiler.request_schema`

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

### Behavior

Constructs an `HttpRequestSpec` with no inference and returns an `HttpTool`.

Use this when you want full control over:

* method selection
* body encoding (`json`, `form`, `raw`)
* TLS verification and redirect policy
* timeouts
* optional Pydantic input/output validation

### Example

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

## `CurlToolCompiler.request_schema_from_dict`

```python
def request_schema_from_dict(self, d: Mapping[str, Any]) -> HttpTool
```

### Behavior

Deterministically rehydrates a tool spec produced by `HttpTool.to_dict()`.

Special fixup:

* if `body_mode == "form"`, it converts stored list pairs back into tuple pairs so form encoding works after JSON reload.

### Example

```python
tool = compiler.parse(curl_text)
spec_dict = tool.to_dict()

tool2 = compiler.request_schema_from_dict(spec_dict)
report2 = await tool2.call({"limit": 10})
```

## `CurlToolCompiler.gpt_parse`

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

### Behavior

Extracts a request description from documentation text using OpenAI structured outputs, then compiles it into an `HttpTool`.

1. Requires `OPENAI_API_KEY` (or `openai_api_key` passed at compiler init). If missing, raises `RuntimeError`.
2. Optionally validates `model_name` by listing available OpenAI models (fail-open if listing fails).
3. Redacts probable secrets in `docs` before sending them to the model.
4. Enforces token and cost ceilings using `gpt_guardrails` (`count_chat_tokens`, `estimate_chat_request_cost`).
5. Calls `AsyncOpenAI.responses.parse(..., text_format=CurlToolBlueprint)`.
6. Converts the resulting `CurlToolBlueprint` into an `HttpRequestSpec` and returns an `HttpTool`.

The returned tool is no different from tools built via `parse(...)` or `request_schema(...)`.

### Example

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

## Behavior

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
