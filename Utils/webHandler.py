from sanic import Sanic
from sanic.response import json, html
import platform,socket,re,uuid,psutil,subprocess, pywifi
from jinja2 import Environment, FileSystemLoader
import tools, helpers



app = Sanic("WardrivingTool")
app.static('Utils/static/', 'Utils/static/', directory_view=True, name="static")  # Assuming your static files are in a 'static' folder

# Configure Jinja2 template environment
template_dir = 'Utils/static/'  # Path to your template directory
env = Environment(loader=FileSystemLoader(template_dir))



# init the session database
helpers.database().__initDatabase__()

app.ctx.interfaces = tools.toolkit.showInterfaces()
if helpers.database().readFromDB("settings") is not None:
    app.ctx.interface = helpers.database().readFromDB("settings")["interfaceInfo"]["idx"]
    app.ctx.interfaceName = helpers.database().readFromDB("settings")["interfaceInfo"]["name"]
else: app.ctx.interface = None; app.ctx.interfaceName = None
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

"""
BACK END CODE HERE
"""


# gets called when user enters site and gets the interface
@app.route('/setInterface', methods=["POST"])
async def setInterface(request):
    app.ctx.interface = request.json["interfaceIdx"]
    app.ctx.interfaceName = request.json["interfaceName"]
    tools.toolkit.__init__(app.ctx.interface)
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



@app.route('/getSettings', methods=["GET"])
async def getSettings(request):
    try:
        return json({"status": "success", "settings": helpers.database().readFromDB("settings")})
    except Exception as e:
        return json({"status": "error", "message": str(e)})




@app.route('/startwardriving', methods=["POST"])
async def startWardrive(request):
    return json({'status': "success", "results": "cum"})




@app.route('/data', methods=["GET"])
async def getData(request):
    return json({'temperature': tools.toolkit.get_cpu_temperature(), 'cpuUsage': tools.toolkit.get_cpu_usage()})


@app.route('/savedNetworks', methods=['GET'])
async def getSaved(request):
    return json({"savedNetworks": helpers.database().readFromDB("savedNetworks")})


@app.route('/networks', methods=['GET'])
async def getNetworks(request):
    
    networkRes = await tools.toolkit.scan_wifi_networks(app.ctx.interface)

    if networkRes is None:
        return json({"status": "error", "message": "No interface selected"})
    
    savedNetworks = helpers.database().readFromDB("savedNetworks")
    
    
    for network in networkRes.values():
        if network["ssid"] in savedNetworks:
            network["saved"] = True
        else:
            savedNetworks[network["ssid"]] = network  
            helpers.database().writeToDB("savedNetworks", savedNetworks) 
            network["saved"] = False
            
    networkUsage = tools.toolkit.getInterfaceUsage(app.ctx.interface)
            

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