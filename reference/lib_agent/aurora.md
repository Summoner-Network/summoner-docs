# <code style="background: transparent;">Summoner<b>.aurora</b></code> (Aurora v1.0.0)

The **Aurora** layer extends the core client runtime with keyed receiver execution, Aurora-aware DNA replay, and a dedicated identity API for sessions, envelopes, continuity, and controls.

Most users start with `SummonerAgent` from `Summoner.aurora.agentclass`. Use `agentmerger` when you want to merge or rebuild Aurora clients from DNA, and use `identity` when you want the deeper identity reference for `SummonerIdentity`, `SummonerIdentityControls`, sessions, envelopes, continuity, and controls.

For installation and `build.txt` setup, see the [Agent Extensions](index.md) overview.

## Modules

* [<code style="background: transparent;">Summoner<b>.aurora.agentclass</b></code>](aurora/agent.md) → Aurora runtime built around `SummonerAgent`: construct an Aurora-aware client, attach identity, register `@keyed_receive(...)`, inspect replay state, and export Aurora DNA.

* [<code style="background: transparent;">Summoner<b>.aurora.agentmerger</b></code>](aurora/merger.md) → Aurora DNA composition utilities:

  * `AgentMerger`: merge imported Aurora clients and/or DNA into one composite Aurora client.
  * `AgentTranslation`: rebuild a fresh Aurora client from a DNA list while preserving Aurora keyed receiver behavior.

* [<code style="background: transparent;">Summoner<b>.aurora.identity</b></code>](aurora/identity/index.md) → identity classes and helpers:

  * `SummonerIdentity`: identity files, sessions, envelopes, continuity, and replay validation.
  * `SummonerIdentityControls`: reusable controls for custom storage, trust, audit, and policy behavior.

## Pick the right module

| You want to… | Go to |
| --- | --- |
| Build one Aurora-aware client and register keyed receivers | `aurora.agentclass` |
| Export or replay Aurora DNA without losing keyed receiver behavior | `aurora.agentclass` + `aurora.agentmerger` |
| Merge several Aurora sources into one client | `aurora.agentmerger` → `AgentMerger` |
| Rebuild one fresh Aurora client from DNA | `aurora.agentmerger` → `AgentTranslation` |
| Work with sessions, envelopes, continuity, and peer state | `aurora.identity` |
| Customize trust, storage, or policy controls | `aurora.identity` → `SummonerIdentityControls` |
| Review streaming, telemetry, metadata, or security notes | `aurora.identity` + companion pages |

## Capabilities at a glance

* **Keyed receiver execution**: serialize work per logical key while still allowing other keys to run concurrently.
* **Aurora-aware DNA portability**: preserve keyed receiver behavior during export and replay.
* **Reconstructed Aurora clients**: merge or translate DNA into a client that still behaves like Aurora.
* **Identity and continuity**: sessions, envelopes, replay checks, peer tracking, and security controls.

## Companion pages

* [Summoner Agent Identity](aurora/agent_identity.md) → identity-profile note for what the portable agent ID is, how it differs from fingerprints and local identity files, and which changes preserve continuity.

<p align="center">
  <a href="../index.md">&laquo; Previous: Agent Extensions</a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="aurora/agent.md">Next: <code style="background: transparent;">Summoner<b>.aurora.agentclass</b></code> &raquo;</a>
</p>
