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


# ==========================================================
# 3. MITIGATION LOGIC (Back-End)
# ==========================================================

import subprocess # Assuming this is imported at the top of your script

# Ensure these variables are at the top of your script and correct:
# VICTIM_IP = "192.168.56.20"
# CORRECT_MAC = "08-00-27-FC-7E-F9" 
# HOST_INTERFACE = "Ethernet 2"

def mitigate_attack():
    VICTIM_IP = "192.168.56.20"
    CORRECT_MAC_RAW = "08-00-27-FC-7E-F9" 
    HOST_INTERFACE = "Ethernet 2"
    
    # CRITICAL FIX: netsh requires hyphenated, lowercase MAC
    netsh_mac = CORRECT_MAC_RAW.replace(':', '-').lower() 
    
    # Use the list format for robust execution!
    command_list = [
        "netsh", "interface", "ip", "add", "neighbors", 
        HOST_INTERFACE, VICTIM_IP, netsh_mac
    ]
    
    try:
        log_message("Attempting to lock ARP entry with NETSH (List Format)...", "orange")
        
        # We use shell=False for security and robust execution with the list format
        # Check=True ensures Python raises an error if the command fails
        subprocess.run(command_list, check=True, timeout=5)
        
        # --- SUCCESS LOGS ---
        status_label.config(text="Status: MITIGATION SUCCESSFUL", fg="green")
        log_message(f"✅ Mitigation Success: ARP entry locked for {VICTIM_IP}.", "green")
        
    except subprocess.CalledProcessError as e:
        # If it fails here, the interface name is almost certainly still wrong
        status_label.config(text="Status: MITIGATION FAILED", fg="red")
        log_message(f"❌ MITIGATION FAILED! CHECK INTERFACE NAME: '{HOST_INTERFACE}'", "red")
        
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

# Start the GUI loop
window.mainloop()