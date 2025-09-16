# Creating an Agent Class

There are two good paths. You can help shape the official `SummonerAgent` classes in the [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass) repository, or you can publish your own module built on `SummonerClient` using the [`starter-template`](https://github.com/Summoner-Network/starter-template) and include it in an SDK with [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk). If you are new to Summoner, start with a small module. It lets you move quickly while staying aligned with the core.

**Shaping the official class.** Proposals land as issues in [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass). Make a clear case for the change, then show it working. A small fork or throwaway repo is perfect. A short screen recording that walks through the problem, the proposed behavior, and the outcome goes a long way. The core team curates the official class, so proposals that are narrowly scoped, compatible with Flow and our decorators, and focused on safety tend to be accepted.

## How to shape the official `SummonerAgent`

Start by opening an issue in [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass) with a crisp problem statement and the smallest behavior change that solves it. Include:

* **What hurts today.** A concrete scenario that fails or is awkward.
* **What you propose.** Describe the smallest API surface or decorator shape that addresses it.
* **Why it belongs here.** Explain why this should live in the official class rather than as a module. Think security, interop, or broad utility.
* **Evidence.** Link a tiny fork or test repo and add a short video (2–5 minutes) that shows before and after. A terminal run or local UI is enough.

A simple issue template you can paste:

```markdown
### Problem
What fails or is awkward today. One paragraph and a tiny repro if possible.

### Proposed change
Smallest addition to the official class (API shape or decorator), expected behavior, and defaults.

### Why official (vs module)
Security, Flow integration, cross-agent consistency, or other reasons.

### Demo
Repo/fork link + 2–5 min screencast (before → after). Include exact commit or tag.

### Compatibility & limits
Flow/route notes, expected performance, edge cases, and what is explicitly out of scope.
```

What happens next: we discuss scope in the issue, may ask for a tighter repro, and decide between integrating into the official class or recommending the module path. If it lands, we capture it in a new release folder so you can pin or upgrade cleanly.

## Why decorators are the center of the design

In Summoner, an agent's behavior is attached to a client through **decorators**. The core already provides `@receive`, `@send`, and `@hook`. Your own framework should look and feel the same so that tools, logs, and the runtime treat your handlers just like native ones. Beyond message handling, similar patterns can be used to compose agent identities, apply cryptographic envelopes, and add validation or policy—see the API catalog for the full surface.

A decorator in Python is just syntax sugar for “wrap this function with another function.” The minimal idea looks like this:

```python
def simple_decorator(fn):
    async def wrapped(*args, **kwargs):
        # do something before
        result = await fn(*args, **kwargs)
        # do something after
        return result
    return wrapped
```

With Summoner you usually do not replace the function object. Instead, you **register** it with the client so the runtime can route messages to it. That registration must happen safely on the client's event loop and with the same metadata the core uses.

## The anatomy of a Summoner-style decorator

When you create a new decorator for your framework, think in four steps.

**First, validate the handler.** Use the core helper `_check_param_and_return` to check that the function is `async`, accepts the right parameters, and returns the expected types. This keeps your behavior consistent with `@receive` and `@send`.

**Second, capture “DNA.”** Store a small record of the decorated function—route, priority, and the function's source—in `self._dna_receivers`, `self._dna_senders`, or `self._dna_hooks`. This allows tooling to serialize your agent, diff changes, and reconstruct handlers during SDK assembly.

**Third, register the callable.** Create a `Receiver` (or `Sender`) and place it into the client's indexes. If Flow is enabled on the client, always normalize the route with `Flow.parse_route(...)` before you register it. Use the client's locks (`routes_lock`, `hooks_lock`) when touching shared state.

**Fourth, schedule the registration.** Never mutate the routing tables directly from the call site. Wrap the registration in a small `async def register()` coroutine and submit it with `self._schedule_registration(register())`. The client will complete all scheduled registrations before it starts.

These steps are already embodied in the core decorators. Reusing them gives you the same safety and observability without rewriting the runtime. The example below shows a **receive-like** decorator purely as an illustration; you can apply the same pattern to `@send`-style emitters, `@hook` transforms, identity or crypto helpers, and other extension points. For additional attributes, types, and helpers you can compose, see the API reference at [`summoner-docs › reference`](https://github.com/Summoner-Network/summoner-docs/blob/main/reference/index.md).

## A minimal “receive-like” decorator

This is the smallest useful template. It shows how to accept a route, validate the handler, capture DNA, register a `Receiver`, and schedule the registration. Replace the marked comments with your behavior, but keep the overall shape.

```python
import inspect
from typing import Awaitable, Callable, Optional, Union, Any
from summoner.client import SummonerClient
from summoner.protocol.triggers import Event
from summoner.protocol.process import Receiver
from summoner.protocol.validation import _check_param_and_return

class MyAgent(SummonerClient):
    def my_receive(
        self,
        route: str,
        *,
        priority: Union[int, tuple[int, ...]] = (),
    ):
        route = route.strip()

        def decorator(fn: Callable[[Union[str, dict, Any]], Awaitable[Optional[Event]]]):
            # 1) Safety checks
            if not inspect.iscoroutinefunction(fn):
                raise TypeError(f"@my_receive handler '{fn.__name__}' must be async")

            _check_param_and_return(
                fn,
                decorator_name="@my_receive",
                allow_param=(str, dict, object),
                allow_return=(type(None), Event),
                logger=self.logger,
            )

            tuple_priority = (priority,) if isinstance(priority, int) else tuple(priority)

            # 2) DNA capture
            self._dna_receivers.append({
                "fn": fn,
                "route": route,
                "priority": tuple_priority,
                "source": inspect.getsource(fn),
            })

            # 3) Registration (wrap here if you add behavior)
            async def register():
                wrapped = fn  # replace with a wrapper if you enforce extra policy
                receiver = Receiver(fn=wrapped, priority=tuple_priority)

                if self._flow.in_use:
                    parsed = self._flow.parse_route(route)
                    norm = str(parsed)
                    async with self.routes_lock:
                        self.receiver_parsed_routes[norm] = parsed
                        self.receiver_index[norm] = receiver
                else:
                    async with self.routes_lock:
                        self.receiver_index[route] = receiver

            # 4) Schedule onto the client loop
            self._schedule_registration(register())
            return fn

        return decorator
```

This template is enough to get you started. You can register dozens of handlers this way and they will participate in routing, Flow, and logging like any built-in decorator.

## Adding behavior without changing the runtime

Many useful frameworks add policy around the handler while leaving the runtime alone. Two common examples are per-entity serialization and replay protection.

**Per-entity serialization** keeps only one handler running at a time for a given key, while allowing other keys to proceed. You implement it by computing a key from the payload, acquiring a per-key asynchronous lock, and releasing it when the handler completes. The lock lives on the agent instance so all handlers can share it.

```python
# inside register(), replace `wrapped = fn` with a tiny wrapper:

async def wrapped(payload):
    k = key_from(payload)         # for example: payload["account_id"]
    async with self._mutex.lock(("my_receive", route, k)):
        return await fn(payload)
```

**Replay protection** drops stale or duplicate messages. Extract a monotonic sequence number, compare it to the last one seen for `(route, key)`, and skip if it is not strictly newer. Keep this state in memory unless your design needs cross-process guarantees.

```python
async def wrapped(payload):
    k = key_from(payload)
    s = seq_from(payload)         # for example: payload["seq"]
    last = self._last_seq.get((route, k))
    if last is not None and s <= last:
        return None
    self._last_seq[(route, k)] = s
    return await fn(payload)
```

Both of these patterns sit entirely inside your wrapper. The rest of the decorator—validation, DNA, registration, scheduling—stays the same and continues to use the core machinery.

## Decorators that take arguments: the three-layer pattern

A decorator with arguments is a **factory**. It returns the actual decorator, which returns the wrapped function. In practice you will see three levels.

1. The **factory** that captures options, for example `route`, `priority`, or your custom flags.
2. The **decorator** that receives the handler function and performs validation and DNA capture.
3. The **wrapper or register step** that wires the function into the client.

Here is the smallest clear example:

```python
class MyAgent(SummonerClient):
    def throttle(self, *, per_second: float):
        # 1) factory level: capture options
        def decorator(fn):
            # 2) decorator level: validate and record DNA if you expose this as a receiver/sender
            async def register():
                # 3) registration level: wrap with behavior and register as needed
                async def wrapped(*args, **kwargs):
                    await self._rate_limiter.wait(per_second)
                    return await fn(*args, **kwargs)
                # register `wrapped` as a hook or use it inside a my_receive/send, depending on design
            self._schedule_registration(register())
            return fn
        return decorator
```

Notice how the factory receives configuration once, while the inner wrapper runs on every call. Keep the wrapper tiny so it does not become a bottleneck.

## Putting it all together

Create a repository from the [`starter-template`](https://github.com/Summoner-Network/starter-template). Add your package under `tooling/`. Write one or two decorators that wrap the core behavior, following the four steps above. Assemble an SDK with [`summoner-sdk`](https://github.com/Summoner-Network/summoner-sdk) so you can import your package alongside the official agent classes. Write one minimal example that shows your decorator working in isolation. Keep configuration in `.env` or flags, avoid secrets in code, and tag releases so `build.txt` can pin versions.

If you want a change to land in the official `SummonerAgent`, open a design issue in [`summoner-agentclass`](https://github.com/Summoner-Network/summoner-agentclass) describing the problem, the smallest surface that solves it, and a link to your minimal example. We will help you decide whether it belongs in the core set or is better as a module.

<p align="center">
  <a href="server_code.md">&laquo; Previous: Contributing to the Server Code Base </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="../../faq/index.md">Next: Frequently Asked Questions &raquo;</a>
</p>
