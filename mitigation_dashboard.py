import tkinter as tk
from tkinter import scrolledtext
import subprocess
import time

# ==========================================================
# 1. CONFIGURATION (REPLACE THESE WITH YOUR ACTUAL LAB VALUES)
# ==========================================================
# IP of the target machine (Victim VM)
VICTIM_IP = "192.168.56.20" 
# MAC Address of the target machine (Victim VM) - Crucial for mitigation
CORRECT_MAC = "08-00-27-FC-7E-F9" 
# Name of the host's adapter connected to the VM network (e.g., from 'ncpa.cpl')
HOST_INTERFACE = "Ethernet 2" 

# ==========================================================
# 2. HELPER FUNCTIONS
# ==========================================================

def log_message(message, color="black"):
    """Inserts a message into the log area with optional color."""
    log_area.insert(tk.END, message + "\n", color)
    log_area.tag_config('green', foreground='green')
    log_area.tag_config('red', foreground='red')
    log_area.tag_config('blue', foreground='blue')
    log_area.tag_config('orange', foreground='orange')
    log_area.yview(tk.END) # Auto-scroll to the bottom

def update_status(text, color="gray"):
    """Updates the main status label."""
    status_label.config(text=f"Status: {text}", fg=color)
    
def detect_interface_for_ip(target_ip):
    """
    Robustly detects the network interface by:
    1. Finding the Host IP that sees the target_ip in `arp -a`.
    2. Finding the Interface Name associated with that Host IP in `netsh`.
    """
    try:
        # Step 1: Find the local Interface IP (Host IP) from arp -a
        arp_output = subprocess.check_output(['arp', '-a'], text=True)
        host_ip = None
        
        # Split by "Interface:" to process each block
        # Example line: "Interface: 192.168.56.1 --- 0x12"
        blocks = arp_output.split('Interface:')
        for block in blocks:
            if target_ip in block:
                # The first word of the block (after "Interface:") should be the Host IP
                # We need to clean it up slightly
                candidate_ip = block.strip().split()[0]
                host_ip = candidate_ip
                log_message(f"Found Host IP {host_ip} communicating with {target_ip}", "blue")
                break
        
        if not host_ip:
            log_message("Could not find Target IP in ARP table. Is the machine on?", "orange")
            return None

        # Step 2: Find the Interface Name for this Host IP using netsh
        # We assume the interface name is quoted in the output
        netsh_output = subprocess.check_output(['netsh', 'interface', 'ip', 'show', 'config'], text=True)
        
        current_interface = None
        for line in netsh_output.splitlines():
            line = line.strip()
            # Start of a new interface block
            if line.startswith('Configuration for interface'):
                # Extract "Interface Name"
                parts = line.split('"')
                if len(parts) >= 2:
                    current_interface = parts[1]
            
            # Check if this interface has the IP we found
            if current_interface and f"IP Address:                       {host_ip}" in line:
                 # Standard format has spaces. We can also try simple containment.
                 return current_interface
            elif current_interface and host_ip in line and "IP Address" in line:
                 return current_interface
                 
    except Exception as e:
        log_message(f"Interface Detection Error: {e}", "orange")
        
    return None


# ==========================================================
# 3. MITIGATION LOGIC (Back-End)
# ==========================================================

import subprocess # Assuming this is imported at the top of your script

# Ensure these variables are at the top of your script and correct:
# VICTIM_IP = "192.168.56.20"
# CORRECT_MAC = "08-00-27-FC-7E-F9" 
# HOST_INTERFACE = "Ethernet 2"

def mitigate_attack():
    
    # CRITICAL FIX: netsh requires hyphenated, lowercase MAC
    netsh_mac = CORRECT_MAC.replace(':', '-').lower() 
    
    # 1. Try to DELETE the entry first to avoid "Object already exists" error
    delete_command = [
        "netsh", "interface", "ip", "delete", "neighbors", 
        HOST_INTERFACE, VICTIM_IP
    ]
    
    # 2. Command to ADD the static entry
    add_command = [
        "netsh", "interface", "ip", "add", "neighbors", 
        HOST_INTERFACE, VICTIM_IP, netsh_mac
    ]
    
    try:
        log_message("Attempting to lock ARP entry with NETSH...", "orange")
        log_message(f"Command: {' '.join(add_command)}", "black")

        # Run DELETE (ignore errors if it doesn't exist)
        subprocess.run(delete_command, capture_output=True, check=False)
        
        # Run ADD
        result = subprocess.run(add_command, check=True, timeout=5, capture_output=True, text=True)
        
        # --- SUCCESS LOGS ---
        status_label.config(text="Status: MITIGATION SUCCESSFUL", fg="green")
        log_message(f"✅ Mitigation Success: ARP entry locked for {VICTIM_IP}.", "green")
        
    except subprocess.CalledProcessError as e:
        # Capture the specific error output from netsh
        error_output = e.stderr.strip() if e.stderr else e.stdout.strip() if e.stdout else "No output captured."
        status_label.config(text="Status: MITIGATION FAILED", fg="red")
        log_message(f"❌ MITIGATION FAILED! Error Code: {e.returncode}", "red")
        log_message(f"DETAILS: {error_output}", "orange")
        
        if "Run as administrator" in error_output or e.returncode == 1:
             log_message("👉 HINT: Try running this script as ADMINISTRATOR.", "blue")
        
    except Exception as e:
        log_message(f"❌ UNEXPECTED ERROR: {e}", "red")


# ==========================================================
# 4. DETECTION LOGIC (Back-End)
# ==========================================================

def check_arp_table():
    """Reads the Host PC's ARP table and checks for poisoning."""
    try:
        # Run arp -a command and capture output
        # Use a list for the command for safer execution
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Look for the Victim's IP address in the output
        if VICTIM_IP in output:
            
            # Simple parsing: Find the IP, then grab the MAC address which follows it
            # The output formats can vary, but this simple split often works in isolated labs.
            start_index = output.find(VICTIM_IP)
            
            # Isolate the line containing the IP, and split it by spaces/tabs to find the MAC
            arp_line = output[start_index:start_index + 50].split()
            
            # The MAC address is usually the second element after the IP
            if len(arp_line) >= 2:
                current_mac = arp_line[1].replace('-', ':').upper()
            else:
                current_mac = "NOT FOUND"

            # Compare the found MAC to the known correct MAC
            if current_mac != CORRECT_MAC and current_mac != "NOT FOUND":
                update_status("ATTACK DETECTED!", "red")
                log_message(f"🚨 ATTACK DETECTED! {VICTIM_IP} is using MAC: {current_mac}", "red")
                # Stop continuous checking once detected, user must mitigate
                return 
        
        # If we reached here, status is OK (still monitoring)
        update_status("MONITORING...", "blue")
        
    except Exception as e:
        update_status("ERROR", "orange")
        log_message(f"Monitoring Error: {e}", "orange")

    # Schedule the next check in 3 seconds (3000 milliseconds)
    window.after(3000, check_arp_table)

def start_detection():
    """Initializes the continuous monitoring loop."""
    log_area.delete('1.0', tk.END) # Clear previous logs
    log_message("Monitoring sequence initiated. Checking ARP table every 3 seconds...", "blue")
    window.after(100, check_arp_table) # Start the loop immediately

# ==========================================================
# 5. TKINTER MAIN WINDOW SETUP
# ==========================================================

window = tk.Tk()
window.title("ARP Mitigation Dashboard (v1.0)")
window.geometry("650x450")

# --- UI Elements ---

# Title Label
title_label = tk.Label(window, text="ARP Spoofing Mitigation Dashboard", font=('Helvetica', 14, 'bold'))
title_label.pack(pady=5)

# Status Indicator
status_label = tk.Label(window, text="Status: IDLE", fg="gray", font=('Helvetica', 12, 'bold'))
status_label.pack()

# Log Area
log_area_frame = tk.Frame(window)
log_area_frame.pack(pady=10)
log_area_label = tk.Label(log_area_frame, text="Event Log:")
log_area_label.pack(anchor='w')
log_area = scrolledtext.ScrolledText(log_area_frame, wrap=tk.WORD, width=70, height=15)
log_area.pack()

# Buttons
button_frame = tk.Frame(window)
button_frame.pack(pady=10)

detect_button = tk.Button(button_frame, text="START DETECTION", command=start_detection, width=20, bg='#4CAF50', fg='white')
detect_button.pack(side=tk.LEFT, padx=10)

mitigate_button = tk.Button(button_frame, text="APPLY ARP LOCK (MITIGATE)", command=mitigate_attack, width=25, bg='#F44336', fg='white')
mitigate_button.pack(side=tk.LEFT, padx=10)


# --- Auto-Detect Interface on Startup ---
detected = detect_interface_for_ip(VICTIM_IP)
if detected:
    HOST_INTERFACE = detected
    log_message(f"✅ Auto-detected Interface: '{HOST_INTERFACE}' for subnet {VICTIM_IP}", "green")
else:
    log_message(f"⚠️ Could not auto-detect interface. Using default: '{HOST_INTERFACE}'", "orange")

# Start the GUI loop
window.mainloop()