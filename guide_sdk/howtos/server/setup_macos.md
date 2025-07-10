# Set up a Server on MacOS


## ✅ macOS-Compatible Version of the Server Setup Checklist

---

### 🧩 Step 1: Get Local IP and MAC Address (on macOS)

#### 🔍 Find LAN IP:

```bash
ipconfig getifaddr en0         # For Wi-Fi
ipconfig getifaddr en1         # For Ethernet (if used)
```

#### 🔍 Find MAC address:

```bash
ifconfig en0 | grep ether
```

✅ **Checkpoint:**

* LAN IP → e.g., `192.168.1.229`
* MAC address → e.g., `cc:15:31:d9:ae:e0`

---

### 📡 Step 2: Set a Static IP in Your Router

Same as before — go into your router admin panel:

* Bind the MAC address to IP `192.168.1.229` under:

  * **Static DHCP**
  * **Address Reservation**
  * Or **LAN > Bind IP to MAC**

✅ Confirm it sticks after reboot:

```bash
ipconfig getifaddr en0
```

---

### 🛡️ Step 3: Allow Incoming Port (macOS Firewall)

* Open **System Preferences > Security & Privacy > Firewall**
* Click **Firewall Options**
* If enabled, ensure your Python app is allowed to accept incoming connections, or disable the firewall temporarily for testing

✅ You can also use the CLI:

```bash
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate off   # disables firewall
```

---

### 📶 Step 4: Check Listening Server Port

macOS doesn't have `ss`, but you can use `lsof`:

```bash
sudo lsof -iTCP:8888 -sTCP:LISTEN
```

✅ Confirms your server is bound to `0.0.0.0:8888`

---

### 🌍 Step 5: Get WAN IP

Same as Linux:

```bash
curl ifconfig.me
```

---

### 🔁 Step 6: Port Forwarding

Same router instructions as on Linux apply.

---

### ✅ Summary of macOS Equivalents

| Purpose            | Linux                | macOS                               |              |
| ------------------ | -------------------- | ----------------------------------- | ------------ |
| Get local IP       | `ip a`               | `ipconfig getifaddr en0`            |              |
| Get MAC address    | `ip a` or `ifconfig` | \`ifconfig en0                      | grep ether\` |
| Show open port     | `ss -tuln`           | `sudo lsof -iTCP:8888 -sTCP:LISTEN` |              |
| Check WAN IP       | `curl ifconfig.me`   | same                                |              |
| Open firewall port | `ufw allow 8888`     | GUI or `socketfilterfw` commands    |              |



<p align="center">
<a href="setup_linux.md">&laquo; Previous: Define Agent Behavior as Asynchronous Tasks
 </a> &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <a href="to_internet.md">Next: Router setup to open a NAT server &raquo;</a>
</p>