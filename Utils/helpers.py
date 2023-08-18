from colorama import Fore, Style, init
import getpass


# the class for the input/output functions
class IOFuncs:

	class Default:
		def __init__(self):
			init()
		def printError(self, Error: str): print(f"{Fore.RED} + [ERROR] -> {Error}{Style.RESET_ALL}") 
		def printSuccess(self, Success: str): print(f"{Fore.GREEN} + [SUCCESS] -> {Success}{Style.RESET_ALL}") 
		def printInfo(self, Info: str): print(f"{Fore.CYAN} + [INFO] -> {Info}{Style.RESET_ALL}") 
		def getUserInput(self, Input: str) ->  str: return input(f"{Fore.MAGENTA} + [INPUT] -> {Input} y/n: {Style.RESET_ALL}") 
		def getMultiOptionInput(self, Input: str, q1, q2, q3) ->  str: return input(f"{Fore.MAGENTA} + [INPUT] --> {Input} ({q1} or {q2} or {q3}): {Style.RESET_ALL}") 
		def getTextInput(self, Input: str) -> str: return input(f"{Fore.MAGENTA} + [INPUT] -> {Input}: {Style.RESET_ALL}")
		def getPassword(self, Input: str) -> str: return getpass.getpass(f"{Fore.MAGENTA} + [INPUT] -> {Input}: {Style.RESET_ALL}")
		def printArgsInfo(self, **kwargs) -> dict:
			for key, value in kwargs.items():
				print(f"{Fore.CYAN} + [INPUT] -> {key} = {value} {Style.RESET_ALL}") 
			return kwargs

    
    
    