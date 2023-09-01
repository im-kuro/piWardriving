
from Utils import tools, helpers
import subprocess, threading,json, argparse, os

from Utils import bettercap

helpersObj = helpers.IOFuncs.Default()

argparseObj = argparse.ArgumentParser()

argparseObj.add_argument("-i", "--install", help="Install the tools, setup ap and web interface", action="store_true")
argparseObj.add_argument("-u", "--uninstall", help="Uninstall everything from your system", action="store_true")

#if os.geteuid() != 0:
#    msg = "[sudo] password for %u:"
#    ret = subprocess.check_call("sudo -v -p '%s'" % msg, shell=True)


def run_web_handler():
    subprocess.run(["python", "Utils/webHandler.py"])

def main():
	helpersObj.printInfo("Kuros Wardriving Tool")
	if argparseObj.parse_args().install:
		helpersObj.printInfo("Installing tools")
	if argparseObj.parse_args().uninstall:
		helpersObj.printInfo("Uninstalling tools")
  
  
    # Create a thread to run the webHandler.py file
	web_handler_thread = threading.Thread(target=run_web_handler)
	web_handler_thread.start()

    # Rest of your main function code


 


# Call the main function
main()