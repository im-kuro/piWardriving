from sanic import Sanic
from sanic.response import json, html
import platform,socket,re,uuid,psutil, asyncio, base64, time, pywifi
from jinja2 import Environment, FileSystemLoader
# Local imports
import tools, helpers

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
app.ctx.currentInterfaceMode = None



"""

FRONT END CODE HERE

"""


    
    
@app.route("/")
async def index(request):

    template = env.get_template('index.html')

    rendered_template = template.render(deviceInfo={
        "machineType": platform.machine(),
        "os": platform.system(),
        "mac": ':'.join(re.findall('..', '%012x' % uuid.getnode())),
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
    template = env.get_template('attackspecific.html')
    rendered_template = template.render(deviceInfo={
        "interfaces": app.ctx.interfaces,
        "interfaceInfo": {"idx": app.ctx.interface, "name": app.ctx.interfaceName},
        "ssid": ssid,
        "bssid": bssid,
        "tarInfo": tarInfo[ssid]
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
        
    # i put this first to hopefully speed up the process since this is the most common call
    if event == "cpuData":
        return json({"temperature": tools.get_cpu_temperature(), "cpuUsage":  tools.get_cpu_usage()})
            
    elif event == "ping":
        if app.ctx.interfaceName is None:
            return json({"status": "error", "message": "noInterfaceSelected"})

        print(f"Current mode: {app.ctx.currentInterfaceMode}")

        #if app.ctx.currentInterfaceMode != "monitor":
        #    print("Interface is not in monitor mode, setting now.")
        #    start_time = time.time()
        #    # If not, change it to monitor mode
        #    await tools.configInterface(app.ctx.interfaceName, "monitor")
        #    end_time = time.time()
        #    execution_time = end_time - start_time
        #    print(f"tools.configInterface(app.ctx.interfaceName, 'monitor') - Execution time: {execution_time} seconds")
#
        #    app.ctx.currentInterfaceMode = "monitor"
        # Use asyncio.gather to concurrently execute dumpAndStore and database reads

        await tools.dumpAndStore(app.ctx.interface, helpers),

        db = await helpers.database().readFromDB()
        active_networks = db["scanResults"]
        saved_networks = db["savedNetworks"]
        
        
        if active_networks == {}:
            pass
        else:
            # Update saved networks if needed
            for network in active_networks.values():
                if network["SSID"] not in saved_networks:
                    saved_networks[network["SSID"]] = network

            await helpers.database().writeToDB("savedNetworks", saved_networks)
        # define variables for use in the for loop
        unknown = 0; unknownSaved = 0; WPANetworks = 0; WPA2Networks = 0; WEPNetworks = 0; savedWPANetworks = 0; savedWPA2Networks = 0; savedWEPNetworks = 0

        networkCount = 0
        savedNetworksCount = 0
        
        for network_info in active_networks.values():
            networkCount += 1
            encryption = network_info["akm"]

            if not encryption:  # Check if the encryption list is empty
                unknown =+ 1
                continue

            
            if network_info["akm"][0] == 4:
                WPA2Networks += 1
            elif network_info["akm"][0] == 2 or network_info["akm"][0] == 3:
                WPANetworks += 1
            elif network_info["akm"][0] == 1:
                WEPNetworks += 1


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

        
    
    
    # Setting the interface
    elif event == "setinterface":
        app.ctx.interface = request.json.get("interfaceIdx")
        app.ctx.interfaceName = request.json.get("interfaceName")
        #app.ctx.currentInterfaceMode = await tools.getInterfaceMode(app.ctx.interfaceName)
        tools.interface = app.ctx.interface
        await helpers.database().writeToDB("interfaceInfo", {"interfaceInfo":{"idx": app.ctx.interface, "name": app.ctx.interfaceName, "mode": app.ctx.currentInterfaceMode}})

        return json({"status": "success", "interface": app.ctx.interface, "interfaceName": app.ctx.interfaceName, "interfaceMode": app.ctx.currentInterfaceMode})
        
        
        
    # setting a setting to the database
    elif event == "setsettings":
        settingCall = request.json.get("call")  # Use .get() to safely get the value
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
    
        #if app.ctx.interface is None:
        #    return json({"status": "error", "message": "noInterfaceSelected"})
        #if tools.checkMonitorModeSupport(app.ctx.interfaceName) == False:
        #    return json({"status": "error", "message": "monitorModeNotSupported"})
        
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
                return json({"status": "error", "message": "loop is already running"})


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
    
            

# async local func handler so we can use global variables
async def wardrivingLoop(actionCall: str, interfaceName: str):
    global loop_running
    if interfaceName is None:
        interfaceName = app.ctx.interfaceName
    # Check if the interface is already in monitor mode
    #current_mode = await tools.getInterfaceMode(interfaceName)
    #print(f"Current mode: {current_mode}")
    
    #if current_mode != "monitor":
    #    print("Interface is not in monitor mode")
    #    # If not, change it to monitor mode 
    #    await tools.configInterface(interfaceName, "monitor")

    
    while loop_running:
        # Use asyncio.gather to concurrently execute dumpAndStore and database reads
        dump_result, saved_networks = await asyncio.gather(
            tools.dumpAndStore(app.ctx.interface, helpers),
            helpers.database().readFromDB("savedNetworks"),
        )
        active_networks = await helpers.database().readFromDB("scanResults")
        
        if actionCall == "captureHandshakes":
            pass
        
        await asyncio.sleep(5)  # Adjust the sleep interval as needed

    # If the loop is stopped, return the interface to its original mode 
    #if current_mode == "monitor":
    #    return await tools.configInterface(interfaceName, current_mode)



if __name__ == "__main__":
    helpers.database().__initDatabase__()
    
    print("You can now browse to http://127.0.0.1:6969/ to view the web interface (please plug in your wifi adapter if you haven't already)")
    # Start the web server
    app.run(host="127.0.0.1", port=6969)
    print("Web server stopped")
    # init the session database again to clear it
    helpers.database().__initDatabase__()