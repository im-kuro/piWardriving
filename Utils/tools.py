
import subprocess, json, re, sys, logging, time, os

import psutil, aioserial, pywifi
from gpiozero import CPUTemperature
import asyncio



logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

logging.getLogger("pywifi").setLevel(logging.WARNING)
wifi = pywifi.PyWiFi()
interface = 0
iface = wifi.interfaces()[int(interface)]

def __installNeeded__():
    try:
        # Run the installation command
        subprocess.run(["sudo", "apt-get", "install", "hostapd", "dnsmasq", "aircrack-ng"], check=True)
        return {"status": "success", "message": "Packages installed successfully"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error during package installation: {e}", "error": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}", "error": str(e)}
    


async def getGPSData(GPSinterface: int = 0):
    ser = aioserial.AioSerial(
        port=f'/dev/{GPSinterface}',
        baudrate=9600,
        parity=aioserial.PARITY_NONE,
        stopbits=aioserial.STOPBITS_ONE,
        bytesize=aioserial.EIGHTBITS,
        timeout=1,
    )

    while True:
        try:
            line = await ser.readline()
            decoded_line = line.decode()  # Decode bytes to string
            logger.debug(decoded_line)
            print(decoded_line)
            # Parse the NMEA sentence and create a dictionary
            #gps_data = PHARSE TO JSON HERE
            
            # Convert the dictionary to JSON and print it
            #json_data = json.dumps(gps_data)
            #print(json_data)
        except aioserial.SerialException as e:
            logger.error(f'SerialException: {e}')
            break
        except UnicodeDecodeError as e:
            logger.error(f'UnicodeDecodeError: {e}')
        continue

    
def checkMonitorModeSupport(interface_name: str):
    try:
        # Run the 'iw list' command to get information about the interface
        iw_output = subprocess.check_output(['iw', 'list', interface_name], stderr=subprocess.STDOUT, text=True)

        # Use regular expressions to check for monitor mode support
        if re.search(r"Monitor", iw_output):
            return True
        else:
            return False

    except subprocess.CalledProcessError:
        # The 'iw' command failed, which may mean the interface does not exist
        return False
    
    

def showInterfaces() -> json:
	interfaces = wifi.interfaces()
	interfacesJson = {}
	for idx, iface in enumerate(interfaces):
		interfacesJson[idx] = {"idx": idx, "interfaceName": iface.name()}
	return interfacesJson
# here we have to pass in helper obj bc of pussy parent package shit
async def dumpAndStore(interfaceIDX: int = 0, helpersObj: object = None):
	#try:
	
	# Scan for WLAN networks
	iface.scan()
	await asyncio.sleep(5)  # Sleep for 5 seconds before the next iteration
	# Get the scan results
	scan_results = iface.scan_results()
    # Create a list to store the scan result data
	scan_data = {}
	for result in scan_results:
		scan_data[result.ssid] ={
		    "SSID": result.ssid,
		    "Signal_Strength": result.signal,
		    "BSSID": result.bssid,
			"akm": result.akm,
			"auth": result.auth,
			"freq": result.freq
		}


	await helpersObj.database().writeToDB("scanResults", scan_data)


	#except Exception as e:
	#	print(f"Error in dumpAndStore: {str(e)}")
	#	await asyncio.sleep(5)  # Sleep for 5 seconds before the next iteration





def getInterfaceUsage(interface: int) -> dict:
	def get_size(bytes):
		"""
		Returns size of bytes in a nice format
		"""
		for unit in ['', 'K', 'M', 'G', 'T', 'P']:
			if bytes < 1024:
				return f"{bytes:.2f}{unit}B"
			bytes /= 1024

	# Define bytes_sent and bytes_recv
	bytes_sent = 0  # Initial value
	bytes_recv = 0  # Initial value

	# Get the stats again
	io_2 = psutil.net_io_counters()

	# Calculate the difference in bytes sent and received
	us, ds = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv

	# Update the bytes_sent and bytes_recv for the next iteration
	bytes_sent, bytes_recv = io_2.bytes_sent, io_2.bytes_recv

	# Return the interface usage as a dictionary
	return {"upload": get_size(us), "download": get_size(ds)}



def get_cpu_temperature():
	try:
		temperatures = CPUTemperature().temperature
		return round(temperatures)
	except Exception as e:
		print(f"Error fetching CPU temperature: {e}")
		return None
def get_cpu_usage():
	try:
		return  round(psutil.cpu_percent(interval=1)) # Interval is in seconds
	except Exception as e:
		print(f"Error fetching CPU usage: {e}")
		return None



def setupAP(interface:int=0):
	hostapd_config = f"""/
interface={interface}
ssid=superSecretNetwork
hw_mode=g
channel=6
		"""

	dnsmasq_config = f"""/
interface={interface}
dhcp-range=10.0.0.2,10.0.0.240,255.255.255.0,6h
domain-needed
bogus-priv
filterwin2k
server=1.1.1.1
listen-address=0.0.0.0
no-hosts
log-dhcp
port=53
		"""
	autoIP = f"""/

allow-hotplug {interface}
iface {interface} inet static
    address 10.0.0.1
    netmask 255.255.255.0
"""


	with open("/etc/hostapd/hostapd.conf", "a") as f:
		f.write(hostapd_config)
	with open("/etc/dnsmasq/dnsmasq.conf", "a") as f:
		f.write(dnsmasq_config)
	with open("/etc/network/interfaces", "a") as f:
		f.write(autoIP)

	subprocess.run(["sudo", "systemctl", "unmask", "hostapd.service", "dnsmasq.service"])
	subprocess.run(["sudo", "systemctl", "enable", "hostapd.service", "dnsmasq.service"])
	subprocess.run(["sudo", "systemctl", "start", "hostapd.service", "dnsmasq.service"])
	subprocess.run(["sudo", "ifconfig", interface, "up"])
	print("Access point setup complete, you may need to reboot for changes to take effect")



















async def getInterfaceMode(interface_name):
	try:
		result = subprocess.run(["iwconfig", interface_name], capture_output=True, text=True, check=True)
		output_lines = result.stdout.splitlines()
		for line in output_lines:
			if "Mode:" in line:
				mode = line.split("Mode:")[1].split()[0]
				return mode.lower()
		return "Unknown"
	except subprocess.CalledProcessError as e:
		print("Error getting interface mode:", e)
		return "Error"





async def deauth(interface: str, ap: str, st: str, count: int):
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
		




async def dump(interface: str, scan_duration: int = 5):
	#try:
	# Define the airodump-ng command
    # Define the airodump-ng command
	cmd = [
	    "sudo", "airodump-ng", "--output-format", "csv", interface
	]		
	# Start airodump-ng to capture network data for the specified duration
	process = await asyncio.create_subprocess_exec(
	    *cmd,
	    stdout=subprocess.PIPE,
	    stderr=subprocess.PIPE,
	    universal_newlines=True,
	)		
	# Create a list to capture the output lines
	output_lines = []		
	# Wait for the specified duration while capturing the output
	await asyncio.sleep(scan_duration)		
	# Terminate the subprocess after the specified duration
	process.terminate()		
	# Read the output lines as they become available
	while True:
		try:
			line = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
			if not line:
				break
			output_lines.append(line)
		except asyncio.TimeoutError:
		    # Handle a timeout if needed
			pass		
	# Check if the process is still running
	if process.returncode is None:
		# If it's still running, force termination
		process.kill()
		await process.wait()		
	# Join the captured output lines
	output = "".join(output_lines)
	print("Command output:", output)
	
	#except subprocess.CalledProcessError as e:
	#	return {"status": "error", "message": "Error running airodump-ng", "error": str(e)}
	#except Exception as e:
	#	return {"status": "error", "message": "An unexpected error occurred", "error": str(e)}
 
 
async def captureHandshake(interface: str, bssid: str, channel: int, timeout: int = 15):
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
async def configInterface(interface: str, mode: str):
	try:
		if mode.lower() == "managed":
			commands = [
		        ["sudo", "ifconfig", interface, "down"],
		        ["sudo", "iwconfig", interface, "mode", "monitor"],
		        ["sudo", "ifconfig", interface, "up"],
		    ]
		elif mode.lower() == "monitor":
			commands = [
		        ["sudo", "ifconfig", interface, "down"],
		        ["sudo", "iwconfig", interface, "mode", "managed"],
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

