# The Zen of Summoner

> Essentials of Summoner’s coding style.

<p align="center">
  <img width="350px" src="../../assets/img/fundamentals_rounded.png" />
</p>

---

Summoner encourages a clear async style. Think in small steps: listen, decide, act, then return. Let the loop advance work while you wait for the next input. Handle one line at a time so behavior stays easy to trace. When a choice depends on earlier steps, make that history visible with simple states and move between them deliberately. The three pages below continue from here.

* **[Servers and relay](server_relay.md)**
  What the local server does as an untrusted relay, how Python and Rust versions differ, and how configuration is resolved.

* **[Clients and agents](client_agent.md)**
  How a Python client becomes an agent, how typed envelopes work, and how client config guides reconnection and send/receive limits.

* **[Agent design principles](design.md)**
  The receive → transition → send model, flows for explicit state, hooks for validation, and patterns that keep agents predictable.


<p align="center">
  <a href="../getting_started/quickstart/begin_async.md">&laquo; Previous: Beginner's Guide to Async Programming </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="server_relay.md">Next: Servers and Relay &raquo;</a>
</p>
