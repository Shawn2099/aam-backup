# Wake-on-LAN (WoL) Findings

**Date:** 2026-05-23
**Environment:** Server 1 (`100.109.221.40`) → Server 2 (`10.10.186.231`, MAC `6C-4B-90-25-70-5F`)
**OS:** Both Windows Server 2016

---

## Problem 1: Unicast WoL Doesn't Wake Sleeping Machines

**Symptom:** `send_magic_packet(mac, server_ip)` used `server_ip` (e.g., `10.10.186.231`) as destination. Server 2 was shut down — ping from Server 1 reported "online after 15s" but the machine was actually still off.

**Root cause:** The `wakeonlan` library's `ip_address` parameter is the **destination** IP for the magic packet. A sleeping NIC cannot receive unicast traffic. The magic packet must go to a **broadcast address** so every NIC on Layer 2 sees it and the target MAC can match.

**Fix (committed `f09947a`):**
- Added `_derive_broadcast()` to compute subnet broadcast from server IP
- Later replaced with hardcoded `255.255.255.255` (global broadcast, per taste preference)
- Always send to `255.255.255.255`

**Verification:** Shut down Server 2 → sent WoL to `255.255.255.255` → Server 2 booted and reached login screen.

---

## Problem 2: Ping is an Unreliable Wake Verification

**Symptom:** `ensure_server_online()` polled with `ping_host()` after sending WoL. Ping returned "online after 15s" but Server 2 was still off. A router or switch on the network was proxy-ARP-ing or responding to ICMP echo for `10.10.186.231`.

**Root cause:** ICMP (ping) can be answered by intermediate network devices, virtual IPs, or proxy ARP. It does not prove the specific host is up.

**Experiments performed:**

| Check type | Server off | Result | Reliable? |
|---|---|---|---|
| `ping 10.10.186.231` | Off | Timed out first, then "online" (false positive) | ❌ No |
| `Test-NetConnection -Port 445` | Off | Timed out (no false positive observed) | ✅ Yes |
| `os.listdir(\\UNC\share)` | Off | Needs `net use` auth first | ❌ N/A for wake check |
| `socket.connect_ex((ip, 445))` | Off | Times out reliably | ✅ Yes |
| `net use` + `dir \\share` | Off | Times out | ✅ Yes (but needs auth) |

**Fix (committed `2446e2a`):**
- Replaced `ping_host()` verification with `_smb_port_open()` — a raw TCP SYN to port 445
- TCP connect proves the **actual host** is alive (no proxy can fake it)
- Port 445 specifically confirms SMB file services are running
- No authentication needed for TCP handshake

**`_smb_port_open()` implementation:**
```python
def _smb_port_open(server_ip: str, port: int = 445, timeout: float = 5.0) -> bool:
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((server_ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False
```

---

## Problem 3: SMB Auth Session Required for File Operations

**Finding:** `os.listdir("\\\\10.10.186.231\\lan_backup")` returns `PermissionError: [WinError 5] Access is denied` without first running `net use` to establish an SMB auth session.

**Impact:** Robocopy also needs `net use` (or equivalent credential) before it can write to the LAN share. This is not a WoL issue — it's an SMB auth requirement.

**Status:** Not fixed in WoL module — handled by Robocopy wrapper calling `net use` before backup.

---

## Commits

| Commit | Description |
|--------|-------------|
| `f09947a` | WoL magic packet must go to broadcast address, not unicast IP |
| `2446e2a` | Replace ping-based verification with SMB port 445 TCP check |

---

## Remaining Concerns

1. **SMB auth persistence:** SSH sessions lose `net use` mappings when disconnected. Production service account needs persistent share access via Credential Manager or a scheduled task that establishes `net use` before backup.

2. **Stability buffer:** `wol.stability_wait_seconds` (default 30s) may be insufficient for Server 2016 boots. SMB port opens before all services are fully ready. Consider increasing to 60s in production config.

3. **Guest/Anonymous SMB:** The LAN share uses `Everyone - FullAccess`. If the server policy allows guest access, `os.listdir` may work without `net use`. If not, explicit credentials are required.
