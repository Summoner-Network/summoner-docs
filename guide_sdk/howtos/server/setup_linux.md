# Set up a Server on Linux

## ✅ Summoner Server Setup Checklist (LAN + WAN)

---

### 🧭 Step 0: Overview

You'll set up:

* A server bound to `0.0.0.0` on port `8888`
* A fixed local IP for the server
* A port forwarding rule from your router's WAN IP to your server
* Optional: Firewall rule to allow the connection

---

### 🧩 Step 1: Get Local IP and MAC Address (on server)

Run:

```bash
ip a | grep inet
ip a | grep ether
```

✅ **Checkpoint:**

* Write down your **LAN IP** (e.g., `192.168.1.229`)
* Write down your **MAC address** (e.g., `cc:15:31:d9:ae:e0`)

  * It's usually under your active Wi-Fi or Ethernet interface

---

### 📡 Step 2: Configure Static IP in Router

In your router admin panel:

1. Go to the **LAN > Static DHCP** or **Address Reservation** section
2. Match your **MAC address** to a **fixed IP**, e.g., `192.168.1.229`
3. Save, apply, and **reboot your server or reconnect Wi-Fi**

✅ **Checkpoint:**

* Run `ip a` again and confirm the IP is now fixed to `192.168.1.229`

---

### 🛡️ Step 3: Allow Incoming Port on Server

If you use a firewall (e.g. `ufw`), open the port:

```bash
sudo ufw allow 8888
```

✅ **Checkpoint:**

* Run `ss -tuln | grep 8888` and confirm your server is listening on `0.0.0.0:8888`

---

### 🌍 Step 4: Find Your WAN IP

On the server:

```bash
curl ifconfig.me
```

✅ **Checkpoint:**

* Note your **WAN IP**, e.g., `12.34.456.789`

---

### 🔁 Step 5: Set Up Port Forwarding in Router

In your router:

1. Go to **Port Forwarding** / **NAT**
2. Create a rule:

   * **External Port**: `8888`
   * **Internal IP**: `192.168.1.229`
   * **Internal Port**: `8888`
   * **Protocol**: TCP (or TCP+UDP)

✅ **Checkpoint:**

* External port `8888` forwards to internal server at `192.168.1.229:8888`

---

### 📶 Step 6: Connect from a Client

#### 🧪 A. Local test (same Wi-Fi):

```python
reader, writer = await asyncio.open_connection('192.168.1.229', 8888)
```

#### 🌐 B. WAN test (different network — e.g., phone hotspot):

```python
reader, writer = await asyncio.open_connection('12.34.456.789', 8888)
```

✅ **Checkpoint:**

* Connection succeeds and the server logs incoming traffic

---

### 🧪 Optional: Port open test from outside

Go to [https://canyouseeme.org](https://canyouseeme.org), enter port `8888`, and test.

Or from CLI (external device):

```bash
nc -vz 12.34.456.789 8888
```



<p align="center">
<a href="../client/async_task.md">&laquo; Previous: Define Agent Behavior as Asynchronous Tasks
 </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="setup_macos.md">Next: Set up a Server on macOS &raquo;</a>
</p>