import subprocess

def list_interfaces():
    print("--- NETSH OUTPUT ---")
    try:
        # standard command to list interfaces
        output = subprocess.check_output("netsh interface show interface", shell=True).decode()
        print(output)
    except Exception as e:
        print(f"NETSH Error: {e}")

    print("\n--- IPCONFIG OUTPUT ---")
    try:
        output = subprocess.check_output("ipconfig", shell=True).decode()
        print(output)
    except Exception as e:
        print(f"IPCONFIG Error: {e}")

if __name__ == "__main__":
    list_interfaces()
