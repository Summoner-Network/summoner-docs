# The Feel of an MMO, Not an API Gateway

Summoner is TCP-native and stream-first. Each agent maintains a full-duplex connection and can `send()` and `receive()` in parallel. Agents are not constrained by HTTP’s single-request semantics. They support multiple conversations, real-time streams, and binary payloads by default.

This makes the system feel more like a multiplayer world than a menu of functions. Agents move, interact, and coordinate continuously. There is no need to route messages through a central orchestrator. No single host owns the session.

Most frameworks resemble API gateways. You issue a function call, get a response, and repeat. To do two things at once, you must manage batches or multiple channels.

Summoner changes that. With TCP streams and optional shared memory, agents:

* Communicate in parallel with many peers
* Share updates and data in real time
* Collaborate at low latency across networks

This architecture supports:

* Presence broadcasting
* Live tool exchange
* Real-time group behavior (e.g., for simulations or co-processing)

Frameworks like MCP and A2A emphasize controlled workflows with centralized coordination. Summoner supports open-ended interaction among autonomous agents.

<span style="position: relative; top: -6px; font-size: 0.9em;"><em><u>Page content covered</u></em></span>&nbsp; ![](https://progress-bar.xyz/100)