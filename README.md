# 🛡️ ARP Spoofing Mitigation Dashboard Project

## 💡 Project Overview

This project simulates a **Man-in-the-Middle (MITM)** attack using **ARP Spoofing** in an isolated virtual lab and implements a robust, automated Python-based **Dynamic ARP Inspection (DAI)**-style defense mechanism to mitigate the threat in real-time.

The project demonstrates successful execution of the attack, detection via packet analysis, and enforcement of host-based mitigation using Windows system commands.

---

## 🛠️ Technology Stack

| Role | Tool / Technology | Purpose |
| :--- | :--- | :--- |
| **Virtualization** | VirtualBox (or VMware) | Creates the isolated Host-Only network lab. |
| **Operating System** | Windows 11 (Host & VMs) | Platform for execution and mitigation. |
| **Attack Tool** | `arpspoof.exe` / SelfishNetV3 | Launches the ARP cache poisoning attack. |
| **Detection Tool** | Wireshark | Manual verification of packet flood and attack detection. |
| **Defense GUI** | Python 3 + Tkinter | Front-end GUI for automated detection and mitigation. |
| **Mitigation Command** | `netsh` (via Python `subprocess`) | Enforces the **Static ARP Entry** (ARP Lock) defense. |

---

## 🌐 Lab Environment Configuration

The entire lab is isolated using a Host-Only Network.

| Component | Role | Static IP Address | Host Interface Name |
| :--- | :--- | :--- | :--- |
| **Host PC** | Defender/Gateway | `192.168.56.1` (Host-Only Adapter) | `"Ethernet 2"` |
| **Attacker VM** | Launches Attack | `192.168.56.10` | N/A |
| **Victim VM** | Target | `192.168.56.20` | N/A |

### Prerequisites

1.  **Python 3** installed on the Host PC with Python added to PATH.
2.  **WinPcap** installed on the Attacker VM (required for attack tools).
3.  The Python script requires **Administrator privileges** to run the mitigation command.

---

## 🚀 Key Project Milestones (Demonstrated Success)

### 1. Attack Execution & Detection

* The **Attacker VM** successfully launched the ARP spoofing flood, targeting the Host PC and the Victim VM.
* **Wireshark** captured a continuous flood of **ARP Reply** packets claiming the Attacker's MAC address belongs to the Victim's IP, confirming successful detection.

### 2. Automated Mitigation

The Python dashboard successfully automates the final mitigation step:

* **Detection:** The GUI automatically detects the poisoned ARP entry by running and parsing the `arp -a` output every few seconds.
* **Mitigation Command:** When the **APPLY ARP LOCK (MITIGATE)** button is clicked, the script executes the definitive command:
    ```bash
    netsh interface ip add neighbors "Ethernet 2" 192.168.56.20 [Victim MAC Address]
    ```
* **Verification:** The Host PC's ARP table entry for `192.168.56.20` is confirmed as **`static`**, proving the defense is active and the MITM threat is neutralized on the host.

---

## ⚙️ Running the Mitigation Dashboard

The mitigation script must be launched from an elevated prompt:

```bash
# 1. Navigate to the project directory
cd [Project-Directory]

# 2. Run the script using an Administrator Command Prompt
python mitigation_dashboard.py







