
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
  
