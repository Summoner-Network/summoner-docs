# Servers and Relay

Explain 
rust and python

agent identities

## Configuration
Explain very well the config (each parameter has a small paragraph or section)

## Validation
Explain the programmation with json file

------------


# Servers and Relay

> Explore how the Summoner relay routes messages between agents, manages identities, and enforces configuration and validation—available as both Python and Rust implementations.

**Purpose & audience**  
- **Who:** Developers deploying, configuring, or extending a Summoner relay  
- **What:**  
  1. Implementation options (Python vs Rust)  
  2. Agent identity management  
  3. Detailed configuration parameters  
  4. JSON-based validation of messages and configs  
- **Outcome:** A tunable, production-ready relay scaffold with built-in safeguards

---

## 1. Python vs Rust Implementations

Summoner provides two relay binaries—choose based on your performance and debugging needs:

### 1.1 Python Relay

- **Pros:**  
  - Fast iteration, easy to debug  
  - Hot-reload support in dev  
- **Cons:**  
  - Higher CPU usage under load  
  - Limited to single-threaded throughput

**Launch example**  
```bash
summoner-server start --config=config.yaml
````

### 1.2 Rust Relay

* **Pros:**

  * High throughput, low latency
  * Optimized for multi-core servers
* **Cons:**

  * Requires Rust toolchain and build step
  * Longer compile times

**Launch example**

```bash
summoner-server-rust start --config=config.yaml
```

---

## 2. Agent Identities

The relay uses agent identities to route and monitor traffic securely:

* **Registration**

  * Agents send a unique `client_name` on connect
  * Server logs `Client connected: <client_name>`
* **Authentication hooks**

  * Optional pre-connect validations (e.g., token or certificate)
  * Custom logic in a “handshake” plugin (see advanced contribution guide)
* **Metrics & quotas**

  * Track per-agent message rates and connection durations
  * Enforce limits from config (e.g., `max_connections_per_agent`)

> **Sample copy:**
> “Each agent must present a unique name. For sensitive deployments, implement a handshake plugin to verify tokens before accepting messages.”

---

## 3. Configuration

Your relay reads a YAML or JSON config file. Below are common parameters; each can be overridden by CLI flags.

```yaml
host: 0.0.0.0            # interface to bind
port: 8000               # TCP port to listen on
max_connections: 200     # total simultaneous agent sockets
max_per_agent: 5         # throttle per-agent concurrency
log_level: INFO          # DEBUG, INFO, WARN, ERROR
metrics_endpoint: true   # expose Prometheus metrics on /metrics
validation_schema:       # path to JSON Schema for message validation
  config: "schema/config.json"
  message: "schema/message.json"
```

### 3.1 Host & Port

* **`host`**: IP/interface (default `0.0.0.0`)
* **`port`**: TCP port (default `8000`)

### 3.2 Connection Limits

* **`max_connections`**: global socket limit
* **`max_per_agent`**: per-agent channel cap

### 3.3 Logging & Metrics

* **`log_level`**: verbosity of server logs
* **`metrics_endpoint`**: enable Prometheus scraping

### 3.4 Validation Schemas

* **`validation_schema.config`**: JSON Schema for your config file
* **`validation_schema.message`**: JSON Schema for inbound messages

---

## 4. Validation

The relay can validate both its own config and all inbound message payloads against JSON Schemas.

### 4.1 Config Validation

* Automatic schema check at startup
* Fails fast on missing or malformed fields

### 4.2 Message Validation

* Rejects messages that don’t match the schema
* Returns a structured error to the sender
* Example schema field:

  ```json
  {
    "type": "object",
    "properties": {
      "route": { "type": "string" },
      "payload": {}
    },
    "required": ["route", "payload"]
  }
  ```

> **Sample copy:**
> “Enable schema validation to catch misconfigured clients or malformed messages before they disrupt your system. Validation errors appear in the server log with detailed diagnostics.”

---

<p align="center">
  <a href="client_agent.md">&laquo; Previous: Clients and Agents</a>
  &nbsp;|&nbsp;
  <a href="traveling.md">Next: Traveling Between Servers &raquo;</a>
</p>




<p align="center">
  <a href="client_agent.md">&laquo; Previous: Clients and Agents </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="traveling.md">Next: Traveling Between Servers &raquo;</a>
</p>
