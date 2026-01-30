# <code style="background: transparent;">Summoner<b>.server</b></code>

The **server** layer runs the relay that connects clients. It accepts TCP connections, forwards messages (broadcast-style), and manages server lifecycle from a single entry point: `SummonerServer`.

Most users only touch this when they want to host a local relay or deploy a shared relay in an environment.

## References

* [<code style="background: transparent;">Summoner<b>.server.server</b></code>](./server/server.md) → `SummonerServer` API reference: constructor, lifecycle methods, and end-to-end examples.

* [<code style="background: transparent;">Summoner<b>.server</b></code> configuration guide](./server/config.md) → Configuration reference: keys, defaults, and how settings affect server behavior.

## Pick the right page

| You want to…                                                     | Go to                                     |
| ---------------------------------------------------------------- | ----------------------------------------- |
| Start a relay from Python and learn the callable methods         | `server.server`                        |
| Load configuration from JSON or a Python dict                     | `server.server` → `SummonerServer.run` |
| Understand what each config key means and how to tune behavior   | configuration guide                        |
| Copy a complete example configuration file                        | configuration guide → complete example     |

## Quick start in one file

```python
from summoner.server import SummonerServer

server = SummonerServer(name="summoner:server")
server.run(
    host="127.0.0.1",
    port=8888,
    config_path="server.json",   # or pass config_dict={...}
)
````

> [!TIP]
> Start with `config_dict` while iterating locally, then move the exact same structure into a JSON file and use `config_path` for reproducible deployments.

<p align="center">
  <a href="client.md">&laquo; Previous: <code style="background: transparent;">Summoner<b>.client</b></code></a>
  &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;
  <a href="proto.md">Next: <code style="background: transparent;">Summoner<b>.protocol</b></code> &raquo;</a>
</p>
