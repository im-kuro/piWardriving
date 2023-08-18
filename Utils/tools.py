
import pywifi, subprocess, json, time
from pywifi import const
import psutil,subprocess, pywifi

wifi = pywifi.PyWiFi()


class toolkit():
	
	def __installNeeded__():
		subprocess.run(["sudo", "apt-get", "install", "hostapd", "dnsmasq", "lm-sensors"])
   
   
	def showInterfaces() -> json:

		interfaces = wifi.interfaces()
		interfacesJson = {}
		for idx, iface in enumerate(interfaces):
			interfacesJson[iface.name()] = {"idx": idx, "interfaceName": iface.name()}
		return interfacesJson

	def get_cpu_temperature_linux():
		try:
			output = subprocess.check_output(['sensors']).decode('utf-8')
			temperature_lines = [line for line in output.split('\n') if 'Core 0' in line]
			temperature = temperature_lines[0].split(':')[1].strip()
			return round(temperature)
		except Exception as e:
			print(f"Error fetching CPU temperature: {e}")
			return None


	def get_cpu_usage():
		try:
			return  round(psutil.cpu_percent(interval=1)) # Interval is in seconds
		except Exception as e:
			print(f"Error fetching CPU usage: {e}")
			return None
   
	def scan_wifi_networks(interface:int=0):
		iface = wifi.interfaces()[int(interface)]
		iface.scan()
		time.sleep(1)
		scan_results = iface.scan_results()

		network_info = {}
		for result in scan_results:
			network_info[result.ssid]={
				"SSID": result.ssid,
				"BSSID": result.bssid,
				"Signal Strength": result.signal,
				"Encryption": result.akm
			}
		print(network_info)
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
  
