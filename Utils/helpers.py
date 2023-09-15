from colorama import Fore, Style, init
import getpass, json, aiofiles


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

class database:
    def __init__(self) -> None:
        self.path = "Utils/database/session.json"

    async def writeToDB(self, objPath: str, jsonData) -> bool:
        try:
            async with aiofiles.open(self.path, mode="r") as file:
                content = await file.read()
                DB = json.loads(content)

            DB[objPath] = jsonData

            async with aiofiles.open(self.path, mode="w") as file:
                await file.write(json.dumps(DB, indent=4))

            return True
        except Exception as e:
            print(f"Error writing to the database: {e}")
            return False

    async def readFromDB(self, obj_path: str = None) -> dict:
        try:
            async with aiofiles.open(self.path, mode="r") as file:
                content = await file.read()
                data = json.loads(content)

            if obj_path is None:
                return data
            else:
                return data.get(obj_path, {})
        except Exception as e:
            print(f"Error reading from the database: {e}")
            return {}

    def __initDatabase__(self):
        try:
            initial_data = {
                "savedNetworks": {},
                "deauthedAPs": {},
                "capturedHandshakes": {},
                "settings": {
                    "darkmode": False,
                    "onlShowWEP": False,
                    "onlyShowWPA": False,
                    "onlyShowWPA2": False,
                    "dontShowUnknown": False,
                    "alertOnWEP": False,
                    "alertOnWPA": False,
                    "alertOnWPA2": False,
                    "filterBySignal": False,
                },
                "interfaceInfo": {
                    "idx": None,
                    "name": None,
                    "mode": None,
                },
                "errors": {},
            }

            with open(self.path, mode="w") as file:
                file.write(json.dumps(initial_data, indent=4))

        except Exception as e:
            print(f"Error initializing database: {e}")