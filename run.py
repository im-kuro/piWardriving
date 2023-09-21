
from Utils import webHandler
import subprocess, threading, argparse, os, sys



argparseObj = argparse.ArgumentParser()

argparseObj.add_argument("-i", "--install", help="Install the tools, setup ap and web interface", action="store_true")
argparseObj.add_argument("-u", "--uninstall", help="Uninstall everything from your system", action="store_true")

    
#if os.geteuid() != 0:
#    msg = "[sudo] password for %u:"
#    ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)
#else: print("You are root!! Please run witgh root privileges!!!!!!!"); exit(1)

def __installNeeded__():
    try:
        # Run the installation command
        subprocess.run(["sudo", "apt-get", "install", "hostapd", "dnsmasq", "aircrack-ng"], check=True)
        return {"status": "success", "message": "Packages installed successfully"}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error during package installation: {e}", "error": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}", "error": str(e)}
    


def main():
	# Print the banner
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
		installRes = __installNeeded__()["status"]
		if installRes == "error":
			print(f"Error installing packages | Output => {installRes}")
		else:
			print("Packages installed successfully")

		configap = input("Would you like to config a AP to auto emit on boot?")
		runonboot = input("Do you want the tool to run on boot?")

   
	if argparseObj.parse_args().uninstall:
		print("Uninstalling tools")






# Call the main function
main()


if __name__ == "__main__":
    
    webHandler.resetDB()
    print("You can now browse to http://127.0.0.1:6969/ to view the web interface (please plug in your wifi adapter if you haven't already)")
    # Start the web server
    webHandler.app.run(host="127.0.0.1", port=6969)
    print("Web server stopped")
    # init the session database again to clear it
    webHandler.resetDB()
    