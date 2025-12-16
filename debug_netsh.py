import subprocess

def debug_netsh():
    try:
        print("Running netsh...")
        # Capture stdout and stderr
        result = subprocess.run(['netsh', 'interface', 'ip', 'show', 'config'], check=False, capture_output=True, text=True)
        print("--- STDOUT ---")
        print(result.stdout)
        print("--- STDERR ---")
        print(result.stderr)
        
        with open("netsh_debug.txt", "w") as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_netsh()
