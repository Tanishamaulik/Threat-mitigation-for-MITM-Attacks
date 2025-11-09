## 💻 Virtual Machine and Lab Environment Setup

This document details the exact configuration required to replicate the ARP Spoofing Detection and Mitigation project.

### 1. Virtual Machines (VMs)

| Role | Operating System | Purpose |
| :--- | :--- | :--- |
| **Attacker VM** | Windows 11 | Launches the ARP Spoofing attack. |
| **Victim VM** | Windows 11 | Target of the attack. |
| **Defender** | Host PC (Windows 11) | Runs the Python Mitigation Dashboard. |

---

### 2. Network Configuration

The environment uses a **Host-Only Adapter** (VirtualBox) for complete isolation from the external network.

| Component | Network Setting | Value |
| :--- | :--- | :--- |
| **Network Type** | VirtualBox Setting | Host-Only Adapter |
| **Host Interface Name** | Windows Adapter Name | `"Ethernet 2"` |
| **Attacker VM IP** | Static IPv4 Address | `192.168.56.10` |
| **Victim VM IP** | Static IPv4 Address | `192.168.56.20` |

---

### 3. Prerequisites (Required Software)

The following software must be installed on the respective machines to run the project successfully:

* **Host PC (Defender):**
    * **Python 3** (Used for the Mitigation Dashboard GUI).
* **Attacker VM:**
    * **WinPcap** (Required by network sniffing tools).
    * **Attack Tool:** `arpspoof.exe` or `SelfishNetV3` (Used to generate the malicious traffic).

---

### 4. Running the Mitigation Dashboard

The Python dashboard script must be run with Administrator privileges:

```bash
# Must be executed in an Administrator Command Prompt on the Host PC
python mitigation_dashboard.py
