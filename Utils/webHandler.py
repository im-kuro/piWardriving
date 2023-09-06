from sanic import Sanic
from sanic.response import json, html
import platform,socket,re,uuid,psutil, asyncio, base64
from jinja2 import Environment, FileSystemLoader
import aircrack
# Local imports
import tools, helpers



app = Sanic("WardrivingTool")
app.static('Utils/static/', 'Utils/static/', directory_view=True, name="static")  # Assuming your static files are in a 'static' folder



# Configure Jinja2 template environment
template_dir = 'Utils/static/'  # Path to your template directory
env = Environment(loader=FileSystemLoader(template_dir))

print("You can now browse to http://127.0.0.1:6969/ to view the web interface (please plug in your wifi adapter if you haven't already)")

# init the session database
helpers.database().__initDatabase__()

app.ctx.interfaces = tools.showInterfaces()
if helpers.database().readFromDB("settings") is not None:
    app.ctx.interface = helpers.database().readFromDB("settings")["interfaceInfo"]["idx"]
    app.ctx.interfaceName = helpers.database().readFromDB("settings")["interfaceInfo"]["name"]
else: app.ctx.interface = None; app.ctx.interfaceName = None
# Shared variable to indicate whether the loop should run or not
loop_running = False



"""

FRONT END CODE HERE

"""


    
    
@app.route("/")
async def index(request):
    template = env.get_template('index.html')

    rendered_template = template.render(deviceInfo={
        "machineType": platform.machine(),
        "os": platform.system(),
        "mac": ':'.join(re.findall('..', '%012x' % uuid.getnode())).upper,
        "ram": str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB",
        "ip": socket.gethostbyname(socket.gethostname()),
        "hostname": socket.gethostname(),
        "interfaces": app.ctx.interfaces,
        "interfaceInfo": {"idx": app.ctx.interface, "name": app.ctx.interfaceName}

    })
    
    return html(rendered_template)

@app.route("/attack")
async def attack(request):
    template = env.get_template('attack.html')

    rendered_template = template.render(deviceInfo={
        "interfaces": app.ctx.interfaces,
        "interfaceInfo": {"idx": app.ctx.interface, "name": app.ctx.interfaceName}

    })
    
    return html(rendered_template)

@app.route("/analytics", methods=["GET"])
async def analytics(request):
    template = env.get_template('analytics.html')
    rendered_template = template.render(deviceInfo={
        "interfaces": app.ctx.interfaces,
        "interfaceInfo": {"idx": app.ctx.interface, "name": app.ctx.interfaceName}
    })
    return html(rendered_template)

@app.route("/attackspecific", methods=["GET"])
async def attackSpecific(request):
    try:
        ssid = base64.b64decode(request.args.get('ssid')).decode('utf-8')
        bssid = base64.b64decode(request.args.get('bssid')).decode('utf-8')
    except Exception as e:
        ssid = "Invalid Base64 encoding"
        bssid = "Invalid Base64 encoding"

    template = env.get_template('attackspecific.html')
    rendered_template = template.render(deviceInfo={
        "interfaces": app.ctx.interfaces,
        "interfaceInfo": {"idx": app.ctx.interface, "name": app.ctx.interfaceName}
    })
    return html(rendered_template)

"""
BACK END CODE HERE
"""


# gets called when user enters site and gets the interface
@app.route('/setInterface', methods=["POST"])
async def setInterface(request):
    app.ctx.interface = request.json["interfaceIdx"]
    app.ctx.interfaceName = request.json["interfaceName"]
    tools.__init__(app.ctx.interface)
    helpers.database().writeToDB("interfaceInfo", {"interfaceInfo":{"idx": app.ctx.interface, "name": app.ctx.interfaceName}})
    return json({"status": "success", "interface": app.ctx.interface})



@app.route('/setsettings', methods=["POST"])
async def setSettings(request):
    settingCall = request.json.get("call")  # Use .get() to safely get the value
    settingPayload = request.json.get("payload")

    try:
        if settingCall == "darkmode":
            settings = helpers.database().readFromDB("settings")
            # Update the "darkmode" setting in the database
            settings["darkmode"] = settingPayload
            helpers.database().writeToDB("settings", settings)
            return json({"status": "success", "message": f"Darkmode set to {settingPayload}"})
        
        if settingCall == "setoption":
            settings = helpers.database().readFromDB("settings")
            # Update the option setting in the database
            settings[str(settingPayload["option"])] = settingPayload["value"]
            helpers.database().writeToDB("settings", settings)
            return json({"status": "success", "message": f"{settingPayload['option']} set to {settingPayload['value']}"})
        
    except Exception as e:
        return json({"status": "error", "message": str(e)})



@app.route('/getsettings', methods=["GET"])
async def getSettings(request):
    try:
        return json({"status": "success", "settings": helpers.database().readFromDB("settings")})
    except Exception as e:
        return json({"status": "error", "message": str(e)})


# async local func handler so we can use global variables
async def wardrivingLoop(actionCall: str, interfaceName: str = app.ctx.interfaceName):
    global loop_running
    
    
    while loop_running:
        # Check if the interface is already in monitor mode
        current_mode = await tools.get_interface_mode(interfaceName)
        if current_mode != "Monitor":
            
            monitorModeStatus = aircrack.aircrackWrapper.configInterface(interfaceName, current_mode.lower())
            if monitorModeStatus["status"] == "error":
                return monitorModeStatus # throw error back up to the main loop
            elif monitorModeStatus["status"] == "success":
                pass
        
        elif current_mode == "Monitor":
            pass
    
        if actionCall == "monitorOnly":
            
            networks = await aircrack.aircrackWrapper.dump(app.ctx.interface)
            
            for network in networks.values():
                print(network["ssid"])

            await asyncio.sleep(5)  # Adjust the sleep interval as needed
        if actionCall == "logNetworks":
            pass
        if actionCall == "captureHandshakes":
            pass
        

@app.route('/startwardriving', methods=["POST"])
async def startWardrive(request):
    if app.ctx.interface is None:
        return json({"status": "error", "message": "noInterfaceSelected"})
    
    global loop_running
    
    action = request.json["action"]
    interfaceName = request.json["interfaceName"]
    
    if action == "terminate":
        # Stop the loop by setting the shared variable to False
        loop_running = False
        return json({"status": "Loop terminated"})

    elif action in ["monitorOnly", "logNetworks", "captureHandshakes"]:
        if not loop_running:
            # Start the loop by setting the shared variable to True
            loop_running = True
            # Create an asyncio task to run the loop function
            status = await asyncio.create_task(wardrivingLoop(action, interfaceName))
            if status["status"] == "error":
                return json({"status": "error", "message": "invalidAction", "response": status})
            return json({"status": "Loop started"})
        else:
            return json({"status": "Loop already running"})

   


@app.route('/data', methods=["GET"])
async def getData(request):
    if request.method == "GET": return json({'temperature': tools.get_cpu_temperature(), 'cpuUsage': tools.get_cpu_usage()})
    else: return json({"status": "error", "message": "Invalid request method"})

@app.route('/savedNetworks', methods=['GET'])
async def getSaved(request):
    if request.method == "GET": return json({"savedNetworks": helpers.database().readFromDB("savedNetworks")})
    else: return json({"status": "error", "message": "Invalid request method"})

@app.route('/networks', methods=['GET'])
async def getNetworks(request):
    if app.ctx.interface is None:
        return json({"status": "error", "message": "noInterfaceSelected"})
    networkRes = await tools.scan_wifi_networks(app.ctx.interface)


    savedNetworks = helpers.database().readFromDB("savedNetworks")
    
    
    for network in networkRes.values():
        if network["ssid"] in savedNetworks:
            network["saved"] = True
        else:
            savedNetworks[network["ssid"]] = network  
            helpers.database().writeToDB("savedNetworks", savedNetworks) 
            network["saved"] = False
            
    networkUsage = tools.getInterfaceUsage(app.ctx.interface)
            

    unknown = 0
    unknownSaved = 0
    WPANetworks = 0
    WPA2Networks = 0
    WEPNetworks = 0
    savedWPANetworks = 0
    savedWPA2Networks = 0
    savedWEPNetworks = 0

    networkCount = 0
    savedNetworksCount = 0
    
    for network_info in networkRes.values():
        networkCount += 1
        encryption = network_info["encryption"]

        if not encryption:  # Check if the encryption list is empty
            unknown =+ 1
            continue

        
        if network_info["encryption"][0] == 4:
            WPA2Networks += 1
        elif network_info["encryption"][0] == 2 or network_info["encryption"][0] == 3:
            WPANetworks += 1
        elif network_info["encryption"][0] == 1:
            WEPNetworks += 1


    for network in savedNetworks.values():
        if not network["encryption"]:  # Check if the encryption list is empty
            unknownSaved =+ 1
            continue
       
        savedNetworksCount += 1
        if network["encryption"][0] == 4:
            savedWPA2Networks += 1
        elif network["encryption"][0] == 2 or network["encryption"][0] == 3:
            savedWPANetworks += 1
        elif network["encryption"][0] == 1:
            savedWEPNetworks += 1

   
    
    return json({
        "networks": networkRes,
        "savedNetworks": savedNetworks,
        "savedNetworksCount": savedNetworksCount,
        "networkCount": networkCount,
        "WPA": WPANetworks,
        "WPA2": WPA2Networks,
        "WEP": WEPNetworks,
        "savedWPA": savedWPANetworks,
        "savedWPA2": savedWPA2Networks,
        "savedWEP": savedWEPNetworks,
        "unknownSaved": unknownSaved,
        "unknownEnc": unknown,
        "interfaceUsage": networkUsage
    })




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=6969)
    helpers.database().__initDatabase__()