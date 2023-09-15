
from Utils import tools, helpers
import subprocess, threading, argparse, os, sys



argparseObj = argparse.ArgumentParser()

argparseObj.add_argument("-i", "--install", help="Install the tools, setup ap and web interface", action="store_true")
argparseObj.add_argument("-u", "--uninstall", help="Uninstall everything from your system", action="store_true")

    
#if os.geteuid() != 0:
#    msg = "[sudo] password for %u:"
#    ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
#else: print("You are root!! Please run witgh root privileges!!!!!!!"); exit(1)



def main():
	helpers.database().__initDatabase__()
	print("Kuros Wardriving Tool")

	#if sys.platform.startswith('win'):
	#	print("################################")
	#	print("## Windows is not supported!! ##")
	#	print("################################")
	#	exit(0)
	#elif sys.platform.startswith('darwin'):
	#	print("#################################################")
	#	print("## Why the fuck are you running this on a mac? ##")
	#	print("#################################################")
	#	exit(0)
	#elif sys.platform.startswith('linux'):
	#	pass


	if argparseObj.parse_args().install:
		print("Installing tools...")
		installRes = tools.__installNeeded__()["status"]
		if installRes == "error":
			print(f"Error installing packages | Output => {installRes}")
		else:
			print("Packages installed successfully")
	if argparseObj.parse_args().uninstall:
		print("Uninstalling tools")
  
	subprocess.run(["python", "Utils/webHandler.py"])



helpers.database().__initDatabase__()


# Call the main function
main()