from sanic import Sanic
from sanic.response import json, html
import platform,socket,re,uuid,psutil, asyncio, base64, time,os, subprocess, threading
from jinja2 import Environment, FileSystemLoader
# Local imports
from Utils import tools, helpers

import json as jsonObj



app = Sanic("WardrivingTool")
app.static('Utils/static/', 'Utils/static/',  name="static")  # Assuming your static files are in a 'static' folder

# Configure Jinja2 template environment
template_dir = 'Utils/static/'  # Path to your template directory
env = Environment(loader=FileSystemLoader(template_dir))


# Shared variable to indicate whether the loop should run or not
loop_running = False

app.ctx.interfaces = tools.showInterfaces()
app.ctx.interface = None
app.ctx.interfaceName = None

def resetDB():
    return helpers.database().__initDatabase__()
    


"""

FRONT END CODE HERE

"""

    
@app.route("/")
async def index(request):

    template = env.get_template('index.html')

    rendered_template = template.render(deviceInfo={
        "machineType": platform.machine(),
        "os": platform.system(),
        "mac": ':'.join(re.findall('..', '%012x' % uuid.getnode())).upper(),
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

    ssid = base64.b64decode(request.args.get('ssid')).decode('utf-8')
    bssid = base64.b64decode(request.args.get('bssid')).decode('utf-8')
    
    tarInfo = await helpers.database().readFromDB("savedNetworks")
    if tarInfo == {}:
        return
    template = env.get_template('attackspecific.html')
    rendered_template = template.render(deviceInfo={
        "interfaces": app.ctx.interfaces,
        "interfaceInfo": {"idx": app.ctx.interface, "name": app.ctx.interfaceName},
        "networkInfo": tarInfo[ssid]
    })
    return html(rendered_template)

"""
BACK END CODE HERE
"""
@app.route('/eventhandler', methods=["POST"])
async def eventhandler(request):
    """
    This is the event handler for the web interface. itll clean up the code a bit and make it easier to read
    
    The calls will be client from js and the event will be the action to preform

  
    """
    try:
        event = request.json.get("event")  # Use .get() to safely access the "event" key
        print(event)
        # Handle the event appropriately based on its value
    except KeyError:
        # Handle the case where "event" key is not present in the JSON request
        return json({"error": "Missing 'event' key in JSON request"})
        # define variables for use in the for loop

    # i put this first to hopefully speed up the process since this is the most common call
    if event == "cpuData":
        cpuUsage = tools.get_cpu_usage() # We use a array here because i dont give a fuck what you think
        if cpuUsage[0] == "error":
            return cpuUsage
        else:
            return json({"temperature": tools.get_cpu_temperature(), "cpuUsage":  cpuUsage[0], "cpuLevel": cpuUsage[1]})

        
    
    
    # Setting the interface
    elif event == "setinterface":
        app.ctx.interface = request.json.get("interfaceIdx")
        app.ctx.interfaceName = request.json.get("interfaceName")
        
        tools.interface = app.ctx.interface
        await helpers.database().writeToDB("interfaceInfo", {"interfaceInfo":{"idx": app.ctx.interface, "name": app.ctx.interfaceName}})

        return json({"status": "success", "interface": app.ctx.interface, "interfaceName": app.ctx.interfaceName})
        
        
        
    # setting a setting to the database
    elif event == "setsettings":
        settingCall = request.json.get("call") 
        settingPayload = request.json.get("payload")

        try:
            if settingCall == "darkmode":
                settings = await helpers.database().readFromDB("settings")
                # Update the "darkmode" setting in the database
                settings["darkmode"] = settingPayload
                await helpers.database().writeToDB("settings", settings)
                return json({"status": "success", "message": f"Darkmode set to {settingPayload}"})
            
            if settingCall == "setoption":
                settings = await helpers.database().readFromDB("settings")
                # Update the option setting in the database
                settings[str(settingPayload["option"])] = settingPayload["value"]
                await helpers.database().writeToDB("settings", settings)
                return json({"status": "success", "message": f"{settingPayload['option']} set to {settingPayload['value']}"})
            
        except Exception as e:
            return json({"status": "error", "message": str(e)})
        
        
        
    # get the settings from the database
    elif event == "getsettings":
        try:
            return json({"status": "success", "settings": await helpers.database().readFromDB("settings")})
        except Exception as e:
            return json({"status": "error", "message": str(e)})


  
    elif event == "startwardriving":
        
        global loop_running
        try:
            data = request.json
            action = data.get("action")
            interface_name = data.get("interfaceName")

            if not action or not interface_name:
                return json({"status": "error", "message": "Invalid request"})

            if action == "terminate":
                if loop_running:
                    loop_running = False
                    return json({"status": "Loop terminated"})
                else:
                    return json({"status": "error", "message": "Loop is not running"})

            elif action == "captureHandshakes":
                if loop_running:
                    return json({"status": "error", "message": "Loop is already running"})


                # Start the loop by setting the shared variable to True
                loop_running = True

                # Create an asyncio task to run the loop function
                #status = await asyncio.create_task(wardrivingLoop(action, interface_name))
                # Create thread for deauthenticateNetwork
                status = threading.Thread(target=wardrivingLoop, args=(action, interface_name))

                # Start the threads
                status.start()
                
                if status["status"] == "error":
                    return json({"status": "error", "message": "Invalid action", "response": status})
                return json({"status": "Loop started"})

        except Exception as e:
            # Handle exceptions and log errors
            print(f"Error in request processing: {str(e)}")
            return json({"status": "error", "message": "Internal error"})

        return json({"status": "error", "message": "Invalid action"})
        
    elif event == "setMode":
        
        settingPayload = request.json.get("mode")
        # retrieve the database (all of it, we'll later write it back after we change the interface mode)
        database = await helpers.database().readFromDB()
        
        try:
            if settingPayload == "monitor":
                await tools.configInterface(app.ctx.interfaceName, "monitor")
                return json({"status": "success", "message": "Interface set to monitor mode"})
            
            elif settingPayload == "managed":
                await tools.configInterface(app.ctx.interfaceName, "managed")
                await helpers.database().writeToDB(database["interfaceInfo"])
                return json({"status": "success", "message": "Interface set to managed mode"})
            
            else:
                return json({"status": "error", "message": "Invalid mode"})
        except Exception as e:  
            return json({"status": "error", "message": str(e)})
            
    elif event == "gpsdata":   
        return await json(tools.getGPSData(GPSinterface=request.json.get("GPSinterface")))
    
    
    
@app.route('/ping', methods=["GET"])
async def ping(request):
    if app.ctx.interfaceName is None:
        return json({"status": "error", "message": "noInterfaceSelected"})

    unknown = 0; unknownSaved = 0; WPANetworks = 0; WPA2Networks = 0; WEPNetworks = 0; savedWPANetworks = 0; savedWPA2Networks = 0; savedWEPNetworks = 0

    networkCount = 0
    savedNetworksCount = 0

    dumpRes = await tools.dumpAndStore(app.ctx.interface, helpers),
    
    db = await helpers.database().readFromDB()
    active_networks = db["scanResults"]
    saved_networks = db["savedNetworks"]
    
    if not active_networks:  # Check if active_networks is empty
        return json({"status": "error", "message": "noNetworksFound"})
    
    else:
        # Update saved networks if needed
        for network in active_networks.values():
            if network["SSID"] not in saved_networks:
                saved_networks[network["SSID"]] = network
    
    for network_info in active_networks.values():
        networkCount += 1
        encryption = network_info["akm"]

        if not encryption:  # Check if the encryption list is empty
            unknown =+ 1
            continue

        
        if network_info["akm"][0] == 4:
            WPA2Networks += 1
            network_info["encryption"] = "WPA2"
        elif network_info["akm"][0] == 2 or network_info["akm"][0] == 3:
            WPANetworks += 1
            network_info["encryption"] = "WPA"
        elif network_info["akm"][0] == 1:
            WEPNetworks += 1
            network_info["encryption"] = "WEP"

    for network in saved_networks.values():
        if not network["akm"]:  # Check if the encryption list is empty
            unknownSaved =+ 1
            continue
    
        savedNetworksCount += 1
        if network["akm"][0] == 4:
            savedWPA2Networks += 1
        elif network["akm"][0] == 2 or network["akm"][0] == 3:
            savedWPANetworks += 1
        elif network["akm"][0] == 1:
            savedWEPNetworks += 1
            
    await helpers.database().writeToDB("savedNetworks", saved_networks)

    return json({
        "savedNetworks": saved_networks,
        "savedNetworksCount": savedNetworksCount,
        "networks": active_networks,
        "networkCount": networkCount,
        "WPA": WPANetworks,
        "WPA2": WPA2Networks,
        "WEP": WEPNetworks,
        "savedWPA": savedWPANetworks,
        "savedWPA2": savedWPA2Networks,
        "savedWEP": savedWEPNetworks,
        "unknownSaved": unknownSaved,
        "unknownEnc": unknown,
        "interfaceUsage": tools.getInterfaceUsage(app.ctx.interface)
    })

# async local func handler so we can use global variables
async def wardrivingLoop(actionCall: str, interfaceName: str):
    """ 
    Lets be real, every function below this is a mess, i dont know what im doing, i just want it to work
    dont ask my whye i did its rthsi wuay butwe EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE 
  
 
    """
    
    global loop_running
    
    
    if interfaceName is None:
        interfaceName = app.ctx.interfaceName
    # Check if the interface is already in monitor mode
    current_mode = await tools.getInterfaceMode(interfaceName)
    print(f"Current mode: {current_mode}")

    if current_mode != "monitor":
        print("Interface is not in monitor mode")
        # If not, change it to monitor mode 
        await tools.configInterface(interfaceName, "monitor")
    

    
    while loop_running:

        active_networks = await helpers.database().readFromDB("scanResults")
         
        if actionCall == "captureHandshakes":
        
            top_5_networks = sorted(active_networks.values(), key=lambda x: x['Signal_Strength'], reverse=True)[:5]
        
            for network in top_5_networks:
                print(f"\nstarting capturing... ==> {network['SSID']}")
                tools.captureHandshake(interfaceName, network["BSSID"], timeout=10)
                print(f"\nfinished with ==> {network['SSID']}")
                asyncio.sleep(2)
                
        await asyncio.sleep(10)  # Adjust the sleep interval as needed

    
    # If the loop is stopped, return the interface to its original mode 
    #if current_mode == "monitor":
    #    return await tools.configInterface(interfaceName, current_mode)
