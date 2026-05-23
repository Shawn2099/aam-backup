import subprocess, sys

server_ip = sys.argv[1] if len(sys.argv) > 1 else "10.10.186.231"

cmd = ["shutdown", "/s", "/m", f"\\\\{server_ip}", "/t", "300", "/f",
       "/c", "Backup complete - server shutting down in 5 minutes"]

print(f"Sending: {' '.join(cmd)}")
r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

if r.returncode == 0:
    print(f"OK - shutdown sent to {server_ip} (5 min delay)")
    print("Run 'shutdown /a' on the target to cancel")
else:
    print(f"FAIL (exit {r.returncode}): {r.stderr.strip()}")
